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


def create_csv_default_vs_mvn_test():
    mvn_test_mapping = {
        'commons-codec': 31.481,
        'commons-collections': 29.142,
        'jfreechart': 8.955
    }
    csv_arr = list()
    cols = ['project', 'replacement_time', 'test_running_time', 'completion_time', 'mvn_test_running_time']
    csv_arr.append(cols)
    for p in mvn_test_mapping.keys():
        replacement_time = 0
        test_running_time = 0
        completion_time = 0
        for r in range(round_number):
            id_others_mapping = json.load(open(f'{parsed_dir}/{p}/default_{r}/id_others_mapping.json', 'r'))
            completion_time_mapping = {tuple(k): int(v) for k, v in json.load(open(f'{parsed_dir}/{p}/completion_time.json', 'r'))}
            for _, others in id_others_mapping.items():
                replacement_time += others[replacement_id]
                test_running_time += others[runtime_id]
            completion_time += completion_time_mapping[('default', r)]
        replacement_time /= 1000 * round_number
        test_running_time /= 1000 * round_number
        completion_time /= round_number
        csv_arr.append([
            p,
            f'{replacement_time:.3f}',
            f'{test_running_time:.3f}',
            f'{completion_time:.3f}',
            f'{mvn_test_mapping[p]:.3f}'
        ])
    with open(f'{main_dir}/vs.mvn_test.csv', 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerows(csv_arr)

if __name__ == '__main__':
    round_number = 6
    main_dir = 'for_checking_OID'
    parsed_dir = f'{main_dir}/parsed_dir'
    create_csv_default_vs_mvn_test()