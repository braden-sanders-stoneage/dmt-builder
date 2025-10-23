from __future__ import annotations

import pandas as pd


def _ensure_str(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    out = df.copy()
    for c in cols:
        out[c] = out[c].fillna("").astype(str)
    return out


def build_variant_ud_tables(df11: pd.DataFrame, ud09_sort_map: dict[str, int] | None = None) -> dict[str, pd.DataFrame]:
    df11 = _ensure_str(df11, ["Company", "Key1", "Key2", "Key3", "Key4", "Key5"])

    ud11 = df11[["Company", "Key1", "Key2", "Key3", "Key4", "Key5"]].copy()

    ud10 = df11[["Company", "Key1", "Key2", "Key3", "Key5"]].copy()
    ud10 = ud10.rename(columns={"Key5": "Key4"})
    ud10["Key5"] = ""
    ud10 = ud10.drop_duplicates(subset=["Company", "Key1", "Key2", "Key3", "Key4"]).reset_index(drop=True)
    ud10 = ud10[["Company", "Key1", "Key2", "Key3", "Key4", "Key5"]]

    ud09 = ud10[["Company", "Key1", "Key2", "Key3"]].copy()
    ud09["Key4"] = ""
    ud09["Key5"] = ""
    ud09 = ud09.drop_duplicates(subset=["Company", "Key1", "Key2", "Key3"]).reset_index(drop=True)
    # Number01 sort order for dropdowns
    if ud09_sort_map:
        ud09["Number01"] = ud09["Key3"].map(ud09_sort_map)
    # assign default order for any missing/unmapped values
    if "Number01" not in ud09.columns:
        ud09["Number01"] = range(1, len(ud09) + 1)
    else:
        # fill any NaNs with sequential order after mapped max
        max_mapped = int(pd.to_numeric(ud09["Number01"], errors="coerce").fillna(0).max())
        missing_mask = ud09["Number01"].isna()
        if missing_mask.any():
            fill_vals = list(range(max_mapped + 1, max_mapped + 1 + missing_mask.sum()))
            ud09.loc[missing_mask, "Number01"] = fill_vals
    # ensure integer dtype
    ud09["Number01"] = pd.to_numeric(ud09["Number01"], errors="coerce").fillna(0).astype(int)
    ud09 = ud09[["Company", "Key1", "Key2", "Key3", "Key4", "Key5", "Number01"]]

    ud08 = ud09[["Company", "Key1", "Key2"]].copy()
    ud08["Key3"] = ""
    ud08["Key4"] = ""
    ud08["Key5"] = ""
    ud08["Character01"] = ud08["Key2"]
    ud08["Checkbox01"] = True
    ud08 = ud08.drop_duplicates(subset=["Company", "Key1", "Key2"]).reset_index(drop=True)
    ud08 = ud08[["Company", "Key1", "Key2", "Key3", "Key4", "Key5", "Character01", "Checkbox01"]]

    return {"UD11": ud11, "UD10": ud10, "UD09": ud09, "UD08": ud08}


def build_attribute_ud_tables(df11: pd.DataFrame, ud09_sort_map: dict[str, int] | None = None) -> dict[str, pd.DataFrame]:
    df11 = _ensure_str(df11, ["Company", "Key1", "Key2", "Key3", "Key4", "Key5"])

    ud11 = df11[["Company", "Key1", "Key2", "Key3", "Key4", "Key5"]].copy()

    ud10 = df11[["Company", "Key1", "Key2", "Key3"]].copy()
    ud10["Key4"] = ""
    ud10["Key5"] = ""
    ud10["Character01"] = ud10["Key3"]
    ud10["Checkbox01"] = True
    ud10 = ud10.drop_duplicates(subset=["Company", "Key1", "Key2", "Key3"]).reset_index(drop=True)
    ud10 = ud10[["Company", "Key1", "Key2", "Key3", "Key4", "Key5", "Character01", "Checkbox01"]]

    ud09 = df11[["Company", "Key1", "Key2"]].copy()
    ud09["Key3"] = ""
    ud09["Key4"] = ""
    ud09["Key5"] = ""
    ud09["Character01"] = ud09["Key2"]
    ud09["Checkbox01"] = True
    ud09["Checkbox02"] = True
    ud09["Checkbox03"] = True
    ud09["Checkbox04"] = True
    ud09["Checkbox05"] = True
    ud09 = ud09.drop_duplicates(subset=["Company", "Key1", "Key2"]).reset_index(drop=True)
    # Number01 sort order for dropdowns
    if ud09_sort_map:
        ud09["Number01"] = ud09["Key2"].map(ud09_sort_map)
    # assign default order for any missing/unmapped values
    if "Number01" not in ud09.columns:
        ud09["Number01"] = range(1, len(ud09) + 1)
    else:
        # fill any NaNs with sequential order after mapped max
        max_mapped = int(pd.to_numeric(ud09["Number01"], errors="coerce").fillna(0).max())
        missing_mask = ud09["Number01"].isna()
        if missing_mask.any():
            fill_vals = list(range(max_mapped + 1, max_mapped + 1 + missing_mask.sum()))
            ud09.loc[missing_mask, "Number01"] = fill_vals
    # ensure integer dtype
    ud09["Number01"] = pd.to_numeric(ud09["Number01"], errors="coerce").fillna(0).astype(int)
    ud09 = ud09[[
        "Company", "Key1", "Key2", "Key3", "Key4", "Key5",
        "Character01", "Checkbox01", "Checkbox02", "Checkbox03", "Checkbox04", "Checkbox05", "Number01",
    ]]

    return {"UD11": ud11, "UD10": ud10, "UD09": ud09}


def build_part_table(df11: pd.DataFrame, variant_parent: str, website: str, is_new: bool, part_desc: str, prod_code: str) -> pd.DataFrame:
    df11 = _ensure_str(df11, ["Company", "Key2", "Key4"])  # only the needed columns

    rows = []

    if is_new:
        first_key2 = df11["Key2"].iloc[0] if not df11.empty else ""
        rows.append({
            "Company": "SAINC",
            "PartNum": variant_parent,
            "Character05": variant_parent,
            "Character06": f"{variant_parent} COPY NEEDED",
            "Character08": f"{variant_parent} COPY NEEDED",
            "Checkbox11": True,
            "Character10": first_key2,
            "Character11": "",
            "Character12": "show",
            "Character13": website,
            # New part defaults (parent)
            "PartDescription": part_desc,
            "ClassID": "FG",
            "ProdCode": prod_code,
            "UserChar1": "Introduction",
        })

    child = df11[["Company", "Key2", "Key4"]].rename(columns={"Key4": "PartNum"}).copy()
    child = child[child["PartNum"].astype(str) != ""]
    child = child.drop_duplicates(subset=["Company", "PartNum"]).reset_index(drop=True)
    if not child.empty:
        child["Character05"] = child["PartNum"]
        child["Character06"] = ""
        child["Character08"] = ""
        child["Checkbox11"] = True
        child["Character10"] = child["Key2"]
        child["Character11"] = variant_parent
        child["Character12"] = "show"
        child["Character13"] = website
        if is_new:
            # New part defaults (children)
            child["PartDescription"] = part_desc
            child["ClassID"] = "FG"
            child["ProdCode"] = prod_code
            child["UserChar1"] = "Introduction"
        child = child[[
            "Company", "PartNum",
            # Optional new part block (will be added later if requested)
            "Character05", "Character06", "Character08",
            "Checkbox11", "Character10", "Character11", "Character12", "Character13",
            *(["PartDescription", "ClassID", "ProdCode", "UserChar1"] if is_new else []),
        ]]
        rows.extend(child.to_dict(orient="records"))

    base_cols = [
        "Company", "PartNum",
        "Character05", "Character06", "Character08",
        "Checkbox11", "Character10", "Character11", "Character12", "Character13",
    ]
    extra_cols = ["PartDescription", "ClassID", "ProdCode", "UserChar1"] if is_new else []
    all_cols = base_cols + extra_cols
    df_part = pd.DataFrame(rows, columns=all_cols)
    return df_part


def build_category_ud08(company: str, website: str, category_string: str) -> pd.DataFrame:
    parent = "-".join([seg for seg in str(category_string).split("-") if seg][: -1]) if "-" in str(category_string) else ""
    df = pd.DataFrame([
        {
            "Company": company or "SAINC",
            "Key1": "Category",
            "Key2": website,
            "Key3": category_string,
            "Key4": parent,
            "Key5": "",
            "Character01": "COPY NEEDED",
            "Character04": "COPY NEEDED",
        }
    ])
    return df[["Company", "Key1", "Key2", "Key3", "Key4", "Key5", "Character01", "Character04"]]


def build_category_ud11_for_parent(company: str, parent_part_num: str, website: str, category_string: str) -> pd.DataFrame:
    if not company:
        company = "SAINC"
    data = [{
        "Company": company,
        "Key1": "Category",
        "Key2": website,
        "Key3": category_string,
        "Key4": parent_part_num,
        "Key5": "",
    }]
    return pd.DataFrame(data, columns=["Company", "Key1", "Key2", "Key3", "Key4", "Key5"])


def build_single_pdp_part(company: str, part_id: str, is_new: bool, part_desc: str, prod_code: str, website: str) -> pd.DataFrame:
    if not company:
        company = "SAINC"
    
    row = {
        "Company": company,
        "PartNum": part_id,
        "Character05": part_id,
        "Character06": "",
        "Character08": "",
        "Checkbox11": True,
        "Character10": "",
        "Character11": "",
        "Character12": "show",
        "Character13": website,
    }
    
    if is_new:
        row["PartDescription"] = part_desc
        row["ClassID"] = "FG"
        row["ProdCode"] = prod_code
        row["UserChar1"] = "Introduction"
    
    base_cols = [
        "Company", "PartNum",
        "Character05", "Character06", "Character08",
        "Checkbox11", "Character10", "Character11", "Character12", "Character13",
    ]
    extra_cols = ["PartDescription", "ClassID", "ProdCode", "UserChar1"] if is_new else []
    all_cols = base_cols + extra_cols
    
    return pd.DataFrame([row], columns=all_cols)


