# Mutation-Testing-Research

This repository contains scripts and data for parsing and analyzing mutation testing results collected from PIT experiments.

It currently includes two main scripts:

- `parse_rough_data.py`: parses raw PIT XMLs and logs into structured JSON data.
- `filter_flakiness.py`: filters out flaky `(mutant_id, test_id)` pairs and computes metrics only on stable pairs.

## `parse_rough_data.py`

### Purpose

This script parses PIT mutation XML files and logs into normalized JSON files for later analysis. 

It reads:

- PIT mutation XMLs: `<project>_<strategy>_<round>.xml`
- PIT logs: `<project>_<strategy>_<round>.log`
- basis mappings: `id_mutant_mapping.json`, `id_test_mapping.json` (under `parsed_dir/basis/<project>/`)

and writes per-project JSON outputs under `parsed_dir/<project>/` describing mutation status, test results, timing, and group information.

### Usage

```bash
python parse_rough_data.py \
  --main-dir /path/to/workspace \
  --projects commons-cli commons-codec \
  --strategies default by-proportions single-group \
  --rounds 6 \
  --verbose
```

Main arguments:

- `--main-dir` : workspace root that contains `xmls/`, `logs/`, and `parsed_dir/`.
- `--projects` / `--projects-file` : project names to process.
- `--strategies` : strategy names used when running PIT (e.g., `default`, `by-proportions`, `single-group`).
- `--rounds` : number of rounds per strategy.
- `--junit-map-file` (optional): JSON mapping from project name to `junit4` / `junit5`.
- `--verbose` : enable detailed logging.

## `filter_flakiness.py`

### Purpose

This script analyzes the parsed JSON data and filters out flaky `(mutant_id, test_id)` pairs.

For each pair, it:

1. Looks at its status across rounds within each strategy.
2. Compresses each strategy to a single value: always true, always false, or unstable (mixed/None).
3. Compares the compressed results across strategies.

If a pair is unstable in any strategy, or different strategies disagree, the pair is marked as flaky and excluded. All metrics can then be computed only on the remaining stable pairs.

Optionally, the script can also compute total runtime per strategy using only stable pairs.

### Usage

```bash
python filter_flakiness.py \
  --parsed-dir /path/to/workspace/parsed_dir \
  --projects commons-cli commons-codec jimfs \
  --strategies default single-group single-group_errors-at-the-end \
  --rounds 6 \
  --output-file /path/to/workspace/INFO_summary.txt \
  --flaky-dir /path/to/workspace/flaky_pairs \
  --total-runtime-dir /path/to/workspace/total_runtime \
  --emit-runtime \
  --verbose
```

Main arguments:

- `--parsed-dir` : the `parsed_dir` produced by `parse_rough_data.py`.
- `--projects` / `--projects-file` : project names to analyze.
- `--strategies` : strategies to analyze/compare (include the default strategy if needed).
- `--default-strategy` : name of the baseline strategy (default: `default`).
- `--rounds` : number of rounds per strategy.
- `--output-file` : text file for optional human-readable summaries.
- `--flaky-dir` : directory for CSVs listing filtered-out flaky pairs.
- `--total-runtime-dir` : directory for per-project total runtime CSVs (computed on stable pairs only).
- `--emit-runtime` : if set, compute and save total runtime tables on stable pairs.
- `--verbose` : enable detailed logging.

## Folder: `for_checking_OID/total_runtime`

This folder contains CSV files summarizing the **total runtime breakdowns** for each project and several strategies.

Each CSV records detailed per-round runtimes and aggregated statistics, covering **all mutants (both flaky and non-flaky)**, to compare execution efficiency across different mutation-testing strategies.