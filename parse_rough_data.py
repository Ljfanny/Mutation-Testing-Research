import json
import numpy as np
import pandas as pd
import os
import re
import xml.etree.ElementTree as ET

project_list = [
    # 'assertj-assertions-generator',
    # 'commons-net',
    'commons-cli',
    # 'commons-csv',
    'commons-codec',
    'delight-nashorn-sandbox',
    'empire-db',
    'jimfs',
    # 'httpcore',
    'handlebars.java',
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
    'single-group',
    'single-group_random-42',
    'single-group_random-43',
    'single-group_random-44',
    'single-group_random-45',
    'single-group_random-46'
    # 'sgl_grp',
    # 'def_ln-freq_def',
    # 'def_def_shuf',
    # 'clz_clz-cvg_def',
    # 'clz_ln-cvg_def',
    # 'n-tst_clz-cvg_def',
    # 'n-tst_ln-cvg_def',
    # 'n-tst_clz-sim_def',
    # 'n-tst_clz-diff_def',
    # 'n-tst_clz-ext_def',
    # 'n-tst_ln-ext_def',
    # '01-tst_clz-cvg_def',
    # '01-tst_ln-cvg_def'
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
replace_time_pattern = r"replaced class with mutant in (\d+) ms"
complete_time_pattern = r"Completed in (\d+) seconds"
group_boundary_pattern = r"Run all (\d+) mutants in (\d+) ms"


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

    mutant = {
        'clazz': mutant_details.group(1),
        'method': mutant_details.group(2),
        'methodDesc': mutant_details.group(3),
        'indexes': [int(i.strip()) for i in mutant_details.group(4).split(',')],
        'mutator': mutant_details.group(5)
    }
    mid = -1
    for k, v in id_mutant_mapping.items():
        if mutant == v:
            mid = k
            break

    # Extract test descriptions
    test_descriptions = re.findall(test_description_pattern, block_str)
    for clazz, name, runtime in test_descriptions:
        t = f'{clazz}.{name}'
        if t not in test_id_mapping.keys():
            continue
        tid = test_id_mapping[t]
        for i, tup in enumerate(id_info_mapping[mid]):
            if tid == tup[0]:
                id_info_mapping[mid][i] = (tup[0], tup[1]) + (int(runtime), )
                break

    replace_time = re.search(replace_time_pattern, block_str)
    if replace_time:
        id_replace_time_mapping[mid] = int(replace_time.group(1))
    else:
        id_replace_time_mapping[mid] = 0

    complete_time = re.search(complete_time_pattern, block_str)
    if complete_time:
        complete_time_arr[rnd] = int(complete_time.group(1))


# Parse log
def parse_log(p, s, rnd):
    log_filename = f'{p}_{s}_{rnd}.log'
    log_path = os.path.join(logs_dir, log_filename)
    with open(log_path, 'r') as f:
        block = []
        capturing = False
        for line in f:
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


# Parse xml file
def parse_xml(p, s, rnd):
    xml_filename = f'{p}_{s}_{rnd}.xml'
    xml_path = os.path.join(xmls_dir, xml_filename)

    try:
        tree = ET.parse(xml_path)
    except FileNotFoundError as e:
        raise RuntimeError(f"XML file not found: {xml_path}") from e
    except ET.ParseError as e:
        raise RuntimeError(f"Error parsing XML ({xml_path}): {e}") from e

    root = tree.getroot()
    for mutation in root.findall("mutation"):
        mutant = dict()
        killing_tests = None
        succeeding_tests = None
        for child in mutation:
            tag = child.tag
            text = child.text.strip() if child.text and child.text.strip() else ""
            if tag == 'mutatedClass':
                mutant['clazz'] = text
            elif tag == 'mutatedMethod':
                mutant['method'] = text
            elif tag == 'methodDescription':
                mutant['methodDesc'] = text
            elif tag == 'indexes':
                values = list(
                    int(elem.text.strip()) for elem in child.findall("*")
                    if elem.text and elem.text.strip()
                )
                mutant[tag] = values
            elif tag == 'mutator':
                mutant['mutator'] = text
            elif tag == "killingTests":
                if not text:
                    killing_tests = list()
                else:
                    parts = [part.strip() for part in text.split("|") if part.strip()]
                    killing_tests = tuple(sorted(set(parts)))
            elif tag == "succeedingTests":
                if not text:
                    succeeding_tests = list()
                else:
                    parts = [part.strip() for part in text.split("|") if part.strip()]
                    succeeding_tests = tuple(sorted(set(parts)))

        for k, v in id_mutant_mapping.items():
            if mutant == v:
                id_info_mapping[k] = list()
                temp_mapping = dict()
                for t in killing_tests:
                    if t not in test_id_mapping.keys():
                        continue
                    tid = test_id_mapping[t]
                    if tid in temp_mapping and temp_mapping[tid] != 0:
                        temp_mapping[tid] = -1
                    else:
                        temp_mapping[tid] = 0
                for t in succeeding_tests:
                    if t not in test_id_mapping.keys():
                        continue
                    tid = test_id_mapping[t]
                    if tid in temp_mapping and temp_mapping[tid] != 1:
                        temp_mapping[tid] = -1
                    else:
                        temp_mapping[tid] = 1
                for tid, status in temp_mapping.items():
                    if status == -1:
                        continue
                    id_info_mapping[k].append((tid, FAIL if status == 0 else PASS, 0))
                id_info_mapping[k].sort(key=lambda x: x[0])
                break


def output_jsons(p, s, rnd):
    output_file = f'{outputs_dir}/{p}_{s}_{rnd}.json'
    with open(output_file, 'w') as f:
        json.dump(id_info_mapping, f, indent=4)
    replace_file = f'{outputs_dir}/{p}_{s}_{rnd}_repl.json'
    with open(replace_file, 'w') as f:
        json.dump(id_replace_time_mapping, f, indent=4)


if __name__ == '__main__':
    round_number = 6
    random_mutant = False
    random_test = False
    FAIL = False
    PASS = True
    main_dir = 'for_checking_OID'
    xmls_dir = f'{main_dir}/xmls'
    logs_dir = f'{main_dir}/logs'
    outputs_dir = f'{main_dir}/temp_outputs/after'
    mutant_pattern_dict = {
        'junit4': mutant_pattern_junit4,
        'junit5': mutant_pattern_junit5
    }
    test_description_pattern_dict = {
        'junit4': test_description_pattern_junit4,
        'junit5': test_description_pattern_junit5
    }
    cols = ['seed'] + [f'round{i}' for i in range(round_number)] + ['avg.', '/avg. default']
    for project in project_list:
        with open(f'{main_dir}/temp_outputs/before/{project}_mutant_mapping.json', 'r') as file:
            id_mutant_mapping = {int(k): v for k, v in json.load(file).items()}
        with open(f'{main_dir}/temp_outputs/before/{project}_test_mapping.json', 'r') as file:
            id_test_mapping = {int(k): v for k, v in json.load(file).items()}
        test_id_mapping = {v: k for k, v in id_test_mapping.items()}
        df = pd.DataFrame(None, columns=cols)
        def_avg = 0
        for seed in seed_list:
            print(f'Process {project} with {seed}... ...')
            junit_version = project_junitVersion_dict[project]
            mutant_pattern = mutant_pattern_dict[junit_version]
            test_description_pattern = test_description_pattern_dict[junit_version]
            complete_time_arr = [0 for _ in range(round_number)]
            for r in range(round_number):
                id_info_mapping = dict()
                id_replace_time_mapping = dict()
                parse_xml(p=project, s=seed, rnd=r)
                parse_log(p=project, s=seed, rnd=r)
                # output_jsons(p=project, s=seed, rnd=r)
            if seed == 'default':
                def_avg = np.mean(complete_time_arr)
                df.loc[len(df.index)] = [seed] + complete_time_arr + [f'{def_avg:.2f}', f'{1.0:.2f}']
            else:
                cur_avg = np.mean(complete_time_arr)
                df.loc[len(df.index)] = [seed] + complete_time_arr + [f'{cur_avg:.2f}', f'{cur_avg / def_avg:.2f}']
        df.to_csv(f'for_checking_OID/complete_runtime/{project}.csv', sep=',', header=True, index=False)
