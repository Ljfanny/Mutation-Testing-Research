import json
import re
import os
import numpy as np

# Project list
project_list = [
    'commons-codec',
    # 'commons-net',
    # 'delight-nashorn-sandbox',
    # 'empire-db',
    # 'jimfs'
]
TIMED_OUT = 'TIMED_OUT'
round_number = 6
random_mutant = False
random_test = True
seed_list = [0, 2024, 99999]
mutant_choice = {
    False: 'default-mutant',
    True: 'random-mutant'
}
test_choice = {
    False: 'default-test',
    True: 'random-test'
}
project_junitVersion_dict = {
    'commons-codec': 'junit5',
    'commons-net': 'junit5',
    'delight-nashorn-sandbox': 'junit4',
    'empire-db': 'junit4',
    'jimfs': 'junit4'
}
junit_version = ''
mutant_pattern = ''
test_description_pattern = ''
mutantId_mutantTuple_dict = {}
mutantId_testsInOrders_dict = {}
mutantId_runtimeList_dict = {}
mutantId_testRuntimeMatrix_dict = {}
test_testId_dict = {}
mutant_array = []
mutant_dict = {}

# Regex patterns
mutant_pattern_junit4 = r"location=Location \[clazz=([^,]+), method=([^,]+), methodDesc=([^]]+)\], indexes=\[([" \
                        r"^]]+)\], mutator=([^,]+)\], filename=([^,]+), block=\[([^]]+)\], lineNumber=(\d+), " \
                        r"description=([^,]+), testsInOrder=\[([^]]+)\]"
mutant_pattern_junit5 = r"location=Location \[clazz=([^,]+), method=([^,]+), methodDesc=([^]]+)\], indexes=\[([" \
                        r"^]]+)\], mutator=([^,]+)\], filename=([^,]+), block=\[([^]]+)\], lineNumber=(\d+), " \
                        r"description=([^,]+), testsInOrder=\[(.*\])\]\]"

test_description_pattern_junit4 = r"testClass=([^,]+), name=([^\]]+).*Running time: (\d+) ms"
test_description_pattern_junit5 = r"testClass=([^,]+), name=(.*)\].*Running time: (\d+) ms"
runtime_pattern = r"run all related tests in (\d+) ms"
group_boundary_pattern = r"Run all (\d+) mutants in (\d+) ms"


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


class Mutant:
    def __init__(self,
                 identifier,
                 filename,
                 block,
                 lineNumber,
                 description):
        self.identifier = identifier
        self.filename = filename
        self.block = block
        self.lineNumber = lineNumber
        self.description = description

    def to_tuple(self):
        return (self.identifier.location.clazz, self.identifier.location.method, self.identifier.location.methodDesc,
                self.identifier.indexes,
                self.identifier.mutator,
                self.filename,
                self.block,
                self.lineNumber,
                self.description)

    def __eq__(self, other):
        if isinstance(other, Mutant):
            return (self.identifier == other.identifier and
                    self.filename == other.filename and
                    self.block == other.block and
                    self.lineNumber == other.lineNumber and
                    self.description == other.description)


def process_block(block,
                  round):
    block_str = ''.join(block)
    # Extract mutation details
    mutant_details = re.search(mutant_pattern, block_str)
    if not mutant_details:
        return
    if junit_version == 'junit5':
        test_list = mutant_details.group(10).split('], ')
        for i in range(len(test_list) - 1):
            test_list[i] += ']'
    else:
        test_list = mutant_details.group(10).split('), ')
        for i in range(len(test_list) - 1):
            test_list[i] += ')'
    mutant = Mutant(
        MutantIdentifier(
            Location(
                mutant_details.group(1),
                mutant_details.group(2),
                mutant_details.group(3)
            ),
            mutant_details.group(4),
            mutant_details.group(5)
        ),
        mutant_details.group(6),
        mutant_details.group(7),
        mutant_details.group(8),
        mutant_details.group(9)
    )

    for test in test_list:
        if test in test_testId_dict:
            continue
        test_testId_dict[len(test_testId_dict)] = test

    complete_mutant = mutant.to_tuple() + (tuple(test_list), )
    if complete_mutant in mutant_array:
        mutant_id = mutant_dict[complete_mutant]
    else:
        mutant_id = len(mutant_array)
        mutant_array.append(complete_mutant)
        mutant_dict[complete_mutant] = mutant_id
        mutantId_mutantTuple_dict[mutant_id] = mutant.to_tuple()
        mutantId_testsInOrders_dict[mutant_id] = test_list
        mutantId_runtimeList_dict[mutant_id] = [np.nan for _ in range(round_number)]
        mutantId_testRuntimeMatrix_dict[mutant_id] = [None for _ in range(round_number)]

    # Extract test descriptions
    test_descriptions = re.findall(test_description_pattern, block_str)
    testRuntime_list = []
    for clazz, name, runtime in test_descriptions:
        testRuntime_list.append(int(runtime))
    run = True
    while len(testRuntime_list) < len(test_list):
        if run:
            testRuntime_list.append(TIMED_OUT)
            run = False
        else:
            testRuntime_list.append(np.nan)
    mutantId_testRuntimeMatrix_dict[mutant_id][round] = testRuntime_list

    # Extract test runtime
    runtime = re.search(runtime_pattern, block_str)
    if runtime:
        mutantId_runtimeList_dict[mutant_id][round] = int(runtime.group(1))
    else:
        mutantId_runtimeList_dict[mutant_id][round] = TIMED_OUT


# Parse log information
def parse_log(project,
              round,
              seed):
    choice = f'{mutant_choice[random_mutant]}_{test_choice[random_test]}'
    with open(f'controlled_logs/{choice}/{seed}/{project}_{round}.log', 'r') as file:
    # with open(f'controlled_logs/{choice}/fastest/{project}_{round}.log', 'r') as file:
        block = []
        capturing = False
        for line in file:
            if "start running" in line:
                if capturing:
                    process_block(block=block, round=round)
                    capturing = False
                if not capturing:
                    capturing = True
                    block = [line]
            elif capturing:
                block.append(line)
        process_block(block=block, round=round)


def output_jsons(seed):
    choice = f'{mutant_choice[random_mutant]}_{test_choice[random_test]}'
    # output_path = f'controlled_parsed_data/{choice}/{project}_fastest'
    output_path = f'controlled_parsed_data/{choice}/{project}_{seed}'
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    with open(f'{output_path}/mutantId_mutantTuple.json', 'w') as file:
        json.dump(mutantId_mutantTuple_dict, file, indent=4)
    with open(f'{output_path}/mutantId_testsInOrder.json', 'w') as file:
        json.dump(mutantId_testsInOrders_dict, file, indent=4)
    with open(f'{output_path}/mutantId_runtimeList.json', 'w') as file:
        json.dump(mutantId_runtimeList_dict, file, indent=4)
    with open(f'{output_path}/mutantId_testRuntimeMatrix.json', 'w') as file:
        json.dump(mutantId_testRuntimeMatrix_dict, file, indent=4)
    with open(f'{output_path}/testId_test.json', 'w') as file:
        json.dump(test_testId_dict, file, indent=4)


if __name__ == '__main__':
    mutant_pattern_dict = {
        'junit4': mutant_pattern_junit4,
        'junit5': mutant_pattern_junit5
    }
    test_description_pattern_dict = {
        'junit4': test_description_pattern_junit4,
        'junit5': test_description_pattern_junit5
    }
    for seed in seed_list:
        for project in project_list:
            print(f'{project} is processing... ...')
            junit_version = project_junitVersion_dict[project]
            mutant_pattern = mutant_pattern_dict[junit_version]
            test_description_pattern = test_description_pattern_dict[junit_version]
            mutantId_mutantTuple_dict.clear()
            mutantId_testsInOrders_dict.clear()
            mutantId_runtimeList_dict.clear()
            mutantId_testRuntimeMatrix_dict.clear()
            test_testId_dict.clear()
            mutant_array.clear()
            mutant_dict.clear()
            for r in range(round_number):
                parse_log(project=project,
                          round=r,
                          seed=seed)
            output_jsons(seed=seed)
