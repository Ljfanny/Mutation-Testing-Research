import os
import json
import pandas as pd

proj_list = [
    'commons-cli',
    'commons-codec',
    'commons-csv',
    'delight-nashorn-sandbox',
    'empire-db',
    'handlebars.java',
    'httpcore',
    'jimfs',
    'riptide'
]

def store_info(xml, mutants, pairs):
    def store_test(arr, sub_id):
        if arr:
            for t in arr:
                if t not in test_list:
                    test_id_mapping[t] = len(test_list)
                    test_list.append(t)
                pair_id = (unq_id, test_id_mapping[t])
                pairs[sub_id].append(pair_id)

    def check_test(arr, sub_id):
        if arr:
            for t in arr:
                pair_id = (unq_id, test_id_mapping[t])
                if sub_id == SURVIVED_ID and pair_id in pairs[KILLED_ID]:
                    pairs[KILLED_ID].remove(pair_id)
                    pairs[UNKNOWN_ID].append(pair_id)
                elif sub_id == KILLED_ID and pair_id in pairs[SURVIVED_ID]:
                    pairs[SURVIVED_ID].remove(pair_id)
                    pairs[UNKNOWN_ID].append(pair_id)

    cnt_arr = [0 for _ in range(max(len(def_xml), len(shuf_xml)))]
    for mut in xml:
        clazz = mut[CLAZZ]
        method = mut[METHOD]
        method_desc = mut[METHOD_DESC]
        indexes = str(mut[INDEXES])
        mutator = mut[MUTATOR]
        succeeding_tests = mut[SUCCEEDING_TESTS]
        killing_tests = mut[KILLING_TESTS]

        unq_tup = (clazz, method, method_desc, indexes, mutator)
        if unq_tup not in mutant_list:
            mutant_id_mapping[unq_tup] = len(mutant_list)
            mutant_list.append(unq_tup)
            cnt_arr.append(0)
        unq_id = mutant_id_mapping[unq_tup]
        cnt_arr[unq_id] += 1
        if cnt_arr[unq_id] == 1:
            if mut[STATUS] == SURVIVED:
                mutants[SURVIVED_ID].append(unq_id)
            elif mut[STATUS] == KILLED:
                mutants[KILLED_ID].append(unq_id)
            store_test(succeeding_tests, SURVIVED_ID)
            store_test(killing_tests, KILLED_ID)
        else:
            if mut[STATUS] == SURVIVED and unq_id in mutants[KILLED_ID]:
                mutants[KILLED_ID].remove(unq_id)
                mutants[UNKNOWN_ID].append(unq_id)
            elif mut[STATUS] == KILLED and unq_id in mutants[SURVIVED_ID]:
                mutants[SURVIVED_ID].remove(unq_id)
                mutants[UNKNOWN_ID].append(unq_id)
            check_test(succeeding_tests, SURVIVED_ID)
            check_test(killing_tests, KILLED_ID)


if __name__ == '__main__':
    columns = [
        "proj",
        "def_mutant_survived",
        "def_mutant_killed",
        "def_mutant_unknown",
        "def_test_pass",
        "def_test_fail",
        "def_test_unknown",
        "shuf_mutant_survived",
        "shuf_mutant_killed",
        "shuf_mutant_unknown",
        "shuf_test_pass",
        "shuf_test_fail",
        "shuf_test_unknown",
        "mutant_diff_cnt",
        "test_diff_cnt"
    ]
    df = pd.DataFrame(columns=columns)
    up_dir = 'controlled_parsed_data/both'
    for proj in proj_list:
        print('Processing', proj)
        with open(f'{up_dir}/{proj}_default/mutations_xml.json', 'r') as f:
            def_xml = json.load(f)
        with open(f'{up_dir}/{proj}_def_def_shuf/mutations_xml.json', 'r') as f:
            shuf_xml = json.load(f)

        SURVIVED_ID = 0
        KILLED_ID = 1
        UNKNOWN_ID = 2
        SURVIVED = 'SURVIVED'
        KILLED = 'KILLED'
        STATUS = 'status'
        CLAZZ = 'mutatedClass'
        METHOD = 'mutatedMethod'
        METHOD_DESC = 'methodDescription'
        INDEXES = 'indexes'
        MUTATOR = 'mutator'
        KILLING_TESTS = 'killingTests'
        SUCCEEDING_TESTS = 'succeedingTests'

        mutant_list = list()
        mutant_id_mapping = dict()
        test_list = list()
        test_id_mapping = dict()

        def_mutants = [[], [], []]
        def_pairs = [[], [], []]
        shuf_mutants = [[], [], []]
        shuf_pairs = [[], [], []]

        store_info(def_xml, def_mutants, def_pairs)
        store_info(shuf_xml, shuf_mutants, shuf_pairs)

        def_mutants[SURVIVED_ID] = list(set(def_mutants[SURVIVED_ID]))
        def_mutants[KILLED_ID] = list(set(def_mutants[KILLED_ID]))
        def_mutants[UNKNOWN_ID] = list(set(def_mutants[UNKNOWN_ID]))
        def_pairs[SURVIVED_ID] = list(set(def_pairs[SURVIVED_ID]))
        def_pairs[KILLED_ID] = list(set(def_pairs[KILLED_ID]))
        def_pairs[UNKNOWN_ID] = list(set(def_pairs[UNKNOWN_ID]))

        shuf_mutants[SURVIVED_ID] = list(set(shuf_mutants[SURVIVED_ID]))
        shuf_mutants[KILLED_ID] = list(set(shuf_mutants[KILLED_ID]))
        shuf_mutants[UNKNOWN_ID] = list(set(shuf_mutants[UNKNOWN_ID]))
        shuf_pairs[SURVIVED_ID] = list(set(shuf_pairs[SURVIVED_ID]))
        shuf_pairs[KILLED_ID] = list(set(shuf_pairs[KILLED_ID]))
        shuf_pairs[UNKNOWN_ID] = list(set(shuf_pairs[UNKNOWN_ID]))

        mutant_diff_cnt = len(set(def_mutants[SURVIVED_ID]) & set(shuf_mutants[KILLED_ID])) + len(set(def_mutants[KILLED_ID]) & set(shuf_mutants[SURVIVED_ID]))
        pair_diff_cnt = len(set(def_pairs[SURVIVED_ID]) & set(shuf_pairs[KILLED_ID])) + len(set(def_pairs[KILLED_ID]) & set(shuf_pairs[SURVIVED_ID]))
        df.loc[len(df.index)] = [proj,
                                 len(def_mutants[SURVIVED_ID]),
                                 len(def_mutants[KILLED_ID]),
                                 len(def_mutants[UNKNOWN_ID]),
                                 len(def_pairs[SURVIVED_ID]),
                                 len(def_pairs[KILLED_ID]),
                                 len(def_pairs[UNKNOWN_ID]),
                                 len(shuf_mutants[SURVIVED_ID]),
                                 len(shuf_mutants[KILLED_ID]),
                                 len(shuf_mutants[UNKNOWN_ID]),
                                 len(shuf_pairs[SURVIVED_ID]),
                                 len(shuf_pairs[KILLED_ID]),
                                 len(shuf_pairs[UNKNOWN_ID]),
                                 mutant_diff_cnt,
                                 pair_diff_cnt]
    df.to_csv('outcomes.csv', sep=',', header=True, index=False)