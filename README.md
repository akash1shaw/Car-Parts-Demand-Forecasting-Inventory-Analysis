# Real Car Parts Demand Forecasting & Inventory Planning

**Stack:** Python, pandas, matplotlib, SQL, Power BI  
**Dataset:** Car Parts Dataset (Monash/Zenodo), 2,674 monthly intermittent-demand series, Jan 1998–Mar 2002 (51 periods).  
**Important:** The public dataset contains part IDs, dates and sales quantity only. Supplier, category, costs, lead times, stock and warranty claims are NOT provided. The optional inventory demo creates clearly labelled assumption-based values.

## Project question
How can historical intermittent spare-parts demand be analyzed, forecasted and translated into a transparent reorder suggestion?

## Setup
1. Download the **without missing values** ZIP from Zenodo: https://zenodo.org/records/4656021
2. Put the ZIP in `data/raw/` (or run downloader script).
3. Python 3.10+ recommended:
   ```bash
   python -m venv .venv
   # Windows: .venv\Scripts\activate
   # macOS/Linux: source .venv/bin/activate
   pip install -r requirements.txt
   ```
4. Run scripts in order:
   ```bash
   python src/01_load_clean.py
   python src/02_eda.py
   python src/03_forecast_benchmark.py
   python src/04_inventory_demo.py
   ```
5. Load `outputs/*.csv` into Power BI. For SQL practice, load `data/processed/sales_monthly.csv` into SQLite using the SQL script or Python.

## Data source & citation
Godahewa et al. (2020), *Car Parts Dataset (without Missing Values)*, Zenodo, DOI: 10.5281/zenodo.4656021. Original dataset extracted from R `expsmooth` package. Dataset is CC BY; cite the source and check Zenodo metadata for exact licensing terms.

## Folder structure
- `data/raw/`: downloaded dataset ZIP / extracted `.tsf`
- `data/processed/`: cleaned long-form data and part-level metrics
- `outputs/`: charts, forecast results, inventory suggestions, Power BI exports
- `sql/`: analysis queries
- `src/`: Python pipeline

## Methods
- EDA: total demand, active/zero months, average demand, demand variability
- Forecast benchmark: Naive, 3-month moving average, SES, Croston, Croston-SBA
- Holdout: last 6 months, rolling-independent evaluation per series
- Metrics: MAE, WAPE, Bias (actual minus forecast); metrics aggregate across parts
- Inventory illustration: estimated lead-time demand and safety stock. Lead time and service level are assumptions, not dataset fields.

## Honest resume wording
“Analyzed 2,674 intermittent monthly car-parts demand series using pandas and SQL. Compared Naive, moving-average, SES and Croston-family forecasts using a six-month time-based holdout and WAPE/MAE. Created a Power BI dashboard for demand frequency, zero-demand patterns, forecast performance and assumption-based reorder recommendations.”

Do not claim real supplier performance, warranty failure rates, actual stock-outs, actual savings or actual lead times from this dataset.
