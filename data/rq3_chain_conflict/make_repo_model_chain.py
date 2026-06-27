import json

# make supply chain between repo model and dataset

def load_json(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        return json.load(file)


def find_model(model_id, model_file, model_mapping):
    if model_id in model_mapping:
        model_id = model_mapping[model_id]
    for model in model_file:
        if model['id'] == model_id:
            return model
    print(f"not found: {model_id}")
    return None

# repo -> model
def create_chains(final_result, model_file, model_mapping):
    chains = []
    repo_no_model = 0
    repo_no_chain = []

    for repo_id, model_ids in final_result.items():
        repo_chains = []

        for model_id in model_ids:
            model = find_model(model_id, model_file, model_mapping)
            if not model:
                continue
            chain = f"{repo_id} -> {model_id}"
            chains.append(chain)
            repo_chains.append(chain)

        if not repo_chains:
            repo_no_model += 1
            repo_no_chain.append(repo_id)

    return chains, repo_no_model, repo_no_chain


def save_no_chain_repos(repo_no_chain, output_dir):
    with open(f'{output_dir}/no_chain_repos.txt', 'w') as file:
        for repo_id in repo_no_chain:
            file.write(repo_id + '\n')

def save_chains_to_file(chains, output_dir):
    chains = list(set(chains))
    length_dict = {}

    for chain in chains:
        length = chain.count('->')
        if length not in length_dict:
            length_dict[length] = []
        length_dict[length].append(chain)

    for length, chain_list in length_dict.items():
        with open(f'{output_dir}/chain_length_{length + 1}.txt', 'w') as file:
            for chain in chain_list:
                file.write(chain + '\n')

    with open(f'{output_dir}/chain_summary.txt', 'w') as file:
        for chain in chains:
            file.write(chain + '\n')

def print_statistics(chains, repo_no_model):
    total_chains = len(chains)
    chain_lengths = {}

    for chain in chains:
        length = chain.count('->')
        chain_lengths[length] = chain_lengths.get(length, 0) + 1

    print(f"all chain num: {total_chains}")
    print(f"different long chain: {chain_lengths}")
    print(f"cant be chain repo: {repo_no_model}")


def main():
    final_result = load_json('../repo_model_12180.json')
    model_file = load_json('../matched_models_3988.json')
    model_mapping = load_json('../mismatch_dict_model.json')

    chains, repo_no_model, repo_no_chain = create_chains(final_result, model_file, model_mapping)

    save_chains_to_file(chains, './')
    save_no_chain_repos(repo_no_chain, './')
    print_statistics(chains, repo_no_model)

if __name__ == '__main__':
    main()
