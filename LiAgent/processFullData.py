import csv
import json
import os

ATTITUDE_MAP = {
    "can": "1",
    "cannot": "2",
    "must": "3"
}

def process_full_license_files(input_csv, output_csv, output_folder):
    # 读取 CSV 文件
    with open(input_csv, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        data = list(reader)

    updated_data = []

    for row in data:
        file_name = row[0]
        terms = row[1:]

        # Find a term that contains multiple numerical values
        multi_value_terms = {
            header[i + 1]: terms[i]
            for i in range(len(terms))
            if "," in terms[i]
        }

        if not multi_value_terms:
            updated_data.append(row)
            continue  # If there is no term with multiple values, skip it.
        else:
            print(f"{file_name} contains multiple attitudes corresponding to the term, {multi_value_terms}")

        result_file = os.path.join(output_folder, f"{file_name.replace('.txt', '_result.txt')}")
        if not os.path.exists(result_file):
            print(f"⚠️ The result file {result_file} does not exist. Skipping {file_name}.")
            updated_data.append(row)
            continue

        with open(result_file, "r", encoding="utf-8") as rf:
            result_data = json.load(rf).get("results", [])

        term_attitude_map = {}
        for entry in result_data:
            term = entry["term"]
            attitude_str = entry["attitude"]

            # Filter out the terms that are not in the multi_value_terms.
            if term not in multi_value_terms:
                continue

            # Check whether the attitude is legal
            if attitude_str not in ATTITUDE_MAP:
                print(f"❌ Error: The term `{term}` in {file_name} has an unknown attitude of `{attitude_str}`. Skipping this term")
                continue

            attitude_value = ATTITUDE_MAP[attitude_str]
            if term in term_attitude_map:
                term_attitude_map[term].add(attitude_value)
            else:
                term_attitude_map[term] = {attitude_value}

        for term, original_value in multi_value_terms.items():
            if term not in term_attitude_map:
                continue  # If the term is not found, skip.

            new_values = sorted(term_attitude_map[term])
            row[header.index(term)] = ",".join(new_values)

        updated_data.append(row)

    with open(output_csv, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(updated_data)

    print(f"✅ Processing completed. The updated file has been saved to {output_csv}")


