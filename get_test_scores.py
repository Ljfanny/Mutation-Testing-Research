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
    'default',
    'fastest'
]
w_kills = 0.5
w_covers = 1 - w_kills
parsed_path = 'controlled_parsed_data'
analyzed_path = 'controlled_analyzed_data'
choice = 'more_projects'
MUTATED_CLASS = 'mutatedClass'
KILLING_TESTS = 'killingTests'
clazz_index = 0
name_index = 1
kills_index = 0
covers_index = 1


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


if __name__ == '__main__':
    for project in project_list:
        clazz_mutantNum_dict = dict()
        test_kills_covers_dict = dict()
        is_recorded = False
        for seed in seed_list:
            with open(f'{analyzed_path}/{choice}/mutant_list/non-flaky/{project}_{seed}.json', 'r') as f:
                non_flaky_id_list = json.load(f)
            per_id_tuple_dict, per_id_tests_dict, per_xml_infos = get_info(f'{parsed_path}/{choice}/{project}_{seed}')
            for mut_id in non_flaky_id_list:
                tup = per_id_tuple_dict[mut_id]
                tests = per_id_tests_dict[mut_id]
                clazz = tup[clazz_index]
                if is_recorded:
                    clazz_mutantNum_dict[clazz] += 1
                else:
                    clazz_mutantNum_dict[clazz] = 1
                for t in tests:
                    if (clazz, t) in test_kills_covers_dict:
                        test_kills_covers_dict[(clazz, t)][covers_index] += 1
                    else:
                        test_kills_covers_dict[(clazz, t)] = [0, 1]
            for mut in per_xml_infos:
                clazz = mut[MUTATED_CLASS]
                killing_tests = mut[KILLING_TESTS]
                if killing_tests:
                    for t in killing_tests:
                        if (clazz, t) in test_kills_covers_dict:
                            test_kills_covers_dict[(clazz, t)][kills_index] += 1
            is_recorded = True
        test_score_dict = dict()
        for t, info_tup in test_kills_covers_dict.items():
            clazz = t[clazz_index]
            kills_ratio = w_kills * (info_tup[kills_index] / info_tup[covers_index])
            covers_ratio = w_covers * (info_tup[covers_index] / clazz_mutantNum_dict[clazz])
            test_score_dict[t] = kills_ratio + covers_ratio
        df = pd.DataFrame(None, columns=['clazz', 'test', 'score'])
        for t, score in test_score_dict.items():
            df.loc[len(df.index)] = [t[clazz_index], t[name_index], score]
        df.to_csv(f'{analyzed_path}/{choice}/test_scores/{project}.csv', sep=',', header=True, index=False)
