import re
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

keyId_runtimeList_dict = {}
mutant_array = []
key_dict = {}
key_array = []
keyId_mutantId_dict = {}

# Regex patterns
mutant_details_pattern = r"location=Location \[clazz=([^,]+), method=([^,]+), methodDesc=([^]]+)\], indexes=\[([" \
                         r"^]]+)\], mutator=([^,]+)\], filename=([^,]+), block=\[([^]]+)\], lineNumber=(\d+), " \
                         r"description=([^,]+), testsInOrder=\[([^]]+)\]"
replacement_time_pattern = r"replaced class with mutant in (\d+) ms"
test_description_pattern = r"Test Description \[testClass=([^,]+), name=([^]]+)\] Running time: (\d+) ms"
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
    mutant_id = len(mutant_array)
    mutant_array.append(mutant)
    key = (mutant.location.clazz, mutant.location.method, mutant.location.methodDesc,
           mutant.indexes,
           mutant.mutator,
           mutant.filename,
           mutant.block,
           mutant.lineNumber,
           mutant.description)
    if random_test:
        key += (tuple(set(mutant.testsInOrder)),)
    else:
        key += (tuple(mutant.testsInOrder),)
    if key not in key_dict:
        key_id = len(key_array)
        key_array.append(key)
        key_dict[key] = key_id
        keyId_mutantId_dict[key_id] = (mutant_id,)
        keyId_runtimeList_dict[key_id] = [np.nan for _ in range(round_number)]
    else:
        key_id = key_dict[key]
        keyId_mutantId_dict[key_id] += (mutant_id,)

    # Extract replacement time
    # replacement_time = re.search(replacement_time_pattern, block_str)
    # if replacement_time:
    # print("Replacement Time:", replacement_time.group(1), "ms")

    # Extract test descriptions
    # test_descriptions = re.findall(test_description_pattern, block_str)
    # for test in test_descriptions:
    #     print("Test Class:", test[0])
    #     print("Test Name:", test[1])
    #     print("Running Time:", test[2], "ms")

    # Extract test runtime
    runtime = re.search(runtime_pattern, block_str)
    if runtime:
        keyId_runtimeList_dict[key_id][round] = int(runtime.group(1))
    else:
        keyId_runtimeList_dict[key_id][round] = 'TIMED_OUT'


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
                    process_block(block=block,
                                  round=round)
                    capturing = False
                if not capturing:
                    capturing = True
                    block = [line]
            elif capturing:
                block.append(line)


def get_mutant_runtime_csv(seed):
    columns = ['mutant']
    for i in range(round_number):
        columns.append(f'round-{i}')
    df = pd.DataFrame(None,
                      columns=columns)
    for key_id, runtime_list in keyId_runtimeList_dict.items():
        key = key_array[key_id]
        df.loc[len(df.index)] = [key] + runtime_list
    df.to_csv(f'analyzed-data/{mutant_choice[random_mutant]}_{test_choice[random_test]}/{seed}_{project}.csv',
              sep=',', header=True, index=False)


if __name__ == '__main__':
    for seed in seed_list:
        for project in project_list:
            keyId_runtimeList_dict.clear()
            mutant_array.clear()
            key_dict.clear()
            key_array.clear()
            keyId_mutantId_dict.clear()
            for i in range(round_number):
                parse_log(project=project,
                          round=i,
                          seed=seed)
            get_mutant_runtime_csv(seed=seed)
