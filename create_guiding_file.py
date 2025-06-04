import math
import json
import numpy as np
import warnings
import random
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from parse_rough_data import project_junitVersion_dict

warnings.filterwarnings("ignore")
project_list = [
    # 'assertj-assertions-generator', all groups cover all classes
    'commons-cli',
    'commons-csv',
    'commons-codec',
    'delight-nashorn-sandbox',
    'empire-db',
    'jimfs',
    'handlebars.java',
    'httpcore',
    'riptide',
    'commons-net',
    # 'commons-collections',
    # 'guava',
    # 'java-design-patterns',
    # 'jooby',
    # 'maven-dependency-plugin',
    # 'maven-shade-plugin',
    # 'sling-org-apache-sling-auth-core',
    # 'stream-lib'
]


def get_infos(proj: str):
    with open(f'parsed_data/default_version/{proj}/mutantId_mutantTuple.json', 'r') as f:
        id_tuple_dict = json.load(f)
    with open(f'parsed_data/default_version/{proj}/mutantId_testsInOrder.json', 'r') as f:
        id_tests_dict = json.load(f)
    return id_tuple_dict, id_tests_dict


def mutant_to_json(mutant, test_list, group_id, clazz_id, exec_seq, junit_version):
    test_order = []
    if junit_version == 'junit4':
        for test in test_list:
            paren_idx = test.find('(')
            for i in range(paren_idx, 0, -1):
                if test[i] == '.':
                    break
            test_order.append({
                'definingClass': test[:i],
                'name': test
            })
    else:
        for test in test_list:
            class_end_idx = test.find('[')
            test_order.append({
                'definingClass': test[:class_end_idx - 1],
                'name': test
            })
    return {
        'id': {
            'location': {
                'clazz': mutant[0],
                'method': mutant[1],
                'methodDesc': mutant[2]
            },
            'indexes': f'[{mutant[3]}]',
            'mutator': mutant[4]
        },
        'testsInOrder': test_order,
        'groupId': group_id,
        'clazzId': clazz_id,
        'executionSeq': exec_seq
    }


def preprocess():
    lineNum_idx = 7
    test_clazzList_dict = dict()
    test_lineNums_dict = dict()
    for mut_id, mut_tup in id_tuple_dict.items():
        clazz = mut_tup[clazz_idx]
        line_num = mut_tup[lineNum_idx]
        tests = id_tests_dict[mut_id]
        for t in tests:
            if t in test_clazzList_dict:
                test_clazzList_dict[t].append(clazz)
                test_lineNums_dict[t].append((clazz, line_num))
            else:
                test_clazzList_dict[t] = [clazz]
                test_lineNums_dict[t] = [(clazz, line_num)]
    test_clazzList_dict = {k: list(set(v)) for k, v in test_clazzList_dict.items()}
    test_lineNums_dict = {k: list(set(v)) for k, v in test_lineNums_dict.items()}
    return test_clazzList_dict, test_lineNums_dict


# Use k-means to get the best group number
def get_best_group_allocation(by='clazz'):
    def based_on_clazz():
        Xs = list()
        n_features = clazz_num
        cur_clazz = ''
        cur_features = None
        for mut_id, mut_tup in id_tuple_dict.items():
            clazz = mut_tup[clazz_idx]
            tests = id_tests_dict[mut_id]
            if cur_clazz != clazz:
                if cur_clazz != '':
                    Xs.append(cur_features)
                cur_features = [0 for _ in range(n_features)]
                cur_clazz = clazz
            for t in tests:
                clz_list = test_clazzes_dict[t]
                for clz in clz_list:
                    cur_features[clazz_idx_dict[clz]] = 1
        Xs.append(cur_features)
        return Xs

    def based_on_test():
        test_set = set()
        total_counts = 0
        for _, tests in id_tests_dict.items():
            total_counts += len(tests)
            for t in tests:
                test_set.add(t)
        test_list = sorted(list(test_set))
        test_idx_dict = {clz: i for i, clz in enumerate(test_list)}
        Xs = list()
        n_features = len(test_set)
        cur_clazz = ''
        cur_features = None
        for mut_id, mut_tup in id_tuple_dict.items():
            clazz = mut_tup[clazz_idx]
            tests = id_tests_dict[mut_id]
            if cur_clazz != clazz:
                if cur_clazz != '':
                    Xs.append(cur_features)
                cur_features = [0 for _ in range(n_features)]
                cur_clazz = clazz
            for t in tests:
                cur_features[test_idx_dict[t]] += 1
                # cur_features[test_idx_dict[t]] = 1 ## worse one!
        Xs.append(cur_features)
        return Xs
    
    Xs = based_on_clazz()
    cur_clazz = ''
    cnt = -1
    for mut_id, mut_tup in id_tuple_dict.items():
        clazz = mut_tup[clazz_idx]
        if cur_clazz != clazz:
            cur_clazz = clazz
            cnt += 1
            clazz_vecSum_dict[clazz] = sum(Xs[cnt])

    if by == 'test':
        Xs = based_on_test()
    n_clazz = clazz_num
    n_clusters_list = [n for n in list(dict.fromkeys([math.ceil(n_clazz * i) for i in np.linspace(0, 1, 21)]))
                       if 1 < n < n_clazz]
    X = np.array(Xs)
    labels_list = []
    score_list = []
    for n_clusters in n_clusters_list:
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        kmeans.fit(X)
        labels = kmeans.labels_
        labels_list.append(labels)
        score_list.append(silhouette_score(X, labels))

    max_idx = score_list.index(max(score_list))
    labels = labels_list[max_idx]
    cur_clazz = ''
    cnt = -1
    id_gid_dict = dict()
    for mut_id, mut_tup in id_tuple_dict.items():
        clazz = mut_tup[clazz_idx]
        if cur_clazz != clazz:
            cur_clazz = clazz
            cnt += 1
        id_gid_dict[mut_id] = labels[cnt]
    return id_gid_dict


def get_default_allocation():
    id_gid_dict = dict()
    grp_id = -1
    cur_clazz = ''
    for mut_id, mut_tup in id_tuple_dict.items():
        clz = mut_tup[clazz_idx]
        if clz != cur_clazz:
            grp_id += 1
            cur_clazz = clz
        id_gid_dict[mut_id] = grp_id
    return id_gid_dict


def reorder_mutants_by_coverage(mutant_id_list, by='clazz', order='descending'):
    idx_by_tup_list = list()
    for i, mut_id in enumerate(mutant_id_list):
        tests = id_tests_dict[mut_id]
        cur_list = list()
        for t in tests:
            if by == 'clazz':
                cur_list += test_clazzes_dict[t]
            elif by == 'line':
                cur_list += test_lines_dict[t]
        idx_by_tup_list.append((i, len(set(cur_list)), len(tests)))
    idx_by_tup_list.sort(key=lambda x: (x[1], x[2]), reverse=True)
    sorted_mid_list = [mutant_id_list[tup[0]] for tup in idx_by_tup_list]
    return sorted_mid_list if order == 'descending' else sorted_mid_list[::-1]


def reorder_mutants_by_more_other_stuffs(group_id, mutant_id_list, by='clazz'):
    idx_by_tup_list = list()
    stuff_in_grp = set()
    if by == 'clazz':
        for i, gid in enumerate(gid_list):
            if group_id == gid:
                stuff_in_grp.add(clazz_list[i])
    elif by == 'line':
        for i, gid in enumerate(gid_list):
            if group_id == gid:
                clz = clazz_list[i]
                for mut_id, mut_tup in id_tuple_dict.items():
                    if clz == mut_tup[clazz_idx]:
                        tests = id_tests_dict[mut_id]
                        for t in tests:
                            stuff_in_grp |= set(test_lines_dict[t])
    for i, mut_id in enumerate(mutant_id_list):
        tests = id_tests_dict[mut_id]
        cur_list = list()
        for t in tests:
            if by == 'clazz':
                cur_list += test_clazzes_dict[t]
            elif by == 'line':
                cur_list += test_lines_dict[t]
        cur_set = set(cur_list) - stuff_in_grp
        idx_by_tup_list.append((i, len(cur_set), len(tests)))
    idx_by_tup_list.sort(key=lambda x: (x[1], x[2]), reverse=True)
    sorted_mid_list = [mutant_id_list[tup[0]] for tup in idx_by_tup_list]
    return sorted_mid_list


# Use Cosine Similarity as score. By clazz.
def reorder_mutants_by_similarity(mutant_id_list, order='descending'):
    mid_set = set(mutant_id_list)
    first_mid = mutant_id_list[0]
    first_x = [0 for _ in range(clazz_num)]
    tests = id_tests_dict[first_mid]
    for t in tests:
        clazzes = test_clazzes_dict[t]
        for clz in clazzes:
            first_x[clazz_idx_dict[clz]] = 1
    mid_set.remove(first_mid)

    sorted_mid_list = list()
    sorted_mid_list.append(first_mid)
    prev_x = first_x
    while len(mid_set) > 0:
        cur_scores = list()
        cur_list = list(mid_set)
        for mut_id in cur_list:
            cur_x = [0 for _ in range(clazz_num)]
            tests = id_tests_dict[mut_id]
            for t in tests:
                clazzes = test_clazzes_dict[t]
                for clz in clazzes:
                    cur_x[clazz_idx_dict[clz]] = 1
            cur_scores.append(np.dot(prev_x, cur_x) / (np.linalg.norm(prev_x) * np.linalg.norm(cur_x)))
        if order == 'descending':
            most_idx = cur_scores.index(max(cur_scores))
        elif order == 'ascending':
            most_idx = cur_scores.index(min(cur_scores))
        cur_mid = cur_list[most_idx]
        sorted_mid_list.append(cur_mid)
        mid_set.remove(cur_mid)
    return sorted_mid_list


def reorder_mutants_by_frequency(mutant_id_list):
    idx_by_tup_list = list()
    for i, mut_id in enumerate(mutant_id_list):
        tests = id_tests_dict[mut_id]
        score = 0
        for t in tests:
            score += len(test_lines_dict[t])
        score /= len(tests)
        idx_by_tup_list.append((i, score, len(tests)))
    idx_by_tup_list.sort(key=lambda x: (x[1], x[2]), reverse=True)
    sorted_mid_list = [mutant_id_list[tup[0]] for tup in idx_by_tup_list]
    return sorted_mid_list


if __name__ == '__main__':
    clazz_idx = 0
    for project in project_list:
        print(f'{project} is processing... ...')
        junit_version = project_junitVersion_dict[project]
        id_tuple_dict, id_tests_dict = get_infos(project)
        test_clazzes_dict, test_lines_dict = preprocess()
        clazz_set = set()
        for _, per_list in test_clazzes_dict.items():
            clazz_set |= set(per_list)
        clazz_num = len(clazz_set)
        clazz_list = sorted(list(clazz_set))
        clazz_idx_dict = {clz: i for i, clz in enumerate(clazz_list)}
        clazz_vecSum_dict = dict()
        
        # mid_gid_dict = get_best_group_allocation(by='test')
        mid_gid_dict = get_default_allocation()
        
        mutants_by_group = [None] * clazz_num
        gid_list = [-1 for _ in range(clazz_num)]
        # vecSum_list = [0 for _ in range(clazz_num)]
        grp_id = -1
        cur_clazz = ''
        cur_list = list()
        for mid, mtup in id_tuple_dict.items():
            grp_id = mid_gid_dict[mid]
            clazz = mtup[clazz_idx]
            if cur_clazz != clazz:
                if len(cur_list) > 0:
                    i = clazz_idx_dict[cur_clazz]
                    mutants_by_group[i] = cur_list
                    gid_list[i] = grp_id
                    # vecSum_list[i] = clazz_vecSum_dict[cur_clazz]
                    cur_list = list()
                cur_clazz = clazz
            cur_list.append(mid)
        i = clazz_idx_dict[cur_clazz]
        mutants_by_group[i] = cur_list
        gid_list[i] = grp_id
        # vecSum_list[i] = clazz_vecSum_dict[cur_clazz]

        # temp_list = [(i, tup[0], tup[1]) for i, tup in enumerate(zip(gid_list, vecSum_list))]
        # sorted_temp_list = sorted(temp_list, key=lambda x: (x[1], x[2]))
        # cid_list = [-1 for _ in range(clazz_num)]
        # cur_gid = -1
        # cur_cid = 0
        # for tup in sorted_temp_list:
        #     grp_id = tup[1]
        #     if cur_gid != grp_id:
        #         cur_gid = grp_id
        #         cur_cid = 0
        #     else:
        #         cur_cid += 1
        #     cid_list[tup[0]] = cur_cid

        output_list = list()
        for i, mutants in enumerate(mutants_by_group):
            grp_id = int(gid_list[i])
            clz_id = 0
            # clz_id = cid_list[i]
            # mid_list = reorder_mutants_by_coverage(mutant_id_list=mutants,
            #                                        by='line')
            # mid_list = reorder_mutants_by_similarity(mutant_id_list=mutants,
            #                                          order='ascending')
            # mid_list = reorder_mutants_by_more_other_stuffs(group_id=grp_id,
            #                                                 mutant_id_list=mutants,
            #                                                 by='line')
            # mid_list = reorder_mutants_by_frequency(mutant_id_list=mutants)
            mid_list = mutants
            for j, mid in enumerate(mid_list):
                tests = id_tests_dict[mid]
                output_list.append(mutant_to_json(mutant=id_tuple_dict[mid],
                                                  test_list=random.sample(tests, k=len(tests)),
                                                  group_id=grp_id,
                                                  clazz_id=clz_id,
                                                  exec_seq=j,
                                                  junit_version=junit_version))
        # [clz, n-tst, 01-tst]_[clz-cvg, ln-cvg, clz-sim, clz-diff, clz-ext, ln-ext]_[def]
        with open(f'controlled_analyzed_data/both/guiding_files/{project}_def_def_shuf.json', 'w') as f:
            f.write(json.dumps(output_list, indent=4))
