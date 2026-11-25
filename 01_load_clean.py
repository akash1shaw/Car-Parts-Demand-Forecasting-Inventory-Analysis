from pathlib import Path
import zipfile, urllib.request, re
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "processed"
RAW.mkdir(parents=True, exist_ok=True); OUT.mkdir(parents=True, exist_ok=True)

URL = "https://zenodo.org/records/4656021/files/car_parts_dataset_without_missing_values.zip?download=1"
zip_path = RAW / "car_parts_dataset_without_missing_values.zip"

if not zip_path.exists():
    print("Downloading dataset from Zenodo...")
    urllib.request.urlretrieve(URL, zip_path)

with zipfile.ZipFile(zip_path) as z:
    tsf_names = [n for n in z.namelist() if n.lower().endswith(".tsf")]
    if not tsf_names:
        raise RuntimeError(f"No .tsf file in archive. Files: {z.namelist()}")
    text = z.read(tsf_names[0]).decode("utf-8", errors="replace")

# Parse the TSF text format: series metadata followed by comma-separated values.
lines = text.splitlines()
data_start = next(i for i, line in enumerate(lines) if line.strip().lower() == "@data") + 1
records = []
for line in lines[data_start:]:
    line=line.strip()
    if not line or line.startswith("#"): continue
    # Dataset entries generally use: series-name:timestamp:value1,value2,...
    parts=line.split(":")
    if len(parts) < 3: continue
    part_id=parts[0].strip()
    timestamp=parts[1].strip().split()[0]
    values=":".join(parts[2:]).strip()
    vals=[v.strip() for v in values.split(",")]
    start=pd.to_datetime(timestamp, errors="coerce")
    if pd.isna(start): continue
    for i,v in enumerate(vals):
        if v in ("", "?"): qty=0
        else:
            try: qty=float(v)
            except ValueError: continue
        date=start + pd.DateOffset(months=i)
        records.append((part_id, date, qty))

df=pd.DataFrame(records, columns=["part_id","date","qty"])
df["date"]=pd.to_datetime(df["date"])
df["qty"]=pd.to_numeric(df["qty"], errors="coerce").fillna(0)
df=df.sort_values(["part_id","date"]).drop_duplicates(["part_id","date"])
# Source's missing values were replaced by zeros in the chosen version.
df.to_csv(OUT/"sales_monthly.csv",index=False)
print("Rows:",len(df),"Parts:",df.part_id.nunique(),"Date range:",df.date.min(),df.date.max())
print(df.head())
