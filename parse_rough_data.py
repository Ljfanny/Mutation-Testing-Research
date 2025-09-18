#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Parse PIT mutation XMLs and corresponding logs into structured JSON outputs.

Example:
  python parse_rough_data.py \
    --main-dir for_checking_OID \
    --projects sling-org-apache-sling-auth-core \
    --strategies by-proportions \
    --rounds 6 \
    --verbose
"""

from __future__ import annotations

import argparse
import json
import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple, Iterable, Optional
import xml.etree.ElementTree as ET


# ------------------------------- Constants -------------------------------- #

KILLED = "KILLED"
SURVIVED = "SURVIVED"
FAIL = False    # test failed (killing test)
PASS = True     # test passed (succeeding test)

# indices for id_others_mapping[mutant_id] = [replacement_time_ms, running_time_ms]
REPLACEMENT_IDX = 0
RUNTIME_IDX = 1


# ------------------------------- Regexes ---------------------------------- #
# Pre-compile regex patterns for performance and safety.
RE_MUTANT = re.compile(
    r"\[clazz=([^,]+), method=([^,]+), methodDesc=([^]]+)\], indexes=\[([^]]+)\], mutator=([^,]+)\]"
)
RE_TEST_DESC_JUNIT4 = re.compile(r"testClass=([^,]+), name=([^\]]+).*Running time: (\d+) ms")
RE_TEST_DESC_JUNIT5 = re.compile(r"testClass=([^,]+), name=(.*)\].*Running time: (\d+) ms")
RE_RUNTIME = re.compile(r"run all related tests in (\d+) ms")
RE_REPLACE_TIME = re.compile(r"replaced class with mutant in (\d+) ms")
RE_COMPLETE_SEC = re.compile(r"Completed in (\d+) seconds")
RE_GROUP_BOUNDARY = re.compile(r"Run all (\d+) mutants in (\d+) ms")
RE_FALLBACK_TEST_MS = re.compile(r"Test Description.*?(\d+)\s*ms", re.DOTALL)


# ------------------------------- Dataclasses ------------------------------- #

@dataclass
class Config:
    main_dir: Path
    xmls_dir: Path
    logs_dir: Path
    outputs_dir: Path
    basis_dir: Path
    projects: List[str]
    strategies: List[str]
    rounds: int
    proj_junit_map: Dict[str, str]
    verbose: bool


@dataclass
class RunState:
    """Per (project, strategy, round) mutable state containers."""
    id_status_mapping: Dict[int, str]                # mutant_id -> {KILLED|SURVIVED|...}
    id_info_mapping: Dict[int, List[Tuple[int, bool, int]]]  # mutant_id -> [(test_id, PASS/FAIL, runtime_ms)]
    id_others_mapping: Dict[int, List[int]]          # mutant_id -> [replacement_ms, running_ms]
    completion_time_mapping: Dict[Tuple[str, str], int]  # (strategy, round) -> seconds
    ids_in_block: List[int]                          # temp collector for group info
    group_info_arr: List[List[object]]               # [[time_ms, mutant_num, (ids...)]]

    # Static cross-round info (filled before each run)
    id_mutant_mapping: Dict[int, Dict[str, object]]  # mutant_id -> mutant dict
    test_id_mapping: Dict[str, int]                  # "class.method" or junit key -> test_id


# ------------------------------- Utilities -------------------------------- #

def setup_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        format="%(asctime)s %(levelname)s: %(message)s",
        level=level
    )


def load_json(path: Path) -> object:
    """Load a JSON file with informative errors."""
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError as e:
        raise RuntimeError(f"Required JSON not found: {path}") from e
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Bad JSON format: {path} ({e})") from e


def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def iter_projects(projects: List[str], projects_file: Optional[Path]) -> List[str]:
    """Merge projects from CLI and optional file."""
    items = list(projects)
    if projects_file:
        try:
            text = projects_file.read_text(encoding="utf-8")
            for line in text.splitlines():
                line = line.strip()
                if line and not line.startswith("#"):
                    items.append(line)
        except FileNotFoundError as e:
            raise RuntimeError(f"Projects file not found: {projects_file}") from e
    # de-duplicate while preserving order
    seen = set()
    uniq = []
    for x in items:
        if x not in seen:
            seen.add(x)
            uniq.append(x)
    return uniq


def load_proj_junit_map(default_map: Dict[str, str], override_json: Optional[Path]) -> Dict[str, str]:
    """Load the project->junit version mapping; allow override via JSON file."""
    if override_json:
        data = load_json(override_json)
        if not isinstance(data, dict):
            raise RuntimeError(f"--junit-map-file must be a JSON object: {override_json}")
        # normalize keys to str, values to 'junit4' | 'junit5'
        out = {}
        for k, v in data.items():
            vs = str(v).strip().lower()
            if vs not in {"junit4", "junit5"}:
                raise RuntimeError(f"Invalid JUnit version for {k}: {v} (must be 'junit4' or 'junit5')")
            out[str(k)] = vs
        return out
    return default_map


# ------------------------------- Core Logic -------------------------------- #

def process_block(block_lines: Iterable[str],
                  strategy: str,
                  rnd: int,
                  state: RunState,
                  test_desc_re: re.Pattern[str],
                  completion_time_mapping: Dict[Tuple[str, int], int]) -> None:
    """
    Process one 'start running ...' block: parse mutant info, timings, tests, group/complete time.
    """
    block_str = "".join(block_lines)

    m_mut = RE_MUTANT.search(block_str)
    if not m_mut:
        return

    # Parse mutant signature from log block
    mutant = {
        "clazz": m_mut.group(1),
        "method": m_mut.group(2),
        "methodDesc": m_mut.group(3),
        "indexes": [int(i.strip()) for i in m_mut.group(4).split(",") if i.strip()],
        "mutator": m_mut.group(5),
    }

    # Map mutant dict -> mutant_id using id_mutant_mapping
    mutant_id = 0
    for mid, md in state.id_mutant_mapping.items():
        if mutant == md:
            mutant_id = mid
            break

    state.ids_in_block.append(mutant_id)
    state.id_others_mapping.setdefault(mutant_id, [0, 0])

    status = state.id_status_mapping.get(mutant_id)

    # Replacement time (per-mutant)
    if m := RE_REPLACE_TIME.search(block_str):
        state.id_others_mapping[mutant_id][REPLACEMENT_IDX] = int(m.group(1))

    # Test descriptions & per-test runtime (only for killed/survived)
    if status in {KILLED, SURVIVED}:
        for clz, name, rt_ms in test_desc_re.findall(block_str):
            test_key = f"{clz}.{name}"
            if test_key not in state.test_id_mapping:
                continue
            test_id = state.test_id_mapping[test_key]
            # Replace the third element (runtime) for the test tuple in id_info_mapping[mutant_id]
            for i, tup in enumerate(state.id_info_mapping.get(mutant_id, [])):
                if test_id == tup[0]:
                    state.id_info_mapping[mutant_id][i] = (tup[0], tup[1], int(rt_ms))
                    break

    # Running time of this mutant (prefer aggregated 'run all related tests'; else sum fallback)
    if m := RE_RUNTIME.search(block_str):
        state.id_others_mapping[mutant_id][RUNTIME_IDX] = int(m.group(1))
    else:
        ms_list = [int(x) for x in RE_FALLBACK_TEST_MS.findall(block_str)]
        state.id_others_mapping[mutant_id][RUNTIME_IDX] = sum(ms_list)

    # Group boundary info
    if m := RE_GROUP_BOUNDARY.search(block_str):
        group_mutants = int(m.group(1))
        group_ms = int(m.group(2))
        state.group_info_arr.append([group_ms, group_mutants, tuple(state.ids_in_block)])
        state.ids_in_block.clear()

    # Completed time (whole run)
    if m := RE_COMPLETE_SEC.search(block_str):
        completion_time_mapping[(strategy, rnd)] = int(m.group(1))


def parse_log(project: str,
              strategy: str,
              rnd: int,
              logs_dir: Path,
              state: RunState,
              test_desc_re: re.Pattern[str],
              completion_time_mapping: Dict[Tuple[str, int], int]) -> None:
    """
    Parse one log file and process its blocks.
    """
    log_path = logs_dir / f"{project}_{strategy}_{rnd}.log"
    if not log_path.exists():
        logging.warning("Log not found: %s", log_path)
        return

    with log_path.open("r", encoding="utf-8", errors="replace") as f:
        blocks: List[str] = []
        capturing = False
        for line in f:
            if "start running" in line:
                if blocks:
                    process_block(blocks, strategy, rnd, state, test_desc_re, completion_time_mapping)
                blocks = [line]
                capturing = True
            elif capturing:
                blocks.append(line)
        # process last block if any
        if blocks:
            process_block(blocks, strategy, rnd, state, test_desc_re, completion_time_mapping)


def parse_xml(project: str,
              strategy: str,
              rnd: int,
              xmls_dir: Path,
              state: RunState) -> None:
    """
    Parse one PIT XML (mutations) to populate:
      - id_status_mapping
      - id_info_mapping [(test_id, PASS/FAIL, runtime_ms placeholder=0)]
    """
    xml_path = xmls_dir / f"{project}_{strategy}_{rnd}.xml"
    try:
        tree = ET.parse(xml_path)
    except FileNotFoundError as e:
        raise RuntimeError(f"XML file not found: {xml_path}") from e
    except ET.ParseError as e:
        raise RuntimeError(f"XML parse error in {xml_path}: {e}") from e

    root = tree.getroot()
    for mutation in root.findall("mutation"):
        mutant: Dict[str, object] = {}
        status = mutation.get("status", "")

        # Defaults for tests (maybe missing)
        killing_tests: Iterable[str] = []
        succeeding_tests: Iterable[str] = []

        for child in mutation:
            tag = child.tag
            text = (child.text or "").strip()

            if tag == "mutatedClass":
                mutant["clazz"] = text
            elif tag == "mutatedMethod":
                mutant["method"] = text
            elif tag == "methodDescription":
                mutant["methodDesc"] = text
            elif tag == "indexes":
                values = []
                for elem in child.findall("*"):
                    if elem.text and elem.text.strip():
                        values.append(int(elem.text.strip()))
                mutant["indexes"] = values
            elif tag == "mutator":
                mutant["mutator"] = text
            elif tag == "killingTests":
                parts = [p.strip() for p in text.split("|") if p.strip()]
                killing_tests = tuple(sorted(set(parts))) if parts else []
            elif tag == "succeedingTests":
                parts = [p.strip() for p in text.split("|") if p.strip()]
                succeeding_tests = tuple(sorted(set(parts))) if parts else []

        # Find mutant_id by exact dict match
        mutant_id = 0
        for mid, md in state.id_mutant_mapping.items():
            if mutant == md:
                mutant_id = mid
                break

        state.id_status_mapping[mutant_id] = status
        state.id_info_mapping[mutant_id] = []

        # Merge tests; mark conflicts as -1 (ignored)
        test_status_info: Dict[int, int] = {}  # test_id -> {0 for FAIL, 1 for PASS, -1 conflict}

        for t in killing_tests:
            if t in state.test_id_mapping:
                tid = state.test_id_mapping[t]
                if tid in test_status_info and test_status_info[tid] != 0:
                    test_status_info[tid] = -1
                else:
                    test_status_info[tid] = 0

        for t in succeeding_tests:
            if t in state.test_id_mapping:
                tid = state.test_id_mapping[t]
                if tid in test_status_info and test_status_info[tid] != 1:
                    test_status_info[tid] = -1
                else:
                    test_status_info[tid] = 1

        # Persist only consistent marks; runtime placeholder = 0
        for tid, mark in sorted(test_status_info.items()):
            if mark == -1:
                continue
            state.id_info_mapping[mutant_id].append((tid, PASS if mark == 1 else FAIL, 0))


def write_round_outputs(output_dir: Path, strategy: str, rnd: int, state: RunState) -> None:
    """
    Write JSON artifacts for one (strategy, round):
      - id_status_mapping.json
      - id_info_mapping.json
      - id_others_mapping.json
      - group_info.json
    """
    out_subdir = output_dir / f"{strategy}_{rnd}"
    ensure_dir(out_subdir)

    (out_subdir / "id_status_mapping.json").write_text(
        json.dumps(state.id_status_mapping, indent=4), encoding="utf-8"
    )
    (out_subdir / "id_info_mapping.json").write_text(
        json.dumps(state.id_info_mapping, indent=4), encoding="utf-8"
    )
    (out_subdir / "id_others_mapping.json").write_text(
        json.dumps(state.id_others_mapping, indent=4), encoding="utf-8"
    )
    (out_subdir / "group_info.json").write_text(
        json.dumps(state.group_info_arr, indent=4), encoding="utf-8"
    )


def write_completion_times(project_dir: Path,
                           completion_time_mapping: Dict[Tuple[str, int], int]) -> None:
    """
    Persist completion times as a list of [ [strategy, round], seconds ] for JSON stability.
    """
    data = [ [list(k), v] for k, v in completion_time_mapping.items() ]
    (project_dir / "completion_time.json").write_text(
        json.dumps(data, indent=4), encoding="utf-8"
    )


# ------------------------------- Main Flow -------------------------------- #

def run_for_project(proj: str, cfg: Config) -> None:
    """
    Execute the full parse pipeline for one project across all strategies and rounds.
    """
    logging.info("== Project: %s ==", proj)

    project_dir = cfg.outputs_dir / proj
    ensure_dir(project_dir)

    # Load mapping files produced by the "basis" phase
    id_mutant_mapping_path = cfg.basis_dir / proj / "id_mutant_mapping.json"
    id_test_mapping_path = cfg.basis_dir / proj / "id_test_mapping.json"

    id_mutant_mapping = {int(k): v for k, v in load_json(id_mutant_mapping_path).items()}
    id_test_mapping = {int(k): v for k, v in load_json(id_test_mapping_path).items()}
    # Inverse mapping: test qualified name -> id
    test_id_mapping = {v: k for k, v in id_test_mapping.items()}

    # Completion time cache
    completion_path = project_dir / "completion_time.json"
    completion_time_mapping: Dict[Tuple[str, int], int] = {}
    if completion_path.exists():
        # old format compatibility: [[ [strategy, round], seconds], ...]
        try:
            loaded = json.loads(completion_path.read_text(encoding="utf-8"))
            for pair, sec in loaded:
                completion_time_mapping[(pair[0], int(pair[1]))] = int(sec)
        except Exception:
            logging.warning("Ignoring invalid completion_time.json (will rewrite): %s", completion_path)

    # Choose test description regex by JUnit flavor
    junit = cfg.proj_junit_map.get(proj)
    if junit not in {"junit4", "junit5"}:
        raise RuntimeError(
            f"Unknown/unspecified JUnit flavor for project '{proj}'. "
            f"Provide it via --junit-map-file or extend the default mapping."
        )
    test_desc_re = RE_TEST_DESC_JUNIT4 if junit == "junit4" else RE_TEST_DESC_JUNIT5

    for strategy in cfg.strategies:
        for rnd in range(cfg.rounds):
            logging.info("Process %s | strategy=%s | round=%d", proj, strategy, rnd)

            state = RunState(
                id_status_mapping={},
                id_info_mapping={},
                id_others_mapping={},
                completion_time_mapping={},  # not used directly; we pass external dict
                ids_in_block=[],
                group_info_arr=[],
                id_mutant_mapping=id_mutant_mapping,
                test_id_mapping=test_id_mapping,
            )

            # Fill from XML first (mutant statuses and per-test lists)
            parse_xml(project=proj, strategy=strategy, rnd=rnd, xmls_dir=cfg.xmls_dir, state=state)

            # Then augment with log info (timings, group info, completion)
            parse_log(
                project=proj,
                strategy=strategy,
                rnd=rnd,
                logs_dir=cfg.logs_dir,
                state=state,
                test_desc_re=test_desc_re,
                completion_time_mapping=completion_time_mapping,
            )

            # Persist per-(strategy, round) artifacts
            write_round_outputs(project_dir, strategy, rnd, state)

    # Persist completion times (across all strategies/rounds for this project)
    write_completion_times(project_dir, completion_time_mapping)

    logging.info("Done project: %s", proj)


def build_default_junit_map() -> Dict[str, str]:
    """
    Default project->JUnit mapping (can be overridden via --junit-map-file).
    """
    return {
        "commons-codec": "junit5",
        "delight-nashorn-sandbox": "junit4",
        "jimfs": "junit4",
        "commons-cli": "junit5",
        "assertj-assertions-generator": "junit5",
        "commons-collections": "junit5",
        "commons-csv": "junit5",
        "commons-net": "junit5",
        "empire-db": "junit4",
        "guava": "junit4",
        "handlebars.java": "junit5",
        "httpcore": "junit5",
        "java-design-patterns": "junit5",
        "jfreechart": "junit5",
        "jooby": "junit5",
        "JustAuth": "junit4",
        "maven-dependency-plugin": "junit5",
        "maven-shade-plugin": "junit4",
        "Mybatis-PageHelper": "junit4",
        "riptide": "junit5",
        "sling-org-apache-sling-auth-core": "junit4",
        "stream-lib": "junit4",
    }


def parse_args() -> Config:
    ap = argparse.ArgumentParser(
        description="Parse mutation XML + logs into normalized JSONs (per strategy/round)."
    )
    ap.add_argument("--main-dir", required=True, type=Path,
                    help="Workspace root (contains 'xmls', 'logs', 'parsed_dir', etc.)")
    ap.add_argument("--projects", nargs="*", default=[],
                    help="Project names (space-separated).")
    ap.add_argument("--projects-file", type=Path,
                    help="Optional file with one project per line (supports comments with '#').")
    ap.add_argument("--strategies", nargs="+", required=True,
                    help="Strategy names to process (e.g., by-proportions default ...).")
    ap.add_argument("--rounds", type=int, default=6,
                    help="Number of rounds per strategy (default: 6).")
    ap.add_argument("--junit-map-file", type=Path,
                    help="Optional JSON file overriding project->JUnit version mapping.")
    ap.add_argument("--verbose", action="store_true",
                    help="Enable verbose logging.")
    args = ap.parse_args()

    projects = iter_projects(args.projects, args.projects_file)
    if not projects:
        raise SystemExit("No projects specified. Use --projects or --projects-file.")

    default_map = build_default_junit_map()
    proj_junit_map = load_proj_junit_map(default_map, args.junit_map_file)

    main_dir: Path = args.main_dir
    xmls_dir = main_dir / "xmls"
    logs_dir = main_dir / "logs"
    outputs_dir = main_dir / "parsed_dir"
    basis_dir = outputs_dir / "basis"

    return Config(
        main_dir=main_dir,
        xmls_dir=xmls_dir,
        logs_dir=logs_dir,
        outputs_dir=outputs_dir,
        basis_dir=basis_dir,
        projects=projects,
        strategies=args.strategies,
        rounds=args.rounds,
        proj_junit_map=proj_junit_map,
        verbose=args.verbose,
    )


def main() -> None:
    cfg = parse_args()
    setup_logging(cfg.verbose)

    # Basic directory checks
    for p in [cfg.xmls_dir, cfg.logs_dir, cfg.basis_dir]:
        if not p.exists():
            logging.warning("Directory not found (it may be created elsewhere): %s", p)

    ensure_dir(cfg.outputs_dir)

    for proj in cfg.projects:
        try:
            run_for_project(proj, cfg)
        except Exception as e:
            logging.error("Project failed: %s (%s)", proj, e)
            # Continue with other projects rather than exiting immediately.

    logging.info("All done.")


if __name__ == "__main__":
    main()
