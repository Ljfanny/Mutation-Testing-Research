#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Anti-flakiness analyzer: filter out unstable (flaky) (mutant_id, test_id) pairs first,
then compute ALL metrics ONLY on the remaining stable pairs (safe_pairs).

Flakiness definition used here:
- For each strategy, look at a pair's statuses across rounds (True/False/None).
- If within a strategy the pair is NOT "all True" AND NOT "all False" (i.e., mixed True/False or contains None),
  then that pair is unstable for that strategy (compressed to None).
- After compressing per-strategy, if any strategy yields None OR different strategies disagree (some True, some False),
  the pair is considered flaky overall and is excluded from all statistics.

Outputs:
- Human-readable per-strategy summaries (optional, for reference).
- A CSV listing the filtered-out flaky pairs (for audit only, NOT used for stats).
- Optional per-project total runtime CSVs computed on safe_pairs only.

Example:
  python filter_flakiness.py \
    --parsed-dir for_checking_OID/parsed_dir \
    --projects commons-cli commons-codec jimfs \
    --strategies default single-group single-group_errors-at-the-end by-proportions \
    --rounds 6 \
    --output-file for_checking_OID/INFO_detailed.txt \
    --flaky-dir for_checking_OID/flaky_tables \
    --total-runtime-dir for_checking_OID/total_runtime \
    --emit-runtime \
    --verbose

"""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Iterable, Optional

import numpy as np
import pandas as pd
from scipy.stats import ttest_ind, mannwhitneyu


# ----------------------------- Logging / FS utils ----------------------------- #

def setup_logging(verbose: bool) -> None:
    """Initialize global logging format and level."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(format="%(asctime)s %(levelname)s: %(message)s", level=level)


def ensure_dir(p: Path) -> None:
    """mkdir -p helper to ensure a directory exists."""
    p.mkdir(parents=True, exist_ok=True)


def append_line(path: Path, text: str, enabled: bool) -> None:
    """Append a line to a text file when enabled (for human-readable summaries)."""
    if not enabled:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(text + "\n")


# ----------------------------- Type aliases ----------------------------- #

Pair = Tuple[int, int]  # (mutant_id, test_id)

# id_info_mapping item: List[Tuple[test_id, status(bool), runtime(int_ms)]]
IdInfoMapping = Dict[str, List[Tuple[int, bool, int]]]
IdReplMapping = Dict[str, int]


# ----------------------------- Load helpers ----------------------------- #

def load_json(path: Path) -> object:
    """Load JSON with clear error messages."""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as e:
        raise RuntimeError(f"File not found: {path}") from e
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Bad JSON: {path} ({e})") from e


def load_basis_mappings(parsed_dir: Path, project: str) -> Tuple[Dict[int, dict], Dict[int, str]]:
    """
    Load basis mappings:
      - id_mutant_mapping.json  (int -> {clazz/method/...})
      - id_test_mapping.json    (int -> test qualified name)
    """
    base = parsed_dir / "basis"
    id_mutant = {int(k): v for k, v in load_json(base / f"{project}/id_mutant_mapping.json").items()}
    id_test = {int(k): v for k, v in load_json(base / f"{project}/id_test_mapping.json").items()}
    return id_mutant, id_test


def load_round_info(parsed_dir: Path, project: str, strategy: str, rounds: int) -> List[IdInfoMapping]:
    """
    Load per-round id_info_mapping for a (project, strategy):
      parsed_dir/<project>/<strategy>_<rnd>/id_info_mapping.json
    Returns a list of dicts (length == rounds).
    """
    out: List[IdInfoMapping] = []
    for rnd in range(rounds):
        path = parsed_dir / f"{project}/{strategy}_{rnd}/id_info_mapping.json"
        if not path.exists():
            raise RuntimeError(f"Missing id_info_mapping: {path}")
        out.append(load_json(path))  # type: ignore
    return out


def load_round_repl(parsed_dir: Path, project: str, strategy: str, rounds: int) -> List[IdReplMapping]:
    """
    Load per-round id_repl_mapping for a (project, strategy):
      parsed_dir/<project>/<strategy>_<rnd>/id_others_mapping.json
    Returns a list of dicts (length == rounds).
    """
    out: List[IdReplMapping] = []
    for rnd in range(rounds):
        path = parsed_dir / f"{project}/{strategy}_{rnd}/id_others_mapping.json"
        if not path.exists():
            raise RuntimeError(f"Missing id_repl_mapping: {path}")
        out.append( {k: v[0] for k, v in load_json(path).items()}) # type: ignore
    return out


# ----------------------------- Aggregation logic ----------------------------- #

def aggregate_pair_status_and_runtime(
    round_infos: List[IdInfoMapping],
) -> Tuple[Dict[Pair, List[Optional[bool]]], Dict[Pair, List[int]]]:
    """
    Aggregate per-strategy, across rounds:
      - status_mapping: pair -> [status per round: True/False/None]
      - runtime_mapping: pair -> [runtime_ms per round]
    Note: This checks stability within a strategy only; cross-strategy stability is resolved later.
    """
    rounds = len(round_infos)
    status_mapping: Dict[Pair, List[Optional[bool]]] = {}
    runtime_mapping: Dict[Pair, List[int]] = {}

    for rnd, id_info in enumerate(round_infos):
        for mutant_id_str, test_tuples in id_info.items():
            mutant_id = int(mutant_id_str)
            for test_id, status_bool, runtime_ms in test_tuples:
                key: Pair = (mutant_id, test_id)
                if key not in status_mapping:
                    status_mapping[key] = [None] * rounds
                    runtime_mapping[key] = [0] * rounds
                status_mapping[key][rnd] = bool(status_bool)
                runtime_mapping[key][rnd] = int(runtime_ms)

    return status_mapping, runtime_mapping


def summarize_strategy_for_humans(
    strategy: str,
    status_mapping: Dict[Pair, List[Optional[bool]]],
    id_mutant_mapping: Dict[int, dict],
    id_test_mapping: Dict[int, str],
    output_stream: Optional[Path],
    enable_append: bool,
) -> None:
    """
    Human-readable per-strategy summary (counts). This does NOT filter flakiness;
    it only describes what's inside a single strategy across its rounds.
    """
    clazz_set = set()
    test_set = set()
    mutant_status_overall: Dict[int, bool] = {}
    pair_num = failed_pair = passed_pair = flaky_pair = 0

    for (mutant_id, test_id), status_arr in status_mapping.items():
        clazz_set.add(id_mutant_mapping[mutant_id]["clazz"])
        test_set.add(test_id)
        pair_num += 1

        all_true = all(s is True for s in status_arr)
        all_false = all(s is False for s in status_arr)

        if all_true:
            passed_pair += 1
            mutant_status_overall.setdefault(mutant_id, True)
        elif all_false:
            failed_pair += 1
            mutant_status_overall[mutant_id] = False
        else:
            # Mixed True/False or contains None inside this strategy -> unstable for this strategy
            flaky_pair += 1

    survived = sum(1 for v in mutant_status_overall.values() if v)
    killed = sum(1 for v in mutant_status_overall.values() if not v)
    mutant_total = len(id_mutant_mapping)

    if output_stream:
        append_line(output_stream, strategy.capitalize() + ":", enabled=enable_append)
        append_line(output_stream, f"Number of classes: {len(clazz_set)}", enable_append)
        append_line(output_stream, f"Number of tests: {len(test_set)}", enable_append)
        append_line(output_stream, f"Number of mutants: {mutant_total}", enable_append)
        append_line(output_stream, f"Number of killed mutants: {killed}", enable_append)
        append_line(output_stream, f"Number of survived mutants: {survived}", enable_append)
        append_line(output_stream, f"Number of pairs: {pair_num}", enable_append)
        append_line(output_stream, f"Number of passed pairs (all True across rounds): {passed_pair}", enable_append)
        append_line(output_stream, f"Number of failed pairs (all False across rounds): {failed_pair}", enable_append)
        append_line(output_stream, f"Number of flaky pairs (mixed/None across rounds): {flaky_pair}\n", enable_append)


def filter_flaky_pairs(
    all_strategy_status: Dict[str, Dict[Pair, List[Optional[bool]]]],
    id_mutant_mapping: Dict[int, dict],
    id_test_mapping: Dict[int, str],
    default_strategy: str,
) -> Tuple[pd.DataFrame, List[Pair], int]:
    """
    Core anti-flakiness filter.

    Step 1 (compress within strategy):
      For each pair, per strategy:
        - True  if all rounds are True
        - False if all rounds are False
        - None  otherwise (mixed True/False or contains None) => unstable for that strategy
    Step 2 (merge across strategies):
      - If any strategy yields None, the pair is flaky.
      - Else if strategies disagree (some True, some False), the pair is flaky.
      - Only all-True or all-False across strategies => stable (safe_pairs).

    Returns:
      - flaky_df: audit rows for excluded pairs (NOT used for stats)
      - safe_pairs: the stable pairs used for all downstream statistics
      - none_count: how many excluded pairs had at least one strategy compressed to None
    """
    pair_info_cols = ["clazz", "method", "methodDesc", "indexes", "mutator", "test"]
    cols = pair_info_cols + [default_strategy] + [s for s in all_strategy_status if s != default_strategy]
    df = pd.DataFrame(None, columns=cols)

    # Strategy-level compression to a single value (True/False/None)
    merged: Dict[Pair, List[Optional[bool]]] = {}
    strategies_order = [default_strategy] + [s for s in all_strategy_status if s != default_strategy]

    for strategy in strategies_order:
        for pair, status_arr in all_strategy_status[strategy].items():
            all_true = all(s is True for s in status_arr)
            all_false = all(s is False for s in status_arr)
            v: Optional[bool] = True if all_true else (False if all_false else None)
            merged.setdefault(pair, [None] * len(strategies_order))
            merged[pair][strategies_order.index(strategy)] = v

    none_num = 0
    safe_pairs: List[Pair] = []

    for pair, condensed_arr in merged.items():
        # Keep only pairs with no None and unanimous agreement (all True or all False)
        if None not in condensed_arr and (all(condensed_arr) or not any(condensed_arr)):
            safe_pairs.append(pair)
            continue

        # Otherwise: flaky -> add to audit table
        mut = id_mutant_mapping[pair[0]]
        test_name = id_test_mapping[pair[1]]
        df.loc[len(df.index)] = [
            mut["clazz"], mut["method"], mut["methodDesc"], mut["indexes"], mut["mutator"], test_name
        ] + condensed_arr
        if None in condensed_arr:
            none_num += 1

    return df, safe_pairs, none_num


def compute_total_runtime_per_round(
    safe_pairs: List[Pair],
    runtime_map: Dict[Pair, List[int]],
    repl_map_by_round: List[IdReplMapping],
) -> np.ndarray:
    """
    Compute total runtime per round on SAFE pairs only:
      - Sum pair runtimes per round.
      - Add per-mutant replacement time once per mutant (per round).
    """
    rounds = len(next(iter(runtime_map.values()))) if runtime_map else 0
    total = np.zeros(rounds, dtype=float)

    # Sum pair runtimes
    for pair in safe_pairs:
        total += np.array(runtime_map[pair], dtype=float)

    return total


# ----------------------------- CLI ----------------------------- #

def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description="Filter out flaky pairs first, then compute metrics ONLY on stable pairs."
    )
    ap.add_argument("--parsed-dir", type=Path, required=True,
                    help="Root parsed dir.")
    ap.add_argument("--projects", nargs="*", default=[],
                    help="Project names (space separated).")
    ap.add_argument("--projects-file", type=Path,
                    help="Optional file with one project per line (# comments allowed).")
    ap.add_argument("--strategies", nargs="+", required=True,
                    help="Strategy/strategies to analyze (include the default strategy if comparing).")
    ap.add_argument("--default-strategy", type=str, default="default",
                    help="Baseline strategy name; used only for column ordering in the audit CSV.")
    ap.add_argument("--rounds", type=int, default=6,
                    help="Number of rounds per strategy (default: 6).")
    ap.add_argument("--output-file", type=Path, default=Path("INFO_others.txt"),
                    help="Append human-readable summaries here (optional).")
    ap.add_argument("--flaky-dir", type=Path, default=Path("flaky_tables"),
                    help="Directory to write the AUDIT table of filtered-out (flaky) pairs (CSV).")
    ap.add_argument("--total-runtime-dir", type=Path, default=Path("total_runtime"),
                    help="Directory to write per-project total runtime CSVs (on SAFE pairs only).")
    ap.add_argument("--emit-runtime", action="store_true",
                    help="If set, compute and emit total runtime tables on SAFE pairs only.")
    ap.add_argument("--verbose", action="store_true", help="Verbose logging.")
    return ap.parse_args()


def iter_projects(cli_projects: List[str], projects_file: Optional[Path]) -> List[str]:
    """Merge project names from CLI and file; de-duplicate while preserving order."""
    items = list(cli_projects)
    if projects_file:
        text = projects_file.read_text(encoding="utf-8")
        for line in text.splitlines():
            s = line.strip()
            if s and not s.startswith("#"):
                items.append(s)
    seen, uniq = set(), []
    for x in items:
        if x not in seen:
            seen.add(x)
            uniq.append(x)
    if not uniq:
        raise SystemExit("No projects specified. Use --projects or --projects-file.")
    return uniq


# ----------------------------- Main ----------------------------- #

def main() -> None:
    args = parse_args()
    setup_logging(args.verbose)

    parsed_dir: Path = args.parsed_dir
    projects = iter_projects(args.projects, args.projects_file)
    strategies = args.strategies
    default_strategy = args.default_strategy
    rounds = args.rounds

    info_out: Path = args.output_file
    flaky_dir: Path = args.flaky_dir
    total_runtime_dir: Path = args.total_runtime_dir
    ensure_dir(flaky_dir)
    ensure_dir(total_runtime_dir)
    enable_append = False  # same semantics as original 'isOK'

    for project in projects:
        logging.info("Process project: %s", project)
        append_line(info_out, f"--------------------------------{project}--------------------------------", enable_append)

        # Load basis mappings
        id_mutant_mapping, id_test_mapping = load_basis_mappings(parsed_dir, project)

        # 1) Default strategy (for reference and as a column order anchor in the audit CSV)
        logging.info("Strategy: %s", default_strategy)
        default_round_infos = load_round_info(parsed_dir, project, default_strategy, rounds)
        def_status_map, def_runtime_map = aggregate_pair_status_and_runtime(default_round_infos)
        summarize_strategy_for_humans(
            default_strategy, def_status_map, id_mutant_mapping, id_test_mapping, info_out, enable_append
        )

        # 2) Other strategies
        all_strategy_status: Dict[str, Dict[Pair, List[Optional[bool]]]] = {default_strategy: def_status_map}
        for strategy in strategies:
            if strategy == default_strategy:
                continue
            logging.info("Strategy: %s", strategy)
            round_infos = load_round_info(parsed_dir, project, strategy, rounds)
            cur_status_map, _ = aggregate_pair_status_and_runtime(round_infos)
            all_strategy_status[strategy] = cur_status_map
            summarize_strategy_for_humans(
                strategy, cur_status_map, id_mutant_mapping, id_test_mapping, info_out, enable_append
            )

        # 3) Anti-flakiness filtering: keep ONLY safe pairs for ALL downstream metrics
        flaky_df, safe_pairs, none_num = filter_flaky_pairs(
            all_strategy_status, id_mutant_mapping, id_test_mapping, default_strategy
        )

        out_subdir = parsed_dir / project
        (out_subdir / "stable_pairs.json").write_text(
            json.dumps(safe_pairs, indent=4), encoding="utf-8"
        )

        append_line(info_out, f"Number of pairs flagged as flaky due to 'None' in any strategy: {none_num}", enable_append)
        append_line(info_out, f"Number of available (stable) pairs used for ALL stats: {len(safe_pairs)}\n", enable_append)

        flaky_out = flaky_dir / f"{project}.csv"
        flaky_df.to_csv(flaky_out, index=False, encoding="utf-8")
        logging.info("Flaky (filtered-out) table -> %s  (rows=%d, safe_pairs=%d)", flaky_out, len(flaky_df), len(safe_pairs))

        # 4) Optional: compute total runtime on SAFE pairs only
        if args.emit_runtime and safe_pairs:
            # Build per-strategy runtime maps and per-round replacement maps
            strategy_runtime_map: Dict[str, Dict[Pair, List[int]]] = {default_strategy: def_runtime_map}
            strategy_repl_round: Dict[str, List[IdReplMapping]] = {
                default_strategy: load_round_repl(parsed_dir, project, default_strategy, rounds)
            }
            for strategy in strategies:
                if strategy == default_strategy:
                    continue
                r_infos = load_round_info(parsed_dir, project, strategy, rounds)
                _, r_map = aggregate_pair_status_and_runtime(r_infos)
                strategy_runtime_map[strategy] = r_map
                strategy_repl_round[strategy] = load_round_repl(parsed_dir, project, strategy, rounds)

            # Total per-round runtime vectors (SAFE pairs)
            totals: Dict[str, np.ndarray] = {
                strategy: compute_total_runtime_per_round(safe_pairs, rmap, strategy_repl_round[strategy])
                for strategy, rmap in strategy_runtime_map.items()
            }

            # Emit per-project runtime CSV (SAFE pairs)
            cols = (
                ["strategy"] + [f"round{i}" for i in range(rounds)]
                + ["avg.", "/avg. default", "T-test vs. default", "U-test vs. default"]
            )
            runtime_df = pd.DataFrame(None, columns=cols)

            def_total = totals[default_strategy]
            def_avg = float(np.mean(def_total))
            runtime_df.loc[len(runtime_df.index)] = (
                [default_strategy] + [int(x) for x in def_total]
                + [f"{def_avg:.2f}", f"{1.0:.4f}", f"{1.0:.4f}", f"{1.0:.4f}"]
            )

            for i, strategy in enumerate(strategies):
                if strategy == default_strategy:
                    continue
                cur = totals[strategy]
                cur_avg = float(np.mean(cur))
                ratio = (cur_avg / def_avg) if def_avg > 0 else float("inf")
                _, p_t = ttest_ind(cur, def_total)
                _, p_u = mannwhitneyu(cur, def_total)
                runtime_df.loc[len(runtime_df.index)] = (
                    [strategy] + [int(x) for x in cur]
                    + [f"{cur_avg:.2f}", f"{ratio:.4f}", f"{p_t:.4f}", f"{p_u:.4f}"]
                )

            out_csv = total_runtime_dir / f"{project}.csv"
            ensure_dir(out_csv.parent)
            runtime_df.to_csv(out_csv, index=False, encoding="utf-8")
            logging.info("Total runtime (SAFE pairs only) -> %s", out_csv)

    logging.info("All done.")


if __name__ == "__main__":
    main()
