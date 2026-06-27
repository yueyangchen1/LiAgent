import json
from collections import defaultdict


def load_json(file_path):

    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def build_model_dict(model_data):

    return {model["id"]: model for model in model_data}


def find_base_models(model):

    base_models = []
    for tag in model.get("tags", []):
        if tag.startswith("base_model:"):
            base_models.append(tag.split("base_model:")[-1])
    return base_models


def build_model_chain(model_id, model_dict, mismatch_dict, visited, current_chain):

    if model_id in visited:
        return []
    visited.add(model_id)

    model = model_dict.get(model_id)
    if not model:
        return [[model_id]]

    base_models = find_base_models(model)


    mapped_base_models = []
    for base_id in base_models:
        if base_id not in model_dict and base_id in mismatch_dict:
            base_id = mismatch_dict[base_id]
        if base_id == model_id:
            self_reference_count[0] += 1
            continue
        mapped_base_models.append(base_id)
    mapped_base_models = list(set(mapped_base_models))  # 去重

    if not mapped_base_models:
        return [[model_id]]

    all_chains = []
    for base_model_id in mapped_base_models:
        if base_model_id in current_chain:
            print(f"回路：{current_chain}")
            loop_count[0] += 1
            continue
        if base_model_id in model_dict:
            sub_chains = build_model_chain(
                base_model_id,
                model_dict,
                mismatch_dict,
                visited.copy(),
                current_chain | {base_model_id}
            )
            for sub_chain in sub_chains:
                all_chains.append([model_id] + sub_chain)
    return all_chains


def main():

    full_model_data = load_json("merged_model_4_unique.json")
    mismatch_dict = load_json("mismatch_dict_model.json")
    matched_model_data = load_json("matched_models_3988.json")

    full_model_dict = build_model_dict(full_model_data)
    matched_model_dict = build_model_dict(matched_model_data)

    global self_reference_count, loop_count
    self_reference_count = [0]
    loop_count = [0]


    chains = []
    for model_id in matched_model_dict.keys():
        visited = set()
        model_chains = build_model_chain(model_id, full_model_dict, mismatch_dict, visited, {model_id})
        for chain in model_chains:
            if len(chain) > 1:
                chains.append(chain)


    chain_lengths = [len(chain) for chain in chains]
    length_distribution = defaultdict(int)
    for length in chain_lengths:
        length_distribution[length] += 1

    print(f"all chain: {len(chains)} ")
    print(f" find {self_reference_count[0]} basemodel == model")
    for length, count in sorted(length_distribution.items()):
        print(f"  length: {length}：{count} ")


    summary_file = "chains_summary.txt"
    with open(summary_file, "w", encoding="utf-8") as summary:
        for length, count in sorted(length_distribution.items()):
            filename = f"chains_length_{length}.txt"
            with open(filename, "w", encoding="utf-8") as f:
                for chain in chains:
                    if len(chain) == length:
                        line = " -> ".join(chain)
                        f.write(line + "\n")
                        summary.write(line + "\n")




if __name__ == "__main__":
    main()
