import xml.etree.ElementTree as ET
import json
import os

#Given a test, tell me which mutants the test kills/succeeds on
test_succeed_dict = {}
test_killed_dict = {}

#Given a test, tell me which mutants the test covers (combo of kills and succeeds)
test_cover_dict = {}

#Given a mutant, tell me which tests kills it or succeeds on it
mutant_succeed_dict = {}
mutant_killed_dict = {}

#Given a mutant, tell me which tests covers it (combo of kills and succeeds)
mutant_cover_dict = {}

def find_files(root_dir, file_name):
    found_files = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename == file_name:
                found_files.append([os.path.join(dirpath, filename), os.path.dirname(dirpath)])
    return found_files

def extract_mutants_results(xml_file, mutation_results_dir):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Find all <mutation> elements in the XML
    mutants = root.findall('.//mutation')

    for mutant in mutants:
        source_file = mutant.find('sourceFile').text
        mutatedClass = mutant.find('mutatedClass').text
        mutatedMethod = mutant.find('mutatedMethod').text
        lineNumber = mutant.find('lineNumber').text
        mutator =  mutant.find('mutator').text
        if type(mutant.find('killingTests').text) == str:
            killingTests = mutant.find('killingTests').text.split("|")
        else:
            killingTests = []
        if type(mutant.find('succeedingTests').text) == str:
            succeedingTests = mutant.find('succeedingTests').text.split("|")
        else:
            succeedingTests = []
        mutant_killed_dict[source_file + "/" + mutatedClass + "/" + lineNumber + "/" + mutator] = killingTests
        mutant_succeed_dict[source_file + "/" + mutatedClass + "/" + lineNumber + "/" + mutator] = succeedingTests
        mutant_cover_dict[source_file + "/" + mutatedClass + "/" + lineNumber + "/" + mutator] = killingTests + succeedingTests
        for succeed in succeedingTests:
            if succeed not in test_succeed_dict:
                test_succeed_dict[succeed] = [source_file + "/" + mutatedClass + "/" + lineNumber + "/" + mutator]
            else:
                test_succeed_dict[succeed].append(source_file + "/" + mutatedClass + "/" + lineNumber + "/" + mutator)
            if succeed not in test_cover_dict:
                test_cover_dict[succeed] = [source_file + "/" + mutatedClass + "/" + lineNumber + "/" + mutator]
            else:
                test_cover_dict[succeed].append(source_file + "/" + mutatedClass + "/" + lineNumber + "/" + mutator)
        for killed in killingTests:
            if killed not in test_killed_dict:
                test_killed_dict[killed] = [source_file + "/" + mutatedClass + "/" + lineNumber + "/" + mutator]
            else:
                test_killed_dict[killed].append(source_file + "/" + mutatedClass + "/" + lineNumber + "/" + mutator)
            if killed not in test_cover_dict:
                test_cover_dict[killed] = [source_file + "/" + mutatedClass + "/" + lineNumber + "/" + mutator]
            else:
                test_cover_dict[killed].append(source_file + "/" + mutatedClass + "/" + lineNumber + "/" + mutator)
    os.makedirs(mutation_results_dir)
    with open(mutation_results_dir + "/test_succeed.json", "w") as outfile:
        json.dump(test_succeed_dict, outfile)
    with open(mutation_results_dir + "/test_killed.json", "w") as outfile:
        json.dump(test_killed_dict, outfile)
    with open(mutation_results_dir + "/test_cover.json", "w") as outfile:
        json.dump(test_cover_dict, outfile)
    with open(mutation_results_dir + "/mutant_succeed.json", "w") as outfile:
        json.dump(mutant_succeed_dict, outfile)
    with open(mutation_results_dir + "/mutant_killed.json", "w") as outfile:
        json.dump(mutant_killed_dict, outfile)
    with open(mutation_results_dir + "/mutant_cover.json", "w") as outfile:
        json.dump(mutant_cover_dict, outfile)
    

if __name__ == "__main__":
    root_directory = os.getcwd()
    target_file_name = "mutations.xml"

    matching_files = find_files(root_directory, target_file_name)

    for file_list in matching_files:
        extract_mutants_results(file_list[0], file_list[1] + "/mutation_results")