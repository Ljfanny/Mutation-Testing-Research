import json
import sys
import copy
import os


def get_pairs():
    value_tests_map = dict()
    conflict_pairs = list()
    with open(test_value_pairs_path, 'r') as ff:
        for line in ff:
            line = line.strip()
            if not line:
                continue
            parts = line.split(',')
            test = parts[0].strip()
            value = parts[1].strip()
            if value in value_tests_map:
                value_tests_map[value].append(test)
            else:
                value_tests_map[value] = [test]
    for v in value_tests_map.keys():
        value_tests_map[v] = list(set(value_tests_map[v]))
    for v, tests in value_tests_map.items():
        if len(tests) <= 1:
            continue
        for ii in range(len(tests)):
            for jj in range(ii + 1, len(tests)):
                if (tests[ii], tests[jj]) in conflict_pairs or (tests[jj], tests[ii]) in conflict_pairs:
                    continue
                conflict_pairs.append((tests[ii], tests[jj]))
    return conflict_pairs


def handle_conflict(pair):
    t1 = pair[0]
    t2 = pair[1]
    new_bucket = list()
    new_test_set = list()
    for ii in range(cur_bucket_cnt):
        if t1 in test_set_list[ii] and t2 in test_set_list[ii]:
            test_set_list[ii].remove(t2)
            bucket = copy.deepcopy(bucket_list[ii])
            bucket_list[ii].clear()
            for pp in bucket:
                if pp['testsInOrder'][0]['name'].split('(')[0] != t2:
                    bucket_list[ii].append(pp)
                else:
                    if ii + 1 < cur_bucket_cnt:
                        bucket_list[ii + 1].append(pp)
                        test_set_list[ii + 1].append(t2)
                    else:
                        new_bucket.append(pp)
                        new_test_set.append(t2)

    if len(new_bucket) != 0:
        bucket_list.append(new_bucket)
        test_set_list.append(new_test_set)


def refresh():
    group_list = list()
    for ii in range(cur_bucket_cnt):
        group = list()
        native_pairs = list()
        remaining_pairs = list()
        for pair in bucket_list[ii]:
            if pair['groupId'] == ii:
                native_pairs.append(pair)
            else:
                remaining_pairs.append(pair)
        native_pairs = sorted(native_pairs, key=lambda x: (x['groupId'], x['clazzId'], x['executionSeq']))
        cur_mutant = None
        for pair in native_pairs:
            if cur_mutant and cur_mutant['id'] == pair['id']:
                cur_mutant['testsInOrder'] += pair['testsInOrder']
            else:
                if cur_mutant:
                    group.append(cur_mutant)
                cur_mutant = pair
        remaining_pairs = sorted(remaining_pairs, key=lambda x: (x['groupId'], x['clazzId'], x['executionSeq']))
        for pair in remaining_pairs:
            if cur_mutant and cur_mutant['id'] == pair['id']:
                cur_mutant['testsInOrder'] += pair['testsInOrder']
            else:
                if cur_mutant:
                    group.append(cur_mutant)
                cur_mutant = pair
        cur_clazz = ''
        cur_clazz_id = -1
        cur_seq = 0
        for mut in group:
            mut['groupId'] = 0
            if cur_clazz != m['id']['location']['clazz']:
                cur_clazz = m['id']['location']['clazz']
                cur_clazz_id += 1
                cur_seq = 0
            mut['clazzId'] = cur_clazz_id
            mut['executionSeq'] = cur_seq
            cur_seq += 1
        group_list.append(group)
    return group_list


if __name__ == '__main__':
    test_value_pairs_path = sys.argv[1]
    guiding_file_name = sys.argv[2]

    pairs = get_pairs()
    with open(f'controlled_analyzed_data/both/guiding_files/{guiding_file_name}', 'r') as f:
        mutants = json.load(f)

    cur_bucket_cnt = 0
    for m in mutants:
        if cur_bucket_cnt < m['groupId']:
            cur_bucket_cnt = m['groupId']
    cur_bucket_cnt += 1
    bucket_list = [list() for _ in range(cur_bucket_cnt)]
    test_set_list = [list() for _ in range(cur_bucket_cnt)]
    for m in mutants:
        bucket_id = m['groupId']
        for t in m['testsInOrder']:
            cur = {
                'id': m['id'],
                'testsInOrder': [t],
                'groupId': bucket_id,
                'clazzId': m['clazzId'],
                'executionSeq': m['executionSeq']
            }
            bucket_list[bucket_id].append(cur)
            test_set_list[bucket_id].append(t['name'].split('(')[0])
    for i in range(cur_bucket_cnt):
        test_set_list[i] = list(set(test_set_list[i]))

    for p in pairs:
        handle_conflict(p)
        cur_bucket_cnt = len(bucket_list)
        for i in range(cur_bucket_cnt):
            test_set_list[i] = list(set(test_set_list[i]))

    output = refresh()
    with open(f'fixing_conflicts/{guiding_file_name}', 'w') as f:
        f.write(json.dumps(output, indent=4))
