import xml.etree.ElementTree as ET
import json
from pitest_log_parser import mutant_choice, test_choice

project_list = [
    # 'assertj-assertions-generator',
    # 'commons-net',
    'commons-cli',
    'commons-csv',
    'commons-codec',
    'delight-nashorn-sandbox',
    'empire-db',
    'jimfs',
    'httpcore',
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
    # 'default',
    # 'sgl_grp',
    'def_ln-freq_def',
    'def_def_shuf',
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
project_subdir_dict = {
    'assertj-assertions-generator': '',
    'commons-cli': '',
    'commons-csv': '',
    'commons-codec': '',
    'commons-net': '',
    'delight-nashorn-sandbox': '',
    'jimfs': 'jimfs/',
    'empire-db': 'empire-db/',
    'httpcore': 'httpcore5/',
    'handlebars.java': 'handlebars/',
    'riptide': 'riptide-core/'
}
round_number = 6
random_mutant = False
random_test = False
choice = 'more_projects'
xmls_dir = f'controlled_projects/both'
parsed_dir = f'controlled_parsed_data/both'


def parse_xml(s, p, rnd):
    xml_path = f'{xmls_dir}/{s}/{p}_{rnd}/{project_subdir_dict[p]}target/pit-reports/mutations.xml'
    tree = ET.parse(xml_path)
    root = tree.getroot()
    mutations = root.findall('mutation')
    for mutation in mutations:
        mutation_dict = mutation.attrib.copy()
        for character in mutation:
            if character.tag in ('indexes', 'blocks'):
                mutation_dict[character.tag] = tuple(c.text for c in character)
            elif character.tag in ('succeedingTests', 'killingTests'):
                if character.text is None:
                    mutation_dict[character.tag] = character.text
                elif '|' in character.text:
                    mutation_dict[character.tag] = tuple(set(character.text.split('|')))
                else:
                    mutation_dict[character.tag] = (character.text, )
            else:
                mutation_dict[character.tag] = character.text
        mutation_set.add(tuple(mutation_dict.items()))


if __name__ == '__main__':
    for project in project_list:
        for seed in seed_list:
            print(f'{project} with {seed} is processing... ...')
            mutation_set = set()
            for i in range(round_number):
                parse_xml(s=seed, p=project, rnd=i)
            with open(f'{parsed_dir}/{project}_{seed}/mutations_xml.json', 'w') as file:
                json.dump([dict(mutation) for mutation in mutation_set], file, indent=4)
