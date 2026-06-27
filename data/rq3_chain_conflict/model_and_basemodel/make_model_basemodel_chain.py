import json


def load_json(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        return json.load(file)


def find_dataset(dataset_id, dataset_mapping, dataset_file):
    if dataset_id in dataset_mapping:
        dataset_id = dataset_mapping[dataset_id]
    for dataset in dataset_file:
        if dataset['id'] == dataset_id:
            return dataset
    return None


def create_model_dataset_chains(model_file, dataset_file, dataset_mapping):
    chains = []
    model_no_dataset = 0

    for model in model_file:
        model_id = model['id']
        model_datasets = []

        for tag in model.get('tags', []):
            if tag.startswith('dataset:'):
                dataset_id = tag.split(':', 1)[1]
                dataset = find_dataset(dataset_id, dataset_mapping, dataset_file)
                if dataset:
                    model_datasets.append(dataset['id'])

        if model_datasets:
            for dataset_id in model_datasets:
                chains.append(f"{model_id} -> {dataset_id}")
        else:
            model_no_dataset += 1

    return chains, model_no_dataset



def save_chains(chains, output_path):
    seen = set()
    duplicates = []

    for chain in chains:
        if chain in seen:
            duplicates.append(chain)
        else:
            seen.add(chain)

    if duplicates:
        print(f"find {len(duplicates)} repeat chain：")
        for dup in duplicates:
            print(f"repeat chain: {dup}")
    else:
        print("no repeat。")

    chains = list(seen)
    print(f"all chain: {len(chains)}")





def print_statistics(chains, model_no_dataset):
    print(f"all chain:{len(chains)}")



def main():
    model_file = load_json('../matched_models_3988.json')
    dataset_file = load_json('../matched_datasets_708.json')
    dataset_mapping = load_json('../merged_mismatch_dict_dataset_new.json')

    chains, model_no_dataset = create_model_dataset_chains(model_file, dataset_file, dataset_mapping)

    save_chains(chains, 'chain_summary.txt')
    print_statistics(chains, model_no_dataset)

if __name__ == '__main__':
    main()
