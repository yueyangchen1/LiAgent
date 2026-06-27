import json
from collections import Counter
from datetime import datetime
# Running this code will enable you to obtain the distribution of model licenses.

model_metadata_file = 'matched_models_3988.json'
output_json = 'model_license_stats_3988.json'


all_models = []

# 读取模型元数据
with open(model_metadata_file, 'r', encoding='utf-8') as f:
    data = json.load(f)
    for model in data:
        likes = model.get('likes', 0)
        created_at = model.get('createdAt', '')
        try:
            year = datetime.strptime(created_at, '%Y-%m-%dT%H:%M:%S.%fZ').year
        except:
            try:
                year = datetime.strptime(created_at, '%Y-%m-%dT%H:%M:%SZ').year
            except:
                year = None

        tags = model.get('tags', [])
        license_tag = next((tag for tag in tags if tag.startswith('license:')), 'license:unknown')
        license_key = license_tag.split(':', 1)[1].lower() if ':' in license_tag else 'unknown'

        all_models.append({
            'likes': likes,
            'year': year,
            'license': license_key
        })

print(f"Total models loaded: {len(all_models)}")

# ----------------------------------------
#
# ----------------------------------------

def count_license_distribution(models, filename):
    counter = Counter(model['license'] for model in models)
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
#
# ----------------------------------------

results = []

results.append(count_license_distribution(all_models, "All Models - License Key.png"))

# top10%
sorted_by_likes = sorted(all_models, key=lambda x: -x['likes'])
top_10_percent = sorted_by_likes[:max(1, int(len(all_models) * 0.1))]
results.append(count_license_distribution(top_10_percent, "Top 10 Percent Models - License Key.png"))

# top100
top_100 = sorted_by_likes[:100]
results.append(count_license_distribution(top_100, "Top 100 Models - License Key.png"))

# likes > 500
above_500 = [model for model in all_models if model['likes'] > 500]
results.append(count_license_distribution(above_500, "Models With _500 Likes - License Key.png"))

# ----------------------------------------
#
# ----------------------------------------

for year in [2022, 2023, 2024, 2025]:
    year_models = [model for model in all_models if model['year'] == year]
    if not year_models:
        continue

    results.append(count_license_distribution(year_models, f"Models Created in {year} - License Key.png"))

    sorted_year = sorted(year_models, key=lambda x: -x['likes'])

    top_10_y = sorted_year[:max(1, int(len(sorted_year) * 0.1))]
    results.append(count_license_distribution(top_10_y, f"Top 10 Percent Models Created in {year} - License Key.png"))

    top_100_y = sorted_year[:100]
    results.append(count_license_distribution(top_100_y, f"Top 100 Models Created in {year} - License Key.png"))

    above_500_y = [model for model in year_models if model['likes'] > 500]
    results.append(count_license_distribution(above_500_y, f"Models With _500 Likes Created in {year} - License Key.png"))

# ----------------------------------------
#
# ----------------------------------------

with open(output_json, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=4)


