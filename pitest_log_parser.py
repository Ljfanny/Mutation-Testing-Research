import json
import re
import os
import pandas as pd
import numpy as np

# Project list
project_list = [
    'commons-codec',
    'commons-net',
    'delight-nashorn-sandbox',
    'empire-db',
    'jimfs'
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
mutant_details_pattern = ''
mutantId_mutantTuple_dict = {}
mutantId_runtimeList_dict = {}
mutantId_testRuntimeListList_dict = {}
test_testId_dict = {}
mutant_array = []
mutant_dict = {}

# Regex patterns
mutant_details_pattern_1 = r"location=Location \[clazz=([^,]+), method=([^,]+), methodDesc=([^]]+)\], indexes=\[([" \
                           r"^]]+)\], mutator=([^,]+)\], filename=([^,]+), block=\[([^]]+)\], lineNumber=(\d+), " \
                           r"description=([^,]+), testsInOrder=\[(.*\])\]\]"
mutant_details_pattern_2 = r"location=Location \[clazz=([^,]+), method=([^,]+), methodDesc=([^]]+)\], indexes=\[([" \
                           r"^]]+)\], mutator=([^,]+)\], filename=([^,]+), block=\[([^]]+)\], lineNumber=(\d+), " \
                           r"description=([^,]+), testsInOrder=\[([^]]+)\]"
replacement_time_pattern = r"replaced class with mutant in (\d+) ms"
test_description_pattern = r"testClass=(.*?), name=(\[.*?\]).*?Running time: (\d+)"
runtime_pattern = r"run all related tests in (\d+) ms"


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


class Mutant:
    def __init__(self,
                 location,
                 indexes,
                 mutator,
                 filename,
                 block,
                 lineNumber,
                 description,
                 testsInOrder):
        self.location = location
        self.indexes = indexes
        self.mutator = mutator
        self.filename = filename
        self.block = block
        self.lineNumber = lineNumber
        self.description = description
        self.testsInOrder = testsInOrder

    def to_tuple(self):
        return (self.location.clazz, self.location.method, self.location.methodDesc,
                self.indexes,
                self.mutator,
                self.filename,
                self.block,
                self.lineNumber,
                self.description,
                tuple(self.testsInOrder))

    def __eq__(self, other):
        if not isinstance(other, Mutant):
            return NotImplemented
        return (self.location == other.location and
                self.indexes == other.indexes and
                self.mutator == other.mutator and
                self.filename == other.filename and
                self.block == other.block and
                self.lineNumber == other.lineNumber and
                self.description == other.description and
                self.testsInOrder == other.testsInOrder)

    def __str__(self):
        return (f"Mutant(Location: {self.location}, Indexes: {self.indexes}, "
                f"Mutator: {self.mutator}, Filename: {self.filename}, "
                f"Block: {self.block}, LineNumber: {self.lineNumber}, "
                f"Description: {self.description}, TestsInOrder: {self.testsInOrder})")


def process_block(block,
                  round):
    block_str = ''.join(block)
    # Extract mutation details
    mutant_details = re.search(mutant_details_pattern, block_str)
    if not mutant_details:
        return
    mutant = Mutant(
        Location(
            mutant_details.group(1),
            mutant_details.group(2),
            mutant_details.group(3)),
        mutant_details.group(4),
        mutant_details.group(5),
        mutant_details.group(6),
        mutant_details.group(7),
        mutant_details.group(8),
        mutant_details.group(9),
        mutant_details.group(10).split(', ')
    )
    for test in mutant.testsInOrder:
        if test in test_testId_dict:
            continue
        test_testId_dict[test] = len(test_testId_dict)

    if mutant.to_tuple() in mutant_array:
        mutant_id = mutant_dict[mutant.to_tuple()]
    else:
        mutant_id = len(mutant_array)
        mutant_array.append(mutant.to_tuple())
        mutant_dict[mutant.to_tuple()] = mutant_id
        mutantId_mutantTuple_dict[mutant_id] = mutant.to_tuple()
        mutantId_runtimeList_dict[mutant_id] = [np.nan for _ in range(round_number)]
        mutantId_testRuntimeListList_dict[mutant_id] = [None for _ in range(round_number)]

    # Extract replacement time
    # replacement_time = re.search(replacement_time_pattern, block_str)
    # if replacement_time:
    # print("Replacement Time:", replacement_time.group(1), "ms")

    # Extract test descriptions
    test_descriptions = re.findall(test_description_pattern, block_str)
    testRuntime_list = []
    for clazz, name, runtime in test_descriptions:
        testRuntime_list.append(runtime)
    run = True
    while len(testRuntime_list) < len(mutant.testsInOrder):
        if run:
            testRuntime_list.append(TIMED_OUT)
            run = False
        else:
            testRuntime_list.append(np.nan)
    mutantId_testRuntimeListList_dict[mutant_id][round] = testRuntime_list

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
    with open(f'pitest-logs/{choice}/{seed}/{project}_{round}.log', 'r') as file:
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
    output_path = f'log-parsed-data/{choice}/{project}_{seed}'
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    with open(f'{output_path}/mutantId_mutantTuple.json', 'w') as file:
        json.dump(mutantId_mutantTuple_dict, file, indent=4)
    with open(f'{output_path}/mutantId_runtimeList.json', 'w') as file:
        json.dump(mutantId_runtimeList_dict, file, indent=4)
    with open(f'{output_path}/mutantId_testRuntimeListList.json', 'w') as file:
        json.dump(mutantId_testRuntimeListList_dict, file, indent=4)
    with open(f'{output_path}/test_testId.json', 'w') as file:
        json.dump(test_testId_dict, file, indent=4)


if __name__ == '__main__':
    project_mutantDetailsPattern_dict = {
        'commons-codec': mutant_details_pattern_1,
        'commons-net': mutant_details_pattern_1,
        'delight-nashorn-sandbox': mutant_details_pattern_2,
        'empire-db': mutant_details_pattern_2,
        'jimfs': mutant_details_pattern_2
    }
    for seed in seed_list:
        for project in project_list:
            mutant_details_pattern = project_mutantDetailsPattern_dict[project]
            mutantId_mutantTuple_dict.clear()
            mutantId_runtimeList_dict.clear()
            mutantId_testRuntimeListList_dict.clear()
            test_testId_dict.clear()
            mutant_array.clear()
            mutant_dict.clear()
            for r in range(round_number):
                parse_log(project=project,
                          round=r,
                          seed=seed)
            output_jsons(seed=seed)
