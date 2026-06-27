import os
import json
import csv
from collections import defaultdict

TERMS = [
    "Distribute", "Modify", "Commercial Use", "Hold Liable", "Include Copyright",
    "Include License", "Sublicense", "Use Trademark", "Private Use", "Disclose Source",
    "State Changes", "Place Warranty", "Include Notice", "Include Original", "Give Credit",
    "Use Patent Claims", "Rename", "Relicense", "Contact Author", "Include Install Instructions",
    "Compensate for Damages", "Statically Link", "Pay Above Use Threshold"
]

ATTITUDE_MAPPING = {
    "can": 1,
    "cannot": 2,
    "must": 3
}


def process_part_license_files(output_dir, csv_file):

    # Obtain all file names and group them by license names.
    license_files = defaultdict(list)
    for filename in os.listdir(output_dir):
        if filename.endswith("_result.txt"):
            parts = filename.rsplit('_', 2)
            license_name = parts[0]
            license_files[license_name].append(os.path.join(output_dir, filename))

    unknown_terms = defaultdict(int)  # Used for recording unknown terms
    csv_data = []

    for license_name, files in license_files.items():
        terms_attitudes = defaultdict(set)  # Each term corresponds to multiple attitudes.

        for file_path in files:
            with open(file_path, 'r', encoding='utf-8') as file:
                try:
                    data = json.load(file)
                    if 'results' not in data or not data['results']:
                        continue

                    for result in data['results']:
                        term = result.get('term', '').strip().lower()
                        attitude = result.get('attitude', '').strip().lower()

                        # Check whether the attitude is legal
                        if attitude not in ATTITUDE_MAPPING:
                            if attitude:
                                unknown_terms[attitude] += 1  # Record the unknown attitude
                            attitude = 'unknown'

                        # Record the "attitude" corresponding to the term
                        if term:
                            terms_attitudes[term].add(ATTITUDE_MAPPING.get(attitude, 'unknown'))

                except json.JSONDecodeError:
                    print(f"Error decoding JSON in {file_path}")
                except Exception as e:
                    print(f"Error processing {file_path}: {str(e)}")

        license_row = [f"{license_name}.txt"]

        # Record the "term" corresponding to "attitude" and create a column for each term, filling in the "attitude" values.
        for term in TERMS:
            term_lower = term.lower()
            attitudes = terms_attitudes.get(term_lower, set())
            if attitudes:
                # If there are multiple attitudes, separate them with commas.
                license_row.append(",".join(sorted(map(str, attitudes))))
            else:
                license_row.append("0")

        csv_data.append(license_row)

    save_to_csv(csv_data, csv_file)

    save_unknown_terms(unknown_terms)


def save_to_csv(csv_data, csv_file):
    """ Save data to a CSV file """
    with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["License Name"] + TERMS)
        writer.writerows(csv_data)
    print(f"CSV file saved as {csv_file}")

def save_unknown_terms(unknown_terms):
    """ Keep the unknown terms and attitudes. """
    if unknown_terms:
        print("\nUnknown terms and attitudes found:")
        for term, count in unknown_terms.items():
            print(f"{term}: {count}")
    else:
        print("\nNo unknown terms or attitudes found.")


