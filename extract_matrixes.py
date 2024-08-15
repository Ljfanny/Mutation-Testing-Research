import os
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup

windows_path = 'E:/Research Topics/Mutation_Testing'
proj = 'commons-lang'
pit_report_path = f'{windows_path}/{proj}/target/pit-reports'
pit_matrix_path = f'{windows_path}/{proj}/pit-matrixes'

if __name__ == '__main__':
    directories = [name for name in os.listdir(pit_report_path)
                   if os.path.isdir(os.path.join(pit_report_path, name))]
    for director in directories:
        dir_path = f'{pit_matrix_path}/{director}'
        if not os.path.isdir(dir_path):
            os.mkdir(dir_path)
        class_htmls = [name for name in os.listdir(f'{pit_report_path}/{director}')
                       if name.endswith('.java.html')]
        for html in class_htmls:
            classname = html.split('.')[0]
            if os.path.isfile(f'{pit_matrix_path}/{director}/{classname}.csv'):
                continue
            with open(f'{pit_report_path}/{director}/{html}', 'r') as f:
                html_content = f.read()
            soup = BeautifulSoup(html_content, 'html.parser')
            mutations_h2 = soup.find('h2', string='Mutations')
            mutations_tr = mutations_h2.find_parent('tr')
            subsequent_trs = mutations_tr.find_all_next('tr')

            test_arr = []
            mutation_arr = []
            test_index_dict = {}
            mutation_index_dict = {}
            matrix = [['' for _ in range(10000)] for _ in range(10000)]
            mutation_index = 0
            for tr in subsequent_trs:
                line_num = tr.find('a').get_text().strip()
                p_tag = tr.find('p')
                p_text = p_tag.get_text(' ', strip=True)
                killed_by = p_tag.find('b', string='Killed by : ').next_sibling.strip()
                status = p_text.split()[-1]
                str_arr = p_tag.text.strip().split()
                if status == 'SURVIVED':
                    init_index = str_arr.index('none')
                else:
                    try:
                        init_index = str_arr.index(killed_by)
                    except ValueError:
                        arrow_index = str_arr.index('→')
                        init_index = arrow_index
                        while True:
                            if str_arr[init_index] in killed_by:
                                break
                            init_index -= 1
                init_index += 1
                mutation_operation = ' '.join(str_arr[init_index:-2])

                mutation_arr.append(f'{line_num}|{mutation_operation}')
                if status == 'SURVIVED':
                    mutation_index += 1
                    continue
                if killed_by not in test_index_dict:
                    test_index_dict[killed_by] = len(test_arr)
                    test_arr.append(killed_by)
                test_index = test_index_dict[killed_by]
                matrix[mutation_index][test_index] = status
                mutation_index += 1
            df = pd.DataFrame(None, columns=test_arr, dtype=str)
            df.insert(0, 'mutation', pd.Series(mutation_arr))
            for i in range(mutation_index):
                for j in range(len(test_arr)):
                    df.iloc[i, j + 1] = matrix[i][j]
            df.to_csv(f'{pit_matrix_path}/{director}/{classname}.csv', sep=',', header=True, index=False)
            print(f'{director}/{html} is Done!')
