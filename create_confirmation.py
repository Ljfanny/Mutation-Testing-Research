import json
import copy
import pandas as pd
import subprocess
import xml.etree.ElementTree as ET

DIR = 'controlled_analyzed_data/both/confirm_files'
SURVIVED = 'SURVIVED'
KILLED = 'KILLED'
EMPTY = 'EMPTY'
FLAKY = 'FLAKY'


def refresh_id(arr):
    grp_id = 0
    clz_id = -1
    exec_seq = 0
    cur_clz = None
    for i in range(len(arr)):
        arr[i]['groupId'] = grp_id
        clz = arr[i]['id']['location']['clazz']
        if clz != cur_clz:
            clz_id += 1
            exec_seq = 0
            cur_clz = clz
        arr[i]['clazzId'] = clz_id
        arr[i]['executionSeq'] = exec_seq
        exec_seq += 1


def binary_search_iterative(arr, target, lo, hi):
    mid = (lo + hi) // 2
    print(lo, mid - 1)
    print(mid, hi - 1)
    with open(f'{DIR}/{subdir}_{lo}-{mid - 1}.json', 'w') as ff:
        cur_arr = arr[lo:mid]
        cur_arr.append(target)
        refresh_id(cur_arr)
        ff.write(json.dumps(cur_arr, indent=4))
    with open(f'{DIR}/{subdir}_{mid}-{hi - 1}.json', 'w') as ff:
        cur_arr = arr[mid:hi]
        cur_arr.append(target)
        refresh_id(cur_arr)
        ff.write(json.dumps(cur_arr, indent=4))

    if mid - lo > 1:
        binary_search_iterative(arr, target, lo, mid)
    if hi - mid > 1:
        binary_search_iterative(arr, target, mid, hi)


# def binary_search_iterative(m, target, lo, hi):
#     if hi - lo <= 1:
#         return
#     mid = (lo + hi) // 2
#     print(lo, mid - 1)
#     print(mid, hi - 1)
#     with open(f'{DIR}/{target_file_name}_{lo}-{mid - 1}.json', 'w') as ff:
#         m['testsInOrder'] = target_tests[lo:mid]
#         output_list = [m, flaky_mutant]
#         ff.write(json.dumps(output_list, indent=4))
#     with open(f'{DIR}/{target_file_name}_{mid}-{hi - 1}.json', 'w') as ff:
#         m['testsInOrder'] = target_tests[mid:hi]
#         output_list = [m, flaky_mutant]
#         ff.write(json.dumps(output_list, indent=4))
#     binary_search_iterative(m, target, lo, mid)
#     binary_search_iterative(m, target, mid, hi)


# def binary_search_iterative(target, lo, hi):
#     def write(left, right):
#         with open(f'{DIR}/{target_file_name}_{left}-{right - 1}.json', 'w') as ff:
#             m = copy.deepcopy(target)
#             m['testsInOrder'] = m['testsInOrder'][lo:mid]
#             m['testsInOrder'].append({
#                 'definingClass': definingClass,
#                 'name': name
#             })
#             ff.write(json.dumps([m], indent=4))
#
#     if hi - lo <= 1:
#         return
#     mid = (lo + hi) // 2
#     print(lo, mid - 1)
#     print(mid, hi - 1)
#     write(lo, mid)
#     write(mid, hi)
#     binary_search_iterative(target, lo, mid)
#     binary_search_iterative(target, mid, hi)


# def comp(m):
#     if m.find('mutatedClass').text != clazz:
#         return False
#     if m.find('mutatedMethod').text != method:
#         return False
#     if m.find('methodDescription').text != methodDesc:
#         return False
#     if m.find('mutator').text != mutator:
#         return False
#     if [i.text for i in m.find('indexes')] != indexes[1:-1].split(', '):
#         return False
#     return True


# def parse_xml(substr):
#     xml_path = f'{DIR}/{proj}_{substr}/target/pit-reports/mutations.xml'
#     tree = ET.parse(xml_path)
#     root = tree.getroot()
#     mutations = root.findall('mutation')
#     for mutation in mutations:
#         if comp(mutation):
#             killingTests = mutation.find('killingTests').text
#             succeedingTests = mutation.find('succeedingTests').text
#             if killingTests and name in killingTests:
#                 return KILLED
#             elif succeedingTests and name in succeedingTests:
#                 return SURVIVED
#             else:
#                 return EMPTY


if __name__ == '__main__':
    # proj = 'handlebars.java'
    # strategy = 'clz_clz-cvg_def'
    # clazz = 'com.github.jknack.handlebars.internal.Partial'
    # method = '<init>'
    # methodDesc = '(Lcom/github/jknack/handlebars/Handlebars;Lcom/github/jknack/handlebars/Template;Ljava/lang/String;Ljava/util/Map;)V'
    # indexes = '[25]'
    # mutator = 'org.pitest.mutationtest.engine.gregor.mutators.NegateConditionalsMutator'
    #
    # cnt = 0
    # subdir = f'{proj}_ln-{cnt}'
    # DIR += '/' + subdir
    # definingClass = 'mustache.specs.SpecTests'
    # name = 'mustache.specs.SpecTests.[engine:junit-platform-suite]/[suite:mustache.specs.SpecTests]/[engine:junit-jupiter]/[class:mustache.specs.PartialsTest]/[test-template:partials(mustache.specs.Spec)]/[test-template-invocation:#1]'

    # with open(f'controlled_analyzed_data/both/guiding_files/{proj}_{strategy}.json', 'r') as f:
    #     guiding_list = json.load(f)
    #
    # groupId = 13
    # clazzId = 9
    # executionSeq = 0
    # before_list = list()
    # cur_mutant = None
    # for mutant in guiding_list:
    #     isOK = True
    #     if mutant['groupId'] != groupId:
    #         isOK = False
    #     if mutant['clazzId'] > clazzId:
    #         isOK = False
    #     if mutant['clazzId'] == clazzId and mutant['executionSeq'] > executionSeq:
    #         isOK = False
    #     if isOK and mutant['clazzId'] == clazzId and mutant['executionSeq'] == executionSeq:
    #         cur_mutant = copy.deepcopy(mutant)
    #         flaky_index = mutant['testsInOrder'].index({'definingClass': definingClass, 'name': name})
    #         cur_mutant['testsInOrder'] = cur_mutant['testsInOrder'][:flaky_index + 1]
    #     elif isOK:
    #         before_list.append(mutant)
    # before_list.sort(key=lambda x: (x['clazzId'], x['executionSeq']))
    # binary_search_iterative(before_list, cur_mutant, 0, len(before_list))

    # lo = 0
    # hi = 112
    # while lo < hi:
    #     mid = (lo + hi) // 2
    #     subprocess.run(['bash', 'run_controlled_tests.sh', f'{lo}', f'{mid - 1}'], capture_output=True, text=True)
    #     if parse_xml(f'ln-1_{lo}-{mid - 1}') == SURVIVED:
    #         subprocess.run(['bash', 'run_controlled_tests.sh', f'{mid}', f'{hi - 1}'], capture_output=True, text=True)
    #         if parse_xml(f'ln-1_{mid}-{hi - 1}') == SURVIVED:
    #             print(f'{proj}_ln-1_{mid}-{hi - 1}: {SURVIVED}')
    #             break
    #         else:
    #             lo = mid
    #     else:
    #         hi = mid

    # target_file_name = f'{proj}_ln-1_0-0'
    # with open(F'{DIR}/{target_file_name}.json', 'r') as f:
    #     target_list = json.load(f)
    #
    # target_mutant = target_list[0]
    # target_tests = target_mutant['testsInOrder']
    # flaky_mutant = target_list[1]
    # binary_search_iterative(copy.deepcopy(target_mutant), flaky_mutant, 0, len(target_tests))

    # temp = copy.deepcopy(flaky_mutant)
    # temp['clazzId'] = 0
    # temp['executionSeq'] = 0
    # temp['testsInOrder'] = temp['testsInOrder'][:-2]
    # binary_search_iterative(temp, 0, len(temp['testsInOrder']))
    strategy_list = [
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
    single_df = pd.read_csv('single.csv')
    output = list()
    for _, row in single_df.iterrows():
        project = row['project']
        clazz = row['clazz']
        method = row['method']
        methodDesc = row['methodDesc']
        indexes = row['indexes']
        mutator = row['mutator']
        test = row['test']
        status_list = [row[f'r{i}'] for i in range(10)]

        pair_df = pd.read_csv(f'controlled_analyzed_data/both/status_info/of_pairs/{project}.csv')

        if len(set(status_list)) <= 1:
            single_status = status_list[0]
        else:
            single_status = FLAKY

        if single_status == EMPTY or single_status == FLAKY:
            continue

        for _, pair in pair_df.iterrows():
            if pair['clazz'] == clazz and pair['method'] == method and pair['methodDesc'] == methodDesc and pair['indexes'] == indexes and pair['mutator'] == mutator and pair['test'] == test:
                for strategy in strategy_list:
                    if pair[f'{strategy}'] != EMPTY and pair[f'{strategy}'] != FLAKY and pair[f'{strategy}'] != single_status:
                        output.append([project, clazz, method, methodDesc, indexes, mutator, test, strategy, single_status, pair[f'{strategy}']])
                        break
    with open('INPUT.json', 'w') as f:
        f.write(json.dumps(output, indent=4))
