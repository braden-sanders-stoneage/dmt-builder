## DMT Builder Wizard (New UI)

A lightweight, colorful console wizard that builds Epicor DMT CSVs (UD08–UD11 and optional Part) and a playlist file. Runs alongside your existing legacy script without modifying it.

### Highlights
- **Clickable console UI**: Arrow keys, space to select, enter to confirm.
- **Native file picker**: Choose your source file via dialog.
- **Fast**: Vectorized pandas pipeline, minimal overhead.
- **Same outputs**: UD tables + optional Part CSV and a DMT playlist.

### Supported source files
- **Excel**: `.xlsx`, `.xls`
- **CSV**: `.csv`

### Quick start
1) Install requirements (consider a venv)
```bash
pip install -r requirements.txt
```

2) Run the wizard (press Play on `Run_DMT_Wizard.py` or run in terminal)
```bash
python Run_DMT_Wizard.py
```

3) Follow the prompts in the console. A file dialog will appear first asking you to select your source file.

### Typical workflow
1) **Pick source file**: Choose `.xlsx`/`.xls`/`.csv` with columns that map to `Company, Key1, Key2, Key3, Key4, Key5` (the first six columns are used and renamed).
2) **Type detection**: Script auto-detects Variant vs Attribute from `Key1`; you can override.
3) **Operation**: Add only, Delete only, or Delete & Add.
4) **Tables to include**: Multi-select UD08–UD11. Defaults depend on type.
5) **Variant only – UD09 sort order**: Enter `Number01` sort order for each unique `Key3` value. A live table shows all values and assigned orders for context.
6) **Variant only – Part options**: Optionally create a Part CSV; if yes, you’ll enter parent part, website (SA/SW/SA~SW), and whether to create a new PDP.
7) **Summary**: Review settings and confirm.
8) **Processing**: Progress bar shows build steps. A green celebration screen appears on success with output paths.

### Outputs
- Folder: `<dir>/<stem>_OUTPUT/`
  - Always: `..._UD11.csv` (normalized input)
  - Variant: `..._UD10.csv`, `..._UD09.csv` (includes `Number01`), `..._UD08.csv`
  - Attribute: `..._UD10.csv`, `..._UD09.csv`
  - Optional: `..._Part.csv` (Variant only if selected)
- Playlist: `<dir>/<stem>_PLAYLIST.csv`

### Playlist logic
- Each generated CSV becomes an entry with flags: `Add`, `Update`, `Delete`, `Wait`.
- Delete-only → Delete=True; Add/Update=False.
- Add-only → Add=True; Update=True; Delete=False.
- Delete & Add → two runs combined (delete rows + add rows).
- Only selected UD tables are included; `Part` is included if generated.

### Column notes (high level)
- `UD11`: `Company, Key1, Key2, Key3, Key4, Key5` (raw normalized input).
- `Variant → UD10`: unique by `Key5→Key4` with `Key5` blank.
- `Variant → UD09`: unique by `Key3`; includes `Number01` from your sort inputs.
- `Variant → UD08`: unique by `Key2`; sets `Character01=Key2`, `Checkbox01=True`.
- `Attribute → UD10`: unique by `Key3`; adds `Character01=Key3`, `Checkbox01=True`.
- `Attribute → UD09`: unique by `Key2`; adds `Character01=Key2`, `Checkbox01..Checkbox05=True`.
- `Part` (optional): parent row (if creating PDP) + child rows for unique `Key4`, linked via `Character11`.

### Tips
- In VSCode, use “Python: Select Interpreter” and pick the same interpreter where you installed requirements.
- CSV inputs are read with `pandas.read_csv`; Excel with `pandas.read_excel`.
- The first six columns of your file are used and renamed to the UD11 schema; extra columns are ignored.

### Troubleshooting
- **ModuleNotFoundError (e.g., rich, InquirerPy)**: You likely installed packages in a different Python than the one running the script.
  - Install with the same interpreter you run: 
```bash
py -3.12 -m pip install -r requirements.txt
py -3.12 Run_DMT_Wizard.py
```
  - Or specify your exact path: 
```bash
"C:\\Users\\<you>\\AppData\\Local\\Programs\\Python\\Python312\\python.exe" -m pip install -r requirements.txt
"C:\\Users\\<you>\\AppData\\Local\\Programs\\Python\\Python312\\python.exe" Run_DMT_Wizard.py
```
- **Excel read errors**: Ensure the file isn’t open/locked and that the first six columns contain your UD keys.
- **Unexpected outputs**: Verify type (Variant vs Attribute) and the selected tables. Re-run and adjust.

### Dependencies
- `pandas`, `rich`, `InquirerPy`, `openpyxl` (Excel), standard library only otherwise.