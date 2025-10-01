import json
import os
from pathlib import Path
from pprint import pformat

import pandas as pd
import numpy as np
import ast
import csv

from dask.rewrite import strategies
from scipy.stats import ttest_ind, ttest_rel, mannwhitneyu
from parse_rough_data import REPLACEMENT_IDX, RUNTIME_IDX

proj_list = [
    'commons-cli',
    'commons-codec',
    'commons-collections',
    'empire-db',
    # 'handlebars.java',
    'jfreechart',
    'jimfs',
    'JustAuth',
    'Mybatis-PageHelper',
    # 'riptide',
    'sling-org-apache-sling-auth-core',
    # 'assertj-assertions-generator',
    # 'commons-net',
    # 'commons-csv',
    # 'delight-nashorn-sandbox',
    # 'httpcore',
    # 'guava',
    # 'java-design-patterns',
    # 'jooby',
    # 'maven-dependency-plugin',
    # 'maven-shade-plugin',
    # 'stream-lib'
]

strategy_list = [
    "default",
    "single-group",
    "single-group_errors-at-the-end",
    "by-proportions",
    "double"
]


def create_csv_vs_mvn_test_including_avg():
    mvn_test_mapping = {
        'commons-cli': 6.840,
        'commons-codec': 31.481,
        'commons-collections': 29.142,
        'empire-db': 6.344,
        'jfreechart': 8.955,
        'jimfs': 4.876,
        'JustAuth': 4.642,
        'Mybatis-PageHelper': 6.714,
        'sling-org-apache-sling-auth-core': 6.617
    }
    proj_cnt = len(mvn_test_mapping.keys())
    s_list = [
        'default',
        'single-group',
        'single-group_errors-at-the-end'
    ]
    csv_arr = list()
    cols = [
        'project',
        'mvn_test_running_time',
        'default_complete',
        'single-group_complete',
        'single-group_rate (vs. default)',
        'single-group*_complete',
        'single-group*_rate (vs. default)',
        'default_total',
        'single-group_total',
        'single-group_rate (vs. default)',
        'single-group*_total',
        'single-group*_rate (vs. default)'
    ]
    csv_arr.append(cols)
    # [replacement, running time, completion]
    ps_avg_mapping = dict()
    for p in mvn_test_mapping.keys():
        ps_avg_mapping[(p, 'default')] = [0.0, 0.0, 0.0]
        ps_avg_mapping[(p, 'single-group')] = [0.0, 0.0, 0.0]
        ps_avg_mapping[(p, 'single-group_errors-at-the-end')] = [0.0, 0.0, 0.0]
    # [avg. sg complete rate, avg. sg* complete rate, avg. sg total rate, avg. sg* total rate]
    avg_avg_arr = [0.0, 0.0, 0.0, 0.0]
    for p in mvn_test_mapping.keys():
        completion_time_mapping = {tuple(k): int(v) for k, v in
                                   json.load(open(f'{parsed_dir}/{p}/completion_time.json', 'r'))}
        cur_avg_avg_arr = [0.0, 0.0, 0.0, 0.0]
        for s in s_list:
            for r in range(round_number):
                id_others_mapping = json.load(open(f'{parsed_dir}/{p}/{s}_{r}/id_others_mapping.json', 'r'))
                for _, others in id_others_mapping.items():
                    ps_avg_mapping[(p, s)][0] += others[REPLACEMENT_IDX]
                    ps_avg_mapping[(p, s)][1] += others[RUNTIME_IDX]
                ps_avg_mapping[(p, s)][2] += completion_time_mapping[(s, r)]
        for s in s_list:
            ps_avg_mapping[(p, s)][0] /= round_number * 1000
            ps_avg_mapping[(p, s)][1] /= round_number * 1000
            ps_avg_mapping[(p, s)][2] /= round_number
        def_avg = ps_avg_mapping[(p, s_list[0])][0] + ps_avg_mapping[(p, s_list[0])][1]
        cur_avg_avg_arr[0] = ps_avg_mapping[(p, s_list[1])][2] / ps_avg_mapping[(p, s_list[0])][2]
        cur_avg_avg_arr[1] = ps_avg_mapping[(p, s_list[2])][2] / ps_avg_mapping[(p, s_list[0])][2]
        cur_avg_avg_arr[2] = (ps_avg_mapping[(p, s_list[1])][0] + ps_avg_mapping[(p, s_list[1])][1]) / def_avg
        cur_avg_avg_arr[3] = (ps_avg_mapping[(p, s_list[2])][0] + ps_avg_mapping[(p, s_list[2])][1]) / def_avg
        csv_arr.append([
            p,
            f'{mvn_test_mapping[p]:.2f}',
            f'{ps_avg_mapping[(p, s_list[0])][2]:.2f}',
            f'{ps_avg_mapping[(p, s_list[1])][2]:.2f}',
            f'{cur_avg_avg_arr[0]:.4f}',
            f'{ps_avg_mapping[(p, s_list[2])][2]:.2f}',
            f'{cur_avg_avg_arr[1]:.4f}',
            f'{def_avg:.2f}',
            f'{ps_avg_mapping[(p, s_list[1])][0] + ps_avg_mapping[(p, s_list[1])][1]:.2f}',
            f'{cur_avg_avg_arr[2]:.4f}',
            f'{ps_avg_mapping[(p, s_list[2])][0] + ps_avg_mapping[(p, s_list[2])][1]:.2f}',
            f'{cur_avg_avg_arr[3]:.4f}'
        ])
        for i in range(len(avg_avg_arr)):
            avg_avg_arr[i] += cur_avg_avg_arr[i]
    for i in range(len(avg_avg_arr)):
        avg_avg_arr[i] /= proj_cnt
    csv_arr.append([
        'avg.',
        '',
        '',
        '',
        f'{avg_avg_arr[0]:.4f}',
        '',
        f'{avg_avg_arr[1]:.4f}',
        '',
        '',
        f'{avg_avg_arr[2]:.4f}',
        '',
        f'{avg_avg_arr[3]:.4f}'
    ])
    # [xxx, def]
    micro_avg_matrix = [[0.0, 0.0] for _ in range(4)]
    for p in mvn_test_mapping.keys():
        for i in range(len(s_list)):
            s = s_list[i]
            if i == 0:
                micro_avg_matrix[0][1] += ps_avg_mapping[(p, s)][2]
                micro_avg_matrix[1][1] += ps_avg_mapping[(p, s)][2]
                micro_avg_matrix[2][1] += ps_avg_mapping[(p, s)][0] + ps_avg_mapping[(p, s)][1]
                micro_avg_matrix[3][1] += ps_avg_mapping[(p, s)][0] + ps_avg_mapping[(p, s)][1]
            elif i == 1:
                micro_avg_matrix[0][0] += ps_avg_mapping[(p, s)][2]
                micro_avg_matrix[2][0] += ps_avg_mapping[(p, s)][0] + ps_avg_mapping[(p, s)][1]
            elif i == 2:
                micro_avg_matrix[1][0] += ps_avg_mapping[(p, s)][2]
                micro_avg_matrix[3][0] += ps_avg_mapping[(p, s)][0] + ps_avg_mapping[(p, s)][1]
    csv_arr.append([
        'micro avg.',
        '',
        '',
        '',
        f'{micro_avg_matrix[0][0] / micro_avg_matrix[0][1]:.4f}',
        '',
        f'{micro_avg_matrix[1][0] / micro_avg_matrix[1][1]:.4f}',
        '',
        '',
        f'{micro_avg_matrix[2][0] / micro_avg_matrix[2][1]:.4f}',
        '',
        f'{micro_avg_matrix[3][0] / micro_avg_matrix[3][1]:.4f}'
    ])
    with open(f'{main_dir}/vs.mvn_test.csv', 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerows(csv_arr)


def compare_between_single_group_and_default_without_errors():
    def check_mutant(mut_in, mut_bs):
        clazz_check = True if mut_in["location"]["clazz"] == mut_bs["clazz"] else False
        method_check = True if mut_in["location"]["method"] == mut_bs["method"] else False
        method_desc_check = True if mut_in["location"]["methodDesc"] == mut_bs["methodDesc"] else False
        index_check = True if ast.literal_eval(mut_in["indexes"]) == mut_bs["indexes"] else False
        mutator_check = True if mut_in["mutator"] == mut_bs["mutator"] else False
        return clazz_check and method_check and method_desc_check and index_check and mutator_check

    input_dir = f'{main_dir}/inputs'
    base_dir = f'{parsed_dir}/basis'
    strategy = "single-group_errors-at-the-end"
    results_arr = []
    cols = (
            ["project"] + ["avg. default"] + ["avg. single-group*"] + ["ratio", "T-test", "U-test"]
    )
    df = pd.DataFrame(None, columns=cols)
    for proj in proj_list:
        input_json_file = f'{input_dir}/{proj}_{strategy}.json'
        with open(input_json_file, 'r', encoding='utf-8') as f:
            input_json = json.load(f)
        with open(f"{base_dir}/{proj}/id_mutant_mapping.json", 'r', encoding='utf-8') as f:
            id_mutant_mapping = json.load(f)
        sorted_input_json = sorted(input_json, key=lambda x: (x["clazzId"], x["executionSeq"]))
        mutant_order = list()
        for mut in sorted_input_json:
            for mut_id, mut_info in id_mutant_mapping.items():
                if check_mutant(mut["id"], mut_info):
                    mutant_order.append(mut_id)
                    break
        def_total_runtime_arr = list()
        sgl_total_runtime_arr = list()
        for rnd in range(round_number):
            success_list = list()
            with open(f"{parsed_dir}/{proj}/default_{rnd}/id_status_mapping.json", 'r', encoding='utf-8') as f:
                def_statuses_mapping = json.load(f)
            with open(f"{parsed_dir}/{proj}/default_{rnd}/id_others_mapping.json", 'r', encoding='utf-8') as f:
                def_others_mapping = json.load(f)
            with open(f"{parsed_dir}/{proj}/{strategy}_{rnd}/id_status_mapping.json", 'r', encoding='utf-8') as f:
                sgl_statuses_mapping = json.load(f)
            with open(f"{parsed_dir}/{proj}/{strategy}_{rnd}/id_others_mapping.json", 'r', encoding='utf-8') as f:
                sgl_others_mapping = json.load(f)
            for mut_id in mutant_order:
                if sgl_statuses_mapping[mut_id] in ["KILLED", "SURVIVED"]:
                    success_list.append(mut_id)
                else:
                    break
            def_total_runtime = 0
            sgl_total_runtime = 0
            for mut_id in success_list:
                if mut_id in def_others_mapping:
                    def_total_runtime += def_others_mapping[mut_id][REPLACEMENT_IDX] + def_others_mapping[mut_id][RUNTIME_IDX]
                    sgl_total_runtime += sgl_others_mapping[mut_id][REPLACEMENT_IDX] + sgl_others_mapping[mut_id][RUNTIME_IDX]
            def_total_runtime_arr.append(def_total_runtime)
            sgl_total_runtime_arr.append(sgl_total_runtime)
        _, p_t = ttest_ind(def_total_runtime_arr, sgl_total_runtime_arr)
        _, p_u = mannwhitneyu(def_total_runtime_arr, sgl_total_runtime_arr)
        def_avg_runtime = np.mean(def_total_runtime_arr)
        sgl_avg_runtime = np.mean(sgl_total_runtime_arr)
        ratio = sgl_avg_runtime / def_avg_runtime
        df.loc[len(df.index)] = [proj, f"{def_avg_runtime:.2f}", f"{sgl_avg_runtime:.2f}",
                                 f"{ratio:.4f}",f"{p_t:.4f}", f"{p_u:.4f}"]
    df.to_csv(f"{main_dir}/default_vs_single-group_without_errors.csv", index=False, encoding="utf-8")


def analyze_cause_of_error():
    errors_record_dir = f'{main_dir}/errors_record'
    if not os.path.exists(errors_record_dir):
        os.makedirs(errors_record_dir)
    cols = (
        ["project", "mutant_id", "clazz", "mutator"] +
        [f"default_{i}" for i in range(round_number)] +
        [f"single-group_{i}" for i in range(round_number)] +
        [f"by-proportions_{i}" for i in range(round_number)]
    )
    base_dir = f'{parsed_dir}/basis'
    strategies = ["default", "single-group", "by-proportions"]
    allowed = {"KILLED", "SURVIVED", None}
    error_cnt = 0
    proj_clazz_cnt_dict = dict()
    mutator_cnt_dict = dict()
    for proj in proj_list:
        df = pd.DataFrame(None, columns=cols)
        with open(f"{base_dir}/{proj}/id_mutant_mapping.json", 'r', encoding='utf-8') as f:
            id_mutant_mapping = json.load(f)
        record_mapping = {
            k: [None for _ in range(round_number * len(strategies))] for k in id_mutant_mapping.keys()
        }
        for i, strategy in enumerate(strategies):
            for rnd in range(round_number):
                j = i * round_number + rnd
                with open(f"{parsed_dir}/{proj}/{strategy}_{rnd}/id_status_mapping.json", 'r', encoding='utf-8') as f:
                    statuses_mapping = json.load(f)
                for mut_id, status in statuses_mapping.items():
                    record_mapping[mut_id][j] = status
        for mut_id, status_arr in record_mapping.items():
            if all(s in allowed for s in status_arr):
                continue
            error_cnt += 1
            proj_clazz_tup = (proj, id_mutant_mapping[mut_id]["clazz"])
            if proj_clazz_tup not in proj_clazz_cnt_dict:
                proj_clazz_cnt_dict[proj_clazz_tup] = 1
            else:
                proj_clazz_cnt_dict[proj_clazz_tup] += 1
            mutator = id_mutant_mapping[mut_id]["mutator"]
            if mutator not in mutator_cnt_dict:
                mutator_cnt_dict[mutator] = 1
            else:
                mutator_cnt_dict[mutator] += 1
            df.loc[len(df.index)] = [proj, mut_id, id_mutant_mapping[mut_id]["clazz"], mutator] + status_arr
        df.to_csv(f"{errors_record_dir}/{proj}.csv", index=False, encoding="utf-8")
    with open(f"{errors_record_dir}/INFO.txt", "w", encoding="utf-8") as f:
        print("error_cnt =", error_cnt, file=f)
        print("proj_clazz_cnt_dict =", pformat(proj_clazz_cnt_dict, sort_dicts=True), file=f)
        print("mutator_cnt_dict =", pformat(mutator_cnt_dict, sort_dicts=True), file=f)


def compare_each_pair_vs_default(proj: str, is_p: bool, alpha=0.05, eps=1e-12):
    pair_arrays_dict = dict()
    with open(f"{parsed_dir}/{proj}/stable_pairs.json", 'r', encoding='utf-8') as f:
        stable_pairs_arr = json.load(f)
    TEST_ID_IDX = 0
    RUNTIME_IDX = 2
    DEF_ARR_IDX = 0
    SGL_ARR_IDX = 1
    for pair in stable_pairs_arr:
        pair_arrays_dict[(str(pair[0]), pair[1])] = [
            [-1 for _ in range(round_number)],
            [-1 for _ in range(round_number)]
        ]
    for rnd in range(round_number):
        with open(f"{parsed_dir}/{proj}/default_{rnd}/id_info_mapping.json", 'r', encoding='utf-8') as f:
            def_info_mapping = json.load(f)
        with open(f"{parsed_dir}/{proj}/single-group_{rnd}/id_info_mapping.json", 'r', encoding='utf-8') as f:
            sgl_info_mapping = json.load(f)
        for mut_id, info_arr in def_info_mapping.items():
            for info in info_arr:
                tup = (mut_id, info[TEST_ID_IDX])
                if tup not in pair_arrays_dict:
                    continue
                pair_arrays_dict[tup][DEF_ARR_IDX][rnd] = info[RUNTIME_IDX]
        for mut_id, info_arr in sgl_info_mapping.items():
            for info in info_arr:
                tup = (mut_id, info[TEST_ID_IDX])
                if tup not in pair_arrays_dict:
                    continue
                pair_arrays_dict[tup][SGL_ARR_IDX][rnd] = info[RUNTIME_IDX]

    total_pairs = len(pair_arrays_dict)
    missing_cnt = 0
    cnt_single_gt_def_sig = 0  # mean_s > mean_d & p < alpha
    cnt_single_lt_def_sig = 0  # mean_s < mean_d & p < alpha
    cnt_single_eq_def_sig = 0

    all_diffs = []

    for (mut_id, test_id), (def_arr, sgl_arr) in pair_arrays_dict.items():
        if any(x == -1 for x in def_arr) or any(x == -1 for x in sgl_arr):
            missing_cnt += 1
            continue

        d = np.asarray(def_arr, dtype=float)
        s = np.asarray(sgl_arr, dtype=float)
        diff_arr = s - d

        if len(d) < 2 or len(s) < 2:
            missing_cnt += 1
            continue

        if np.allclose(diff_arr, 0.0, rtol=0.0, atol=eps) or np.var(diff_arr, ddof=1) < eps:
            stat = 0.0
            p = 1.0
        else:
            stat, p = ttest_rel(s, d)

        mean_s = float(np.mean(s))
        mean_d = float(np.mean(d))
        diff = mean_s - mean_d

        if is_p:
            if diff > 0 and p < alpha:
                cnt_single_gt_def_sig += 1
            elif diff < 0 and p < alpha:
                cnt_single_lt_def_sig += 1
            else:
                cnt_single_eq_def_sig += 1
        else:
            if diff > 0:
                cnt_single_gt_def_sig += 1
            elif diff < 0:
                cnt_single_lt_def_sig += 1
            else:
                cnt_single_eq_def_sig += 1

        all_diffs.extend((s - d).tolist())

    prop_gt = (cnt_single_gt_def_sig / total_pairs) if total_pairs else 0.0
    prop_lt = (cnt_single_lt_def_sig / total_pairs) if total_pairs else 0.0
    prop_eq = (cnt_single_eq_def_sig / total_pairs) if total_pairs else 0.0

    out_dir = Path(f"{main_dir}/strange_research")
    out_dir.mkdir(parents=True, exist_ok=True)

    if is_p:
        out_name = f"{proj}.txt"
    else:
        out_name = f"{proj}_no_p.txt"

    with open(f"{out_dir}/{out_name}", "w", encoding="utf-8") as f:
        print(f"[ignored pairs with -1] {missing_cnt}", file=f)
        print(f"[pairs evaluated] {total_pairs}", file=f)
        if is_p:
            print(f"[single > default & p < {alpha}] count={cnt_single_gt_def_sig}, proportion={prop_gt:.3f}", file=f)
            print(f"[single < default & p < {alpha}] count={cnt_single_lt_def_sig}, proportion={prop_lt:.3f}", file=f)
        else:
            print(f"[single > default] count={cnt_single_gt_def_sig}, proportion={prop_gt:.3f}", file=f)
            print(f"[single < default] count={cnt_single_lt_def_sig}, proportion={prop_lt:.3f}", file=f)
        print(f"[single == default] count={cnt_single_eq_def_sig}, proportion={prop_eq:.3f}", file=f)
        if all_diffs:
            mean_diff = float(np.mean(all_diffs))
            med_diff = float(np.median(all_diffs))
            print(f"[overall single - default] mean={mean_diff:.4f}, median={med_diff:.4f}", file=f)


def sum_up_mutant_runtimes():
    cols = (
        ["strategy"] + [f"round{rnd}" for rnd in range(round_number)] +
        ["avg.", "/avg. default", "T-test vs. default", "U-test vs. default"]
    )
    for proj in proj_list:
        def_runtime_arr = []
        def_avg = 0.0
        df = pd.DataFrame(None, columns=cols)
        for strategy in strategy_list:
            cur_runtime_arr = []
            for rnd in range(round_number):
                with open(f"{parsed_dir}/{proj}/{strategy}_{rnd}/id_others_mapping.json", 'r', encoding='utf-8') as f:
                    others_mapping = json.load(f)
                cur_runtime = 0.0
                for _, others in others_mapping.items():
                    cur_runtime += others[REPLACEMENT_IDX] + others[RUNTIME_IDX]
                cur_runtime_arr.append(cur_runtime)
            cur_avg = float(np.mean(cur_runtime_arr))
            if strategy == "default":
                def_runtime_arr = cur_runtime_arr
                def_avg = cur_avg
                df.loc[len(df.index)] = (["default"] + def_runtime_arr +
                                         [f"{cur_avg:.2f}", f"{1.0:.4f}", f"{1.0:.4f}", f"{1.0:.4f}"])
                continue
            ratio = (cur_avg / def_avg) if def_avg > 0 else float("inf")
            _, p_t = ttest_ind(cur_runtime_arr, def_runtime_arr)
            _, p_u = mannwhitneyu(cur_runtime_arr, def_runtime_arr)
            df.loc[len(df.index)] = ([strategy] + cur_runtime_arr
                    + [f"{cur_avg:.2f}", f"{ratio:.4f}", f"{p_t:.4f}", f"{p_u:.4f}"]
            )
        out_csv = f"{main_dir}/total_runtime/{proj}_TOT.csv"
        df.to_csv(out_csv, index=False, encoding="utf-8")


if __name__ == '__main__':
    round_number = 6
    main_dir = 'for_checking_OID'
    parsed_dir = f'{main_dir}/parsed_dir'
    # create_csv_vs_mvn_test_including_avg()
    # compare_between_single_group_and_default_without_errors()
    # analyze_cause_of_error()
    for proj in proj_list:
        compare_each_pair_vs_default(proj=proj, is_p=True)
        compare_each_pair_vs_default(proj=proj, is_p=False)
    # sum_up_mutant_runtimes()
