import copy
import json
import random

from create_guiding_file import mutant_to_json
from parse_rough_data import project_junitVersion_dict

if __name__ == '__main__':
    proj_list = [
        'commons-codec',
        'riptide',
        'commons-cli',
        'jimfs',
        'empire-db',
        'delight-nashorn-sandbox',
        'handlebars.java'
    ]
    rand_seeds = [42 + i for i in range(5)]
    main_dir = 'for_checking_OID'
    DEFAULT = 'default'
    for proj in proj_list:
        with open(f'controlled_parsed_data/both/{proj}_{DEFAULT}/mutantId_mutantTuple.json', 'r') as f:
            id_tup_mapping = json.load(f)
        with open(f'controlled_parsed_data/both/{proj}_{DEFAULT}/mutantId_testsInOrder.json', 'r') as f:
            id_tests_mapping = json.load(f)

        clazz_seq = list()
        for _, tup in id_tup_mapping.items():
            if tup[0] in clazz_seq:
                continue
            clazz_seq.append(tup[0])

        sorted_items = sorted(
            id_tup_mapping.items(),
            key=lambda item: item[1][0]
        )
        sorted_id_tup_mapping = {k: v for k, v in sorted_items}
        id_list = list(sorted_id_tup_mapping.keys())
        group_list = list()
        temp = list()
        cur_clazz = ''
        for mut_id in id_list:
            mut = id_tup_mapping[mut_id]
            clazz = mut[0]
            if clazz != cur_clazz and len(temp) > 0:
                group_list.append(temp)
                cur_clazz = clazz
                temp = list()
            temp.append(mut_id)
        group_list.append(temp)

        i = 0
        uniq_id_tup_mapping = dict()
        uniq_id_test_mapping = dict()
        for v in id_tup_mapping.values():
            v_to_json = {'clazz': v[0],
                         'method': v[1],
                         'methodDesc': v[2],
                         'indexes': tuple(int(itm.strip()) for itm in v[3].split(',')),
                         'mutator': v[4]}
            if v_to_json not in uniq_id_tup_mapping.values():
                uniq_id_tup_mapping[i] = v_to_json
                i += 1
        i = 0
        for test_list in id_tests_mapping.values():
            if len(test_list) > 0:
                for t in test_list:
                    if t not in uniq_id_test_mapping.values():
                        uniq_id_test_mapping[i] = t
                        i += 1
        with open(f'{main_dir}/temp_outputs/before/{proj}_mutant_mapping.json', 'w') as f:
            f.write(json.dumps(uniq_id_tup_mapping, indent=4))
        with open(f'{main_dir}/temp_outputs/before/{proj}_test_mapping.json', 'w') as f:
            f.write(json.dumps(uniq_id_test_mapping, indent=4))

        # group_id = 0
        # clazz_id = 0
        # exeq_seq = 0
        # mutant_list = list()
        # for clazz in clazz_seq:
        #     for group in group_list:
        #         if clazz == id_tup_mapping[group[0]][0]:
        #             for mut_id in group:
        #                 mut = id_tup_mapping[mut_id]
        #                 mutant_list.append(mutant_to_json(mutant=mut,
        #                                                   test_list=id_tests_mapping[mut_id],
        #                                                   group_id=group_id,
        #                                                   clazz_id=clazz_id,
        #                                                   exec_seq=exeq_seq,
        #                                                   junit_version=project_junitVersion_dict[proj]))
        #                 exeq_seq += 1
        #             break
        #     group_id += 1
        #     exeq_seq = 0
        # with open(f'for_checking_OID/inputs/{proj}_default.json', 'w') as f:
        #     f.write(json.dumps(mutant_list, indent=4))

        # group_id = 0
        # clazz_id = 0
        # exeq_seq = 0
        # mutant_list = list()
        # for clazz in clazz_seq:
        #     for group in group_list:
        #         if clazz == id_tup_mapping[group[0]][0]:
        #             for mut_id in group:
        #                 mut = id_tup_mapping[mut_id]
        #                 mutant_list.append(mutant_to_json(mutant=mut,
        #                                                   test_list=id_tests_mapping[mut_id],
        #                                                   group_id=group_id,
        #                                                   clazz_id=clazz_id,
        #                                                   exec_seq=exeq_seq,
        #                                                   junit_version=project_junitVersion_dict[proj]))
        #                 exeq_seq += 1
        #             break
        #     clazz_id += 1
        #     exeq_seq = 0
        # with open(f'for_checking_OID/inputs/{proj}_single-group.json', 'w') as f:
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