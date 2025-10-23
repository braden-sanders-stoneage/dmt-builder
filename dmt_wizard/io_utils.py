from __future__ import annotations

import os
import sys
from typing import Tuple

import pandas as pd


def pick_excel_file(title: str = "Select source file") -> str:
    try:
        import tkinter as tk
        from tkinter import filedialog
    except Exception:
        return ""

    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    root.update()
    filetypes = [
        ("Source files", "*.xlsx *.xls *.csv"),
        ("Excel files", "*.xlsx *.xls"),
        ("CSV files", "*.csv"),
        ("All files", "*.*"),
    ]
    path = filedialog.askopenfilename(title=title, filetypes=filetypes, parent=root)
    root.update()
    root.destroy()
    return path or ""


def read_excel_normalized(path: str) -> pd.DataFrame:
    ext = os.path.splitext(path)[1].lower()
    if ext == ".csv":
        df = pd.read_csv(path)
    else:
        df = pd.read_excel(path)
    cols = list(df.columns[:6])
    if len(cols) < 6 and df.shape[1] >= 6:
        cols = list(df.columns[:6])
    if len(cols) != 6:
        raise ValueError("Expected at least 6 columns in the Excel file.")

    df = df.iloc[:, :6].copy()
    df.columns = ["Company", "Key1", "Key2", "Key3", "Key4", "Key5"]
    return df


def ensure_output_dir(base_dir: str, name: str) -> str:
    out_dir = os.path.join(base_dir, name)
    os.makedirs(out_dir, exist_ok=True)
    return out_dir


def write_csv(df: pd.DataFrame, path: str) -> None:
    df.to_csv(path, index=False, encoding='utf-8-sig')


def get_stem_and_dir(path: str) -> Tuple[str, str]:
    base_dir = os.path.dirname(path)
    stem = os.path.splitext(os.path.basename(path))[0]
    return stem, base_dir


def open_folder_in_os(path: str) -> None:
    if sys.platform.startswith("win"):
        os.startfile(path)
        return
    if sys.platform == "darwin":
        import subprocess
        subprocess.run(["open", path], check=False)
        return
    import subprocess
    subprocess.run(["xdg-open", path], check=False)


