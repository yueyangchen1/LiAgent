import os
import json
from collections import defaultdict, Counter
from datetime import datetime

metadata_dir = 'metadata'
output_json = 'license_stats_12180.json'

all_repos = []
all_repos_name = []
all_repos_spdx_id = []

# Traverse the metadata directory to read all repo json files
for filename in os.listdir(metadata_dir):
    if filename.endswith('.json'):
        filepath = os.path.join(metadata_dir, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                stars = data.get('stargazers_count', 0)
                created_at = data.get('created_at', '')
                try:
                    year = datetime.strptime(created_at, '%Y-%m-%dT%H:%M:%SZ').year
                except:
                    year = None
                license_info = data.get('license')
                if not license_info or 'key' not in license_info:
                    license_key = 'no license'
                else:
                    license_key = license_info['key']
                all_repos.append({
                    'stars': stars,
                    'year': year,
                    'license': license_key
                })

                if not license_info or 'name' not in license_info:
                    license_name = 'no license'
                else:
                    license_name = license_info['name']
                all_repos_name.append({
                    'stars': stars,
                    'year': year,
                    'license': license_name
                })

                if not license_info or 'spdx_id' not in license_info:
                    license_spdx_id = 'no license'
                else:
                    license_spdx_id = license_info['spdx_id']
                all_repos_spdx_id.append({
                    'stars': stars,
                    'year': year,
                    'license': license_spdx_id
                })
        except Exception as e:
            print(f"Error reading {filename}: {e}")

print(f"Total repos loaded: {len(all_repos)}")

# ----------------------------------------
# statistics
# ----------------------------------------

def count_license_distribution(repos, filename):
    counter = Counter(repo['license'] for repo in repos)
    sorted_items = sorted(counter.items(), key=lambda x: -x[1])
    labels = [k for k, _ in sorted_items]
    values = [v for _, v in sorted_items]
    print(f"\n== {filename} ==")
    for k, v in zip(labels, values):
        print(f"{k}: {v}")
    return {
        'labels': labels,
        'values': values,
        'filename': filename,
        'ymax': 1000
    }

# ----------------------------------------
# Handling the main set and subsets
# ----------------------------------------

results = []

# all repo
results.append(count_license_distribution(all_repos, "All Repos - License Key.png"))
results.append(count_license_distribution(all_repos_name, "All Repos - License name.png"))
results.append(count_license_distribution(all_repos_spdx_id, "All Repos - License spdx_id.png"))

# rank10%
sorted_by_star = sorted(all_repos, key=lambda x: -x['stars'])
top_10_percent = sorted_by_star[:max(1, int(len(all_repos) * 0.1))]
results.append(count_license_distribution(top_10_percent, "Top 10 Percent Repos - License Key.png"))

# rank100
top_100 = sorted_by_star[:100]
results.append(count_license_distribution(top_100, "Top 100 Repos - License Key.png"))

# star > 500
above_500 = [repo for repo in all_repos if repo['stars'] > 500]
results.append(count_license_distribution(above_500, "Repos With _500 Stars - License Key.png"))

# ----------------------------------------
# 2022~2025
# ----------------------------------------

for year in [2022, 2023, 2024, 2025]:
    year_repos = [repo for repo in all_repos if repo['year'] == year]
    if not year_repos:
        continue

    results.append(count_license_distribution(year_repos, f"Repos Created in {year} - License Key.png"))

    sorted_year = sorted(year_repos, key=lambda x: -x['stars'])

    top_10_y = sorted_year[:max(1, int(len(sorted_year) * 0.1))]
    results.append(count_license_distribution(top_10_y, f"Top 10 Percent Repos Created in {year} - License Key.png"))

    top_100_y = sorted_year[:100]
    results.append(count_license_distribution(top_100_y, f"Top 100 Repos Created in {year} - License Key.png"))

    above_500_y = [repo for repo in year_repos if repo['stars'] > 500]
    results.append(count_license_distribution(above_500_y, f"Repos With _500 Stars Created in {year} - License Key.png"))

# ----------------------------------------
# save to json
# ----------------------------------------

with open(output_json, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=4)

print(f"\n📁 All the statistical results have been saved to {output_json}")
