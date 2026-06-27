from typing import List, Tuple
import os
import re
import json
import csv

def load_terms(file_path="resources/termDefinitions.json"):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def read_txt_files(input_folder: str) -> List[str]:
    """
    Read the paths of all txt files in the specified folder.
    """
    if not os.path.exists(input_folder):
        print(f"Error: The input folder '{input_folder}' does not exist.")
        return []
    return [os.path.join(input_folder, f) for f in os.listdir(input_folder) if f.endswith(".txt")]


def split_and_save_text(file_path: str, char_limit: int, output_folder: str) -> List[str]:
    """
    Divide the text according to the character limit and save it to a separate txt file.
    """
    os.makedirs(output_folder, exist_ok=True)

    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    sentences = re.split(r"(?<=[.!?])\s+", content)
    segments = []
    current_segment = ""

    for sentence in sentences:
        if len(current_segment) + len(sentence) <= char_limit:
            current_segment += sentence + " "
        else:
            segments.append(current_segment.strip())
            current_segment = sentence + " "
    if current_segment.strip():
        segments.append(current_segment.strip())

    split_files = []
    base_name = os.path.basename(file_path).replace(".txt", "")
    for i, segment in enumerate(segments, start=1):
        split_file = os.path.join(output_folder, f"{base_name}_{i}.txt")
        with open(split_file, "w", encoding="utf-8") as out_file:
            out_file.write(segment)
        split_files.append(split_file)

    return split_files

def save_part_results(output_folder: str, file_name: str, results: List[Tuple[int, str]]):
    """
    Save the processed results of the split licenses to a new txt file.
    """
    os.makedirs(output_folder, exist_ok=True)
    for i, result in results:
        if result is None:
            print(f"Warning: The content of the file {file_name}_{i}_result.txt is empty. It has been skipped.")
            continue
        result_file = os.path.join(output_folder, f"{file_name}_{i}_result.txt")
        with open(result_file, "w", encoding="utf-8") as out_file:
            out_file.write(result)

def save_global_results(output_folder: str, file_name: str, result):
    """
    Save the processed results of the complete license to a new txt file.
    """
    os.makedirs(output_folder, exist_ok=True)
    if result is None:
        print(f"Warning: The content of the file {file_name}_result.txt is empty, so it has been skipped.")
        return
    result_file = os.path.join(output_folder, f"{file_name}_result.txt")
    with open(result_file, "w", encoding="utf-8") as out_file:
        out_file.write(result)

def get_conflicting_files(csv_file):
    """
    Read the CSV file, identify the terms that have multiple "attitude" values, and return the corresponding file names along with the list of conflicting terms.
    """
    conflicting_files = {}

    with open(csv_file, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)

        for row in reader:
            file_name = row[0]
            conflicting_terms = []

            for term, value in zip(header[1:], row[1:]):
                if "," in value:
                    conflicting_terms.append(term)

            if conflicting_terms:
                conflicting_files[file_name] = conflicting_terms

    return conflicting_files

def find_conflicting_terms(result):
    """
    Process the JSON results returned by the llm API, and identify the terms with inconsistent attitudes.
    """
    if isinstance(result, str):
        try:
            result = json.loads(result)
        except json.JSONDecodeError:
            print("Error: Failed to decode result string into JSON.")
            return []

    term_attitude_map = {}
    conflict_terms = set()

    for entry in result.get("results", []):
        term = entry["term"]
        attitude = entry["attitude"]

        if term in term_attitude_map:
            if term_attitude_map[term] != attitude:
                conflict_terms.add(term)
        else:
            term_attitude_map[term] = attitude

    return list(conflict_terms)

def update_result_with_result_round_2(result, conflict_terms, result_round_2):
    """
    Correct the "result", examine each term in "conflict_terms", and compare it with the entries in "result_round_2".
    If a term in "conflict_terms" finds a match in "result_round_2", remove all relevant entries in "result" and add the new one.
    """

    if isinstance(result_round_2, str):
        try:
            result_round_2 = json.loads(result_round_2)
        except json.JSONDecodeError:
            print("Error: Failed to decode result_round_2 string into JSON.")
            return result

    if isinstance(result, str):
        try:
            result_json = json.loads(result)
        except json.JSONDecodeError:
            print("Error: Failed to decode result string into JSON.")
            return result

    for term in conflict_terms:
        matching_entries = [entry for entry in result_round_2["results"] if entry["term"] == term]

        if matching_entries:
            result_json["results"] = [entry for entry in result_json["results"] if entry["term"] != term]

            result_json["results"].extend(matching_entries)

    result = json.dumps(result_json, indent=2)
    return result

def generate_license_summaries(csv_file_path):
    output_dir = 'result'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    disclaimer = (
        "**************************************************\n"
        "⚠️  IMPORTANT: LiAgent-GENERATED SUMMARY - PLEASE READ\n"
        "This document is for informational purposes ONLY.\n"
        "It was automatically generated by an AI model and\n"
        "may contain inaccuracies. DO NOT rely on this as\n"
        "legal advice. Always verify with the original\n"
        "license text.\n"
        "**************************************************\n\n"
    )

    try:
        with open(csv_file_path, mode='r', encoding='utf-8') as f:
            reader = csv.reader(f)
            headers = next(reader)
            terms = headers[1:]

            for row in reader:
                if not row or len(row) < 2: continue

                license_name = row[0]
                attitudes = row[1:]

                can_list, cannot_list, must_list = [], [], []

                for i in range(len(attitudes)):
                    if i >= len(terms): break
                    term_name = terms[i]
                    val = row[i + 1].strip()
                    if val == '1':
                        can_list.append(term_name)
                    elif val == '2':
                        cannot_list.append(term_name)
                    elif val == '3':
                        must_list.append(term_name)

                file_path = os.path.join(output_dir, f"{license_name}")

                with open(file_path, 'w', encoding='utf-8') as out_f:
                    out_f.write(disclaimer)
                    out_f.write(f"==================================================\n")
                    out_f.write(f"LICENSE SUMMARY: {license_name}\n")
                    out_f.write(f"==================================================\n\n")

                    sections = [
                        ("🟢 YOU CAN:", can_list),
                        ("🔴 YOU CANNOT:", cannot_list),
                        ("⚠️ YOU MUST:", must_list)
                    ]

                    for title, items in sections:
                        if items:
                            out_f.write(f"{title}\n")
                            out_f.write("-" * 50 + "\n")
                            for item in items:
                                out_f.write(f"- {item}\n")
                            out_f.write("\n")

                    out_f.write("==================================================\n")
                    out_f.write("Processed by: LiAgent \n")

    except Exception as e:
        print(f"An error occurred: {e}")