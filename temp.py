# Keep mutant order.
import copy
import json
from pitest_log_parser import project_junitVersion_dict

project_list = [
    'assertj-assertions-generator',
    'commons-cli',
    'commons-csv',
    'commons-codec',
    'delight-nashorn-sandbox',
    'empire-db',
    'jimfs'
]
parsed_dir = 'controlled_parsed_data'
analyzed_dir = 'controlled_analyzed_data'
choice = 'more_projects'


def mutant_sort(mutant):
    return (
        mutant['id']['location']['clazz'],
        -len(mutant['testsInOrder'])
    )


def get_info(file_path):
    with open(f'{file_path}/mutantId_mutantTuple.json', 'r') as f:
        id_tuple_dict = json.load(f)
    with open(f'{file_path}/mutantId_testsInOrder.json', 'r') as f:
        id_tests_dict = json.load(f)
    return id_tuple_dict, id_tests_dict


def mutant_to_json(mutant, test_list, junit_version):
    test_order = []
    if junit_version == 'junit4':
        for test in test_list:
            paren_index = test.find('(')
            for i in range(paren_index, 0, -1):
                if test[i] == '.': break
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
        'testsInOrder': test_order
    }


if __name__ == '__main__':
    for project in project_list:
        id_tuple_dict, id_tests_dict = get_info(f'parsed_data/default_version/{project}')
        output_list = list()
        for mut_id, mut_tup in id_tuple_dict.items():
            output_list.append(mutant_to_json(mutant=mut_tup,
                                              test_list=id_tests_dict[mut_id],
                                              junit_version=project_junitVersion_dict[project]))
        output_list.sort(key=mutant_sort)
        with open(f'{analyzed_dir}/{choice}/guiding_files/{project}_GC_morder.json', 'w') as f:
            f.write(json.dumps(output_list, indent=4))

        # id_tuple_dict, id_tests_dict = get_info(f'parsed_data/default_version/{project}')
        # reordered_mutants = list()
        # for mut_id, mut_tup in id_tuple_dict.items():
        #     mut = mut_tup[:5] + [id_tests_dict[mut_id]]
        #     reordered_mutants.append(mut)
        # reordered_mutants.sort(key=mutant_sort)
        # output_list = list()
        # recorded_clazz_set = set()
        # stack = list()
        # for mut in reordered_mutants:
        #     clazz = mut[clazz_index]
        #     tests = mut[tests_index]
        #     if clazz in recorded_clazz_set:
        #         reordered_tests = list()
        #         cur_stack = list()
        #         remains = copy.deepcopy(tests)
        #         while len(stack) > 0:
        #             t = stack.pop()
        #             if t in tests:
        #                 reordered_tests.append(t)
        #                 cur_stack.append(t)
        #                 remains.remove(t)
        #         reordered_tests += remains
        #         stack = cur_stack + remains
        #         output_list.append(mutant_to_json(mutant=mut,
        #                                           test_list=reordered_tests,
        #                                           junit_version=project_junitVersion_dict[project]))
        #     else:
        #         recorded_clazz_set.add(clazz)
        #         stack = list()
        #         for t in tests:
        #             stack.append(t)
        #         output_list.append(mutant_to_json(mutant=mut,
        #                                           test_list=tests,
        #                                           junit_version=project_junitVersion_dict[project]))
        # with open(f'{analyzed_dir}/{choice}/guiding_files/{project}_GC_torder.json', 'w') as f:
        #     f.write(json.dumps(output_list, indent=4))
