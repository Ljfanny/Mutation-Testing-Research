import pandas as pd
import numpy as np
import os
import json
from pitest_log_parser import project_junitVersion_dict, mutant_choice, test_choice


project_list = [
    'assertj-assertions-generator',
    'commons-cli',
    'commons-csv',
    'commons-codec',
    'delight-nashorn-sandbox',
    'empire-db',
    # 'jimfs',
    # 'commons-net',
    # 'commons-collections',
    # 'commons-net',
    # 'empire-db',
    # 'guava',
    # 'handlebars.java',
    # 'httpcore',
    # 'java-design-patterns',
    # 'jooby',
    # 'maven-dependency-plugin',
    # 'maven-shade-plugin',
    # 'riptide',
    # 'sling-org-apache-sling-auth-core',
    # 'stream-lib'
]
seed_list = [
    0,
    42,
    123,
    216,
    1202,
    1999,
    2002,
    2024,
    31415,
    99999,
    'default',
    'fastest'
]
round_number = 6
random_mutant = False
random_test = False
choice = 'more_projects'
seed_number = len(seed_list)
EMPTY = ''
KILLED = 'killed'
SURVIVED = 'survived'
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
    with open(f'{file_path}/mutantId_runtimeList.json', 'r') as f:
        id_runtimes_dict = json.load(f)
    with open(f'{file_path}/mutantId_testsInOrder.json', 'r') as f:
        id_tests_dict = json.load(f)
    xml_file = f'{file_path}/mutations_xml.json'
    mutants = None
    if os.path.exists(xml_file):
        with open(xml_file, 'r') as f:
            mutants = json.load(f)
    return id_tuple_dict, id_runtimes_dict, id_tests_dict, mutants


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


def discard_flaky_mutants(mutants, p, s):
    per_id_tuple_dict, per_id_runtimes_dict, _, per_xml_infos = get_info(f'{up_dir}/{p}_{s}')
    # flaky mutants due to diff test orders
    for mut_id, runtimes in per_id_runtimes_dict.items():
        if np.isnan(runtimes).any():
            mutants.discard(log_to_key(per_id_tuple_dict[mut_id]))

    # flaky mutants due to flaky tests
    for mut in per_xml_infos:
        tup = xml_to_key(mut)
        killing_tests = mut[KILLING_TESTS]
        succeeding_tests = mut[SUCCEEDING_TESTS]
        if killing_tests:
            for test in killing_tests:
                tup_test = tup + (test, )
                if tup_test in tup_test_status_dict:
                    if tup_test_status_dict[tup_test] == EMPTY:
                        tup_test_status_dict[tup_test] = KILLED
                    elif tup_test_status_dict[tup_test] == SURVIVED:
                        mutants.discard(tup)
        if succeeding_tests:
            for test in succeeding_tests:
                tup_test = tup + (test, )
                if tup_test in tup_test_status_dict:
                    if tup_test_status_dict[tup_test] == EMPTY:
                        tup_test_status_dict[tup_test] = SURVIVED
                    elif tup_test_status_dict[tup_test] == KILLED:
                        mutants.discard(tup)


if __name__ == '__main__':
    up_dir = 'controlled_parsed_data/more_projects'
    for project in project_list:
        print(f'{project} is processing... ...')
        fastest_dir = f'{up_dir}/{project}_fastest'
        is_convenient = False
        total_mutants = set()
        tup_test_status_dict = dict()
        if os.path.exists(fastest_dir):
            total_id_tuple_dict, _, total_id_tests_dict, _ = get_info(fastest_dir)
            is_convenient = True
        else:
            total_id_tuple_dict, _, total_id_tests_dict, _ = get_info(f'parsed_data/default_version/{project}')
        
        for mut_id, mut_tup in total_id_tuple_dict.items():
            tup = log_to_key(mut_tup)
            total_mutants.add(tup)
            tests = total_id_tests_dict[mut_id]
            for test in tests:
                tup_test_status_dict[tup + (test, )] = ''

        for seed in seed_list:
            if is_convenient:
                discard_flaky_mutants(mutants=total_mutants, p=project, s='fastest')
                break
            discard_flaky_mutants(mutants=total_mutants, p=project, s=seed)

        # record non-flaky id per seed
        for seed in seed_list:
            non_flaky_id_list = []
            per_id_tuple_dict, _, _, _ = get_info(f'{up_dir}/{project}_{seed}')
            for mut_id, mut_tup in per_id_tuple_dict.items():
                tup = log_to_key(mut_tup)
                if tup in total_mutants:
                    non_flaky_id_list.append(mut_id)
            print(len(non_flaky_id_list))
            with open(f'controlled_analyzed_data/more_projects/mutant_list/non-flaky/{project}_{seed}.json', 'w') as f:
                json.dump(non_flaky_id_list, f, indent=4)
