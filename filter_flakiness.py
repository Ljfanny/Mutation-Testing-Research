import pandas as pd
import numpy as np
import os
import json
from scipy.stats import ttest_ind, mannwhitneyu

project_list = [
    # 'assertj-assertions-generator',
    # 'commons-net',
    'commons-cli',
    # 'commons-csv',
    # 'commons-codec',
    'delight-nashorn-sandbox',
    'empire-db',
    'jimfs',
    # # 'httpcore',
    'handlebars.java',
    'riptide',
    # 'commons-collections',
    # 'guava',
    # 'java-design-patterns',
    # 'jooby',
    # 'maven-dependency-plugin',
    # 'maven-shade-plugin',
    # 'sling-org-apache-sling-auth-core',
    # 'stream-lib'
]
seed_list = [
    'single-group',
    'single-group_random-42',
    'single-group_random-43',
    'single-group_random-44',
    'single-group_random-45',
    'single-group_random-46',
    # 'sgl_grp',
    # 'def_ln-freq_def',
    # 'def_def_shuf',
    # 'clz_clz-cvg_def',
    # 'clz_ln-cvg_def',
    # 'n-tst_clz-cvg_def',
    # 'n-tst_ln-cvg_def',
    # 'n-tst_clz-sim_def',
    # 'n-tst_clz-diff_def',
    # 'n-tst_clz-ext_def',
    # 'n-tst_ln-ext_def',
    # '01-tst_clz-cvg_def',
    # '01-tst_ln-cvg_def'
]
seed_number = len(seed_list)


def append_line(file_path, text):
    if isOK:
        with open(file_path, 'a', encoding='utf-8') as f:
            f.write(text + '\n')


def process_info(s):
    status_mapping = dict()
    runtime_mapping = dict()
    for rnd in range(round_number):
        with open(os.path.join(f'{parsed_dir}/after', f'{project}_{s}_{rnd}.json'), 'r') as f:
            id_info_mapping = json.load(f)
        for k, v in id_info_mapping.items():
            for tup in v:
                p = (k, tup[0])
                if p not in status_mapping:
                    status_mapping[(k, tup[0])] = [None for _ in range(rnd)] + [tup[1]] + [None for _ in range(round_number - rnd - 1)]
                    runtime_mapping[(k, tup[0])] = [0 for _ in range(rnd)] + [tup[2]] + [0 for _ in range(round_number - rnd - 1)]
                else:
                    status_mapping[(k, tup[0])][rnd] = tup[1]
                    runtime_mapping[(k, tup[0])][rnd] = tup[2]
    return status_mapping, runtime_mapping


def parse_info(s, status_mapping):
    clazz_set = set()
    test_set = set()
    mutant_status_mapping = dict()
    pair_num = 0
    failed_pair_num = 0
    passed_pair_num = 0
    flaky_pair_num = 0
    comp_to_def = 0
    for p, _status_arr in status_mapping.items():
        clazz_set.add(id_mutant_mapping[p[0]]['clazz'])
        if p[0] not in mutant_status_mapping:
            mutant_status_mapping[p[0]] = True
        pair_num += 1
        test_set.add(p[1])
        if all(_status_arr):
            passed_pair_num += 1
            if s == 'default':
                p_status_mapping[p] = [True] + [None for _ in range(seed_number)]
            else:
                if not p in p_status_mapping.keys():
                    sid = seed_list.index(s)
                    p_status_mapping[p] = [None for _ in range(sid + 1)] + [True] + [None for _ in range(seed_number - sid - 1)]
                else:
                    if not p_status_mapping[p][0]:
                        comp_to_def += 1
                    sid = seed_list.index(s) + 1
                    p_status_mapping[p][sid] = True
        elif not any(_status_arr):
            failed_pair_num += 1
            mutant_status_mapping[p[0]] = False
            if s == 'default':
                p_status_mapping[p] = [False] + [None for _ in range(seed_number)]
            else:
                if not p in p_status_mapping.keys():
                    sid = seed_list.index(s)
                    p_status_mapping[p] = [None for _ in range(sid + 1)] + [False] + [None for _ in range(seed_number - sid - 1)]
                else:
                    if p_status_mapping[p][0]:
                        comp_to_def += 1
                    sid = seed_list.index(s) + 1
                    p_status_mapping[p][sid] = False
        else:
            flaky_pair_num += 1
            if s == 'default':
                p_status_mapping[p] = [None for _ in range(seed_number + 1)]
            else:
                if not p in p_status_mapping.keys():
                    p_status_mapping[p] = [None for _ in range(seed_number + 1)]
                else:
                    sid = seed_list.index(s) + 1
                    p_status_mapping[p][sid] = None
    survived_mutant_num = 0
    killed_mutant_num = 0
    for _, status in mutant_status_mapping.items():
        if status:
            survived_mutant_num += 1
        else:
            killed_mutant_num += 1
    append_line(output_file, s.capitalize() + ':')
    append_line(output_file, f'Number of classes: {len(clazz_set)}')
    append_line(output_file, f'Number of tests: {len(test_set)}')
    append_line(output_file, f'Number of mutants: {mutant_num}')
    append_line(output_file, f'Number of killed mutants: {killed_mutant_num}')
    append_line(output_file, f'Number of survived mutants: {survived_mutant_num}')
    append_line(output_file, f'Number of pairs: {pair_num}')
    append_line(output_file, f'Number of failed pairs: {failed_pair_num}')
    append_line(output_file, f'Number of passed pairs: {passed_pair_num}')
    append_line(output_file, f'Number of flaky pairs: {flaky_pair_num}')
    append_line(output_file, f'Different outcomes for number of pairs compared to default: {comp_to_def}\n')


def process_repl_time(s):
    repl_time_mapping = dict()
    for rnd in range(round_number):
        with open(os.path.join(f'{parsed_dir}/after', f'{project}_{s}_{rnd}_repl.json'), 'r') as f:
            id_repl_mapping = json.load(f)
        for k, v in id_repl_mapping.items():
            if k not in repl_time_mapping:
                repl_time_mapping[k] = [0 for _ in range(round_number)]
            repl_time_mapping[k][rnd] = v
    return repl_time_mapping


def get_total_runtime(s):
    _, runtime_mapping = process_info(s)
    id_repl_time_mapping = process_repl_time(s)
    repl_recording = set()
    runtime_arr = np.array([0.0 for _ in range(round_number)])
    for p in safe_pair_arr:
        runtime_arr += np.array(runtime_mapping[p])
        if p[0] not in repl_recording and p[0] in id_repl_time_mapping.keys():
            runtime_arr += np.array(id_repl_time_mapping[p[0]])
            repl_recording.add(p[0])
    seed_runtime_arr_mapping[s] = runtime_arr


if __name__ == '__main__':
    round_number = 6
    random_mutant = False
    random_test = False
    parsed_dir = 'for_checking_OID/temp_outputs'
    output_file = 'INFO.txt'
    isOK = False
    significant_df = pd.DataFrame(None, columns=['project', 'seed1', 'seed2', 'T-test', 'U-test'])
    for project in project_list:
        print(f'Process {project}... ...')
        append_line(output_file, f'--------------------------------{project}--------------------------------')
        with open(os.path.join(f'{parsed_dir}/before', f'{project}_mutant_mapping.json'), 'r') as file:
            id_mutant_mapping = json.load(file)
        with open(os.path.join(f'{parsed_dir}/before', f'{project}_test_mapping.json'), 'r') as file:
            id_test_mapping = json.load(file)
        mutant_num = len(id_mutant_mapping)
        p_status_mapping = dict()

        print('Process default.')
        def_p_status_mapping, def_p_runtime_mapping = process_info('default')
        parse_info('default', def_p_status_mapping)

        for seed in seed_list:
            print(f'Process {seed}.')
            cur_p_status_mapping, _ = process_info(seed)
            parse_info(seed, cur_p_status_mapping)

        pair_info_cols = ['clazz', 'method', 'methodDesc', 'indexes', 'mutator', 'test']
        pair_df = pd.DataFrame(None, columns=pair_info_cols + ['default'] + seed_list)
        none_num = 0
        safe_pair_arr = list()
        for pair, status_arr in p_status_mapping.items():
            if None not in status_arr:
                if all(status_arr) or not any(status_arr):
                    safe_pair_arr.append(pair)
                    continue
                mut = id_mutant_mapping[pair[0]]
                pair_df.loc[len(pair_df.index)] = [mut['clazz'], mut['method'], mut['methodDesc'], mut['indexes'], mut['mutator']] + [id_test_mapping[str(pair[1])]] + status_arr
            else:
                none_num += 1
        append_line(output_file, f'Number of pairs where at least one of strategies is none: {none_num}')
        # pair_df.to_csv(f'for_checking_OID/flaky_tables/{project}.csv', sep=',', header=True, index=False)

        # Focus on different runtime of pairs between seeds
        other_cols = list()
        other_cols.append('default')
        for seed in seed_list:
            other_cols.append(seed)
            other_cols.append('U-test against default')
        pair_df = pd.DataFrame(None, columns=pair_info_cols + other_cols)
        # temp_mapping = dict()
        # for pair in safe_pair_arr:
        #     temp_mapping[pair] = [np.mean(def_p_runtime_mapping[pair])]

        sign_diff_mapping = dict()
        better_dict = {k: 0 for k in safe_pair_arr}
        worse_dict = {k: 0 for k in safe_pair_arr}
        for seed in seed_list:
            _, cur_p_runtime_mapping = process_info(seed)
            # [better, worse]
            sign_diff_mapping[seed] = [0, 0]
            for pair in safe_pair_arr:
                cur_avg = np.mean(cur_p_runtime_mapping[pair])
                def_avg = np.mean(def_p_runtime_mapping[pair])
                # temp_mapping[pair].append(cur_avg)
                _, u_p_value = mannwhitneyu(def_p_runtime_mapping[pair], cur_p_runtime_mapping[pair])
                if u_p_value < 0.05:
                    if cur_avg < def_avg:
                        sign_diff_mapping[seed][0] += 1
                        better_dict[pair] += 1
                    elif cur_avg > def_avg:
                        sign_diff_mapping[seed][1] += 1
                        worse_dict[pair] += 1
                # temp_mapping[pair].append(u_p_value)
        with open(f'for_checking_OID/consistently_better_{project}.txt', 'w') as file:
            for pair, cnt in better_dict.items():
                if cnt >= seed_number:
                    file.write(f'{id_mutant_mapping[pair[0]]}.{id_test_mapping[str(pair[1])]}\n')
        with open(f'for_checking_OID/consistently_worse_{project}.txt', 'w') as file:
            for pair, cnt in worse_dict.items():
                if cnt >= seed_number:
                    file.write(f'{id_mutant_mapping[pair[0]]}.{id_test_mapping[str(pair[1])]}\n')
        # for pair, arr in temp_mapping.items():
        #     mut = id_mutant_mapping[pair[0]]
        #     pair_df.loc[len(pair_df.index)] = [mut['clazz'], mut['method'], mut['methodDesc'], mut['indexes'], mut['mutator']] + [id_test_mapping[str(pair[1])]] + [f'{t:.2f}' for t in arr]
        # pair_df.to_csv(f'for_checking_OID/{project}.csv', sep=',', header=True, index=False)

        print(len(safe_pair_arr))
        print(sign_diff_mapping)

        # Total running time
        append_line(output_file, f'Number of available pairs: {len(safe_pair_arr)}\n')
        seed_runtime_arr_mapping = dict()
        # get_total_runtime('default')
        # for seed in seed_list:
        #     get_total_runtime(seed)
        #
        # cols = ['seed'] + [f'round{i}' for i in range(round_number)] + ['avg.', '/avg. default', 'T-test vs. default', 'U-test vs. default']
        # runtime_df = pd.DataFrame(None, columns=cols)
        # def_runtime_arr = seed_runtime_arr_mapping['default']
        # def_avg_runtime = np.mean(def_runtime_arr)
        # runtime_df.loc[len(runtime_df.index)] = ['default'] + [int(runtime) for runtime in seed_runtime_arr_mapping['default']] + [f'{def_avg_runtime:.2f}', f'{1.0:.4f}', f'{1.0:.4f}', f'{1.0:.4f}']
        # for i in range(seed_number):
        #     seed1 = seed_list[i]
        #     runtime_arr1 = seed_runtime_arr_mapping[seed1]
        #     avg_runtime = np.mean(runtime_arr1)
        #     ratio_vs_def = avg_runtime / def_avg_runtime
        #     _, t_p_value = ttest_ind(runtime_arr1, def_runtime_arr)
        #     _, u_p_value = mannwhitneyu(runtime_arr1, def_runtime_arr)
        #     info_arr = [seed1] + [int(runtime) for runtime in runtime_arr1] + [f'{avg_runtime:.2f}', f'{ratio_vs_def:.4f}', f'{t_p_value:.4f}', f'{u_p_value:.4f}']
        #     runtime_df.loc[len(runtime_df.index)] = info_arr
        #     for j in range(i + 1, seed_number):
        #         seed2 = seed_list[j]
        #         runtime_arr2 = seed_runtime_arr_mapping[seed2]
        #         t_stat, t_p_value = ttest_ind(runtime_arr1, runtime_arr2)
        #         u_stat, u_p_value = mannwhitneyu(runtime_arr1, runtime_arr2)
        #         significant_df.loc[len(significant_df.index)] = [project, seed1, seed2, f'{t_p_value:.4f}', f'{u_p_value:.4f}']
        # runtime_df.to_csv(f'for_checking_OID/total_runtime/{project}.csv', sep=',', header=True, index=False)
    # significant_df.to_csv(f'for_checking_OID/total_runtime/significant.csv', sep=',', header=True, index=False)
