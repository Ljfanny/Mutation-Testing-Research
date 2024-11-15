import xml.etree.ElementTree as ET
import json
from pitest_log_parser import mutant_choice, test_choice

project_list = [
    'assertj-assertions-generator',
    'commons-cli',
    'commons-csv',
    'commons-codec',
    'delight-nashorn-sandbox',
    # 'empire-db',
    # 'jimfs',
    # 'commons-net',
    # 'commons-collections',
    # 'commons-net',
    # 'empire-db',
    # 'guava',
    # 'handlebars.java',
    # 'httpcore',
    # 'java-design-patterns',
    # 'jooby',
    # 'maven-dependency-plugin',
    # 'maven-shade-plugin',
    # 'riptide',
    # 'sling-org-apache-sling-auth-core',
    # 'stream-lib'
]
seed_list = [
    # 0,
    # 42,
    # 123,
    # 216,
    # 1202,
    # 1999,
    # 2002,
    # 2024,
    # 31415,
    # 99999,
    # 'default',
    'fastest'
]
round_number = 6
random_mutant = False
random_test = False
parent_dir = 'controlled_mutation_xmls'


def parse_xml(s, p, rnd):
    xml_path = f'{parent_dir}/more_projects/{s}/{p}_{rnd}/target/pit-reports/mutations.xml'
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
                    mutation_dict[character.tag] = tuple(character.text.split('|'))
                else:
                    mutation_dict[character.tag] = (character.text, )
            else:
                mutation_dict[character.tag] = character.text
        mutation_set.add(tuple(mutation_dict.items()))


if __name__ == '__main__':
    choice = 'more_projects'
    for project in project_list:
        for seed in seed_list:
            print(f'{project} with {seed} is processing... ...')
            mutation_set = set()
            for i in range(round_number):
                parse_xml(s=seed, p=project, rnd=i)
            with open(f'controlled_parsed_data/more_projects/{project}_{seed}/mutations_xml.json', 'w') as file:
                json.dump([dict(mutation) for mutation in mutation_set], file, indent=4)
