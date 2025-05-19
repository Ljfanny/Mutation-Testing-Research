import sys
import pandas as pd
import numpy as np
import os
import json

project_list = [
    # 'assertj-assertions-generator',
    # 'commons-net',
    # 'commons-cli',
    # 'commons-csv',
    'commons-codec',
    # 'delight-nashorn-sandbox',
    # 'empire-db',
    # 'jimfs',
    # 'httpcore',
    # 'handlebars.java',
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
    'default',
    'sgl_grp',
    'shuffled',
    'def_ln-freq_def',
    'def_def_shuf',
    'clz_clz-cvg_def',
    'clz_ln-cvg_def',
    'n-tst_clz-cvg_def',
    'n-tst_ln-cvg_def',
    'n-tst_clz-sim_def',
    'n-tst_clz-diff_def',
    'n-tst_clz-ext_def',
    'n-tst_ln-ext_def',
    '01-tst_clz-cvg_def',
    '01-tst_ln-cvg_def'
]
seed_number = len(seed_list)
EMPTY = 0
KILLED = -1
SURVIVED = 1
UNKNOWN = sys.maxsize
KILLING_TESTS = 'killingTests'
SUCCEEDING_TESTS = 'succeedingTests'
clazz_index = 0
method_index = 1
methodDesc_index = 2
indexes_index = 3
mutator_index = 4


def get_info(file_path):
    with open(f'{file_path}/mutantId_mutantTuple.json', 'r') as f:
        id_tuple_dict = json.load(f)
    with open(f'{file_path}/mutantId_testsInOrder.json', 'r') as f:
        id_tests_dict = json.load(f)
    with open(f'{file_path}/mutantId_runtimeList.json', 'r') as f:
        id_runtimes_dict = json.load(f)
    xml_file = f'{file_path}/mutations_xml.json'
    xml_infos = None
    if os.path.exists(xml_file):
        with open(xml_file, 'r') as f:
            xml_infos = json.load(f)
    return id_tuple_dict, id_tests_dict, id_runtimes_dict, xml_infos


def xml_to_key(obj):
    return (obj['mutatedClass'],
            obj['mutatedMethod'],
            obj['methodDescription'],
            str([int(i) for i in obj['indexes']]),
            obj['mutator'])


def log_to_key(obj):
    return (obj[clazz_index],
            obj[method_index],
            obj[methodDesc_index],
            str([int(i) for i in obj[indexes_index].split(', ')]),
            obj[mutator_index])


def discard_flaky_mutants(p:str, s:str, cd:int):
    id_tuple_dict, id_tests_dict, id_runtimes_dict, xml_infos = get_info(f'{parsed_dir}/{p}_{s}')
    # flaky mutants due to errors
    pair_set = set()
    discard_mutant_set = set()
    for mut_id, mut_tup in id_tuple_dict.items():
        tup = log_to_key(mut_tup)
        tests = id_tests_dict[mut_id]
        for t in tests:
            pair_set.add(tup + (t, ))
    cur_pairs_num = len(pair_set)
    print(f'STRATEGY-{s} total pair number:', cur_pairs_num)
    for mut_id, runtimes in id_runtimes_dict.items():
        if np.isnan(runtimes).any():
            tup = log_to_key(id_tuple_dict[mut_id])
            tests = id_tests_dict[mut_id]
            for t in tests:
                pair = tup + (t, )
                pair_set.discard(pair)
                discard_mutant_set.add(pair[:-1])
    print(f'STRATEGY-{s} pair number with errors:', cur_pairs_num - len(pair_set))
    cur_pairs_num = len(pair_set)
    # flaky mutants due to flaky tests
    missing_num = 0
    killed_mutant_set = set()
    for mut in xml_infos:
        tup = xml_to_key(mut)
        killing_tests = mut[KILLING_TESTS]
        succeeding_tests = mut[SUCCEEDING_TESTS]
        if killing_tests:
            if tup in mutant_statuses_dict:
                if mutant_statuses_dict[tup][cd] == EMPTY:
                    mutant_statuses_dict[tup][cd] = KILLED
                    killed_mutant_set.add(tup)
                elif mutant_statuses_dict[tup][cd] == SURVIVED:
                    mutant_statuses_dict[tup][cd] = UNKNOWN
            else:
                print(f'{tup} is not in the guiding file!!!')
            for t in killing_tests:
                pair = tup + (t, )
                if pair in pair_statuses_dict:
                    if pair_statuses_dict[pair][cd] == EMPTY:
                        pair_statuses_dict[pair][cd] = KILLED
                    elif pair_statuses_dict[pair][cd] == SURVIVED:
                        pair_statuses_dict[pair][cd] = UNKNOWN
                        pair_set.discard(pair)
                        discard_mutant_set.add(pair[:-1])
                else:
                    missing_num += 1
        else:
            if mutant_statuses_dict[tup][cd] == EMPTY:
                mutant_statuses_dict[tup][cd] = SURVIVED
            elif mutant_statuses_dict[tup][cd] == KILLED:
                mutant_statuses_dict[tup][cd] = UNKNOWN
        if succeeding_tests:
            for t in succeeding_tests:
                pair = tup + (t, )
                if pair in pair_statuses_dict:
                    if pair_statuses_dict[pair][cd] == EMPTY:
                        pair_statuses_dict[pair][cd] = SURVIVED
                    elif pair_statuses_dict[pair][cd] == KILLED:
                        pair_statuses_dict[pair][cd] = UNKNOWN
                        pair_set.discard(pair)
                        discard_mutant_set.add(pair[:-1])
                else:
                    missing_num += 1
    print(f'STRATEGY-{s} killed mutant number:', len(killed_mutant_set))
    print(f'STRATEGY-{s} missing pair number:', missing_num)
    print(f'STRATEGY-{s} pair number with flaky tests:', cur_pairs_num - len(pair_set))
    print(f'STRATEGY-{s} available pair number:', len(pair_set))
    print()
    return discard_mutant_set


if __name__ == '__main__':
    round_number = 6
    random_mutant = False
    random_test = False
    parsed_dir = 'controlled_parsed_data/both'
    analyzed_dir = 'controlled_analyzed_data/both'
    code_status_dict = {
        0: 'EMPTY',
        1: 'SURVIVED',
        -1: 'KILLED',
        sys.maxsize: 'UNKNOWN'
    }
    for project in project_list:
        print(f'Process {project}... ...')
        def_id_tuple_dict, def_id_tests_dict, _, _ = get_info(f'parsed_data/default_version/{project}')
        mutant_set = set()
        pair_statuses_dict = dict()
        mutant_statuses_dict = dict()
        for mut_id, mut_tup in def_id_tuple_dict.items():
            tup = log_to_key(mut_tup)
            mutant_set.add(tup)
            if tup not in mutant_statuses_dict:
                mutant_statuses_dict[tup] = [EMPTY for _ in range(len(seed_list))]
            tests = def_id_tests_dict[mut_id]
            for t in tests:
                pair = tup + (t, )
                pair_statuses_dict[pair] = [EMPTY for _ in range(len(seed_list))]
        
        print('Total number of mutants:', len(mutant_set))
        for i, seed in enumerate(seed_list):
            cur_discard_mutant_set = discard_flaky_mutants(p=project, s=seed, cd=i)
            for mut in cur_discard_mutant_set:
                mutant_set.discard(mut)
        
        # mutant_info_cols = ['clazz', 'method', 'methodDesc', 'indexes', 'mutator']
        # mutant_df = pd.DataFrame(None, columns=mutant_info_cols + seed_list)
        # for mut, status_list in mutant_statuses_dict.items():
        #     mut_info = list(mut)
        #     available_list = [cd for cd in status_list if cd != UNKNOWN and cd != EMPTY]
        #     if len(set(available_list)) > 1:
        #         mutant_df.loc[len(mutant_df.index)] = mut_info + [code_status_dict[cd] for cd in status_list]
        # mutant_df.to_csv(f'{analyzed_dir}/status_info/of_mutants/{project}.csv', sep=',', header=True, index=False)

        flaky_test_set = set()
        pair_info_cols = ['clazz', 'method', 'methodDesc', 'indexes', 'mutator', 'test']
        pair_df = pd.DataFrame(None, columns=pair_info_cols + seed_list)
        for pr, status_list in pair_statuses_dict.items():
            pr_info = list(pr)
            available_list = [cd for cd in status_list if cd != UNKNOWN and cd != EMPTY]
            if len(set(available_list)) > 1:
                flaky_test_set.add(pr[-1])
                mutant_set.discard(pr[:-1])
                pair_df.loc[len(pair_df.index)] = pr_info + [code_status_dict[cd] for cd in status_list]
            if EMPTY in status_list:
                mutant_set.discard(pr[:-1])
        # pair_df.to_csv(f'{analyzed_dir}/status_info/of_pairs/{project}.csv', sep=',', header=True, index=False)
        pair_df.to_csv(f'for_checking_OID/{project}.csv', sep=',', header=True, index=False)

        # for seed in seed_list:
        #     non_flaky_id_list = []
        #     cur_id_tuple_dict, cur_id_tests_dict, _, _ = get_info(f'{parsed_dir}/{project}_{seed}')
        #     for mut_id, mut_tup in cur_id_tuple_dict.items():
        #         tup = log_to_key(mut_tup)
        #         if tup in mutant_set:
        #             non_flaky_id_list.append(mut_id)
        #     with open(f'{analyzed_dir}/mutant_list/non-flaky/{project}_{seed}.json', 'w') as f:
        #         json.dump(non_flaky_id_list, f, indent=4)