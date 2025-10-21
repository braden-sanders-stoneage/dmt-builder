from __future__ import annotations

import os
from typing import Iterable, Tuple, Set, List

import pandas as pd


def build_playlist_name(operation: str, file_paths: List[str]) -> str:
    stems = []
    for path in file_paths:
        base = os.path.basename(path)
        stem = os.path.splitext(base)[0]
        stems.append(stem)
    
    if operation == "add":
        return f"ADD_{stems[0]}"
    elif operation == "delete":
        return f"DEL_{stems[0]}"
    else:
        return f"DEL_{stems[0]}_ADD_{stems[1]}"


def _table_from_path(path: str) -> str:
    name = os.path.basename(path)
    stem = os.path.splitext(name)[0]
    if "_" in stem:
        suffix = stem.rsplit("_", 1)[-1]
    else:
        suffix = stem
    return suffix


def build_playlist_df(entries: Iterable[Tuple[str, str]], include_tables: Set[str]) -> pd.DataFrame:
    imports = []
    sources = []
    adds = []
    updates = []
    deletes = []
    waits = []

    for path, op in entries:
        table = _table_from_path(path)
        if table != "Part" and table not in include_tables:
            continue

        if op == "delete":
            add_flag = False
            update_flag = False
            delete_flag = True
        else:
            add_flag = True
            update_flag = True
            delete_flag = False

        imports.append(table)
        sources.append(path)
        adds.append(add_flag)
        updates.append(update_flag)
        deletes.append(delete_flag)
        waits.append(True)

    df = pd.DataFrame({
        "Import": imports,
        "Source": sources,
        "Add": adds,
        "Update": updates,
        "Delete": deletes,
        "Wait": waits,
    })
    return df


