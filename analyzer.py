import json
import csv
from scipy.stats import ttest_ind, mannwhitneyu
from parse_rough_data import replacement_id, runtime_id

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
    'sling-org-apache-sling-auth-core',
    # 'assertj-assertions-generator',
    # 'commons-net',
    # 'commons-csv',
    # 'delight-nashorn-sandbox',
    # 'httpcore',
    # 'guava',
    # 'java-design-patterns',
    # 'jooby',
    # 'maven-dependency-plugin',
    # 'maven-shade-plugin',
    # 'stream-lib'
]


def create_csv_vs_mvn_test_including_avg():
    mvn_test_mapping = {
        'commons-cli': 6.840,
        'commons-codec': 31.481,
        'commons-collections': 29.142,
        'empire-db': 6.344,
        'jfreechart': 8.955,
        'jimfs': 4.876,
        'JustAuth': 4.642,
        'Mybatis-PageHelper': 6.714,
        'sling-org-apache-sling-auth-core': 6.617
    }
    proj_cnt = len(mvn_test_mapping.keys())
    s_list = [
        'default',
        'single-group',
        'single-group_errors-at-the-end'
    ]
    csv_arr = list()
    cols = [
        'project',
        'mvn_test_running_time',
        'default_complete',
        'single-group_complete',
        'single-group_rate (vs. default)',
        'single-group*_complete',
        'single-group*_rate (vs. default)',
        'default_total',
        'single-group_total',
        'single-group_rate (vs. default)',
        'single-group*_total',
        'single-group*_rate (vs. default)'
    ]
    csv_arr.append(cols)
    # [replacement, running time, completion]
    ps_avg_mapping = dict()
    for p in mvn_test_mapping.keys():
        ps_avg_mapping[(p, 'default')] = [0.0, 0.0, 0.0]
        ps_avg_mapping[(p, 'single-group')] = [0.0, 0.0, 0.0]
        ps_avg_mapping[(p, 'single-group_errors-at-the-end')] = [0.0, 0.0, 0.0]
    # [avg. sg complete rate, avg. sg* complete rate, avg. sg total rate, avg. sg* total rate]
    avg_avg_arr = [0.0, 0.0, 0.0, 0.0]
    for p in mvn_test_mapping.keys():
        completion_time_mapping = {tuple(k): int(v) for k, v in
                                   json.load(open(f'{parsed_dir}/{p}/completion_time.json', 'r'))}
        cur_avg_avg_arr = [0.0, 0.0, 0.0, 0.0]
        for s in s_list:
            for r in range(round_number):
                id_others_mapping = json.load(open(f'{parsed_dir}/{p}/{s}_{r}/id_others_mapping.json', 'r'))
                for _, others in id_others_mapping.items():
                    ps_avg_mapping[(p, s)][0] += others[replacement_id]
                    ps_avg_mapping[(p, s)][1] += others[runtime_id]
                ps_avg_mapping[(p, s)][2] += completion_time_mapping[(s, r)]
        for s in s_list:
            ps_avg_mapping[(p, s)][0] /= round_number * 1000
            ps_avg_mapping[(p, s)][1] /= round_number * 1000
            ps_avg_mapping[(p, s)][2] /= round_number
        def_avg = ps_avg_mapping[(p, s_list[0])][0] + ps_avg_mapping[(p, s_list[0])][1]
        cur_avg_avg_arr[0] = ps_avg_mapping[(p, s_list[1])][2] / ps_avg_mapping[(p, s_list[0])][2]
        cur_avg_avg_arr[1] = ps_avg_mapping[(p, s_list[2])][2] / ps_avg_mapping[(p, s_list[0])][2]
        cur_avg_avg_arr[2] = (ps_avg_mapping[(p, s_list[1])][0] + ps_avg_mapping[(p, s_list[1])][1]) / def_avg
        cur_avg_avg_arr[3] = (ps_avg_mapping[(p, s_list[2])][0] + ps_avg_mapping[(p, s_list[2])][1]) / def_avg
        csv_arr.append([
            p,
            f'{mvn_test_mapping[p]:.2f}',
            f'{ps_avg_mapping[(p, s_list[0])][2]:.2f}',
            f'{ps_avg_mapping[(p, s_list[1])][2]:.2f}',
            f'{cur_avg_avg_arr[0]:.4f}',
            f'{ps_avg_mapping[(p, s_list[2])][2]:.2f}',
            f'{cur_avg_avg_arr[1]:.4f}',
            f'{def_avg:.2f}',
            f'{ps_avg_mapping[(p, s_list[1])][0] + ps_avg_mapping[(p, s_list[1])][1]:.2f}',
            f'{cur_avg_avg_arr[2]:.4f}',
            f'{ps_avg_mapping[(p, s_list[2])][0] + ps_avg_mapping[(p, s_list[2])][1]:.2f}',
            f'{cur_avg_avg_arr[3]:.4f}'
        ])
        for i in range(len(avg_avg_arr)):
            avg_avg_arr[i] += cur_avg_avg_arr[i]
    for i in range(len(avg_avg_arr)):
        avg_avg_arr[i] /= proj_cnt
    csv_arr.append([
        'avg.',
        '',
        '',
        '',
        f'{avg_avg_arr[0]:.4f}',
        '',
        f'{avg_avg_arr[1]:.4f}',
        '',
        '',
        f'{avg_avg_arr[2]:.4f}',
        '',
        f'{avg_avg_arr[3]:.4f}'
    ])
    # [xxx, def]
    micro_avg_matrix = [[0.0, 0.0] for _ in range(4)]
    for p in mvn_test_mapping.keys():
        for i in range(len(s_list)):
            s = s_list[i]
            if i == 0:
                micro_avg_matrix[0][1] += ps_avg_mapping[(p, s)][2]
                micro_avg_matrix[1][1] += ps_avg_mapping[(p, s)][2]
                micro_avg_matrix[2][1] += ps_avg_mapping[(p, s)][0] + ps_avg_mapping[(p, s)][1]
                micro_avg_matrix[3][1] += ps_avg_mapping[(p, s)][0] + ps_avg_mapping[(p, s)][1]
            elif i == 1:
                micro_avg_matrix[0][0] += ps_avg_mapping[(p, s)][2]
                micro_avg_matrix[2][0] += ps_avg_mapping[(p, s)][0] + ps_avg_mapping[(p, s)][1]
            elif i == 2:
                micro_avg_matrix[1][0] += ps_avg_mapping[(p, s)][2]
                micro_avg_matrix[3][0] += ps_avg_mapping[(p, s)][0] + ps_avg_mapping[(p, s)][1]
    csv_arr.append([
        'micro avg.',
        '',
        '',
        '',
        f'{micro_avg_matrix[0][0] / micro_avg_matrix[0][1]:.4f}',
        '',
        f'{micro_avg_matrix[1][0] / micro_avg_matrix[1][1]:.4f}',
        '',
        '',
        f'{micro_avg_matrix[2][0] / micro_avg_matrix[2][1]:.4f}',
        '',
        f'{micro_avg_matrix[3][0] / micro_avg_matrix[3][1]:.4f}'
    ])
    with open(f'{main_dir}/vs.mvn_test.csv', 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerows(csv_arr)

if __name__ == '__main__':
    round_number = 6
    main_dir = 'for_checking_OID'
    parsed_dir = f'{main_dir}/parsed_dir'
    create_csv_vs_mvn_test_including_avg()