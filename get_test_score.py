import numpy as np
import pandas as pd
import json
import os

project_list = [
    'assertj-assertions-generator',
    'commons-cli',
    'commons-csv',
    'commons-codec',
    'delight-nashorn-sandbox',
    'empire-db',
    'jimfs',
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
    'default'
]
seed_num = len(seed_list)
w_kill = 0.5
w_cover = 1 - w_kill
choice = 'more_projects'
parsed_dir = f'controlled_parsed_data/{choice}'
analyzed_dir = f'controlled_analyzed_data/{choice}'
MUTATED_CLASS = 'mutatedClass'
KILLING_TESTS = 'killingTests'
clazz_index = 0
method_index = 1
methodDesc_index = 2
indexes_index = 3
mutator_index = 4
name_index = 1


def get_info(file_path):
    with open(f'{file_path}/mutantId_mutantTuple.json', 'r') as f:
        id_tuple_dict = json.load(f)
    with open(f'{file_path}/mutantId_testsInOrder.json', 'r') as f:
        id_tests_dict = json.load(f)
    xml_file = f'{file_path}/mutations_xml.json'
    mutants = None
    if os.path.exists(xml_file):
        with open(xml_file, 'r') as f:
            mutants = json.load(f)
    return id_tuple_dict, id_tests_dict, mutants


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


if __name__ == '__main__':
    for project in project_list:
        mutants = set()
        clazz_mutantNum_dict = dict()
        test_killingRatios_dict = dict()
        test_coverageRatios_dict = dict()
        is_recorded = False
        for seed in seed_list:
            print(f'{project} with {seed} is processing... ...')
            test_killNum_dict = dict()
            test_coverNum_dict = dict()
            with open(f'{analyzed_dir}/mutant_list/non-flaky/{project}_{seed}.json', 'r') as f:
                non_flaky_id_list = json.load(f)
            per_id_tuple_dict, per_id_tests_dict, per_xml_infos = get_info(f'{parsed_dir}/{project}_{seed}')
            for mut_id in non_flaky_id_list:
                tup = per_id_tuple_dict[mut_id]
                tests = per_id_tests_dict[mut_id]
                clazz = tup[clazz_index]
                if not is_recorded:
                    mutants.add(log_to_key(tup))
                    if clazz in clazz_mutantNum_dict:
                        clazz_mutantNum_dict[clazz] += 1
                    else:
                        clazz_mutantNum_dict[clazz] = 1
                for t in tests:
                    if (clazz, t) in test_coverNum_dict:
                        test_coverNum_dict[(clazz, t)] += 1
                    else:
                        test_coverNum_dict[(clazz, t)] = 1
                        test_killNum_dict[(clazz, t)] = 0
                        if not is_recorded:
                            test_coverageRatios_dict[(clazz, t)] = 0
                            test_killingRatios_dict[(clazz, t)] = 0
            for mut in per_xml_infos:
                if xml_to_key(mut) in mutants:
                    clazz = mut[MUTATED_CLASS]
                    killing_tests = mut[KILLING_TESTS]
                    if killing_tests:
                        for t in killing_tests:
                            if (clazz, t) in test_killNum_dict:
                                test_killNum_dict[(clazz, t)] += 1
            
            for t, cover_num in test_coverNum_dict.items():
                clazz = t[clazz_index]
                test_coverageRatios_dict[t] += cover_num / clazz_mutantNum_dict[clazz]
                test_killingRatios_dict[t] += test_killNum_dict[t] / cover_num
            is_recorded = True

        test_score_dict = dict()
        for t, cover_ratios in test_coverageRatios_dict.items():
            clazz = t[clazz_index]
            cover_ratio = cover_ratios / seed_num
            kill_ratio = test_killingRatios_dict[t] / seed_num
            test_score_dict[t] = w_kill * kill_ratio + w_cover * cover_ratio
        df = pd.DataFrame(None, columns=['clazz', 'test', 'score'])
        for t, score in test_score_dict.items():
            df.loc[len(df.index)] = [t[clazz_index], t[name_index], score]
        with open(f'{analyzed_dir}/test_scores/{project}.json', 'w') as f:
            f.write(json.dumps({str(k): v for k, v in test_score_dict.items()}, indent=4))
        df.to_csv(f'{analyzed_dir}/test_scores/{project}.csv', sep=',', header=True, index=False)
