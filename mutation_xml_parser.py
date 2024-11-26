import xml.etree.ElementTree as ET
import json
from pitest_log_parser import mutant_choice, test_choice

project_list = [
    'assertj-assertions-generator',
    'commons-cli',
    'commons-csv',
    'commons-codec',
    # 'delight-nashorn-sandbox',
    'empire-db',
    'jimfs',
    # 'handlebars.java',
    # 'httpcore',
    # 'riptide',

    # 'commons-net',
    # 'commons-collections',
    # 'commons-net',
    # 'empire-db',
    # 'guava',
    # 'java-design-patterns',
    # 'jooby',
    # 'maven-dependency-plugin',
    # 'maven-shade-plugin',
    # 'sling-org-apache-sling-auth-core',
    # 'stream-lib'
]
seed_list = [
    0,
    42,
    # 123,
    # 216,
    # 1202,
    # 1999,
    # 2002,
    # 2024,
    # 31415,
    # 99999,
    'default',
    'fastest',
    # 'GC_torder',
    # 'GC_morder'
]
project_subdir_dict = {
    'assertj-assertions-generator': '',
    'commons-cli': '',
    'commons-csv': '',
    'commons-codec': '',
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
xmls_dir = f'tested_projects'
parsed_dir = f'tested_parsed_data'


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
