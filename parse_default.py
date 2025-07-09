import json
import re
import os

from pygments.lexer import default

from parse_rough_data import proj_junit_mapping, mutant_pattern

tests_in_order_pattern_junit4 = r"testsInOrder=\[(.*)\]\]"
tests_in_order_pattern_junit5 = r"testsInOrder=\[(.*\])\]\]"

class Location:
    def __init__(self,
                 clazz,
                 method,
                 methodDesc):
        self.clazz = clazz
        self.method = method
        self.methodDesc = methodDesc

    def __eq__(self, other):
        if isinstance(other, Location):
            return (self.clazz == other.clazz and
                    self.method == other.method and
                    self.methodDesc == other.methodDesc)
        return False


class MutantIdentifier:
    def __init__(self, location, indexes, mutator):
        self.location = location
        self.indexes = indexes
        self.mutator = mutator

    def __eq__(self, other):
        if isinstance(other, MutantIdentifier):
            return (self.location == other.location and
                    self.indexes == other.indexes and
                    self.mutator == other.mutator)
        return False

    def to_tuple(self):
        return (self.location.clazz,
                self.location.method,
                self.location.methodDesc,
                self.indexes,
                self.mutator)


def process_block(blk):
    block_str = ''.join(blk)
    mutant_details = re.search(mutant_pattern, block_str)
    if not mutant_details:
        return
    mutant_id = MutantIdentifier(
        Location(
            mutant_details.group(1),
            mutant_details.group(2),
            mutant_details.group(3)
        ),
        mutant_details.group(4),
        mutant_details.group(5)
    )
    tests_in_order = re.search(tests_in_order_pattern, block_str)
    if junit_version == 'junit5':
        test_list = tests_in_order.group(1).split('], ')
        for i in range(len(test_list) - 1):
            test_list[i] += ']'
    else:
        test_list = tests_in_order.group(1).split('), ')
        for i in range(len(test_list) - 1):
            test_list[i] += ')'
    mutant_tup = mutant_id.to_tuple()
    if mutant_tup not in mutant_set:
        cnt = len(mutant_set)
        mutant_set.add(mutant_tup)
        id_tuple_mapping[cnt] = mutant_tup
        id_test_mapping[cnt] = test_list
    else:
        print('WRONG!')


# Parse log information
def parse_log(p):
    with open(f'{logs_dir}/{p}.log', 'r') as file:
        block = []
        capturing = False
        for line in file:
            if "start running" in line:
                if capturing:
                    process_block(block)
                    capturing = False
                if not capturing:
                    capturing = True
                    block = [line]
            elif capturing:
                block.append(line)
        process_block(block)


def output_jsons(p, s):
    output_path = f'{parsed_dir}/{p}_{s}'
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    with open(f'{output_path}/mutantId_mutantTuple.json', 'w') as file:
        json.dump(id_tuple_mapping, file, indent=4)
    with open(f'{output_path}/mutantId_testsInOrder.json', 'w') as file:
        json.dump(id_test_mapping, file, indent=4)


if __name__ == '__main__':
    project_list = ['commons-collections',
                    'Mybatis-PageHelper',
                    'jfreechart',
                    'JustAuth',
                    'sling-org-apache-sling-auth-core']
    logs_dir = 'pitest_logs'
    parsed_dir = 'controlled_parsed_data/both'
    tests_in_order_pattern_dict = {
        'junit4': tests_in_order_pattern_junit4,
        'junit5': tests_in_order_pattern_junit5
    }
    DEFAULT = 'default'
    for project in project_list:
        print(f'Process {project} with {DEFAULT}... ...')
        mutant_set = set()
        test_set = set()
        id_tuple_mapping = dict()
        id_test_mapping = dict()
        coverage_mapping = dict()
        default_seq = list()
        junit_version = proj_junit_mapping[project]
        tests_in_order_pattern = tests_in_order_pattern_dict[junit_version]
        parse_log(p=project)
        output_jsons(p=project, s=DEFAULT)
        # cnt = 0
        # uniq_id_tup_mapping = dict()
        # uniq_id_test_mapping = dict()
        # for v in id_tuple_mapping.values():
        #     v_to_json = {'clazz': v[0],
        #                  'method': v[1],
        #                  'methodDesc': v[2],
        #                  'indexes': tuple(int(itm.strip()) for itm in v[3].split(',')),
        #                  'mutator': v[4]}
        #     if v_to_json not in uniq_id_tup_mapping.values():
        #         uniq_id_tup_mapping[cnt] = v_to_json
        #         cnt += 1
        # cnt = 0
        # for test_list in id_tests_mapping.values():
        #     if len(test_list) > 0:
        #         for t in test_list:
        #             if t not in uniq_id_test_mapping.values():
        #                 uniq_id_test_mapping[cnt] = t
        #                 cnt += 1