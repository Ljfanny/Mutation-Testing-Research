import sys
import pandas as pd
import numpy as np
import os
import json
from pitest_log_parser import project_junitVersion_dict, mutant_choice, test_choice


project_list = [
    # 'assertj-assertions-generator',
    # 'commons-net',
    'commons-cli',
    'commons-csv',
    'commons-codec',
    'delight-nashorn-sandbox',
    'empire-db',
    'jimfs',
    'httpcore',
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
    'default',
    'sgl_grp',
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
round_number = 6
random_mutant = False
random_test = False
choice = 'more_projects'
parsed_dir = f'controlled_parsed_data/both'
analyzed_dir = f'controlled_analyzed_data/both'
seed_number = len(seed_list)
EMPTY = 0
KILLED = -1
SURVIVED = 1
UNAVAILABLE = sys.maxsize
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
    print(f'STRATEGY-{s} pair number with deleted errors:', cur_pairs_num - len(pair_set))
    cur_pairs_num = len(pair_set)
    # flaky mutants due to flaky tests
    for mut in xml_infos:
        tup = xml_to_key(mut)
        killing_tests = mut[KILLING_TESTS]
        succeeding_tests = mut[SUCCEEDING_TESTS]
        if killing_tests:
            for t in killing_tests:
                pair = tup + (t, )
                if pair in pair_statuses_dict:
                    if pair_statuses_dict[pair][cd] == EMPTY:
                        pair_statuses_dict[pair][cd] = KILLED
                    elif pair_statuses_dict[pair][cd] == SURVIVED:
                        pair_statuses_dict[pair][cd] = UNAVAILABLE
                        pair_set.discard(pair)
                        discard_mutant_set.add(pair[:-1])
        if succeeding_tests:
            for t in succeeding_tests:
                pair = tup + (t, )
                if pair in pair_statuses_dict:
                    if pair_statuses_dict[pair][cd] == EMPTY:
                        pair_statuses_dict[pair][cd] = SURVIVED
                    elif pair_statuses_dict[pair][cd] == KILLED:
                        pair_statuses_dict[pair][cd] = UNAVAILABLE
                        pair_set.discard(pair)
                        discard_mutant_set.add(pair[:-1])
    print(f'STRATEGY-{s} pair number with deleted flaky tests:', cur_pairs_num - len(pair_set))
    print(f'STRATEGY-{s} available pair number:', len(pair_set))
    return discard_mutant_set


if __name__ == '__main__':
    code_status_dict = {
        0: 'EMPTY',
        1: 'SURVIVED',
        -1: 'KILLED',
        sys.maxsize: 'UNAVAILABLE'
    }
    for project in project_list:
        print(f'{project} is processing... ...')
        def_id_tuple_dict, def_id_tests_dict, _, _ = get_info(f'parsed_data/default_version/{project}')
        mutant_set = set()
        pair_statuses_dict = dict()
        for mut_id, mut_tup in def_id_tuple_dict.items():
            tup = log_to_key(mut_tup)
            mutant_set.add(tup)
            tests = def_id_tests_dict[mut_id]
            for t in tests:
                pair = tup + (t, )
                pair_statuses_dict[pair] = [0 for _ in range(len(seed_list))]
        
        for i, seed in enumerate(seed_list):
            cur_discard_mutant_set = discard_flaky_mutants(p=project, s=seed, cd=i)
            for mut in cur_discard_mutant_set:
                mutant_set.discard(mut)
        
        flaky_pair_num = 0
        flaky_test_set = set()
        pair_info_cols = ['clazz', 'method', 'methodDesc', 'indexes', 'mutator', 'test']
        df = pd.DataFrame(None, columns=pair_info_cols + seed_list)
        for pr, status_list in pair_statuses_dict.items():
            pr_info = list(pr)
            available_list = [cd for cd in status_list if cd != UNAVAILABLE and cd != EMPTY]
            if len(set(available_list)) > 1:
                flaky_pair_num += 1
                flaky_test_set.add(pr[-1])
                mutant_set.discard(pr[:-1])
                df.loc[len(df.index)] = pr_info + [code_status_dict[cd] for cd in status_list]
            if EMPTY in status_list:
                mutant_set.discard(pr[:-1])
        df.to_csv(f'{analyzed_dir}/status_info/{project}.csv', sep=',', header=True, index=False)
        print('Flaky counts BETWEEN strategies:', flaky_pair_num)
        for t in flaky_test_set:
            print(t)

        for seed in seed_list:
            non_flaky_id_list = []
            cur_id_tuple_dict, cur_id_tests_dict, _, _ = get_info(f'{parsed_dir}/{project}_{seed}')
            for mut_id, mut_tup in cur_id_tuple_dict.items():
                tup = log_to_key(mut_tup)
                if tup in mutant_set:
                    non_flaky_id_list.append(mut_id)
            # with open(f'{analyzed_dir}/mutant_list/non-flaky/{project}_{seed}.json', 'w') as f:
            #     json.dump(non_flaky_id_list, f, indent=4)
