import json
import csv


chain_summary_file = 'chains_summary.txt'
merged_model_file = 'merged_model_4_unique.json'
mismatch_dict_model_file = 'mismatch_dict_model.json'
license_name_map_file = 'license_name_map.json'
oss_ai_edit_file = 'oss_ai_edit.csv'

# absentAtti = [2,2,2,2,1, 1,2,2,2,1, 1,2,1,1,1, 2,1,2,1,1, 1,2,1]
absentAtti = [1,1,1,1,1, 1,1,1,1,1, 1,1,1,1,1, 1,1,1,1,1, 1,1,1]
allowed_license_combinations = [
    ('77', 'creativeml-openrail-m'),
    ('77', 'openrail++'),
    ('77', 'llama2'),
    ('9', 'llama2'),
    ('77', 'bigscience-bloom-rail-1.0'),
    ('creativeml-openrail-m', '42'),
    ('openrail++', '42'),

    ('77', '9'),
    ('9', '31'),
    ('9', '42'),
    ('9', '41'),
    ('9', '30'),
    ('9', '39'),
    ('77', '31'),
    ('77', '30'),
    ('77', '39'),
]

matched_chains = {}

basemodel_model_conflictions = {}
basemodel_model_pair_list = []
conflict_positions = {}
node_3_chain_conflictions = {
    "1-2" : 0,
    "2-3" : 0,
    "all" : 0
}

def write_dict_to_json(data, filename):

    data_json = {str(key): value for key, value in data.items()}


    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data_json, file, indent=4, ensure_ascii=False)
    print(f"Data written to {filename}")

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



def get_license_name_mapping(license, license_name_map):
    return license_name_map.get(license, "")



def convert_license_terms(license, absentAtti, oss_ai_edit_data):
    if license == 'no_license':
        return absentAtti
    license_file = f'{license}.txt'
    if license_file not in oss_ai_edit_data:
        raise ValueError(f"License {license_file} not found in oss_ai_edit data.")

    terms = oss_ai_edit_data[license_file]
    return [absentAtti[i] if terms[i] == 0 else terms[i] for i in range(len(terms))]



def check_license_compatibility(terms_a, terms_b):
    for i in range(len(terms_a)):
        if terms_a[i] == 1:
            continue
        elif terms_a[i] == 2 and terms_b[i] != 2:
            return False
        elif terms_a[i] == 3 and terms_b[i] != 3:
            return False
    return True



def parse_chain_summary(chain_summary_file):
    with open(chain_summary_file, 'r', encoding='utf-8') as f:
        return [line.strip().split(" -> ") for line in f]



def process_chains():
    # 加载数据
    models = load_json_file(merged_model_file)
    mismatch_dict_model = load_json_file(mismatch_dict_model_file)
    license_name_map = load_json_file(license_name_map_file)
    header, oss_ai_edit_data = load_csv_file(oss_ai_edit_file)


    incompatibility_reverse_stats = {
        f"{i}-nodes": {} for i in range(2, 8)
    }
    compatibility_stats = {
        f"{i}-nodes": {"compatible": 0, "incompatible": 0} for i in range(2, 8)
    }

    license_compatible_chains = 0
    license_incompatible_chains = 0
    processed_chains = 0
    skipped_chains = 0


    chains = parse_chain_summary(chain_summary_file)

    for chain in chains:
        flag1_2 = False
        flag2_3 = False
        if len(chain) < 2:
            skipped_chains += 1
            print(chain + 'chain < 2')
            continue

        chain_length_key = f"{len(chain)}-nodes"
        if chain_length_key not in compatibility_stats:

            compatibility_stats[chain_length_key] = {"compatible": 0, "incompatible": 0}
            incompatibility_reverse_stats[chain_length_key] = {}

        licenses = []
        original_licenses = []
        skip_chain = False
        chain_models = []


        for model_id in chain:
            chain_models.append(model_id)
            license = get_model_license(model_id, models, mismatch_dict_model)
            if license == "no_license":
                licenses.append(license)
                original_licenses.append(license)
                continue

            mapped_license = get_license_name_mapping(license, license_name_map)
            if mapped_license == "":
                skip_chain = True
                break
            licenses.append(mapped_license)
            original_licenses.append(license)

        if skip_chain:
            skipped_chains += 1
            continue


        all_compatible = True
        reverse_incompat_position = -1

        for i in range(len(chain) - 1, 0, -1):
            try:
                terms_current = convert_license_terms(licenses[i], absentAtti, oss_ai_edit_data)
                terms_previous = convert_license_terms(licenses[i - 1], absentAtti, oss_ai_edit_data)
            except ValueError as e:

                skip_chain = True
                break
            basemodel_model_pair = (chain_models[i], chain_models[i - 1])
            if basemodel_model_pair not in basemodel_model_pair_list:
                basemodel_model_pair_list.append(basemodel_model_pair)
            if not check_license_compatibility(terms_current, terms_previous):

                original_licenses_key = (original_licenses[i], original_licenses[i - 1])
                if original_licenses[i - 1] != "no_license" and original_licenses[i] != "no_license":

                    license_pair = (licenses[i - 1], licenses[i])
                    if license_pair in allowed_license_combinations:
                        matched_chains.setdefault(license_pair, []).append(chain)
                if basemodel_model_pair not in basemodel_model_conflictions:
                    basemodel_model_conflictions[basemodel_model_pair] = original_licenses_key
                all_compatible = False
                if f"{len(chain)}_{len(chain) - i}" in conflict_positions:
                    conflict_positions[f"{len(chain)}_{len(chain) - i}"] += 1
                else:
                    conflict_positions[f"{len(chain)}_{len(chain) - i}"] = 1
                reverse_incompat_position = len(chain) - i
                if len(chain) == 3:
                    if i == 2:

                        flag1_2 = True
                    if i == 1:
                        flag2_3 = True
        if len(chain) == 3:
            if flag1_2 and not flag2_3:
                node_3_chain_conflictions["1-2"] += 1
            if flag2_3 and not flag1_2:
                node_3_chain_conflictions["2-3"] += 1
            if flag1_2 and flag2_3:
                node_3_chain_conflictions["all"] += 1

        if skip_chain:
            skipped_chains += 1
            continue


        processed_chains += 1
        if all_compatible:
            license_compatible_chains += 1
            compatibility_stats[chain_length_key]["compatible"] += 1
        else:
            license_incompatible_chains += 1
            compatibility_stats[chain_length_key]["incompatible"] += 1
            if reverse_incompat_position != -1:
                reverse_stats = incompatibility_reverse_stats[chain_length_key]
                reverse_stats[reverse_incompat_position] = reverse_stats.get(reverse_incompat_position, 0) + 1




    print("\n====== License Compatibility Summary ======")
    print(f"Total chains processed: {processed_chains}")
    print(f"Total chains skipped due to license issues: {skipped_chains}")
    print(f"Compatible chains: {license_compatible_chains}")
    print(f"Incompatible chains: {license_incompatible_chains}")
    print("Details by chain length:")
    for length, stats in sorted(compatibility_stats.items()):
        print(f"{length}: {stats}")

    print("\nIncompatibility start position from tail (reverse index):")
    for length_key, reverse_pos_dict in sorted(incompatibility_reverse_stats.items()):
        if reverse_pos_dict:
            print(f"{length_key}:")
            for rev_pos, count in sorted(reverse_pos_dict.items()):
                print(f"  Incompatibility starts from reverse position {rev_pos}: {count} chains")

    write_dict_to_json(matched_chains, "matched_chains.json")
    write_dict_to_json(basemodel_model_conflictions, "basemodel_model_conflictions.json")
    print(conflict_positions)
    print("3node chain：")
    print(node_3_chain_conflictions)
    print(f"{len(basemodel_model_pair_list)}model and basemodel pair")
    print(f"has {len(basemodel_model_conflictions)} conflict")


if __name__ == "__main__":
    process_chains()
