import json
import csv
import numpy as np
import pandas as pd
import os
import re
import xml.etree.ElementTree as ET
from scipy.stats import ttest_ind, mannwhitneyu

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
    'single-group_errors-at-the-end',
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
project_junit_mapping = {
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
test_description_pattern = ''

# Regex patterns
mutant_pattern = r"\[clazz=([^,]+), method=([^,]+), methodDesc=([^]]+)\], indexes=\[([^]]+)\], mutator=([^,]+)\]"
test_description_pattern_junit4 = r"testClass=([^,]+), name=([^\]]+).*Running time: (\d+) ms"
test_description_pattern_junit5 = r"testClass=([^,]+), name=(.*)\].*Running time: (\d+) ms"
runtime_pattern = r"run all related tests in (\d+) ms"
replace_time_pattern = r"replaced class with mutant in (\d+) ms"
complete_time_pattern = r"Completed in (\d+) seconds"
group_boundary_pattern = r"Run all (\d+) mutants in (\d+) ms"

KILLED = 'KILLED'
SURVIVED = 'SURVIVED'
TIMED_OUT = 'TIMED_OUT'
RUN_ERROR = 'RUN_ERROR'

def process_block(blk: list, rnd: int, csv_arr: list):
    global total_mutant_count, total_replacement_time, total_runtime, total_error_count
    block_str = ''.join(blk)
    mutant_details = re.search(mutant_pattern, block_str)
    if not mutant_details:
        return
    mutant = {
        'clazz': mutant_details.group(1),
        'method': mutant_details.group(2),
        'methodDesc': mutant_details.group(3),
        'indexes': [int(i.strip()) for i in mutant_details.group(4).split(',')],
        'mutator': mutant_details.group(5)
    }
    mid = 0
    for k, v in id_mutant_mapping.items():
        if mutant == v:
            mid = k
            break

    cur_clazz = mutant['clazz']
    if cur_clazz not in clazz_info_mapping.keys():
        # [replacement time, running time, error count, mutant count]
        clazz_info_mapping[cur_clazz] = [0, 0, 0, 0]

    status = id_status_mapping[mid]
    # [class name, mutant id, replacement time, running time, error description (error count), (mutant count)]
    arr = [None, None, None, None, None, None]
    arr[0] = cur_clazz
    arr[1] = mid
    replace_time = re.search(replace_time_pattern, block_str)
    if replace_time:
        id_replace_time_mapping[mid] = int(replace_time.group(1))
        arr[2] = id_replace_time_mapping[mid]
        clazz_info_mapping[cur_clazz][0] += arr[2]
        total_replacement_time += arr[2]

    # Extract test descriptions
    if status in [KILLED, SURVIVED]:
        test_descriptions = re.findall(test_description_pattern, block_str)
        for clz, name, runtime in test_descriptions:
            t = f'{clz}.{name}'
            if t not in test_id_mapping.keys():
                continue
            tid = test_id_mapping[t]
            for i, tup in enumerate(id_info_mapping[mid]):
                if tid == tup[0]:
                    id_info_mapping[mid][i] = (tup[0], tup[1]) + (int(runtime), )
                    break

    mutant_runtime = re.search(runtime_pattern, block_str)
    if mutant_runtime:
        arr[3] = int(mutant_runtime.group(1))
    else:
        pattern = re.compile(r'Test Description.*?(\d+)\s*ms', re.DOTALL)
        ms_arr = pattern.findall(block_str)
        arr[3] = 0
        for ms in ms_arr:
            arr[3] += int(ms)
        arr[4] = status
        total_error_count += 1
        clazz_info_mapping[cur_clazz][2] += 1

    clazz_info_mapping[cur_clazz][3] += 1
    total_mutant_count += 1
    clazz_info_mapping[cur_clazz][1] += arr[3]
    total_runtime += arr[3]
    csv_arr.append(arr)
    group_runtime = re.search(group_boundary_pattern, block_str)
    if group_runtime:
        csv_arr.append(['Group Runtime', None, int(group_runtime.group(2)), None, None, int(group_runtime.group(1))])

    complete_time = re.search(complete_time_pattern, block_str)
    if complete_time:
        complete_time_arr[rnd] = int(complete_time.group(1))
        csv_arr.append(['Total Runtime', None, total_replacement_time, total_runtime, total_error_count, total_mutant_count])
        csv_arr.append(['Complete Runtime', None, complete_time_arr[rnd], None, None, None])


# Parse log
def parse_log(p, s, rnd):
    log_filename = f'{p}_{s}_{rnd}.log'
    csv_arr = list()
    log_path = os.path.join(logs_dir, log_filename)
    with open(log_path, 'r') as f:
        blocks = []
        capturing = False
        for line in f:
            if 'start running' in line:
                if capturing:
                    process_block(blocks, rnd, csv_arr)
                    capturing = False
                if not capturing:
                    capturing = True
                    blocks = [line]
            elif capturing:
                blocks.append(line)
        process_block(blocks, rnd, csv_arr)
    # with open(f'{main_dir}/runtime_analysis_dir/{p}_{s}_{rnd}.csv', 'w', newline='', encoding='utf-8') as f:
    #     w = csv.writer(f)
    #     w.writerows(csv_arr)


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
        status = mutation.get('status')
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

        mid = 0
        for k, v in id_mutant_mapping.items():
            if mutant == v:
                mid = k
                break
        if status not in [KILLED, SURVIVED]:
            error_set.add(mid)
        id_status_mapping[mid] = status
        id_info_mapping[mid] = list()
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
        for tid, mark in temp_mapping.items():
            if mark == -1:
                continue
            id_info_mapping[mid].append((tid, FAIL if mark == 0 else PASS, 0))
        id_info_mapping[mid].sort(key=lambda x: x[0])


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
    test_description_pattern_mapping = {
        'junit4': test_description_pattern_junit4,
        'junit5': test_description_pattern_junit5
    }
    cols = ['seed'] + [f'round{i}' for i in range(round_number)] + ['avg.', '/avg. default', 'T-test', 'U-test']
    for project in project_list:
        with open(f'{main_dir}/temp_outputs/before/{project}_mutant_mapping.json', 'r') as file:
            id_mutant_mapping = {int(k): v for k, v in json.load(file).items()}
        mutant_id_mapping = {str(v): k for k, v in id_mutant_mapping.items()}
        with open(f'{main_dir}/temp_outputs/before/{project}_test_mapping.json', 'r') as file:
            id_test_mapping = {int(k): v for k, v in json.load(file).items()}
        test_id_mapping = {v: k for k, v in id_test_mapping.items()}
        seed_runtime_mapping = dict()
        df = pd.DataFrame(None, columns=cols)
        def_avg = 1.0
        def_arr = list()
        error_set = set()
        for seed in seed_list:
            print(f'Process {project} with {seed}... ...')
            junit_version = project_junit_mapping[project]
            test_description_pattern = test_description_pattern_mapping[junit_version]
            complete_time_arr = [0 for _ in range(round_number)]
            seed_runtime_mapping[seed] = [0 for _ in range(round_number)]
            clazz_percentages_mapping = dict()
            for r in range(round_number):
                # [test id, status, running time]
                id_info_mapping = dict()
                id_replace_time_mapping = dict()
                id_status_mapping = dict()
                clazz_info_mapping = dict()
                total_error_count = 0
                total_mutant_count = 0
                total_replacement_time = 0
                total_runtime = 0
                parse_xml(p=project, s=seed, rnd=r)
                parse_log(p=project, s=seed, rnd=r)
                # output_jsons(p=project, s=seed, rnd=r)
                seed_runtime_mapping[seed][r] = total_replacement_time + total_runtime

                with open(f'{main_dir}/runtime_analysis_dir/per_class/{project}_{seed}_{r}.csv', 'w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerows([[k] + v for k, v in dict(sorted(clazz_info_mapping.items(), key=lambda kv: kv[0])).items()])
                # if seed == 'default':
                #     for clazz, info_arr in clazz_info_mapping.items():
                #         if clazz not in clazz_percentages_mapping.keys():
                #             clazz_percentages_mapping[clazz] = [0 for _ in range(round_number)]
                #         clazz_percentages_mapping[clazz][r] = (info_arr[0] + info_arr[1]) / (1000 * complete_time_arr[r])

            # if seed == 'default':
            #     # complete time
            #     def_arr = complete_time_arr
            #     def_avg = np.mean(complete_time_arr)
            #     df.loc[len(df.index)] = [seed] + complete_time_arr + [f'{def_avg:.2f}', f'{1.0:.2f}', f'{1.0:.4f}', f'{1.0:.4f}']
            #
            #     # for percentage
            #     percentages_arr = list()
            #     for clazz, percentages in clazz_percentages_mapping.items():
            #         percentages_arr.append([clazz] + percentages + [np.mean(percentages)])
            #     percentages_arr.sort(key=lambda x: x[-1], reverse=True)
            #     percentages_arr.insert(0, ['clazz', 'round0', 'round1', 'round2', 'round3', 'round4', 'round5', 'avg.'])
            #     for i in range(1, len(percentages_arr)):
            #         percentages_arr[i] = [percentages_arr[i][0]] + [f'{x:.4f}' for x in percentages_arr[i][1:]]
            #     with open(f'{main_dir}/runtime_analysis_dir/per_class/{project}_{seed}.csv', 'w', newline='', encoding='utf-8') as file:
            #         writer = csv.writer(file)
            #         writer.writerows(percentages_arr)
            # else:
            #     cur_avg = np.mean(complete_time_arr)
            #     _, t_p_value = ttest_ind(def_arr, complete_time_arr)
            #     _, u_p_value = mannwhitneyu(def_arr, complete_time_arr)
            #     df.loc[len(df.index)] = [seed] + complete_time_arr + [f'{cur_avg:.2f}', f'{cur_avg / def_avg:.2f}', f'{t_p_value:.4f}', f'{u_p_value:.4f}']

        # with open(f'{main_dir}/mutant_list/erroneous/{project}.json', 'w') as f:
        #     f.write(json.dumps(sorted(list(error_set)), indent=4))

        for seed in seed_list:
            cur_avg = np.mean(seed_runtime_mapping[seed])
            seed_runtime_mapping[seed].append(f'{cur_avg:.2f}')
            if seed == 'default':
                def_avg = cur_avg
                seed_runtime_mapping[seed].append(f'{1.0:.2f}')
                seed_runtime_mapping[seed].append(f'{1.0:.4f}')
                seed_runtime_mapping[seed].append(f'{1.0:.4f}')
            else:
                _, t_p_value = ttest_ind(seed_runtime_mapping['default'][:6], seed_runtime_mapping[seed][:6])
                _, u_p_value = mannwhitneyu(seed_runtime_mapping['default'][:6], seed_runtime_mapping[seed][:6])
                seed_runtime_mapping[seed].append(f'{cur_avg / def_avg:.2f}')
                seed_runtime_mapping[seed].append(f'{t_p_value:.4f}')
                seed_runtime_mapping[seed].append(f'{u_p_value:.4f}')
        with open(f'{main_dir}/runtime_analysis_dir/total_runtime/{project}.csv', 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerows([cols] + [[k] + v for k, v in seed_runtime_mapping.items()])

        # df.to_csv(f'{main_dir}/runtime_analysis_dir/complete_runtime/{project}.csv', sep=',', header=True, index=False)