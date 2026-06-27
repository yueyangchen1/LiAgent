import json
import numpy as np



company_file = 'make_chart/model_and_dataset/model_and_dataset_3.json'
non_company_file = 'make_chart/repo_chart/output_with_groups.json'


def load_json(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data[0]

company_data = load_json(company_file)
non_company_data = load_json(non_company_file)


company_licenses = company_data['labels']
non_company_licenses = non_company_data['labels']

all_licenses = sorted(set(company_licenses) | set(non_company_licenses))


def build_count_map(labels, values):
    return {label: value for label, value in zip(labels, values)}

company_map = build_count_map(company_licenses, company_data['values'])
non_company_map = build_count_map(non_company_licenses, non_company_data['values'])

company_counts = [company_map.get(lic, 0) for lic in all_licenses]
non_company_counts = [non_company_map.get(lic, 0) for lic in all_licenses]

print("License Types:", all_licenses)
print("Company Counts:", company_counts)
print("Non-Company Counts:", non_company_counts)

observed = np.array([company_counts, non_company_counts])  # shape = (2, num_licenses)

def chi2_stat(counts):
    total = counts.sum()
    row_sums = counts.sum(axis=1, keepdims=True)
    col_sums = counts.sum(axis=0, keepdims=True)
    expected = row_sums @ col_sums / total
    with np.errstate(divide='ignore', invalid='ignore'):
        chi2 = (counts - expected)**2 / expected
        chi2[np.isnan(chi2)] = 0
    return chi2.sum()


actual_stat = chi2_stat(observed)


data = []
for i, lic in enumerate(all_licenses):
    data.extend([(lic, 0)] * company_counts[i])
    data.extend([(lic, 1)] * non_company_counts[i])

data = np.array(data, dtype=object)


n_perm = 1000
perm_stats = []

for _ in range(n_perm):
    shuffled_labels = np.random.permutation(data[:,1])
    shuffled_data = np.column_stack((data[:,0], shuffled_labels))

    perm_counts_company = []
    perm_counts_noncompany = []
    for lic in all_licenses:
        perm_counts_company.append(np.sum((shuffled_data[:,0] == lic) & (shuffled_data[:,1] == 0)))
        perm_counts_noncompany.append(np.sum((shuffled_data[:,0] == lic) & (shuffled_data[:,1] == 1)))
    perm_counts = np.array([perm_counts_company, perm_counts_noncompany])

    perm_stat = chi2_stat(perm_counts)
    perm_stats.append(perm_stat)

perm_stats = np.array(perm_stats)


p_value = np.mean(perm_stats >= actual_stat)


print(f"Actual chi-square statistic {actual_stat:.4f}")
print(f"Number of permutations: {n_perm}")
print(f"p : {p_value:.4e}")

N = observed.sum()
df = min(observed.shape[0] - 1, observed.shape[1] - 1)
cramers_v = np.sqrt(actual_stat / (N * df))

print(f"Cramér's V: {cramers_v:.2f}")
