import json
# run this py you can merger model and dataset license distribution
# before run this you should manually modify the result of analyse_model_license.py and analyse_dataset_license.py because these are distribution by years

def load_json_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)[0]  #

def merge_license_data(file1_data, file2_data):
    merged = {}

    for label, value, gid in zip(file1_data["labels"], file1_data["values"], file1_data["group_ids"]):
        merged[label] = {
            "value": value,
            "group_id": gid
        }

    for label, value, gid in zip(file2_data["labels"], file2_data["values"], file2_data["group_ids"]):
        if label in merged:
            merged[label]["value"] += value
        else:
            merged[label] = {
                "value": value,
                "group_id": gid
            }

    sorted_items = sorted(merged.items(), key=lambda x: x[1]["value"], reverse=True)

    labels = [item[0] for item in sorted_items]
    values = [item[1]["value"] for item in sorted_items]
    group_ids = [item[1]["group_id"] for item in sorted_items]

    result = {
        "labels": labels,
        "values": values,
        "filename": file1_data["filename"],
        "ymax": file1_data["ymax"],
        "group_ids": group_ids
    }

    return result

def print_value_sums(file1_data, file2_data):
    sum1 = sum(file1_data["values"])
    sum2 = sum(file2_data["values"])
    print(f"File 1 total values: {sum1}")
    print(f"File 2 total values: {sum2}")

def main():

    file1_path = 'model_license_stats_3988_processed.json'
    file2_path = 'dataset_license_stats_708_processed.json'
    output_path = 'test.json'

    file1_data = load_json_file(file1_path)
    file2_data = load_json_file(file2_path)

    print_value_sums(file1_data, file2_data)

    merged_result = merge_license_data(file1_data, file2_data)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump([merged_result], f, indent=4)

    print(f"Merged result saved to {output_path}")

if __name__ == "__main__":
    main()
