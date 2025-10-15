from __future__ import annotations

import os
import sys
from typing import List, Tuple, Dict, Set
import time

import pandas as pd

from .io_utils import (
    pick_excel_file,
    read_excel_normalized,
    ensure_output_dir,
    write_csv,
    get_stem_and_dir,
)
from .builders import (
    build_variant_ud_tables,
    build_attribute_ud_tables,
    build_part_table,
    build_category_ud08,
    build_category_ud11_for_parent,
)
from .playlist import build_playlist_df

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress
from InquirerPy import inquirer


console = Console()


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


def prompt_part_options() -> Tuple[bool, str, str, bool, str]:
    create_part = inquirer.confirm(message="Create Part file?", default=True).execute()
    if not create_part:
        return False, "", "", False, ""

    variant_parent = inquirer.text(message="Variant Parent Part ID:").execute().strip()
    website = inquirer.select(
        message="Website:",
        choices=["SA", "SW", "SA~SW"],
        default="SA",
    ).execute()
    new_pdp = inquirer.confirm(message="Create new PDP?", default=True).execute()
    prod_code = inquirer.text(message="ProdCode (for new PDP parts):").execute().strip()
    return True, variant_parent, website, new_pdp, prod_code


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


def show_summary(
    operation: str,
    files: List[str],
    import_type: str,
    include_tables: Set[str],
    part_enabled: bool,
    variant_parent: str,
    website: str,
    new_pdp: bool,
    prod_code: str,
    cat_enabled: bool,
    cat_site: str,
    cat_str: str,
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
            table.add_row("New PDP?", "Yes" if new_pdp else "No")
            if new_pdp:
                table.add_row("ProdCode", prod_code or "(none)")
        # Category details
        table.add_row("Category?", "Yes" if cat_enabled else "No")
        if cat_enabled:
            table.add_row("Category Website", cat_site)
            table.add_row("Category Path (Key3)", cat_str)

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
    new_pdp: bool,
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
            dfs = build_attribute_ud_tables(df11_out)
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
            df_part = build_part_table(df11_out, variant_parent, website, new_pdp, prod_code)
            csv_path = os.path.join(out_dir, f"{stem}_Part.csv")
            write_csv(df_part, csv_path)
            written["Part"] = csv_path
        progress.update(task, advance=1)

    # Category files (outside progress so prompts are clean)
    if import_type == "variant" and cat_opts:
        cat_site = cat_opts.get("website", "").strip()
        cat_str = cat_opts.get("category", "").strip()
        if cat_site and cat_str:
            # UD08 category definition
            df_cat08 = build_category_ud08(df11_out["Company"].iloc[0] if not df11_out.empty else "SAINC", cat_site, cat_str)
            path08 = os.path.join(out_dir, f"{stem}_Categories_UD08.csv")
            write_csv(df_cat08, path08)
            written["UD08_Categories"] = path08

            # UD11 assignment (parent only)
            parent_part = variant_parent if variant_parent else inquirer.text(message="Parent Part ID for category:").execute().strip()
            company_val = df11_out["Company"].iloc[0] if not df11_out.empty else "SAINC"
            df_cat11 = build_category_ud11_for_parent(company_val, parent_part, cat_site, cat_str)
            path11 = os.path.join(out_dir, f"{stem}_Categories_UD11.csv")
            write_csv(df_cat11, path11)
            written["UD11_Categories"] = path11

    return stem, written


def run() -> None:
    console.print(Panel.fit("DMT Builder Wizard", border_style="magenta"))

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
    new_pdp = False
    prod_code = ""
    cat_opts: Dict[str, str] | None = None
    ud09_sort_map = None
    
    if operation != "delete":
        if import_type == "variant":
            # Select UD09 sort order BEFORE other prompts
            ud09_sort_map = prompt_variant_ud09_sort(df11_detect["Key3"].dropna().astype(str).tolist())
            # Part first so we have the parent ID
            part_enabled, variant_parent, website, new_pdp, prod_code = prompt_part_options()
            # Category step (optional) – now we can use the parent
            if inquirer.confirm(message="Add/assign a category?", default=True).execute():
                cat_site = inquirer.select(message="Website for category:", choices=["SA", "SW"], default="SA").execute()
                cat_str = inquirer.text(message="Category string (Key3):").execute().strip()
                cat_opts = {"website": cat_site, "category": cat_str}

    # Prepare category flags for summary
    cat_enabled = bool(cat_opts)
    cat_site = cat_opts.get("website", "") if cat_enabled else ""
    cat_str = cat_opts.get("category", "") if cat_enabled else ""

    if not show_summary(operation, files, import_type, include_tables, part_enabled, variant_parent, website, new_pdp, prod_code, cat_enabled, cat_site, cat_str):
        console.print("Cancelled.", style="yellow")
        return

    playlist_entries: List[Tuple[str, str]] = []  # (filepath, op)
    playlist_stem = None
    playlist_dir = None

    # Execute runs
    if operation == "add":
        stem, written = process_single(files[0], import_type, include_tables, part_enabled, variant_parent, website, new_pdp, ud09_sort_map, cat_opts, prod_code)
        playlist_stem = stem
        playlist_dir = os.path.dirname(list(written.values())[0]) if written else os.path.dirname(files[0])
        for path in written.values():
            playlist_entries.append((path, "add"))
    elif operation == "delete":
        stem, written = process_single(files[0], import_type, include_tables, False, variant_parent, website, new_pdp, ud09_sort_map, cat_opts, prod_code)
        playlist_stem = stem
        playlist_dir = os.path.dirname(list(written.values())[0]) if written else os.path.dirname(files[0])
        for path in written.values():
            playlist_entries.append((path, "delete"))
    else:  # both
        # delete first
        del_stem, del_written = process_single(files[0], import_type, include_tables, False, variant_parent, website, new_pdp, ud09_sort_map, cat_opts, prod_code)
        # add second (Part only on add)
        add_stem, add_written = process_single(files[1], import_type, include_tables, part_enabled, variant_parent, website, new_pdp, ud09_sort_map, cat_opts, prod_code)
        playlist_stem = del_stem
        playlist_dir = os.path.dirname(list(del_written.values())[0]) if del_written else os.path.dirname(files[0])
        for path in del_written.values():
            playlist_entries.append((path, "delete"))
        for path in add_written.values():
            playlist_entries.append((path, "add"))

    # Build playlist
    include_for_playlist = include_tables.copy()
    df_playlist = build_playlist_df(playlist_entries, include_for_playlist)
    playlist_path = os.path.join(os.path.dirname(playlist_dir), f"{playlist_stem}_PLAYLIST.csv") if playlist_dir else os.path.join(os.path.dirname(files[0]), f"{playlist_stem}_PLAYLIST.csv")
    df_playlist.to_csv(playlist_path, index=False)

    celebrate_success(playlist_dir, playlist_path)


if __name__ == "__main__":
    run()


