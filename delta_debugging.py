import json
import copy
import os
import subprocess
import xml.etree.ElementTree as ET

iterations = 0
project_module_dict = {
    'delight-nashorn-sandbox': '.',
    'jimfs': '.',
    'empire-db': 'empire-db',
    'handlebars.java': 'handlebars'
}
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


def comp(m):
    if m.find('mutatedClass').text != clazz:
        return False
    if m.find('mutatedMethod').text != method:
        return False
    if m.find('methodDescription').text != methodDesc:
        return False
    if m.find('mutator').text != mutator:
        return False
    if [i.text for i in m.find('indexes')] != indexes[1:-1].split(', '):
        return False
    return True


def create_file(elements: list, postfix: int):
    target_path = 'pitest-random/pitest/src/main/resources'
    file_name = f'{project}-{identifier}_{iterations}-{postfix}'
    with open(f'{target_path}/{file_name}.json', 'w') as ff:
        arr = elements + [cur_mutant]
        refresh_id(arr)
        ff.write(json.dumps(arr, indent=4))
    return file_name


def check_valid(elements: list, postfix: int):
    file_name = create_file(elements, postfix)
    module = project_module_dict[project]
    subprocess.run(['bash', 'local_runner.sh', project, f'{file_name}.json', module], capture_output=True, text=True)
    if module == '.':
        xml_path = f'{project}/target/pit-reports/mutations.xml'
    else:
        xml_path = f'{project}/{module}/target/pit-reports/mutations.xml'

    if not os.path.exists(xml_path):
        return EMPTY
    tree = ET.parse(xml_path)
    root = tree.getroot()
    mutations = root.findall('mutation')
    for mutation in mutations:
        if comp(mutation):
            killingTests = mutation.find('killingTests').text
            succeedingTests = mutation.find('succeedingTests').text
            if killingTests and test in killingTests:
                return KILLED
            elif succeedingTests and test in succeedingTests:
                return SURVIVED
            else:
                return EMPTY


def delta_debug(elements: list, n: int):
    global iterations
    iterations += 1
    if len(elements) < n:
        return elements

    chunk_size = round(len(elements) / n)
    chunk_size = max(1, chunk_size)
    for i in range(0, len(elements), chunk_size):
        mini = min(len(elements), i + chunk_size)
        chunk = elements[i: mini]
        other_chunk = elements[:i] + elements[mini:]

        value0 = check_valid(other_chunk, 0)
        print(f'Round {iterations}: [:{i}], [{mini}:] {value0}')
        if value0 == flaky_status:
            return delta_debug(other_chunk, 2)

        value1 = check_valid(chunk, 1)
        print(f'Round {iterations}: [{i}:{mini}] {value1}')
        if value1 == flaky_status:
            return delta_debug(chunk, 2)

    if len(elements) == n:
        return elements

    if len(elements) < n * 2:
        return delta_debug(elements, len(elements))
    else:
        return delta_debug(elements, n * 2)


if __name__ == '__main__':
    with open('guiding_files/INPUT.json', 'r') as f:
        flaky_pair_list = json.load(f)

    for identifier, flaky_pair in enumerate(flaky_pair_list):
        project = flaky_pair[0]
        clazz = flaky_pair[1]
        method = flaky_pair[2]
        methodDesc = flaky_pair[3]
        indexes = flaky_pair[4]
        mutator = flaky_pair[5]
        test = flaky_pair[6]
        strategy = flaky_pair[7]
        status = flaky_pair[8]
        flaky_status = flaky_pair[9]

        with open(f'guiding_files/{project}_{strategy}.json', 'r') as f:
            mutant_list = json.load(f)

        # Search IDs
        group_id = -1
        clazz_id = -1
        execution_seq = -1
        cur_mutant = None
        for mutant in mutant_list:
            isOK = True
            if mutant['id']['location']['clazz'] != clazz:
                isOK = False
            if mutant['id']['location']['method'] != method:
                isOK = False
            if mutant['id']['location']['methodDesc'] != methodDesc:
                isOK = False
            if mutant['id']['indexes'] != indexes:
                isOK = False
            if mutant['id']['mutator'] != mutator:
                isOK = False
            if isOK:
                group_id = mutant['groupId']
                clazz_id = mutant['clazzId']
                execution_seq = mutant['executionSeq']
                cur_mutant = copy.deepcopy(mutant)
                cur_mutant['testsInOrder'] = list()
                for t in mutant['testsInOrder']:
                    cur_mutant['testsInOrder'].append(t)
                    if t['name'] == test:
                        break
                break

        before_list = list()
        for mutant in mutant_list:
            isOK = True
            if mutant['groupId'] != group_id:
                isOK = False
            if mutant['clazzId'] > clazz_id:
                isOK = False
            if mutant['clazzId'] == clazz_id and mutant['executionSeq'] > execution_seq:
                isOK = False
            if isOK:
                before_list.append(mutant)
        before_list.sort(key=lambda x: (x['clazzId'], x['executionSeq']))
        delta_debug(before_list, 2)
