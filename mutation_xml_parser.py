import xml.etree.ElementTree as ET
from types import MappingProxyType
import json

project_list = [
    # 'commons-codec',
    # 'commons-net',
    # 'delight-nashorn-sandbox',
    'empire-db',
    'jimfs'
]
TIMED_OUT = 'TIMED_OUT'
round_number = 6
random_mutant = False
random_test = True
seed_list = [0, 2024, 99999]
mutant_choice = {
    False: 'default-mutant',
    True: 'random-mutant'
}
test_choice = {
    False: 'default-test',
    True: 'random-test'
}
parent_dir = 'controlled_mutation_xmls'


def parse_xml(mutation_set, seed, project, round_cnt):
    choice = f'{mutant_choice[random_mutant]}_{test_choice[random_test]}'
    xml_path = f'{parent_dir}/{choice}/{seed}/{project}_{round_cnt}/{project}/target/pit-reports/mutations.xml'
    # xml_path = f'{parent_dir}/{choice}/{seed}/{project}_{round_cnt}/target/pit-reports/mutations.xml'
    tree = ET.parse(xml_path)
    root = tree.getroot()
    mutations = root.findall('mutation')
    for mutation in mutations:
        mutation_dict = mutation.attrib
        for character in mutation:
            if character.tag == 'indexes' or character.tag == 'blocks':
                mutation_dict[character.tag] = tuple([c.text for c in character])
            elif (character.tag == 'succeedingTests' or character.tag == 'killingTests')\
                    and character.text is not None\
                    and '|' in character.text:
                mutation_dict[character.tag] = tuple(character.text.split('|'))
            else:
                mutation_dict[character.tag] = character.text
        mutation_set.add(tuple(mutation_dict.items()))


if __name__ == '__main__':
    choice = f'{mutant_choice[random_mutant]}_{test_choice[random_test]}'
    for project in project_list:
        for seed in seed_list:
            print(f'{project} with {seed} is processing... ...')
            mutation_set = set()
            for i in range(round_number):
                parse_xml(mutation_set=mutation_set, seed=seed, project=project, round_cnt=i)
            with open(f'controlled_parsed_data/{choice}/{project}_{seed}/mutations_xml.json', 'w') as file:
                json.dump([dict(mutation) for mutation in mutation_set], file, indent=4)
