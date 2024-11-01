import pandas as pd
import numpy as np
import json
from pitest_log_parser import project_junitVersion_dict, mutant_choice, test_choice, TIMED_OUT
from scipy.stats import ttest_ind, mannwhitneyu

project_list = [
    'commons-codec',
    # 'commons-net',
    'delight-nashorn-sandbox',
    # 'empire-db',
    'jimfs',
    'assertj-assertions-generator',
    'commons-cli',
    # 'commons-collections',
    'commons-csv',
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
    99999
]
round_number = 6
parsed_path = 'controlled_parsed_data'
analyzed_path = 'controlled_analyzed_data'
random_mutant = False
random_test = True
# choice = f'{mutant_choice[random_mutant]}_{test_choice[random_test]}'
choice = 'more_projects'
seed_number = len(seed_list)
MEMORY_ERROR = 'MEMORY_ERROR'
KILLED = 'killed'
SURVIVED = 'survived'
BOTH = 'killed/survived'
KILLING_TESTS = 'killingTests'
SUCCEEDING_TESTS = 'succeedingTests'


def filter_mutation(mutations, non_flaky_list, mutantId_mutantTuple_dict):
    non_flaky_mutations = []
    for idx in non_flaky_list:
        mutuple = mutantId_mutantTuple_dict[idx]
        if ',' in mutuple[3]:
            indexes = mutuple[3].split(', ')
        else:
            indexes = [mutuple[3]]
        non_flaky_mutations.append({
            'mutatedClass': mutuple[0],
            'mutatedMethod': mutuple[1],
            'methodDescription': mutuple[2],
            'indexes': indexes,
            'mutator': mutuple[4]
        })
    filtered_mutations = []
    filtered_indexes = []
    keys_to_extract = ['mutatedClass', 'mutatedMethod', 'methodDescription', 'indexes', 'mutator']
    for i, mut in enumerate(mutations):
        if {k: mut[k] for k in keys_to_extract} in non_flaky_mutations:
            filtered_mutations.append(mut)
            filtered_indexes.append(i)
    return filtered_mutations, filtered_indexes


def is_different(tests0, tests1):
    if tests0 is None and tests1 is None:
        return False
    if tests0 is None or tests1 is None:
        return True
    if set(tests0) == set(tests1):
        return False
    return True


def get_info(file_path):
    with open(f'{file_path}/mutantId_mutantTuple.json', 'r') as f:
        mutantId_mutantTuple_dict = json.load(f)
    with open(f'{file_path}/mutantId_runtimeList.json', 'r') as f:
        mutantId_runtimeList_dict = json.load(f)
    return mutantId_mutantTuple_dict, mutantId_runtimeList_dict


def add_list(array1, array2):
    for i in range(round_number):
        if array2[i] == TIMED_OUT:
            array1[i] += 6000
        else:
            array1[i] += int(array2[i])


def recode_test(test_statuses_dict, i, tests, status):
    if tests is None:
        return
    for t in tests:
        if not t in test_statuses_dict:
            test_statuses_dict[t] = ['' for _ in range(seed_number)]
        if test_statuses_dict[t][i] == '' or test_statuses_dict[t][i] == status:
            test_statuses_dict[t][i] = status
        else:
            test_statuses_dict[t][i] = BOTH


if __name__ == '__main__':
    parent_path = f'controlled_parsed_data/{choice}'
    significant_df = pd.DataFrame(None, columns=['project', 'seed1', 'seed2', 'T-test', 'U-test', 'ratio(avg. fastest/avg. seed)'])
    for project in project_list:
        muid_isConsistent_dict = {}
        muid_killedTests_dict = {}
        muid_succeedingTests_dict = {}
        muid_indexMatrix_dict = {}
        is_visited = False
        for i, seed in enumerate(seed_list):
            with open(f'{parent_path}/{project}_{seed}/mutations_xml.json', 'r') as file:
                mutation_list = json.load(file)
            with open(f'{parent_path}/{project}_{seed}/mutantId_mutantTuple.json', 'r') as file:
                mutantId_mutantTuple_dict = json.load(file)
            with open(f'controlled_analyzed_data/{choice}/mutant_list/non-flaky/{project}_{seed}.json', 'r') as file:
                non_flaky_list = json.load(file)
            filtered_mutations, filtered_indexes = filter_mutation(mutation_list,
                                                                   non_flaky_list,
                                                                   mutantId_mutantTuple_dict)
            if not is_visited:
                for mutation in filtered_mutations:
                    muid = (mutation['mutatedClass'], mutation['mutatedMethod'], mutation['methodDescription'])
                    muid += (str([int(i) for i in mutation['indexes']]), mutation['mutator'])
                    muid_isConsistent_dict[muid] = True
                    muid_indexMatrix_dict[muid] = [[] for _ in range(seed_number)]
                    muid_killedTests_dict[muid] = mutation[KILLING_TESTS]
                    muid_succeedingTests_dict[muid] = mutation[SUCCEEDING_TESTS]

            # the same order has different statuses.
            for j, mutation in enumerate(filtered_mutations):
                muid = (mutation['mutatedClass'], mutation['mutatedMethod'], mutation['methodDescription'])
                muid += (str([int(i) for i in mutation['indexes']]), mutation['mutator'])
                if len(muid_indexMatrix_dict[muid][i]) >= 1:
                    k = muid_indexMatrix_dict[muid][i][0]
                    if is_different(mutation_list[k][KILLING_TESTS], mutation[KILLING_TESTS]) or is_different(
                            mutation_list[k][SUCCEEDING_TESTS], mutation[SUCCEEDING_TESTS]):
                        muid_isConsistent_dict[muid] = False
                muid_indexMatrix_dict[muid][i] += [filtered_indexes[j]]

            # the different order has different statuses.
            if is_visited:
                for j, mutation in enumerate(filtered_mutations):
                    muid = (mutation['mutatedClass'], mutation['mutatedMethod'], mutation['methodDescription'])
                    muid += (str([int(i) for i in mutation['indexes']]), mutation['mutator'])
                    if not muid_isConsistent_dict[muid]:
                        continue
                    killing_tests = mutation[KILLING_TESTS]
                    succeeding_tests = mutation[SUCCEEDING_TESTS]
                    if is_different(muid_killedTests_dict[muid], killing_tests) or is_different(
                            muid_succeedingTests_dict[muid], succeeding_tests):
                        muid_isConsistent_dict[muid] = False
            is_visited = True
        cnt = 0
        df = pd.DataFrame(None, columns=['mutated_class',
                                         'mutated_method',
                                         'method_description',
                                         'indexes',
                                         'mutator',
                                         'test'] + [f'seed_{s}' for s in seed_list])
        for muid, is_consistent in muid_isConsistent_dict.items():
            if is_consistent:
                continue
            cnt += 1
            test_statuses_dict = {}
            for i, indexes in enumerate(muid_indexMatrix_dict[muid]):
                with open(f'{parent_path}/{project}_{seed_list[i]}/mutations_xml.json', 'r') as file:
                    mutation_list = json.load(file)
                for index in indexes:
                    mutation = mutation_list[index]
                    recode_test(test_statuses_dict, i, mutation[KILLING_TESTS], KILLED)
                    recode_test(test_statuses_dict, i, mutation[SUCCEEDING_TESTS], SURVIVED)
            for i, indexes in enumerate(muid_indexMatrix_dict[muid]):
                with open(f'{parent_path}/{project}_{seed_list[i]}/mutations_xml.json', 'r') as file:
                    mutation_list = json.load(file)
                for index in indexes:
                    mutation = mutation_list[index]
                    if mutation['status'] in [TIMED_OUT, MEMORY_ERROR]:
                        for t, statuses in test_statuses_dict.items():
                            if test_statuses_dict[t][i] == '':
                                test_statuses_dict[t][i] = mutation['status']
            for test, statuses in test_statuses_dict.items():
                if len(set(statuses)) == 1:
                    continue
                df.loc[len(df.index)] = list(muid) + [test] + statuses
        df.to_csv(f'controlled_analyzed_data/{choice}/xml_results/{project}.csv', sep=',', header=True, index=False)
        print(f'{project}: {cnt}/{len(muid_isConsistent_dict)}')

        # calculate total running time... ...
        columns = ['seed'] + [f'round{i}' for i in range(round_number)]
        runtime_df = pd.DataFrame(None, columns=columns)
        seed_totalRuntimeList_dict = {}
        # normal one
        for seed in seed_list:
            runtime_list = [0 for _ in range(round_number)]
            mutantId_mutantTuple_dict, mutantId_runtimeList_dict = get_info(f'{parsed_path}/{choice}/{project}_{seed}')
            for mutant_id, mutant_tuple in mutantId_mutantTuple_dict.items():
                muid = tuple(mutant_tuple[:3])
                muid += (str([int(i) for i in mutant_tuple[3].split(', ')]), mutant_tuple[4])
                if muid in muid_isConsistent_dict and muid_isConsistent_dict[muid]:
                    add_list(runtime_list, mutantId_runtimeList_dict[mutant_id])
            seed_totalRuntimeList_dict[seed] = runtime_list
            runtime_df.loc[len(runtime_df.index)] = [seed] + runtime_list
        fastest_array = runtime_list
        # fastest one
        mutantId_mutantTuple_dict, mutantId_runtimeList_dict = get_info(f'{parsed_path}/{choice}/{project}_fastest')
        fastest_array = [0 for _ in range(round_number)]
        for mutant_id, mutant_tuple in mutantId_mutantTuple_dict.items():
            muid = tuple(mutant_tuple[:3])
            muid += (str([int(i) for i in mutant_tuple[3].split(', ')]), mutant_tuple[4])
            if muid in muid_isConsistent_dict and muid_isConsistent_dict[muid]:
                add_list(fastest_array, mutantId_runtimeList_dict[mutant_id])
        runtime_df.loc[len(runtime_df.index)] = ['fastest'] + fastest_array
        for i in range(seed_number):
            i_seed = seed_list[i]
            i_array = seed_totalRuntimeList_dict[i_seed]
            for j in range(seed_number):
                if j > i:
                    j_seed = seed_list[j]
                    j_array = seed_totalRuntimeList_dict[j_seed]
                    t_stat, t_p_value = ttest_ind(i_array, j_array)
                    u_stat, u_p_value = mannwhitneyu(i_array, j_array)
                    significant_df.loc[len(significant_df.index)] = [project,
                                                                     i_seed,
                                                                     j_seed,
                                                                     f'{t_p_value:.5f}',
                                                                     f'{u_p_value:.3f}',
                                                                     '']
            avg_rate = np.mean(fastest_array) / np.mean(i_array)
            t_stat, t_p_value = ttest_ind(i_array, fastest_array)
            u_stat, u_p_value = mannwhitneyu(i_array, fastest_array)
            significant_df.loc[len(significant_df.index)] = [project,
                                                             i_seed,
                                                             'fastest',
                                                             f'{t_p_value:.5f}',
                                                             f'{u_p_value:.5f}',
                                                             f'{avg_rate:.5f}']
        runtime_df.to_csv(f'{analyzed_path}/{choice}/total_running_time/{project}.csv',
                          sep=',', header=True, index=False)
    significant_df.to_csv(f'{analyzed_path}/{choice}/total_running_time/significant_results.csv',
                          sep=',', header=True, index=False)
