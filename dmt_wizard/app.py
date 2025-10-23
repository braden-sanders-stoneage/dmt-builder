from __future__ import annotations

import os
import sys
from typing import List, Tuple, Dict, Set
import time

import pandas as pd

from .io_utils import (
    pick_excel_file,
    pick_output_folder,
    read_excel_normalized,
    ensure_output_dir,
    write_csv,
    get_stem_and_dir,
    sanitize_filename,
)
from .builders import (
    build_variant_ud_tables,
    build_attribute_ud_tables,
    build_part_table,
    build_category_ud08,
    build_category_ud11_for_parent,
    build_single_pdp_part,
)
from .playlist import build_playlist_df, build_playlist_name

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress
from InquirerPy import inquirer


console = Console()


def prompt_mode() -> str:
    choice = inquirer.select(
        message="Select mode:",
        choices=[
            {"name": "Standard Mode", "value": "standard"},
            {"name": "New PDP Mode", "value": "new_pdp"},
        ],
        default="standard",
    ).execute()
    return choice


def detect_type_from_df(df11: pd.DataFrame) -> str:
    key1_series = df11["Key1"].dropna().astype(str)
    if key1_series.empty:
        return "variant"
    first = key1_series.iloc[0].strip().lower()
    if first.startswith("attr"):
        return "attribute"
    return "variant"


def prompt_operation() -> str:
    choice = inquirer.select(
        message="Select operation:",
        choices=[
            {"name": "Add only", "value": "add"},
            {"name": "Delete only", "value": "delete"},
            {"name": "Delete & Add", "value": "both"},
        ],
        default="add",
    ).execute()
    return choice


def prompt_type(detected: str) -> str:
    choice = inquirer.select(
        message=f"Detected type: {detected.capitalize()}. Confirm or override:",
        choices=[
            {"name": "Variant", "value": "variant"},
            {"name": "Attribute", "value": "attribute"},
        ],
        default=detected,
    ).execute()
    return choice


def prompt_tables(import_type: str) -> Set[str]:
    default_checked = ["UD09", "UD10", "UD11"] if import_type == "attribute" else ["UD08", "UD09", "UD10", "UD11"]
    choices = [
        {"name": "UD08", "value": "UD08", "enabled": "UD08" in default_checked},
        {"name": "UD09", "value": "UD09", "enabled": "UD09" in default_checked},
        {"name": "UD10", "value": "UD10", "enabled": "UD10" in default_checked},
        {"name": "UD11", "value": "UD11", "enabled": "UD11" in default_checked},
    ]
    selected = inquirer.checkbox(message="Select tables to include in playlist:", choices=choices).execute()
    return set(selected)


def prompt_part_details() -> Tuple[str, bool, str, str, str]:
    variant_parent = inquirer.text(message="Variant Parent Part ID:").execute().strip()
    is_new = inquirer.confirm(message="Is this a new part number?", default=True).execute()
    
    part_desc = ""
    prod_code = ""
    if is_new:
        part_desc = inquirer.text(message="PartDescription:").execute().strip()
        prod_code = inquirer.text(message="ProdCode:").execute().strip()
    
    website = inquirer.select(
        message="Website:",
        choices=["SA", "SW", "SA~SW"],
        default="SA",
    ).execute()
    
    return variant_parent, is_new, part_desc, prod_code, website


def prompt_variant_ud09_sort(keys3: List[str]) -> Dict[str, int]:
    unique_vals = sorted({k for k in keys3 if k is not None and str(k).strip() != ""})
    if not unique_vals:
        return {}

    console.print(Panel.fit("Configure UD09 sort order (Number01) for dropdown values.", border_style="cyan"))

    mapping: Dict[str, int] = {}
    
    def render_status() -> None:
        tbl = Table(show_lines=False)
        tbl.add_column("Value", style="cyan", no_wrap=True)
        tbl.add_column("Number01", style="white")
        for v in unique_vals:
            assigned = mapping.get(v)
            tbl.add_row(v, "" if assigned is None else str(assigned))
        console.print(Panel.fit(tbl, title="UD09 values", border_style="blue"))

    for val in unique_vals:
        try:
            render_status()
            order_str = inquirer.text(
                message=f"Order for '{val}':",
                validate=lambda r: r.isdigit() and int(r) >= 1,
                invalid_message="Enter a positive integer",
            ).execute()
            mapping[val] = int(order_str)
        except Exception:
            # fallback sequential if user escapes
            mapping[val] = len(mapping) + 1
    return mapping


def prompt_attribute_ud09_sort(keys2: List[str]) -> Dict[str, int]:
    unique_vals = sorted({k for k in keys2 if k is not None and str(k).strip() != ""})
    if not unique_vals:
        return {}

    console.print(Panel.fit("Configure UD09 sort order (Number01) for attribute dropdown values.", border_style="cyan"))

    mapping: Dict[str, int] = {}
    
    def render_status() -> None:
        tbl = Table(show_lines=False)
        tbl.add_column("Value", style="cyan", no_wrap=True)
        tbl.add_column("Number01", style="white")
        for v in unique_vals:
            assigned = mapping.get(v)
            tbl.add_row(v, "" if assigned is None else str(assigned))
        console.print(Panel.fit(tbl, title="UD09 values", border_style="blue"))

    for val in unique_vals:
        try:
            render_status()
            order_str = inquirer.text(
                message=f"Order for '{val}':",
                validate=lambda r: r.isdigit() and int(r) >= 1,
                invalid_message="Enter a positive integer",
            ).execute()
            mapping[val] = int(order_str)
        except Exception:
            # fallback sequential if user escapes
            mapping[val] = len(mapping) + 1
    return mapping


def show_summary(
    operation: str,
    files: List[str],
    import_type: str,
    include_tables: Set[str],
    part_enabled: bool,
    variant_parent: str,
    website: str,
    is_new: bool,
    part_desc: str,
    prod_code: str,
    cat_enabled: bool,
    cat_site: str,
    cat_list: List[str],
    cat_is_new: bool,
) -> bool:
    table = Table(title="Summary", show_lines=False)
    table.add_column("Field", style="cyan", no_wrap=True)
    table.add_column("Value", style="white")

    table.add_row("Operation", operation)
    table.add_row("File(s)", "\n".join(files))
    table.add_row("Type", import_type)
    table.add_row("Include Tables", ", ".join(sorted(include_tables)))
    if import_type == "variant":
        table.add_row("Create Part?", "Yes" if part_enabled else "No")
        if part_enabled:
            table.add_row("Variant Parent", variant_parent)
            table.add_row("Part Website", website)
            table.add_row("New part?", "Yes" if is_new else "No")
            if is_new:
                table.add_row("PartDescription", part_desc or "(none)")
                table.add_row("ProdCode", prod_code or "(none)")
        # Category details
        table.add_row("Category?", "Yes" if cat_enabled else "No")
        if cat_enabled:
            table.add_row("Category Type", "New (UD08 + UD11)" if cat_is_new else "Existing (UD11 only)")
            table.add_row("Category Website", cat_site)
            cat_display = f"{len(cat_list)} categories" if len(cat_list) > 1 else cat_list[0] if cat_list else "(none)"
            table.add_row("Categories", cat_display)

    console.print(Panel.fit(table, title="Please confirm", border_style="green"))
    return inquirer.confirm(message="Proceed?", default=True).execute()


def celebrate_success(output_dir: str | None, playlist_path: str) -> None:
    console.print(Panel.fit(
        f"🎉 Success!\n\nOutput folder:\n- {output_dir}\nPlaylist:\n- {playlist_path}",
        border_style="green",
    ))
    # Big orange warning reminder
    warning_text = (
        "⚠ WARNING! Before importing, replace any 'COPY NEEDED' values in Categories_UD08 and Part!"
    )
    console.print(Panel.fit(warning_text, border_style="orange1"))
    part_warning = (
        "⚠ WARNING! Review Part fields (PartDescription, ClassID, ProdCode) and update if necessary before import."
    )
    console.print(Panel.fit(part_warning, border_style="orange1"))


def process_single(
    excel_path: str,
    import_type: str,
    include_tables: Set[str],
    create_part: bool,
    variant_parent: str,
    website: str,
    is_new: bool,
    part_desc: str,
    ud09_sort_map: Dict[str, int] | None,
    cat_opts: Dict[str, str] | None,
    prod_code: str,
) -> Tuple[str, Dict[str, str]]:
    df11 = read_excel_normalized(excel_path)
    stem, base_dir = get_stem_and_dir(excel_path)
    out_dir = ensure_output_dir(base_dir, f"{stem}_OUTPUT")

    written: Dict[str, str] = {}

    with Progress() as progress:
        task = progress.add_task("Building tables", total=5)

        # UD11
        df11_out = df11.copy()
        progress.update(task, advance=1)

        if import_type == "variant":
            dfs = build_variant_ud_tables(df11_out, ud09_sort_map)
        else:
            dfs = build_attribute_ud_tables(df11_out, ud09_sort_map)
        progress.update(task, advance=2)

        # Write selected tables
        for tbl_name, df_tbl in dfs.items():
            if tbl_name == "UD11" or tbl_name in include_tables:
                csv_path = os.path.join(out_dir, f"{stem}_{tbl_name}.csv")
                write_csv(df_tbl, csv_path)
                written[tbl_name] = csv_path
        progress.update(task, advance=1)

        # Part (variant + requested, only for add runs, handled by caller)
        if import_type == "variant" and create_part:
            df_part = build_part_table(df11_out, variant_parent, website, is_new, part_desc, prod_code)
            csv_path = os.path.join(out_dir, f"{stem}_Part.csv")
            write_csv(df_part, csv_path)
            written["Part"] = csv_path
        progress.update(task, advance=1)

    # Category files (outside progress so prompts are clean)
    if import_type == "variant" and cat_opts:
        cat_site = cat_opts.get("website", "").strip()
        cat_list = cat_opts.get("categories", [])
        cat_is_new = cat_opts.get("is_new", False)
        if cat_site and cat_list:
            company_val = df11_out["Company"].iloc[0] if not df11_out.empty else "SAINC"
            # UD08 category definition (only for new categories)
            if cat_is_new:
                df_cat08_list = [build_category_ud08(company_val, cat_site, cat_str) for cat_str in cat_list]
                df_cat08 = pd.concat(df_cat08_list, ignore_index=True)
                path08 = os.path.join(out_dir, f"{stem}_Categories_UD08.csv")
                write_csv(df_cat08, path08)
                written["UD08_Categories"] = path08

            # UD11 assignment (always created when working with categories)
            parent_part = variant_parent if variant_parent else inquirer.text(message="Parent Part ID for category:").execute().strip()
            df_cat11_list = [build_category_ud11_for_parent(company_val, parent_part, cat_site, cat_str) for cat_str in cat_list]
            df_cat11 = pd.concat(df_cat11_list, ignore_index=True)
            path11 = os.path.join(out_dir, f"{stem}_Categories_UD11.csv")
            write_csv(df_cat11, path11)
            written["UD11_Categories"] = path11

    return stem, written


def run_new_pdp_mode() -> None:
    console.print(Panel.fit("New PDP Mode", border_style="magenta"))
    
    part_id = inquirer.text(message="Part ID:").execute().strip()
    if not part_id:
        console.print("No Part ID provided. Exiting.", style="red")
        return
    
    is_new = inquirer.confirm(message="Is this a new part number?", default=True).execute()
    
    part_desc = ""
    prod_code = ""
    if is_new:
        part_desc = inquirer.text(message="PartDescription:").execute().strip()
        prod_code = inquirer.text(message="ProdCode:").execute().strip()
    
    website = inquirer.select(
        message="Website:",
        choices=["SA", "SW", "SA~SW"],
        default="SA",
    ).execute()
    
    cat_opts: Dict[str, str] | None = None
    if inquirer.confirm(message="Work with categories?", default=False).execute():
        cat_type = inquirer.select(
            message="Category type:",
            choices=[
                {"name": "New category (create UD08 + UD11)", "value": "new"},
                {"name": "Existing category (UD11 only)", "value": "existing"},
            ],
            default="new",
        ).execute()
        cat_site = inquirer.select(message="Website for category:", choices=["SA", "SW"], default="SA").execute()
        cat_input = inquirer.text(
            message="Category string(s) - paste multiple categories (one per line):",
            multiline=True
        ).execute().strip()
        cat_list = [cat.strip() for cat in cat_input.split("\n") if cat.strip()]
        cat_opts = {"website": cat_site, "categories": cat_list, "is_new": cat_type == "new"}
    
    cat_enabled = bool(cat_opts)
    cat_site = cat_opts.get("website", "") if cat_enabled else ""
    cat_list = cat_opts.get("categories", []) if cat_enabled else []
    cat_is_new = cat_opts.get("is_new", False) if cat_enabled else False
    
    table = Table(title="Summary", show_lines=False)
    table.add_column("Field", style="cyan", no_wrap=True)
    table.add_column("Value", style="white")
    table.add_row("Mode", "New PDP")
    table.add_row("Part ID", part_id)
    table.add_row("New part?", "Yes" if is_new else "No")
    if is_new:
        table.add_row("PartDescription", part_desc or "(none)")
        table.add_row("ProdCode", prod_code or "(none)")
    table.add_row("Website", website)
    table.add_row("Category?", "Yes" if cat_enabled else "No")
    if cat_enabled:
        table.add_row("Category Type", "New (UD08 + UD11)" if cat_is_new else "Existing (UD11 only)")
        table.add_row("Category Website", cat_site)
        cat_display = f"{len(cat_list)} categories" if len(cat_list) > 1 else cat_list[0] if cat_list else "(none)"
        table.add_row("Categories", cat_display)
    
    console.print(Panel.fit(table, title="Please confirm", border_style="green"))
    if not inquirer.confirm(message="Proceed?", default=True).execute():
        console.print("Cancelled.", style="yellow")
        return
    
    import os
    console.print(Panel.fit("Select output folder", border_style="yellow"))
    output_base = pick_output_folder(title="Select output folder")
    if not output_base:
        console.print("No folder selected. Exiting.", style="red")
        return
    
    part_id_safe = sanitize_filename(part_id)
    out_dir = ensure_output_dir(output_base, f"{part_id_safe}_OUTPUT")
    written: Dict[str, str] = {}
    
    company = "SAINC"
    df_part = build_single_pdp_part(company, part_id, is_new, part_desc, prod_code, website)
    part_path = os.path.join(out_dir, f"{part_id_safe}_Part.csv")
    write_csv(df_part, part_path)
    written["Part"] = part_path
    
    if cat_opts:
        cat_site = cat_opts.get("website", "").strip()
        cat_list = cat_opts.get("categories", [])
        cat_is_new = cat_opts.get("is_new", False)
        if cat_site and cat_list:
            if cat_is_new:
                df_cat08_list = [build_category_ud08(company, cat_site, cat_str) for cat_str in cat_list]
                df_cat08 = pd.concat(df_cat08_list, ignore_index=True)
                path08 = os.path.join(out_dir, f"{part_id_safe}_Categories_UD08.csv")
                write_csv(df_cat08, path08)
                written["UD08_Categories"] = path08
            
            df_cat11_list = [build_category_ud11_for_parent(company, part_id, cat_site, cat_str) for cat_str in cat_list]
            df_cat11 = pd.concat(df_cat11_list, ignore_index=True)
            path11 = os.path.join(out_dir, f"{part_id_safe}_Categories_UD11.csv")
            write_csv(df_cat11, path11)
            written["UD11_Categories"] = path11
    
    playlist_entries: List[Tuple[str, str]] = []
    for path in written.values():
        playlist_entries.append((path, "add"))
    
    df_playlist = build_playlist_df(playlist_entries, set())
    playlist_path = os.path.join(os.path.dirname(out_dir), f"ADD_{part_id_safe}_PLAYLIST.csv")
    df_playlist.to_csv(playlist_path, index=False, encoding='utf-8-sig')
    
    celebrate_success(out_dir, playlist_path)


def run() -> None:
    console.print(Panel.fit("DMT Builder Wizard", border_style="magenta"))

    mode = prompt_mode()
    
    if mode == "new_pdp":
        run_new_pdp_mode()
        return

    # First: source file selection
    console.print(Panel.fit("Select your source Excel file", border_style="yellow"))
    first_path = pick_excel_file(title="Select source Excel file")
    if not first_path:
        console.print("No file selected. Exiting.", style="red")
        return

    # Detect & confirm type using first file
    try:
        df11_detect = read_excel_normalized(first_path)
        detected = detect_type_from_df(df11_detect)
    except Exception:
        detected = "variant"
    import_type = prompt_type(detected)

    # Operation selection (after file so context exists)
    operation = prompt_operation()

    # Files list (may be expanded if 'both')
    files: List[str] = [first_path]
    if operation == "both":
        # Ask whether the first file is DELETE or ADD, then pick the other accordingly
        first_role = inquirer.select(
            message="How should the selected file be used?",
            choices=[
                {"name": "Use as DELETE file", "value": "delete"},
                {"name": "Use as ADD file", "value": "add"},
            ],
            default="delete",
        ).execute()
        if first_role == "delete":
            console.print(Panel.fit("Select the ADD Excel file", border_style="yellow"))
            add_path = pick_excel_file(title="Select ADD Excel file")
            if not add_path:
                console.print("No file selected. Exiting.", style="red")
                return
            files = [first_path, add_path]
        else:
            console.print(Panel.fit("Select the DELETE Excel file", border_style="yellow"))
            del_path = pick_excel_file(title="Select DELETE Excel file")
            if not del_path:
                console.print("No file selected. Exiting.", style="red")
                return
            files = [del_path, first_path]

    # Recompute df11_detect if needed (for 'both' we always base on first file)
    try:
        df11_detect = read_excel_normalized(files[0])
    except Exception:
        pass

    include_tables = prompt_tables(import_type)

    part_enabled = False
    variant_parent = ""
    website = ""
    is_new = False
    part_desc = ""
    prod_code = ""
    cat_opts: Dict[str, str] | None = None
    ud09_sort_map = None
    
    if operation != "delete":
        if import_type == "variant":
            # Select UD09 sort order BEFORE other prompts
            ud09_sort_map = prompt_variant_ud09_sort(df11_detect["Key3"].dropna().astype(str).tolist())
            # Part first so we have the parent ID
            part_enabled = inquirer.confirm(message="Create Part file?", default=True).execute()
            if part_enabled:
                variant_parent, is_new, part_desc, prod_code, website = prompt_part_details()
            # Category step (optional) – now we can use the parent
            if inquirer.confirm(message="Work with categories?", default=True).execute():
                cat_type = inquirer.select(
                    message="Category type:",
                    choices=[
                        {"name": "New category (create UD08 + UD11)", "value": "new"},
                        {"name": "Existing category (UD11 only)", "value": "existing"},
                    ],
                    default="new",
                ).execute()
                cat_site = inquirer.select(message="Website for category:", choices=["SA", "SW"], default="SA").execute()
                cat_input = inquirer.text(
                    message="Category string(s) - paste multiple categories (one per line):",
                    multiline=True
                ).execute().strip()
                cat_list = [cat.strip() for cat in cat_input.split("\n") if cat.strip()]
                cat_opts = {"website": cat_site, "categories": cat_list, "is_new": cat_type == "new"}
        else:
            # Select UD09 sort order for attributes
            ud09_sort_map = prompt_attribute_ud09_sort(df11_detect["Key2"].dropna().astype(str).tolist())

    # Prepare category flags for summary
    cat_enabled = bool(cat_opts)
    cat_site = cat_opts.get("website", "") if cat_enabled else ""
    cat_list = cat_opts.get("categories", []) if cat_enabled else []
    cat_is_new = cat_opts.get("is_new", False) if cat_enabled else False

    if not show_summary(operation, files, import_type, include_tables, part_enabled, variant_parent, website, is_new, part_desc, prod_code, cat_enabled, cat_site, cat_list, cat_is_new):
        console.print("Cancelled.", style="yellow")
        return

    playlist_entries: List[Tuple[str, str]] = []  # (filepath, op)
    playlist_dir = None

    # Execute runs
    if operation == "add":
        stem, written = process_single(files[0], import_type, include_tables, part_enabled, variant_parent, website, is_new, part_desc, ud09_sort_map, cat_opts, prod_code)
        playlist_dir = os.path.dirname(list(written.values())[0]) if written else os.path.dirname(files[0])
        for path in written.values():
            playlist_entries.append((path, "add"))
    elif operation == "delete":
        stem, written = process_single(files[0], import_type, include_tables, False, variant_parent, website, False, "", ud09_sort_map, cat_opts, "")
        playlist_dir = os.path.dirname(list(written.values())[0]) if written else os.path.dirname(files[0])
        for path in written.values():
            playlist_entries.append((path, "delete"))
    else:  # both
        # delete first
        del_stem, del_written = process_single(files[0], import_type, include_tables, False, variant_parent, website, False, "", ud09_sort_map, cat_opts, "")
        # add second (Part only on add)
        add_stem, add_written = process_single(files[1], import_type, include_tables, part_enabled, variant_parent, website, is_new, part_desc, ud09_sort_map, cat_opts, prod_code)
        playlist_dir = os.path.dirname(list(del_written.values())[0]) if del_written else os.path.dirname(files[0])
        for path in del_written.values():
            playlist_entries.append((path, "delete"))
        for path in add_written.values():
            playlist_entries.append((path, "add"))

    # Build playlist
    playlist_stem = build_playlist_name(operation, files)
    include_for_playlist = include_tables.copy()
    df_playlist = build_playlist_df(playlist_entries, include_for_playlist)
    playlist_path = os.path.join(os.path.dirname(playlist_dir), f"{playlist_stem}_PLAYLIST.csv") if playlist_dir else os.path.join(os.path.dirname(files[0]), f"{playlist_stem}_PLAYLIST.csv")
    df_playlist.to_csv(playlist_path, index=False, encoding='utf-8-sig')

    celebrate_success(playlist_dir, playlist_path)


if __name__ == "__main__":
    run()


