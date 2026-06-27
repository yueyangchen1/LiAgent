import json
from collections import Counter
from datetime import datetime
# run this file you can get the license distribution of company model and individual model and different tast distribution

model_metadata_file = 'matched_models_3988.json'
output_json = 'model_license_stats_extended.json'
company_authors_file = 'company_owner_id.txt'
# from hugging face
model_task_file = 'task/model_task.json'

with open(company_authors_file, 'r', encoding='utf-8') as f:
    company_authors = set(line.strip().lower() for line in f if line.strip())

with open(model_task_file, 'r', encoding='utf-8') as f:
    task_map = json.load(f)


with open(model_metadata_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

all_models = []
models_by_task_group = {}
company_models = []
personal_models = []

for model in data:
    model_id = model.get('id', '')
    author = model_id.split('/')[0].lower() if '/' in model_id else 'unknown'
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

    pipeline_tag = model.get('pipeline_tag', None)

    entry = {
        'id': model_id,
        'author': author,
        'likes': likes,
        'year': year,
        'license': license_key,
        'pipeline_tag': pipeline_tag
    }

    all_models.append(entry)

    if author in company_authors:
        company_models.append(entry)
    else:
        personal_models.append(entry)

    matched_group = None
    if pipeline_tag:
        for group, tags in task_map.items():
            if pipeline_tag in tags:
                matched_group = group
                break
        if matched_group:
            models_by_task_group.setdefault(matched_group, []).append(entry)
        else:
            models_by_task_group.setdefault('Other Task Tags', []).append(entry)
    else:
        models_by_task_group.setdefault('No Pipeline Tag', []).append(entry)

print(f"Total models loaded: {len(all_models)}")
print(f"Company models: {len(company_models)}")
print(f"Personal models: {len(personal_models)}")



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



results = []


results.append(count_license_distribution(all_models, "All Models - License Key.png"))




results.append(count_license_distribution(company_models, "Company Models - License Key.png"))
results.append(count_license_distribution(personal_models, "Personal Models - License Key.png"))

#
for group, models in models_by_task_group.items():
    results.append(count_license_distribution(models, f"Models In Task Group: {group} - License Key.png"))

# ----------------------------------------
#
# ----------------------------------------

with open(output_json, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=4)

print(f"\n📁 {output_json}")
