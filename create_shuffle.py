import copy
import json
import random
import pandas as pd
from parse_rough_data import build_default_junit_map


proj_list = [
    'commons-cli',
    'commons-codec',
    'commons-collections',
    'empire-db',
    'handlebars.java',
    'jfreechart',
    'jimfs',
    'JustAuth',
    'Mybatis-PageHelper',
    'riptide',
    'sling-org-apache-sling-auth-core',
    # 'assertj-assertions-generator',
    # 'commons-net',
    # 'commons-csv',
    # 'delight-nashorn-sandbox',
    # 'httpcore',
    # 'guava',
    # 'java-design-patterns',
    # 'jooby',
    # 'maven-dependency-plugin',
    # 'maven-shade-plugin',
    # 'stream-lib'
]


def mutant_to_json(mutant, test_id_list, group_id, clazz_id, exec_seq, junit_version):
    test_order = []
    if junit_version == 'junit4':
        for test_id in test_id_list:
            t = id_test_mapping[test_id]
            paren_idx = t.find('(')
            i = 0
            for i in range(paren_idx, 0, -1):
                if t[i] == '.':
                    break
            test_order.append({
                'definingClass': t[:i],
                'name': t
            })
    else:
        for test_id in test_id_list:
            t = id_test_mapping[test_id]
            class_end_idx = t.find('[')
            test_order.append({
                'definingClass': t[:class_end_idx - 1],
                'name': t
            })
    return {
        'id': {
            'location': {
                'clazz': mutant['clazz'],
                'method': mutant['method'],
                'methodDesc': mutant['methodDesc'],
            },
            'indexes': f'{mutant['indexes']}',
            'mutator': mutant['mutator']
        },
        'testsInOrder': test_order,
        'groupId': group_id,
        'clazzId': clazz_id,
        'executionSeq': exec_seq
    }


# def create_default(p):
#     group_id = 0
#     clazz_id = 0
#     exec_seq = 0
#     mutant_list = list()
#     for clazz in default_seq:
#         group = clazz_ids_mapping[clazz]
#         for mutant_id in group:
#             mutant = id_tuple_mapping[mutant_id]
#             mutant_list.append(mutant_to_json(
#                 mutant=mutant,
#                 test_id_list=coverage_mapping[mutant_id],
#                 group_id=group_id,
#                 clazz_id=clazz_id,
#                 exec_seq=exec_seq,
#                 junit_version=proj_junit_mapping[p]
#             ))
#             exec_seq += 1
#             break
#         group_id += 1
#         exec_seq = 0
#     with open(f'for_checking_OID/inputs/{p}_default.json', 'w') as f:
#         f.write(json.dumps(mutant_list, indent=4))


def create_double(p):
    group_id = 0
    clazz_id = 0
    exec_seq = 0
    mutant_list = list()
    proj_junit_mapping = build_default_junit_map()
    for clazz in default_seq:
        group = clazz_ids_mapping[clazz]
        mid = int(len(group) / 2)
        is_refresh = False
        for i, mutant_id in enumerate(group):
            mutant = id_tuple_mapping[mutant_id]
            mutant_list.append(mutant_to_json(
                mutant=mutant,
                test_id_list=coverage_mapping[mutant_id],
                group_id=group_id,
                clazz_id=clazz_id,
                exec_seq=exec_seq,
                junit_version=proj_junit_mapping[p]
            ))
            exec_seq += 1
            if exec_seq >= mid and not is_refresh:
                group_id += 1
                exec_seq = 0
                is_refresh = True
        group_id += 1
        exec_seq = 0
    with open(f'for_checking_OID/inputs/{p}_double.json', 'w') as f:
        f.write(json.dumps(mutant_list, indent=4))


# def create_single(p):
    # group_id = 0
    # clazz_id = 0
    # exec_seq = 0
    # mutant_list = list()
    # with open(f'{main_dir}/mutant_list/erroneous/{project}.json', 'r') as f:
    #     error_arr = json.load(f)
    # for clazz in default_seq:
    #     group = clazz_ids_mapping[clazz]
    #     for mutant_id in group:
    #         if int(mut_id) in error_arr:
    #             continue
    #         mutant = id_tuple_mapping[mut_id]
    #         mutant_list.append(mutant_to_json(mutant=mut,
    #                                                   test_list=id_tests_mapping[mut_id],
    #                                                   group_id=group_id,
    #                                                   clazz_id=clazz_id,
    #                                                   exec_seq=exeq_seq,
    #                                                   junit_version=proj_junit_mapping[project]))
    #                 exeq_seq += 1
    #             break
    #     clazz_id += 1
        exeq_seq = 0
    # with open(f'for_checking_OID/inputs/{project}_single-group.json', 'w') as f:
    #     f.write(json.dumps(mutant_list, indent=4))


def create_by_proportion(p):
    print('creating by_proportion: {}'.format(p))
    df = pd.read_csv(f'{main_dir}/runtime_analysis_dir/percentage/{p}_default.csv')
    df = df[['clazz', 'avg.']]
    capacity = df['avg.'].max()
    items = list(zip(df['clazz'], df['avg.']))
    items.sort(key=lambda x: x[1], reverse=True)
    bins = []
    bin_sums = []
    for clazz, weight in items:
        placed = False
        for i, total in enumerate(bin_sums):
            if total + weight <= capacity:
                bins[i].append(clazz)
                bin_sums[i] += weight
                placed = True
                break
        if not placed:
            bins.append([clazz])
            bin_sums.append(weight)
    group_id = 0
    clazz_id = 0
    exec_seq = 0
    mutant_list = list()
    for clazz_arr in bins:
        for clazz in clazz_arr:
            mutant_id_list = clazz_ids_mapping[clazz]
            for mutant_id in mutant_id_list:
                mutant = id_tuple_mapping[mutant_id]
                mutant_list.append(mutant_to_json(
                    mutant=mutant,
                    test_id_list=coverage_mapping[mutant_id],
                    group_id=group_id,
                    clazz_id=clazz_id,
                    exec_seq=exec_seq,
                    junit_version=proj_junit_mapping[p]
                ))
                exec_seq += 1
            clazz_id += 1
            exec_seq = 0
        group_id += 1
        clazz_id = 0
    with open(f'for_checking_OID/inputs/{p}_by-proportions.json', 'w') as f:
        f.write(json.dumps(mutant_list, indent=4))


if __name__ == '__main__':
    rand_seeds = [42 + i for i in range(5)]
    main_dir = 'for_checking_OID'
    inputs_dir = f'{main_dir}/inputs'
    parsed_basis_dir = f'{main_dir}/parsed_dir/basis'
    for proj in proj_list:
        id_tuple_mapping = {int(k): v for k, v in json.load(open(f'{parsed_basis_dir}/{proj}/id_mutant_mapping.json', 'r')).items()}
        id_test_mapping = {int(k): v for k, v in json.load(open(f'{parsed_basis_dir}/{proj}/id_test_mapping.json', 'r')).items()}
        coverage_mapping = {int(k): v for k, v in json.load(open(f'{parsed_basis_dir}/{proj}/coverage_mapping.json', 'r')).items()}
        default_seq = json.load(open(f'{parsed_basis_dir}/{proj}/default_seq.json', 'r'))
        clazz_ids_mapping = json.load(open(f'{parsed_basis_dir}/{proj}/clazz_ids_mapping.json', 'r'))

        create_double(proj)

        # create_by_proportion(proj)

        # clazz_id -= 1
        # cur_clazz = clazz_seq[-1]
        # for mut_id in error_arr:
        #     mut_id = str(mut_id)
        #     mut = id_tup_mapping[mut_id]
        #     clazz = mut[0]
        #     if clazz != cur_clazz:
        #         cur_clazz = clazz
        #         clazz_id += 1
        #         exeq_seq = 0
        #     mutant_list.append(mutant_to_json(mutant=mut,
        #                                       test_list=id_tests_mapping[mut_id],
        #                                       group_id=group_id,
        #                                       clazz_id=clazz_id,
        #                                       exec_seq=exeq_seq,
        #                                       junit_version=project_junit_mapping[project]))
        #     exeq_seq += 1
        # with open(f'for_checking_OID/inputs/{project}_single-group_errors-at-the-end.json', 'w') as f:
        #     f.write(json.dumps(mutant_list, indent=4))

        # for seed in rand_seeds:
        #     random.seed(seed)
        #     group_list_copy = copy.deepcopy(group_list)
        #     random.shuffle(group_list_copy)
        #     mutant_list = list()
        #     group_id = 0
        #     clazz_id = 0
        #     exeq_seq = 0
        #     for group in group_list_copy:
        #         random.shuffle(group)
        #         exeq_seq = 0
        #         for mut_id in group:
        #             mut = id_tup_mapping[mut_id]
        #             shuf_test_list = random.sample(id_tests_mapping[mut_id], k=len(id_tests_mapping[mut_id]))
        #             mutant_list.append(mutant_to_json(mutant=mut,
        #                                               test_list=shuf_test_list,
        #                                               group_id=group_id,
        #                                               clazz_id=clazz_id,
        #                                               exec_seq=exeq_seq,
        #                                               junit_version=project_junitVersion_dict[proj]))
        #             exeq_seq += 1
        #         clazz_id += 1
        #     with open(f'for_checking_OID/inputs/{proj}_single-group_random-{seed}.json', 'w') as f:
        #         f.write(json.dumps(mutant_list, indent=4))