import math
import json
import numpy as np
import warnings
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from pitest_log_parser import project_junitVersion_dict

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
            paren_index = test.find('(')
            for i in range(paren_index, 0, -1):
                if test[i] == '.':
                    break
            test_order.append({
                'definingClass': test[:i],
                'name': test
            })
    else:
        for test in test_list:
            class_end_index = test.find('[')
            test_order.append({
                'definingClass': test[:class_end_index - 1],
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


# Use k-means to get the best group number
def get_best_group_allocation(by='clazz'):
    def based_on_clazz():
        clazz_set = set()
        test_clazzList_dict = dict()
        for mut_id, mut_tup in id_tuple_dict.items():
            clazz = mut_tup[clazz_idx]
            tests = id_tests_dict[mut_id]
            clazz_set.add(clazz)
            for t in tests:
                if t in test_clazzList_dict:
                    test_clazzList_dict[t].append(clazz)
                else:
                    test_clazzList_dict[t] = [clazz]
        clazz_list = sorted(list(clazz_set))
        # print('Number of mutants:', len(id_tuple_dict))
        # print('Number of classes:', len(clazz_list))
        clazz_idx_dict = {clz: i for i, clz in enumerate(clazz_list)}
        test_clazzList_dict = {k: list(set(v)) for k, v in test_clazzList_dict.items()}
        Xs = list()
        n_features = len(clazz_set)
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
                clazz_list = test_clazzList_dict[t]
                for clz in clazz_list:
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
        # print('Number of tests:', len(test_list))
        # print('Number of total counts:', total_counts)
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
                # cur_features[test_idx_dict[t]] += 1
                cur_features[test_idx_dict[t]] = 1
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
            clazz_count_dict[clazz] = sum(Xs[cnt])

    if by == 'test':
        Xs = based_on_test()

    clazz_set = set()
    for mut_id, mut_tup in id_tuple_dict.items():
        clazz = mut_tup[clazz_idx]
        clazz_set.add(clazz)
    n_clazz = len(clazz_set)
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
    # print('Number of groups based on tests:', n_clusters_list[max_idx])
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


def reorder_mutants_by_coverage(mid_list, by='clazz', order='descending'):
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

    idx_by_tup_list = list()
    for i, mut_id in enumerate(mid_list):
        tests = id_tests_dict[mut_id]
        clazz_list = list()
        for t in tests:
            if by == 'clazz':
                clazz_list += test_clazzList_dict[t]
            elif by == 'line':
                clazz_list += test_lineNums_dict[t]
        idx_by_tup_list.append((i, len(set(clazz_list)), len(tests)))
    idx_by_tup_list.sort(key=lambda x: (x[1], x[2]), reverse=True)
    sorted_mid_list = [mid_list[tup[0]] for tup in idx_by_tup_list]
    return sorted_mid_list if order == 'descending' else sorted_mid_list[::-1]


if __name__ == '__main__':
    clazz_idx = 0
    for project in project_list:
        print(f'{project} is processing... ...')
        junit_version = project_junitVersion_dict[project]
        id_tuple_dict, id_tests_dict = get_infos(project)
        clazz_count_dict = dict()
        mid_gid_dict = get_best_group_allocation(by='test')
        mutants_by_group = list()
        gid_list = list()
        cnt_list = list()
        cur_clazz = ''
        cur_list = list()
        gid = -1
        for mid, mtup in id_tuple_dict.items():
            gid = mid_gid_dict[mid]
            clazz = mtup[clazz_idx]
            if cur_clazz != clazz:
                if len(cur_list) > 0:
                    mutants_by_group.append(cur_list)
                    gid_list.append(gid)
                    cnt_list.append(clazz_count_dict[cur_clazz])
                    cur_list = list()
                cur_clazz = clazz
            cur_list.append(mid)
        mutants_by_group.append(cur_list)
        gid_list.append(gid)
        cnt_list.append(clazz_count_dict[cur_clazz])

        temp_list = [(i, tup[0], tup[1]) for i, tup in enumerate(zip(gid_list, cnt_list))]
        sorted_temp_list = sorted(temp_list, key=lambda x: (x[1], x[2]))
        cid_list = [-1 for _ in range(len(temp_list))]
        cur_gid = -1
        cur_cid = 0
        for tup in sorted_temp_list:
            gid = tup[1]
            if cur_gid != gid:
                cur_gid = gid
                cur_cid = 0
            else:
                cur_cid += 1
            cid_list[tup[0]] = cur_cid

        output_list = list()
        for i, mutants in enumerate(mutants_by_group):
            gid = int(gid_list[i])
            cid = cid_list[i]
            mid_list = reorder_mutants_by_coverage(mid_list=mutants,
                                                   by='line')
            for j, mid in enumerate(mid_list):
                output_list.append(mutant_to_json(mutant=id_tuple_dict[mid],
                                                  test_list=id_tests_dict[mid],
                                                  group_id=gid,
                                                  clazz_id=cid,
                                                  exec_seq=j,
                                                  junit_version=junit_version))
        # [clz, tst]_[clz-cvg, ln-cvg]_[def]
        with open(f'controlled_analyzed_data/both/guiding_files/{project}_01-tst_ln-cvg_def.json', 'w') as f:
            f.write(json.dumps(output_list, indent=4))
