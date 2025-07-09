import json
import re
import os
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

    def to_json(self):
        return {'clazz': self.location.clazz,
                'method': self.location.method,
                'methodDesc': self.location.methodDesc,
                'indexes': tuple(int(itm.strip()) for itm in self.indexes.split(',')),
                'mutator': self.mutator}


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

    if mutant_id.location.clazz not in default_seq:
        default_seq.append(mutant_id.location.clazz)
        clazz_ids_mapping[mutant_id.location.clazz] = list()

    mutant_cnt = -1
    mutant = mutant_id.to_json()
    if mutant not in id_tuple_mapping.values():
        mutant_cnt = len(id_tuple_mapping.values())
        id_tuple_mapping[mutant_cnt] = mutant

    if mutant_cnt >= 0:
        id_arr = list()
        clazz_ids_mapping[mutant_id.location.clazz].append(mutant_cnt)
        for t in test_list:
            if t not in id_test_mapping.values():
                test_cnt = len(id_test_mapping.values())
                id_test_mapping[test_cnt] = t
                test_id_mapping[t] = test_cnt
            else:
                test_cnt = test_id_mapping[t]
            id_arr.append(test_cnt)
        coverage_mapping[mutant_cnt] = id_arr


# Parse log information
def parse_log(p):
    with open(f'{logs_dir}/{p}.log', 'r') as f:
        block = []
        capturing = False
        for line in f:
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


def output_jsons(p):
    output_path = f'{parsed_dir}/{p}'
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    with open(f'{output_path}/id_mutant_mapping.json', 'w') as f:
        json.dump(id_tuple_mapping, f, indent=4)
    with open(f'{output_path}/id_test_mapping.json', 'w') as f:
        json.dump(id_test_mapping, f, indent=4)
    with open(f'{output_path}/default_seq.json', 'w') as f:
        json.dump(default_seq, f, indent=4)
    with open(f'{output_path}/coverage_mapping.json', 'w') as f:
        json.dump(coverage_mapping, f, indent=4)
    with open(f'{output_path}/clazz_ids_mapping.json', 'w') as f:
        json.dump(clazz_ids_mapping, f, indent=4)


if __name__ == '__main__':
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
        'sling-org-apache-sling-auth-core'
    ]
    logs_dir = 'pitest_logs'
    parsed_dir = 'for_checking_OID/parsed_dir/basis'
    tests_in_order_pattern_dict = {
        'junit4': tests_in_order_pattern_junit4,
        'junit5': tests_in_order_pattern_junit5
    }
    DEFAULT = 'default'
    for proj in proj_list:
        print(f'Process {proj} with {DEFAULT}... ...')
        id_tuple_mapping = dict()
        id_test_mapping = dict()
        test_id_mapping = dict()
        coverage_mapping = dict()
        clazz_ids_mapping = dict()
        default_seq = list()
        junit_version = proj_junit_mapping[proj]
        tests_in_order_pattern = tests_in_order_pattern_dict[junit_version]
        parse_log(p=proj)
        output_jsons(p=proj)