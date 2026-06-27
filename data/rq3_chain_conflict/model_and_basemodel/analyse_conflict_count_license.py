import json
import pandas as pd
from collections import defaultdict

pair_file = "basemodel_model_conflictions.json"
conflict_detail_file = "conflict_pair_dict.json"
license_map_file = "license_name_map.json"

output_format = "excel"
output_name = "base_model_model_license_pairs"
decimal_places = 4
# =====================================


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_forward_map(license_map):

    fm = {}
    for orig, mapped in license_map.items():
        if orig is None:
            continue
        fm[orig.lower()] = str(mapped)
    return fm


def normalize_name(n):
    return n.strip().lower() if isinstance(n, str) else str(n)


def make_pair_key(a, b):

    return str((str(a), str(b)))


def process_pairs_count(pair_dict):

    combo_count = defaultdict(int)
    for key, value in pair_dict.items():
        # value 期望是 [base_license, model_license]
        if not isinstance(value, list) or len(value) != 2:
            continue
        base_license, model_license = value
        base_norm = normalize_name(base_license)
        model_norm = normalize_name(model_license)
        combo_count[(base_norm, model_norm)] += 1
    return combo_count


def process_term_conflicts_from_detail(combo_count, conflict_detail_dict, forward_map, collect_missing_pairs=False):

    term_counter = defaultdict(int)
    missing_pairs = []

    for (base_norm, model_norm), combo_cnt in combo_count.items():

        mapped_base = forward_map.get(base_norm, base_norm)
        mapped_model = forward_map.get(model_norm, model_norm)


        key1 = make_pair_key(mapped_base, mapped_model)

        if key1 not in conflict_detail_dict:

            if collect_missing_pairs:
                missing_pairs.append({"base": base_norm, "model": model_norm, "mapped_key": key1, "count": combo_cnt})
            continue

        detail_entry = conflict_detail_dict[key1]


        if not isinstance(detail_entry, list):
            continue

        for term_info in detail_entry:

            term = None
            if isinstance(term_info, dict):
                term = term_info.get("term") or term_info.get("Term") or term_info.get("name")
            elif isinstance(term_info, str):
                term = term_info
            if term is None:
                continue
            term_norm = normalize_name(term)
            term_counter[term_norm] += combo_cnt

    df_terms = pd.DataFrame(
        [{"term": t, "conflict_count": c} for t, c in term_counter.items()]
    ).sort_values(by="conflict_count", ascending=False).reset_index(drop=True)

    return df_terms, missing_pairs



def process_attitude_conflicts_from_detail(combo_count, conflict_detail_dict, forward_map):

    attitude_map = defaultdict(lambda: defaultdict(int))

    for (base_norm, model_norm), combo_cnt in combo_count.items():
        mapped_base = forward_map.get(base_norm, base_norm)
        mapped_model = forward_map.get(model_norm, model_norm)

        key1 = make_pair_key(mapped_base, mapped_model)
        if key1 not in conflict_detail_dict:

            continue

        detail_entry = conflict_detail_dict[key1]
        if not isinstance(detail_entry, list):
            continue

        for term_info in detail_entry:
            if not isinstance(term_info, dict):
                continue
            term = term_info.get("term") or term_info.get("Term") or term_info.get("name")
            att1 = term_info.get("license1_attitude")
            att2 = term_info.get("license2_attitude")
            if term is None or att1 is None or att2 is None:

                continue
            term_norm = normalize_name(term)
            att_key = f"{att1}|{att2}"  # 顺序敏感
            attitude_map[term_norm][att_key] += combo_cnt


    rows = []
    for term, att_dict in attitude_map.items():
        for att_key, cnt in att_dict.items():
            rows.append({"term": term, "attitude_pair": att_key, "count": cnt})

    df_attitudes = pd.DataFrame(rows).sort_values(by=["term", "count"], ascending=[True, False]).reset_index(drop=True)

    attitude_map_serializable = {term: dict(att_dict) for term, att_dict in attitude_map.items()}

    return attitude_map_serializable, df_attitudes


# =============================================================


def main():

    pair_dict = load_json(pair_file)
    conflict_detail_dict = load_json(conflict_detail_file)
    license_map = load_json(license_map_file)


    combo_count = process_pairs_count(pair_dict)
    total_count = sum(combo_count.values()) if combo_count else 0


    rows = []
    for (base_norm, model_norm), cnt in combo_count.items():
        rows.append({
            "base_model_license": base_norm,
            "model_license": model_norm,
            "count": cnt,
            "percentage": (cnt / total_count) if total_count else 0.0
        })
    df_pairs = pd.DataFrame(rows).sort_values(by="count", ascending=False).reset_index(drop=True)
    df_pairs["percentage_str"] = (df_pairs["percentage"] * 100).map(lambda x: f"{x:.{decimal_places}f}%")
    df_pairs = df_pairs[["base_model_license", "model_license", "count", "percentage_str"]]


    forward_map = build_forward_map(license_map)


    df_terms, missing_pairs = process_term_conflicts_from_detail(combo_count, conflict_detail_dict, forward_map, collect_missing_pairs=True)


    attitude_map, df_attitudes = process_attitude_conflicts_from_detail(combo_count, conflict_detail_dict, forward_map)


    if output_format == "csv":
        pair_path = f"{output_name}_pairs.csv"
        term_path = f"{output_name}_terms.csv"
        att_path = f"{output_name}_attitude_pairs.csv"
        missing_path = f"{output_name}_missing_pairs.json"

        df_pairs.to_csv(pair_path, index=False, encoding="utf-8-sig")
        df_terms.to_csv(term_path, index=False, encoding="utf-8-sig")
        df_attitudes.to_csv(att_path, index=False, encoding="utf-8-sig")


        with open(missing_path, "w", encoding="utf-8") as f:
            json.dump(missing_pairs, f, ensure_ascii=False, indent=2)


        attitude_json_path = f"{output_name}_attitude_map.json"
        with open(attitude_json_path, "w", encoding="utf-8") as f:
            json.dump(attitude_map, f, ensure_ascii=False, indent=2)

    else:
        pair_path = f"{output_name}_pairs.xlsx"
        term_path = f"{output_name}_terms.xlsx"
        attitude_json_path = f"{output_name}_attitude_map.json"
        missing_path = f"{output_name}_missing_pairs.json"

        with pd.ExcelWriter(pair_path) as writer:
            df_pairs.to_excel(writer, index=False, sheet_name="license_pairs")
            df_terms.to_excel(writer, index=False, sheet_name="term_conflicts")
            df_attitudes.to_excel(writer, index=False, sheet_name="attitude_conflicts")

        with open(attitude_json_path, "w", encoding="utf-8") as f:
            json.dump(attitude_map, f, ensure_ascii=False, indent=2)
        with open(missing_path, "w", encoding="utf-8") as f:
            json.dump(missing_pairs, f, ensure_ascii=False, indent=2)




if __name__ == "__main__":
    main()
