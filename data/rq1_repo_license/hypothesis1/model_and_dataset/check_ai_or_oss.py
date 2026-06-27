import json


with open("model_and_dataset/dataset_license_stats_708.json", "r", encoding="utf-8") as f:
    data = json.load(f)
with open("key_to_spdx.json", "r", encoding="utf-8") as f:
    key_to_spdx = json.load(f)

with open("ai_license_daxie.json", "r", encoding="utf-8") as f:
    ai_license_daxie = json.load(f)

# 处理逻辑
for item in data:
    new_labels = []
    group_ids = []
    for label in item["labels"]:
        if label in key_to_spdx:
            new_labels.append(key_to_spdx[label])
            group_ids.append(0)
        elif label in ai_license_daxie:
            new_labels.append(ai_license_daxie[label])
            group_ids.append(1)
        else:
            new_labels.append(label)
            group_ids.append(-1)  #
    item["labels"] = new_labels
    item["group_ids"] = group_ids


# with open("../company/com/model_company_processed_2.json", "w", encoding="utf-8") as f:
#     json.dump(data, f, indent=4, ensure_ascii=False)
with open("model_and_dataset/dataset_license_stats_708_processed.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4, ensure_ascii=False)