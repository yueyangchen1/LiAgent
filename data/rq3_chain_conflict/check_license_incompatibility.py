import ast
import json
import csv
import re

from pandas.core.arrays.period import raise_on_incompatible

# run this file can analyse conflict of chain
# chain_summary_file = 'test.txt'
chain_summary_file = 'chain_summary.txt'
# record the map of license name and number
repo_license_map_file = '../repo_license_map.json'
# model file
merged_model_file = '../merged_model_4_unique.json'
# map of model name and correct model name
mismatch_dict_model_file = '../mismatch_dict_model.json'

# dataset file
merged_dataset_file = '../merged_dataset_new.json'
# map of dataset name and correct dataset name
mismatch_dict_dataset_file = '../mismatch_dict_dataset.json'
license_name_map_file = '../license_name_map.json'
# license term groundtruth oss and ai
oss_ai_edit_file = '../oss_ai_edit.csv'

allowed_license_combinations = [
    # ('77', 'creativeml-openrail-m'),
    # ('77', 'openrail++'),
    # ('77', 'llama2'),
    # ('9', 'llama2'),
    # ('77', 'bigscience-bloom-rail-1.0'),
    # ('creativeml-openrail-m', '42'),
    # ('openrail++', '42')
    # ('77', '9'),
    # ('9', '31'),
    # ('9', '42'),
    # ('9', '30'),
    # ('9', '39'),
    # ('77', '31'),
    # ('77', '30'),
    # ('77', '39'),
]

matched_chains = {}

absentAtti = [2,2,2,2,1, 1,2,2,2,1, 1,2,1,1,1, 2,1,2,1,1, 1,2,1]
# absentAtti = [1,1,1,1,1, 1,1,1,1,1, 1,1,1,1,1, 1,1,1,1,1, 1,1,1]
term_list = ['Distribute', #0
                   'Modify', #1
                   'Commercial Use', #2
                   'Hold Liable', #3
                   'Include Copyright',#4
                   'Include License', #5
                   'Sublicense', #6
                   'Use Trademark', #7
                   'Private Use', #8
                   'Disclose Source', #9
                   'State Changes', #10
                   'Place Warranty', #11
                   'Include Notice', #12
                   'Include Original', #13
                   'Give Credit',#14
                   'Use Patent Claims', #15
                   'Rename', #16
                   'Relicense', #17
                   'Contact Author', #18
                   'Include Install Instructions', #19
                   'Compensate for Damages', #20
                   'Statically Link', #21
                   'Pay Above Use Threshold'#22
            ]
conflict_pair_dict = {}
conflict_pair_count = {}
conflict_term_count = {}


def load_json_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)



def load_csv_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        data = {
            rows[0].lower(): [int(float(val)) if '.' in val else int(val) for val in rows[1:]]
            for rows in reader
        }
    return header, data



def get_repo_license(repo_id, repo_license_map):
    return repo_license_map.get(repo_id, "no_license")


def get_model_license(model_id, models, mismatch_dict_model):
    model = next((m for m in models if m['id'] == model_id), None)
    if model:
        for tag in model['tags']:
            if tag.startswith('license:'):
                return tag.split(':')[1].lower()

    mapped_model_id = mismatch_dict_model.get(model_id)
    if mapped_model_id:
        model = next((m for m in models if m['id'] == mapped_model_id), None)
        if model:
            for tag in model['tags']:
                if tag.startswith('license:'):
                    return tag.split(':')[1].lower()
    return "no_license"


def get_dataset_license(dataset_id, datasets, mismatch_dict_dataset):
    dataset = next((d for d in datasets if d['id'] == dataset_id), None)
    if dataset:
        for tag in dataset['tags']:
            if tag.startswith('license:'):
                return tag.split(':')[1].lower()

    mapped_dataset_id = mismatch_dict_dataset.get(dataset_id)
    if mapped_dataset_id:
        dataset = next((d for d in datasets if d['id'] == mapped_dataset_id), None)
        if dataset:
            for tag in dataset['tags']:
                if tag.startswith('license:'):
                    return tag.split(':')[1].lower()
    return "no_license"


def get_license_name_mapping(license, license_name_map):

    license_lower = license.lower()
    return license_name_map.get(license_lower, "")


def convert_license_terms(license_name, absentAtti, oss_ai_edit_data):
    if license_name == 'no_license':
        return absentAtti, [True] * len(absentAtti)

    license_file = f'{license_name}.txt'
    if license_file not in oss_ai_edit_data:
        raise ValueError(f"License {license_file} not found in oss_ai_edit data.")

    terms = oss_ai_edit_data[license_file]

    converted_terms = []
    used_default_flags = []

    for i in range(len(terms)):
        if terms[i] == 0:
            converted_terms.append(absentAtti[i])
            used_default_flags.append(True)
        else:
            converted_terms.append(terms[i])
            used_default_flags.append(False)

    return converted_terms, used_default_flags



def check_term_compatibility(terms_a, terms_b):

    conflict_terms = []
    conflict_terms_index = []
    for i in range(len(terms_a)):
        if terms_a[i] == 1:
            continue
        elif terms_a[i] == 2 and terms_b[i] != 2:
            conflict_terms.append(term_list[i])
            conflict_terms_index.append(i)
        elif terms_a[i] == 3 and terms_b[i] != 3:
            conflict_terms.append(term_list[i])
            conflict_terms_index.append(i)

    return conflict_terms, conflict_terms_index

def check_license_compatibility(license_a, terms_a, license_b, terms_b, license_a_default_flags, license_b_default_flags):
    key = (license_a, license_b)  # 方向不同需要区分
    attitude_map = {
        1: "can",
        2: "cannot",
        3: "must"
    }
    if key in conflict_pair_dict:
        if conflict_pair_dict[key]:
            conflict_pair_count[key] += 1  # 直接增加冲突次数
        return conflict_pair_dict[key]  # 返回已存的冲突 term 列表

    conflict_terms, conflict_terms_index = check_term_compatibility(terms_a, terms_b)

    if conflict_terms:
        conflict_details = []
        for idx, term in enumerate(conflict_terms):
            detail = {
                "term": term,  # term 名字
                "license1_attitude": attitude_map[terms_a[conflict_terms_index[idx]]],
                "license2_attitude": attitude_map[terms_b[conflict_terms_index[idx]]],
                "license1_is_default": license_a_default_flags[conflict_terms_index[idx]],
                "license2_is_default": license_b_default_flags[conflict_terms_index[idx]]
            }
            conflict_details.append(detail)

        conflict_pair_dict[key] = conflict_details
        conflict_pair_count[key] = 1
    else:
        conflict_pair_dict[key] = []
        conflict_pair_count[key] = 0

    return conflict_terms



def parse_chain_summary(chain_summary_file):
    with open(chain_summary_file, 'r', encoding='utf-8') as f:
        return [line.strip().split(" -> ") for line in f]


def write_dict_to_json(data, filename):
    data_json = {str(key): value for key, value in data.items()}


    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data_json, file, indent=4, ensure_ascii=False)
    print(f"Data written to {filename}")


def process_chains():
    repo_license_map = load_json_file(repo_license_map_file)
    models = load_json_file(merged_model_file)
    mismatch_dict_model = load_json_file(mismatch_dict_model_file)
    datasets = load_json_file(merged_dataset_file)
    mismatch_dict_dataset = load_json_file(mismatch_dict_dataset_file)
    license_name_map = load_json_file(license_name_map_file)
    header, oss_ai_edit_data = load_csv_file(oss_ai_edit_file)

    chains = parse_chain_summary(chain_summary_file)

    compliant_chains = 0
    non_compliant_chains = 0
    license_compatible_chains = 0
    license_incompatible_chains = 0
    compatibility_stats = {
        '2-nodes': {'compatible': 0, 'incompatible': 0},
        '3-nodes': {
            'compatible': 0,
            'incompatible': 0,
            'dataset_model_compatible_but_repo_incompatible': 0,  # 预先初始化
            'model_repo_compatible_but_dataset_incompatible': 0,  # 预先初始化
        }
    }
    incompatible_2_node_chain_has_ai_or_eidt_count = 0
    incompatible_3_node_chain_has_ai_or_eidt_count = 0
    incompatible_2_node_chain_has_no_license = 0
    incompatible_3_node_chain_has_no_license = 0
    for chain in chains:
        repo_id = chain[0]
        model_id = chain[1]
        dataset_id = chain[2] if len(chain) > 2 else None

        repo_license = get_repo_license(repo_id, repo_license_map)
        model_license = get_model_license(model_id, models, mismatch_dict_model)
        dataset_license = get_dataset_license(dataset_id, datasets,
                                              mismatch_dict_dataset) if dataset_id else "no_license"

        licenses = [repo_license, model_license, dataset_license]
        all_compliant = True

        for i, license in enumerate(licenses):
            if license != 'no_license':
                mapped_license = get_license_name_mapping(license, license_name_map)
                if mapped_license:
                    licenses[i] = mapped_license
                else:
                    all_compliant = False
                    break
            # else:
            #     all_compliant = False


        #  repo_license, model_license, dataset_license
        repo_license, model_license, dataset_license = licenses

        if all_compliant:
            compliant_chains += 1
            # compatability check
            if len(chain) == 2:
                license_pair = (repo_license, model_license)
                if license_pair in allowed_license_combinations:
                    matched_chains.setdefault(license_pair, []).append(chain)
                model_terms, model_terms_default_flags = convert_license_terms(model_license, absentAtti, oss_ai_edit_data)
                repo_terms, repo_terms_default_flags = convert_license_terms(repo_license, absentAtti, oss_ai_edit_data)
                #
                if not check_license_compatibility(model_license, model_terms, repo_license, repo_terms, model_terms_default_flags, repo_terms_default_flags):
                    license_compatible_chains += 1
                    compatibility_stats['2-nodes']['compatible'] += 1
                else:
                    if not (repo_license.isdigit() or repo_license == "no_license") or not (model_license.isdigit() or model_license == "no_license"):
                        incompatible_2_node_chain_has_ai_or_eidt_count += 1
                    if repo_license == "no_license" or model_license == "no_license":
                        incompatible_2_node_chain_has_no_license += 1
                    license_incompatible_chains += 1
                    compatibility_stats['2-nodes']['incompatible'] += 1

            elif len(chain) == 3:
                license_pair = (repo_license, model_license)
                if license_pair in allowed_license_combinations:
                    # if repo_license != "no_license" and model_license != "no_license" and dataset_license != "no_license":
                    #     print(chain)
                    matched_chains.setdefault(license_pair, []).append(chain)
                dataset_terms, dataset_terms_default_flags = convert_license_terms(dataset_license, absentAtti, oss_ai_edit_data)
                model_terms, model_terms_default_flags = convert_license_terms(model_license, absentAtti, oss_ai_edit_data)
                repo_terms, repo_terms_default_flags = convert_license_terms(repo_license, absentAtti, oss_ai_edit_data)
                # 兼容性检测
                model_repo_compatible = check_license_compatibility(model_license, model_terms, repo_license, repo_terms, model_terms_default_flags, repo_terms_default_flags)
                dataset_model_compatible = check_license_compatibility(dataset_license, dataset_terms, model_license, model_terms, dataset_terms_default_flags, model_terms_default_flags)

                if not (model_license.isdigit() or model_license == "no_license") and not (dataset_license == "no_license") and not (repo_license == "no_license"):
                    print(chain)


                #
                if not model_repo_compatible and not dataset_model_compatible:
                    license_compatible_chains += 1
                    compatibility_stats['3-nodes']['compatible'] += 1
                else:
                    license_incompatible_chains += 1
                    compatibility_stats['3-nodes']['incompatible'] += 1

                    if not dataset_model_compatible and model_repo_compatible:
                        # if license_pair in allowed_license_combinations:
                        #     if repo_license != "no_license" and model_license != "no_license" and dataset_license != "no_license":
                        #         print(chain)
                        compatibility_stats['3-nodes']['dataset_model_compatible_but_repo_incompatible'] += 1
                        if not (repo_license.isdigit() or repo_license == "no_license") or not (model_license.isdigit() or model_license == "no_license"):
                            incompatible_3_node_chain_has_ai_or_eidt_count += 1
                            # if repo_license != "no_license" and model_license != "no_license" and dataset_license != "no_license":
                            #     print(chain)
                        if repo_license == "no_license" or model_license == "no_license":
                            incompatible_3_node_chain_has_no_license += 1
                    #
                    elif dataset_model_compatible and not model_repo_compatible:
                        compatibility_stats['3-nodes']['model_repo_compatible_but_dataset_incompatible'] += 1
                        if not (dataset_license.isdigit() or dataset_license == "no_license") or not (model_license.isdigit() or model_license == "no_license"):
                            incompatible_3_node_chain_has_ai_or_eidt_count += 1
                            # if repo_license != "no_license" and model_license != "no_license" and dataset_license != "no_license":
                            #     print(chain)
                        if model_license == "no_license" or dataset_license == "no_license":
                            incompatible_3_node_chain_has_no_license += 1
                    elif not dataset_model_compatible and not model_repo_compatible:
                        if repo_license != "no_license" and model_license != "no_license" and dataset_license != "no_license":
                            print(chain)
                        if not (repo_license.isdigit() or repo_license == "no_license") or not (model_license.isdigit() or model_license == "no_license") or not (dataset_license.isdigit() or dataset_license == "no_license"):
                            incompatible_3_node_chain_has_ai_or_eidt_count += 1
                            # if repo_license != "no_license" and model_license != "no_license" and dataset_license != "no_license":
                            #     print(chain)
                        if repo_license == "no_license" or model_license == "no_license" or dataset_license == "no_license":
                            incompatible_3_node_chain_has_no_license += 1


        else:
            non_compliant_chains += 1

    total_sum = sum(conflict_pair_count.values())
    print("all conflict pair num:", total_sum)

    filtered_sum = 0
    pattern = re.compile(r"\('([^']+)', '([^']+)'\)")

    for key, value in conflict_pair_count.items():
        key_str = str(key)
        match = pattern.match(key_str)  # 匹配

        if match:
            first, second = match.groups()

            if not (first.isdigit() or first == "no_license") or not (second.isdigit() or second == "no_license"):
                filtered_sum += value

    print("ai conflict pair:", filtered_sum)

    for pair_str, term_list in conflict_pair_dict.items():
        if pair_str not in conflict_pair_count:
            print(f"pair{pair_str}找不到")
            continue

        count = conflict_pair_count[pair_str]

        for term_info in term_list:
            term = term_info["term"]
            if term not in conflict_term_count:
                conflict_term_count[term] = 0
            conflict_term_count[term] += count


    sorted_conflict_term_count = dict(sorted(conflict_term_count.items(), key=lambda x: x[1], reverse=True))



    sorted_conflict_pair_count = dict(sorted(conflict_pair_count.items(), key=lambda item: item[1], reverse=True))

    sorted_keys = list(sorted_conflict_pair_count.keys())

    sorted_conflict_pair_dict = {key: conflict_pair_dict[key] for key in sorted_keys if key in conflict_pair_dict}
    write_dict_to_json(sorted_conflict_pair_dict, "conflict_pair_dict.json")
    write_dict_to_json(sorted_conflict_pair_count, "conflict_pair_count.json")
    write_dict_to_json(sorted_conflict_term_count, "conflict_term_count.json")
    print(f"ai license 2 node chain conflict num {incompatible_2_node_chain_has_ai_or_eidt_count}")
    print(f"ai license 3 node chain conflict num {incompatible_3_node_chain_has_ai_or_eidt_count}")
    print(f"no license 2 node chain conflict num {incompatible_2_node_chain_has_no_license}")
    print(f"no license 3 node chain conflict num {incompatible_3_node_chain_has_no_license}")
    print(f"Total chains: {len(chains)}")
    print(f"Total compliant chains: {compliant_chains}")
    print(f"Total non-compliant chains: {non_compliant_chains}")
    print(f"License compatible chains: {license_compatible_chains}")
    print(f"License incompatible chains: {license_incompatible_chains}")
    print(f"Compatibility stats: {compatibility_stats}")

    # write_dict_to_json(matched_chains, "matched_chains.json")

if __name__ == "__main__":
    process_chains()
