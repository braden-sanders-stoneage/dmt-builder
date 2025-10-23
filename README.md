## DMT Builder Wizard (New UI)

A lightweight, colorful console wizard that builds Epicor DMT CSVs (UD08–UD11 and optional Part) and a playlist file. Runs alongside your existing legacy script without modifying it.

### Highlights
- **Two modes**: Standard Mode (Excel-based) and New PDP Mode (create standalone PDP-enabled parts)
- **Clickable console UI**: Arrow keys, space to select, enter to confirm.
- **Native file picker**: Choose your source file via dialog.
- **Fast**: Vectorized pandas pipeline, minimal overhead.
- **Categories (Variant-only, optional)**: Create a category (UD08) and/or assign it to parts (UD11).
- **Same outputs**: UD tables + optional Part CSV and a DMT playlist.

### Supported source files
- **Excel**: `.xlsx`, `.xls`
- **CSV**: `.csv`

### Quick start
1) Install requirements (consider a venv)
```bash
pip install -r requirements.txt
```

2) Run the wizard (press Play on `DMT_Wizard.py` or run in terminal)
```bash
python DMT_Wizard.py
```

3) Follow the prompts in the console. First, select your mode (Standard or New PDP), then follow the appropriate workflow below.

### Workflow Options

#### New PDP Mode
Quick workflow to create a single PDP-enabled part without Excel input:
1) **Mode selection**: Choose "New PDP Mode"
2) **Part ID**: Enter the part number you want to configure for website use
3) **New part?**: Choose whether this is a new part number or an existing part in Epicor
   - If **new**: Enter PartDescription and ProdCode (ClassID="FG" and UserChar1="Introduction" are set automatically)
   - If **existing**: Skip to website selection (only PDP configuration fields are populated)
4) **Website**: Select SA, SW, or SA~SW
5) **Categories** (optional): Optionally create/assign categories
6) **Summary & confirm**: Review and proceed
7) **Output**: Part CSV + optional Category CSVs + Playlist

#### Standard Mode (Typical workflow)
1) **Pick source file**: Choose `.xlsx`/`.xls`/`.csv` with columns that map to `Company, Key1, Key2, Key3, Key4, Key5` (the first six columns are used and renamed).
2) **Type detection**: Script auto-detects Variant vs Attribute from `Key1`; you can override.
3) **Operation**: Add only, Delete only, or Delete & Add. If choosing Delete & Add, you'll specify which file is the DELETE file and which is the ADD file.
4) **Tables to include**: Multi-select UD08–UD11. Defaults depend on type.
5) **UD09 sort order** (Add operations only): Enter `Number01` for dropdown order. For variants, this is based on `Key3` values; for attributes, this is based on `Key2` values. A live table shows all values and assigned orders.
6) **Variant only – Part options**: 
   - Optionally create a Part CSV
   - If yes: Enter parent part ID, choose if it's a new part number
   - If new: Enter PartDescription and ProdCode (ClassID and UserChar1 are set automatically)
   - Choose website: SA, SW, or SA~SW
7) **Variant only – Categories (optional)**:
   - Choose website: SA or SW.
   - Enter category string (Key3), e.g. `Products-Accessories-Fittings`.
   - UD08 parent path is derived by removing the last segment of the category string.
   - UD08 will set `Character01='COPY NEEDED'` and `Character04='COPY NEEDED'`.
   - UD11 assignments will link all child parts to the category.
8) **Summary**: Review settings and confirm.
9) **Processing**: Progress bar shows build steps. A green celebration screen + an orange reminder appear on success.

### Outputs

#### Standard Mode
- Folder: `<dir>/<stem>_OUTPUT/`
  - Always: `..._UD11.csv` (normalized input)
  - Variant: `..._UD10.csv`, `..._UD09.csv` (includes `Number01`), `..._UD08.csv`
  - Attribute: `..._UD10.csv`, `..._UD09.csv` (includes `Number01`)
  - Optional: `..._Part.csv` (Variant only if selected)
  - Optional (Categories, Variant only):
    - `..._Categories_UD08.csv` (category definition)
    - `..._Categories_UD11.csv` (assignments to child parts)
- Playlist: `<dir>/<stem>_PLAYLIST.csv`

#### New PDP Mode
- Folder: `<cwd>/<PartID>_OUTPUT/`
  - Always: `<PartID>_Part.csv` (single PDP-enabled part)
  - Optional (Categories):
    - `<PartID>_Categories_UD08.csv` (category definition, if creating new category)
    - `<PartID>_Categories_UD11.csv` (assignment to part)
- Playlist: `<cwd>/ADD_<PartID>_PLAYLIST.csv`

### Playlist logic
- Each generated CSV becomes an entry with flags: `Add`, `Update`, `Delete`, `Wait`.
- Delete-only → Delete=True; Add/Update=False.
- Add-only → Add=True; Update=True; Delete=False.
- Delete & Add → two runs combined (delete rows + add rows).
- Only selected UD tables are included; `Part` is included if generated. Category files are included when UD08 and/or UD11 are selected.

### Column notes (high level)
- `UD11`: `Company, Key1, Key2, Key3, Key4, Key5` (raw normalized input).
- `Variant → UD10`: unique by `Key5→Key4` with `Key5` blank.
- `Variant → UD09`: unique by `Key3`; includes `Number01` from your sort inputs.
- `Variant → UD08`: unique by `Key2`; sets `Character01=Key2`, `Checkbox01=True`.
- `Attribute → UD10`: unique by `Key3`; adds `Character01=Key3`, `Checkbox01=True`.
- `Attribute → UD09`: unique by `Key2`; adds `Character01=Key2`, `Checkbox01..Checkbox05=True`, `Number01` from your sort inputs.
- `Part` (optional): 
  - Standard Mode: parent row (if brand new part) + child rows for unique `Key4`, linked via `Character11`.
  - New PDP Mode: single row with Character10 and Character11 blank (no variant relationship).
  - If brand new: includes PartDescription, ClassID="FG", ProdCode, UserChar1="Introduction".
  - If existing: only includes PDP configuration fields (Character05-13, Checkbox11).
- `Categories (Variant)`:
  - UD08 category row: `Key1='Category'`, `Key2=website`, `Key3=category string`, `Key4=parent path`, `Character01='COPY NEEDED'`, `Character04='COPY NEEDED'`.
  - UD11 assignment rows: `Key1='Category'`, `Key2=website`, `Key3=category string`, `Key4=PartNum`, `Key5=''` (one per unique part).

### Tips
- In VSCode, use "Python: Select Interpreter" and pick the same interpreter where you installed requirements.
- CSV inputs are read with `pandas.read_csv`; Excel with `pandas.read_excel`.
- The first six columns of your file are used and renamed to the UD11 schema; extra columns are ignored.
- Generated CSVs are compatible with Excel and will properly display special characters (em dashes, degree symbols, etc.)
- If the file picker dialog doesn't appear, ensure `tkinter` is installed with your Python distribution.

### Reminder
- After a successful run, the app shows an orange warning: replace any 'COPY NEEDED' placeholders in Categories_UD08 and Part before importing.

### Dependencies
- `pandas`, `rich`, `InquirerPy`, `openpyxl` (Excel), standard library only otherwise.