import json
from collections import Counter
from datetime import datetime
# Running this code will enable you to obtain the distribution of dataset licenses.
dataset_metadata_file = 'datasets_metadata_708.json'
output_json = 'dataset_license_stats_708.json'

all_datasets = []

with open(dataset_metadata_file, 'r', encoding='utf-8') as f:
    data = json.load(f)
    for ds in data:
        likes = ds.get('likes', 0)
        created_at = ds.get('createdAt', '')
        try:
            year = datetime.strptime(created_at, '%Y-%m-%dT%H:%M:%S.%fZ').year
        except:
            try:
                year = datetime.strptime(created_at, '%Y-%m-%dT%H:%M:%SZ').year
            except:
                year = None

        tags = ds.get('tags', [])
        license_tag = next((tag for tag in tags if tag.startswith('license:')), 'license:unknown')
        if ds.get("id") == 'allenai/cord19':
            print(license_tag)
        license_key = license_tag.split(':', 1)[1].lower() if ':' in license_tag else 'unknown'

        all_datasets.append({
            'likes': likes,
            'year': year,
            'license': license_key
        })

print(f"Total datasets loaded: {len(all_datasets)}")

# ----------------------------------------
#
# ----------------------------------------

def count_license_distribution(items, filename):
    counter = Counter(item['license'] for item in items)
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
        'ymax': 100
    }

# ----------------------------------------
#
# ----------------------------------------

results = []

results.append(count_license_distribution(all_datasets, "All Datasets - License Key.png"))

# Top 10%
sorted_by_likes = sorted(all_datasets, key=lambda x: -x['likes'])
top_10_percent = sorted_by_likes[:max(1, int(len(all_datasets) * 0.1))]
results.append(count_license_distribution(top_10_percent, "Top 10 Percent Datasets - License Key.png"))

# top100
top_100 = sorted_by_likes[:100]
results.append(count_license_distribution(top_100, "Top 100 Datasets - License Key.png"))

# likes > 500
above_500 = [item for item in all_datasets if item['likes'] > 500]
results.append(count_license_distribution(above_500, "Datasets With _500 Likes - License Key.png"))

# ----------------------------------------
#
# ----------------------------------------

for year in [2022, 2023, 2024, 2025]:
    year_items = [item for item in all_datasets if item['year'] == year]
    if not year_items:
        continue

    results.append(count_license_distribution(year_items, f"Datasets Created in {year} - License Key.png"))

    sorted_year = sorted(year_items, key=lambda x: -x['likes'])

    top_10_y = sorted_year[:max(1, int(len(sorted_year) * 0.1))]
    results.append(count_license_distribution(top_10_y, f"Top 10 Percent Datasets Created in {year} - License Key.png"))

    top_100_y = sorted_year[:100]
    results.append(count_license_distribution(top_100_y, f"Top 100 Datasets Created in {year} - License Key.png"))

    above_500_y = [item for item in year_items if item['likes'] > 500]
    results.append(count_license_distribution(above_500_y, f"Datasets With _500 Likes Created in {year} - License Key.png"))

# ----------------------------------------
#
# ----------------------------------------

with open(output_json, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=4)

print(f"\n📁 {output_json}")
