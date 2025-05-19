import json
import re
import os
import numpy as np

project_list = [
    # 'assertj-assertions-generator',
    # 'commons-net',
    # 'commons-cli',
    # 'commons-csv',
    'commons-codec',
    # 'delight-nashorn-sandbox',
    # 'empire-db',
    # 'jimfs',
    # 'httpcore',
    # 'handlebars.java',
    'riptide',
    # 'commons-collections',
    # 'guava',
    # 'java-design-patterns',
    # 'jooby',
    # 'maven-dependency-plugin',
    # 'maven-shade-plugin',
    # 'sling-org-apache-sling-auth-core',
    # 'stream-lib'
]
seed_list = [
    'default',
    'sgl_grp',
    'def_ln-freq_def',
    'def_def_shuf',
    'clz_clz-cvg_def',
    'clz_ln-cvg_def',
    'n-tst_clz-cvg_def',
    'n-tst_ln-cvg_def',
    'n-tst_clz-sim_def',
    'n-tst_clz-diff_def',
    'n-tst_clz-ext_def',
    'n-tst_ln-ext_def',
    '01-tst_clz-cvg_def',
    '01-tst_ln-cvg_def'
]
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
    'delight-nashorn-sandbox': 'junit4',
    'jimfs': 'junit4',
    'commons-cli': 'junit5',
    'assertj-assertions-generator': 'junit5',
    'commons-collections': 'junit5',
    'commons-csv': 'junit5',
    'commons-net': 'junit5',
    'empire-db': 'junit4',
    'guava': 'junit4',
    'handlebars.java': 'junit5',
    'httpcore': 'junit5',
    'java-design-patterns': 'junit5',
    'jooby': 'junit5',
    'maven-dependency-plugin': 'junit5',
    'maven-shade-plugin': 'junit4',
    'riptide': 'junit5',
    'sling-org-apache-sling-auth-core': 'junit4',
    'stream-lib': 'junit4'
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
                        r"description=([^,]+), testsInOrder=\[(.*)\]\]"
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

    def to_tuple(self):
        return (self.location.clazz,
                self.location.method,
                self.location.methodDesc,
                self.indexes,
                self.mutator)


def process_block(blk: list, rnd: int):
    block_str = ''.join(blk)
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
    mutant_id = MutantIdentifier(
        Location(
            mutant_details.group(1),
            mutant_details.group(2),
            mutant_details.group(3)
        ),
        mutant_details.group(4),
        mutant_details.group(5)
    )
    for test in test_list:
        if test in test_testId_dict:
            continue
        test_testId_dict[len(test_testId_dict)] = test

    complete_mutant = mutant_id.to_tuple() + (tuple(test_list),)
    if complete_mutant in mutant_array:
        mutant_cnt = mutant_dict[complete_mutant]
    else:
        mutant_cnt = len(mutant_array)
        mutant_array.append(complete_mutant)
        mutant_dict[complete_mutant] = mutant_cnt
        mutantId_mutantTuple_dict[mutant_cnt] = mutant_id.to_tuple()
        mutantId_testsInOrders_dict[mutant_cnt] = test_list
        mutantId_runtimeList_dict[mutant_cnt] = [np.nan for _ in range(round_number)]
        mutantId_testRuntimeMatrix_dict[mutant_cnt] = [None for _ in range(round_number)]

    # Extract test descriptions
    test_descriptions = re.findall(test_description_pattern, block_str)
    test_runtime_list = []
    for clazz, name, runtime in test_descriptions:
        test_runtime_list.append(int(runtime))
    while len( test_runtime_list) < len(test_list):
         test_runtime_list.append(np.nan)
    mutantId_testRuntimeMatrix_dict[mutant_cnt][rnd] =  test_runtime_list

    # Extract test runtime
    runtime = re.search(runtime_pattern, block_str)
    if runtime:
        mutantId_runtimeList_dict[mutant_cnt][rnd] = int(runtime.group(1))
    else:
        mutantId_runtimeList_dict[mutant_cnt][rnd] = np.nan


# Parse log information
def parse_log(p, rnd, s):
    # with open(f'{logs_dir}/{s}/{p}_{rnd}.log', 'r') as file:
    with open(f'{logs_dir}/{p}_{s}_{rnd}.log', 'r') as file:
        block = []
        capturing = False
        for line in file:
            if "start running" in line:
                if capturing:
                    process_block(block, rnd)
                    capturing = False
                if not capturing:
                    capturing = True
                    block = [line]
            elif capturing:
                block.append(line)
        process_block(block, rnd)


def output_jsons(p, s):
    output_path = f'{parsed_dir}/{p}_{s}'
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
    round_number = 6
    random_mutant = False
    random_test = False
    logs_dir = 'for_checking_OID/logs'
    parsed_dir = 'controlled_parsed_data/both'
    mutant_pattern_dict = {
        'junit4': mutant_pattern_junit4,
        'junit5': mutant_pattern_junit5
    }
    test_description_pattern_dict = {
        'junit4': test_description_pattern_junit4,
        'junit5': test_description_pattern_junit5
    }
    seed_list = ['shuffled']
    for project in project_list:
        for seed in seed_list:
            print(f'Process {project} with {seed}... ...')
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
                parse_log(p=project,
                          rnd=r,
                          s=seed)
            output_jsons(p=project, s=seed)
