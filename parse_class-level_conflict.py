import json
import sys
import os
import numpy as np
from sklearn.metrics import silhouette_score


class MutatedClazz:
    def __init__(self, name, mutant_arr):
        self.name = name
        self.mutant_arr = mutant_arr


def get_pairs():
    # if os.path.exists(f'{project}_pairs'):
    #     with open(f'{project}_pairs', 'r') as ff:
    #         return json.load(ff)
    value_tests_map = dict()
    with open(test_value_pairs_path, 'r') as ff:
        for ll in ff:
            ll = ll.strip()
            if not ll or ',' not in ll:
                continue
            parts = ll.split(',')
            test = parts[0].strip()
            value = parts[1].strip()
            if value not in value_tests_map:
                value_tests_map[value] = list()
            value_tests_map[value].append(test)

    for v in value_tests_map.keys():
        value_tests_map[v] = list(set(value_tests_map[v]))
        value_tests_map[v].sort()
    conflict_test_pairs = set()
    final_cnt = 0
    outside_cnt = 0
    rm_pairs = set()
    for v, arr in value_tests_map.items():
        isOK = True
        prefix_v = v[:v.rfind('.')]
        if v in final_static_vars:
            final_cnt += 1
            isOK = False
        if prefix_v not in prefix_class_paths:
            outside_cnt += 1
            isOK = False
        arr_num = len(arr)
        if arr_num < 2:
            continue
        if isOK:
            print(v)
            print(arr)
        for ii in range(arr_num):
            for jj in range(ii + 1, arr_num):
                if isOK:
                    conflict_test_pairs.add((arr[ii], arr[jj]))
                else:
                    rm_pairs.add((arr[ii], arr[jj]))
    print(project)
    print(len(final_static_vars), len(value_tests_map), final_cnt, outside_cnt)
    print(len(conflict_test_pairs), len(rm_pairs))
    with open(f'{project}_pairs', 'w') as ff:
        ff.write(json.dumps(sorted(list(conflict_test_pairs)), indent=4))
    return sorted(list(conflict_test_pairs))


if __name__ == '__main__':
    tests_path = sys.argv[1]
    test_arr = list()
    with open(tests_path, 'r') as f:
        for ln in f:
            ln = ln.strip()
            test_arr.append(ln)

    final_static_vars_path = sys.argv[2]
    final_static_vars = set()
    with open(final_static_vars_path, 'r') as f:
        for ln in f:
            ln = ln.strip()
            final_static_vars.add(ln)

    class_list_path = sys.argv[3]
    prefix_class_paths = set()
    with open(class_list_path, 'r') as f:
        for ln in f:
            ln = ln.strip()
            prefix_class_paths.add(ln)

    test_value_pairs_path = sys.argv[4]
    guiding_file_name = sys.argv[5]

    project = test_value_pairs_path.split('_')[0]
    # 01-tst/n-tst/clz
    regrouping_type = guiding_file_name.split('_')[1]
    test_pairs = get_pairs()

    test_arr = list(set(test_arr))
    test_arr.sort()
    test_num = len(test_arr)
    test_id_map = {t: i for i, t in enumerate(test_arr)}
    id_test_map = {i: t for i, t in enumerate(test_arr)}
    testId_pairs = [(test_id_map[p[0]], test_id_map[p[1]]) for p in test_pairs]

    with open(f'controlled_analyzed_data/both/guiding_files/{guiding_file_name}', 'r') as f:
        mutants = json.load(f)

    clazz_testIdArr_map = dict()
    bucket_num = 0
    for m in mutants:
        clazz = m['id']['location']['clazz']
        bucket_num = max(bucket_num, m['groupId'] + 1)
        if clazz not in clazz_testIdArr_map:
            clazz_testIdArr_map[clazz] = [0 for _ in range(test_num)]
        for t in m['testsInOrder']:
            t_name = t['name'].split('(')[0]
            clazz_testIdArr_map[clazz][test_id_map[t_name]] = 1

    initial_bucket_num = bucket_num
    clazz_arr = list(clazz_testIdArr_map.keys())
    clazz_arr.sort()
    clazz_num = len(clazz_arr)
    clazz_id_map = {c: i for i, c in enumerate(clazz_arr)}
    id_clazz_map = {i: c for i, c in enumerate(clazz_arr)}
    testIdArr_arr = [clazz_testIdArr_map[c] for c in clazz_arr]
    mutatedClazz_arr = [None for _ in range(clazz_num)]

    vector_arr = [None for _ in range(clazz_num)]
    clazzIdArr_arr = [[0 for _ in range(clazz_num)] for _ in range(test_num)]
    testCount_arr = [[0 for _ in range(test_num)] for _ in range(clazz_num)]

    bucket_arr = [[0 for _ in range(clazz_num)] for _ in range(bucket_num)]
    label_arr = [0 for _ in range(clazz_num)]
    cur_clazz = ''
    cur_mutant_arr = list()
    for m in mutants:
        bucket_id = m['groupId']
        clazz = m['id']['location']['clazz']
        clazz_id = clazz_id_map[clazz]
        if clazz != cur_clazz:
            if cur_clazz != '':
                cur_clazz_id = clazz_id_map[cur_clazz]
                mutatedClazz_arr[cur_clazz_id] = MutatedClazz(name=cur_clazz, mutant_arr=cur_mutant_arr)
                if regrouping_type == '01-tst':
                    vector_arr[cur_clazz_id] = clazz_testIdArr_map[cur_clazz]
                elif regrouping_type == 'n-tst':
                    vector_arr[cur_clazz_id] = testCount_arr[cur_clazz_id]
            cur_clazz = clazz
            cur_mutant_arr = list()
        bucket_arr[bucket_id][clazz_id] = 1
        label_arr[clazz_id] = bucket_id
        cur_mutant_arr.append(m)
        for t in m['testsInOrder']:
            t_name = t['name'].split('(')[0]
            t_id = test_id_map[t_name]
            clazzIdArr_arr[t_id][clazz_id] = 1
            testCount_arr[clazz_id][t_id] += 1
    cur_clazz_id = clazz_id_map[cur_clazz]
    mutatedClazz_arr[cur_clazz_id] = MutatedClazz(name=cur_clazz, mutant_arr=cur_mutant_arr)
    if regrouping_type == '01-tst':
        vector_arr[cur_clazz_id] = clazz_testIdArr_map[cur_clazz]
    elif regrouping_type == 'n-tst':
        vector_arr[cur_clazz_id] = testCount_arr[cur_clazz_id]

    if regrouping_type == 'clz':
        cur_clazz = ''
        cur_vector = np.array([0 for _ in range(clazz_num)])
        for m in mutants:
            clazz = m['id']['location']['clazz']
            clazz_id = clazz_id_map[clazz]
            if clazz != cur_clazz:
                if cur_clazz != '':
                    cur_clazz_id = clazz_id_map[cur_clazz]
                    vector_arr[cur_clazz_id] = [1 if i > 0 else 0 for i in cur_vector]
                cur_clazz = clazz
                cur_vector = np.array([0 for _ in range(clazz_num)])
            for t in m['testsInOrder']:
                t_name = t['name'].split('(')[0]
                t_id = test_id_map[t_name]
                cur_vector += np.array(clazzIdArr_arr[t_id])
        cur_clazz_id = clazz_id_map[cur_clazz]
        vector_arr[cur_clazz_id] = [1 if i > 0 else 0 for i in cur_vector]

    # Find conflict between clazz
    # conflict_count_map = dict()
    conflict_mat = [[0 for _ in range(clazz_num)] for _ in range(clazz_num)]
    for i in range(clazz_num):
        for j in range(i + 1, clazz_num):
            for p in testId_pairs:
                case0 = testIdArr_arr[i][p[0]] and testIdArr_arr[j][p[1]]
                case1 = testIdArr_arr[i][p[1]] and testIdArr_arr[j][p[0]]
                if case0 or case1:
                    conflict_mat[i][j] = 1
                    conflict_mat[j][i] = 1
                    # if p in conflict_count_map:
                    #     conflict_count_map[p] += 1
                    # else:
                    #     conflict_count_map[p] = 1

    # for p, num in sorted(conflict_count_map.items(), key=lambda x: x[1], reverse=True):
    #     print(f'({id_test_map[p[0]]}, {id_test_map[p[1]]}): {num}')

    # handle conflict
    i = 0
    Xs = np.array(vector_arr)
    while i < bucket_num:
        cur_arr = list()
        for j, b in enumerate(bucket_arr[i]):
            if b:
                cur_arr.append(j)
        cur_num = len(cur_arr)
        clazzId_conflictCount_tuples = list()
        for j in range(cur_num):
            cur_clz_cnt = 0
            cur_mut_cnt = 0
            for k in range(cur_num):
                if conflict_mat[cur_arr[j]][cur_arr[k]]:
                    cur_clz_cnt += 1
                    cur_mut_cnt += len(mutatedClazz_arr[cur_arr[k]].mutant_arr)
            clazzId_conflictCount_tuples.append((cur_arr[j], cur_clz_cnt, cur_mut_cnt))
        clazzId_conflictCount_tuples.sort(key=lambda x: (x[1], x[2]), reverse=True)
        if clazzId_conflictCount_tuples[0][1] == 0:
            i += 1
            continue
        mv_clz_id = clazzId_conflictCount_tuples[0][0]
        bucket_arr[i][mv_clz_id] = 0
        max_score = -1
        max_bucket_id = -1
        for j in range(bucket_num):
            if i != j:
                is_compatible = True
                for k, b in enumerate(bucket_arr[j]):
                    if b and conflict_mat[mv_clz_id][k]:
                        is_compatible = False
                if not is_compatible:
                    continue
                label_arr[mv_clz_id] = j
                score = silhouette_score(Xs, label_arr)
                if score > max_score:
                    max_score = score
                    max_bucket_id = j
        label_arr[mv_clz_id] = bucket_num
        score = silhouette_score(Xs, label_arr)
        if max_score >= score:
            label_arr[mv_clz_id] = max_bucket_id
            bucket_arr[max_bucket_id][mv_clz_id] = 1
        else:
            label_arr[mv_clz_id] = bucket_num
            bucket_arr.append([0 for _ in range(clazz_num)])
            bucket_arr[bucket_num][mv_clz_id] = 1
            bucket_num = len(bucket_arr)
    print(clazz_num, initial_bucket_num, bucket_num)
