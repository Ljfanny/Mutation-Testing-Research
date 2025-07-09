import copy
import json
import random
from parse_rough_data import proj_junit_mapping


def mutant_to_json(mutant, test_list, group_id, clazz_id, exec_seq, junit_version):
    test_order = []
    if junit_version == 'junit4':
        for test in test_list:
            paren_idx = test.find('(')
            i = 0
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


def create_default(p):
    group_id = 0
    clazz_id = 0
    exec_seq = 0
    mutant_list = list()
    for clazz in default_seq:
        group = clazz_ids_mapping[clazz]
        for mutant_id in group:
            mutant = id_tuple_mapping[mutant_id]
            mutant_list.append(mutant_to_json(
                mutant=mutant,
                test_list=coverage_mapping[mutant_id],
                group_id=group_id,
                clazz_id=clazz_id,
                exec_seq=exec_seq,
                junit_version=proj_junit_mapping[p]
            ))
            exec_seq += 1
            break
        group_id += 1
        exec_seq = 0
    with open(f'for_checking_OID/inputs/{p}_default.json', 'w') as f:
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


if __name__ == '__main__':
    proj_list = [
        'commons-collections',
        'Mybatis-PageHelper',
        'jfreechart',
        'JustAuth',
        'sling-org-apache-sling-auth-core'
    ]
    rand_seeds = [42 + i for i in range(5)]
    inputs_dir = 'for_checking_OID/inputs'
    parsed_basis_dir = 'for_checking_OID/parsed_data/basis'
    for proj in proj_list:
        with open(f'{parsed_basis_dir}/id_mutant_mapping.json', 'r') as f:
            id_tuple_mapping = {int(k): v for k, v in json.load(f).items()}
        with open(f'{parsed_basis_dir}/id_test_mapping.json', 'r') as f:
            id_test_mapping = {int(k): v for k, v in json.load(f).items()}
        with open(f'{parsed_basis_dir}/default_seq.json', 'r') as f:
            default_seq = json.load(f)
        with open(f'{parsed_basis_dir}/coverage_mapping.json', 'r') as f:
            coverage_mapping = {int(k): v for k, v in json.load(f).items()}
        with open(f'{parsed_basis_dir}/clazz_ids_mapping.json', 'r') as f:
            clazz_ids_mapping = json.load(f)



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