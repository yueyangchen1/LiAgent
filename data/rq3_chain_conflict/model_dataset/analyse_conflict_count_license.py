import json
import ast
import pandas as pd
from collections import defaultdict


conflict_file = "conflict_pair_count.json"
conflict_detail_file = "conflict_pair_dict.json"
license_map_file = "../license_name_map.json"

output_format = "excel"
output_name = "conflict_pairs"
decimal_places = 4
# =====================================


def load_json(file_path):

    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def reverse_license_map(license_map):

    reverse = defaultdict(list)
    for orig_name, mapped_value in license_map.items():
        reverse[str(mapped_value)].append(orig_name)
    return reverse


def unmapped_name(mapped_id, reverse_map):

    mapped_id_str = str(mapped_id)
    names = reverse_map.get(mapped_id_str, [])
    if not names:
        return mapped_id_str
    return "|".join(sorted(names))


def process_conflict_data(conflict_dict, reverse_map):

    rows = []
    total_count = sum(conflict_dict.values())

    for k, cnt in conflict_dict.items():
        try:
            pair = ast.literal_eval(k)
            model_id, repo_id = pair
        except Exception:
            continue

        model_name = unmapped_name(model_id, reverse_map)
        repo_name = unmapped_name(repo_id, reverse_map)

        rows.append({
            "model_license": model_name,
            "repo_license": repo_name,
            "count": cnt,
            "percentage": (cnt / total_count) if total_count != 0 else 0.0
        })

    return rows, total_count


def process_term_conflicts(conflict_count_dict, conflict_detail_dict, reverse_map):

    term_counter = defaultdict(int)

    for k, cnt in conflict_count_dict.items():
        try:
            pair = ast.literal_eval(k)
            model_id, repo_id = pair
        except Exception:
            continue


        model_name = unmapped_name(model_id, reverse_map)
        repo_name = unmapped_name(repo_id, reverse_map)


        if k not in conflict_detail_dict:
            continue

        term_list = conflict_detail_dict[k]
        for term_info in term_list:

            if isinstance(term_info, dict):
                term = term_info.get("term")
            else:

                term = term_info

            if term:

                term_counter[term] += cnt

    # 转换为DataFrame
    df_terms = pd.DataFrame(
        [{"term": t, "conflict_count": c} for t, c in term_counter.items()]
    ).sort_values(by="conflict_count", ascending=False).reset_index(drop=True)

    return df_terms




def process_attitude_conflicts(conflict_detail_dict, conflict_count_dict):

    attitude_map = defaultdict(lambda: defaultdict(int))

    for k, detail_list in conflict_detail_dict.items():

        pair_count = conflict_count_dict.get(k, 1)


        if not isinstance(detail_list, list):
            continue


        for term_info in detail_list:

            if not isinstance(term_info, dict):
                continue

            term = term_info.get("term")
            att1 = term_info.get("license1_attitude")
            att2 = term_info.get("license2_attitude")

            if term is None or att1 is None or att2 is None:

                continue

            att_key = f"{att1}|{att2}"
            attitude_map[term][att_key] += pair_count


    rows = []
    for term, att_dict in attitude_map.items():
        for att_key, cnt in att_dict.items():
            rows.append({"term": term, "attitude_pair": att_key, "count": cnt})

    df_attitudes = pd.DataFrame(rows).sort_values(by=["term", "count"], ascending=[True, False]).reset_index(drop=True)

    return attitude_map, df_attitudes


# =============================================================


def main():

    conflict_dict = load_json(conflict_file)
    conflict_detail_dict = load_json(conflict_detail_file)
    license_map = load_json(license_map_file)


    reverse_map = reverse_license_map(license_map)


    rows, total_count = process_conflict_data(conflict_dict, reverse_map)


    df_pairs = pd.DataFrame(rows)
    df_pairs = df_pairs.sort_values(by="count", ascending=False).reset_index(drop=True)
    df_pairs["percentage_str"] = (df_pairs["percentage"] * 100).map(
        lambda x: f"{x:.{decimal_places}f}%"
    )
    df_pairs = df_pairs[["model_license", "repo_license", "count", "percentage_str"]]


    df_terms = process_term_conflicts(conflict_dict, conflict_detail_dict, reverse_map)


    attitude_map, df_attitudes = process_attitude_conflicts(conflict_detail_dict, conflict_dict)

    attitude_json_path = f"{output_name}_attitude_map.json"

    attitude_map_serializable = {term: dict(att_dict) for term, att_dict in attitude_map.items()}
    with open(attitude_json_path, "w", encoding="utf-8") as f:
        json.dump(attitude_map_serializable, f, ensure_ascii=False, indent=2)

    if output_format == "csv":
        pair_path = f"{output_name}_pairs.csv"
        term_path = f"{output_name}_terms.csv"
        att_path = f"{output_name}_attitude_pairs.csv"
        df_pairs.to_csv(pair_path, index=False, encoding="utf-8-sig")
        df_terms.to_csv(term_path, index=False, encoding="utf-8-sig")
        df_attitudes.to_csv(att_path, index=False, encoding="utf-8-sig")
    else:
        pair_path = f"{output_name}_pairs.xlsx"
        term_path = f"{output_name}_terms.xlsx"
        with pd.ExcelWriter(pair_path) as writer:
            df_pairs.to_excel(writer, index=False, sheet_name="license_pairs")
            df_terms.to_excel(writer, index=False, sheet_name="term_conflicts")
            df_attitudes.to_excel(writer, index=False, sheet_name="attitude_conflicts")


    print(f"✅ license pair: {pair_path}")
    print(f"✅ term conflict {term_path}")
    print(f"✅ attitude conflict map {attitude_json_path}")
    print(f"📊  count = {total_count}")
    print("\n📘 license conflict pair num")
    print(df_pairs.head(10))
    print("\n📕 term conflict num")
    print(df_terms.head(10))
    print("\n📗 Attitude conflict ：")
    print(df_attitudes.head(10))


if __name__ == "__main__":
    main()
