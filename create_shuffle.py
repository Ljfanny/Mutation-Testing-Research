import json
import random

from create_guiding_file import mutant_to_json
from parse_pitest_log import project_junitVersion_dict

if __name__ == '__main__':
    proj_list = ['commons-codec', 'riptide']
    DEFAULT = 'default'
    for proj in proj_list:
        with open(f'controlled_parsed_data/both/{proj}_{DEFAULT}/mutantId_mutantTuple.json', 'r') as f:
            id_tup_mapping = json.load(f)
        with open(f'controlled_parsed_data/both/{proj}_{DEFAULT}/mutantId_testsInOrder.json', 'r') as f:
            id_tests_mapping = json.load(f)
        with open(f'controlled_analyzed_data/both/mutant_list/non-flaky/{proj}_{DEFAULT}.json', 'r') as f:
            non_flaky_list = json.load(f)

        random.shuffle(non_flaky_list)
        mutant_list = list()
        group_id = 0
        cur_clazz = ''
        clazz_id = -1
        exeq_seq = 0
        for mut_id in non_flaky_list:
            shuf_test_list = random.sample(id_tests_mapping[mut_id], k=len(id_tests_mapping[mut_id]))
            mut = id_tup_mapping[mut_id]
            clazz = mut[0]
            if clazz != cur_clazz:
                clazz_id += 1
                cur_clazz = clazz
                exeq_seq = 0
            mutant_list.append(mutant_to_json(mutant=mut,
                                              test_list=shuf_test_list,
                                              group_id=group_id,
                                              clazz_id=clazz_id,
                                              exec_seq=exeq_seq,
                                              junit_version=project_junitVersion_dict[proj]))

        with open(f'controlled_analyzed_data/both/guiding_files/{proj}_shuffled.json', 'w') as f:
            f.write(json.dumps(mutant_list, indent=4))