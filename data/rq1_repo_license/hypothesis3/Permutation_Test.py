import json
import numpy as np
import itertools


file_list = [
    'license_distribution/Audio.json',
    'license_distribution/Computer_Vision.json',
    'license_distribution/Multimodal.json',
    'license_distribution/Natural_Language_Processing.json',
   'license_distribution/Reinforcement_Learning.json',
    'license_distribution/No_Task.json',
    'license_distribution/Other.json',

]

def load_json(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data[0]  # 取第一个字典


def build_count_map(labels, values):
    return {label: value for label, value in zip(labels, values)}

def chi2_stat(counts):
    total = counts.sum()
    row_sums = counts.sum(axis=1, keepdims=True)
    col_sums = counts.sum(axis=0, keepdims=True)
    expected = row_sums @ col_sums / total
    with np.errstate(divide='ignore', invalid='ignore'):
        chi2 = (counts - expected) ** 2 / expected
        chi2[np.isnan(chi2)] = 0
    return chi2.sum()


data_map = {}
for file in file_list:
    data = load_json(file)
    data_map[file] = {
        'labels': data['labels'],
        'values': data['values'],
        'map': build_count_map(data['labels'], data['values'])
    }


for file_a, file_b in itertools.combinations(file_list, 2):
    print(f"\n===  {file_a} vs {file_b} ===")

    data_a = data_map[file_a]
    data_b = data_map[file_b]

    all_licenses = sorted(set(data_a['labels']) | set(data_b['labels']))

    counts_a = [data_a['map'].get(lic, 0) for lic in all_licenses]
    counts_b = [data_b['map'].get(lic, 0) for lic in all_licenses]

    observed = np.array([counts_a, counts_b])

    actual_stat = chi2_stat(observed)


    data = []
    for i, lic in enumerate(all_licenses):
        data.extend([(lic, 0)] * counts_a[i])
        data.extend([(lic, 1)] * counts_b[i])
    data = np.array(data, dtype=object)


    n_perm = 1000
    perm_stats = []

    for _ in range(n_perm):
        shuffled_labels = np.random.permutation(data[:,1])
        shuffled_data = np.column_stack((data[:,0], shuffled_labels))

        perm_counts_a = []
        perm_counts_b = []
        for lic in all_licenses:
            perm_counts_a.append(np.sum((shuffled_data[:,0] == lic) & (shuffled_data[:,1] == 0)))
            perm_counts_b.append(np.sum((shuffled_data[:,0] == lic) & (shuffled_data[:,1] == 1)))
        perm_counts = np.array([perm_counts_a, perm_counts_b])

        perm_stat = chi2_stat(perm_counts)
        perm_stats.append(perm_stat)

    perm_stats = np.array(perm_stats)
    p_value = np.mean(perm_stats >= actual_stat)

    N = observed.sum()
    df = min(observed.shape[0] - 1, observed.shape[1] - 1)
    cramers_v = np.sqrt(actual_stat / (N * df))

    print(f"Actual Chi-square Statistic: {actual_stat:.4f}")
    print(f"Number of permutations: {n_perm}")
    print(f"p : {p_value:.4e}")
    print(f"Cramér's V: {cramers_v:.2f}")
