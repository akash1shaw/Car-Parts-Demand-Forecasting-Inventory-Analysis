from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"data/processed/sales_monthly.csv"
OUT=ROOT/"outputs"; OUT.mkdir(exist_ok=True)
df=pd.read_csv(DATA,parse_dates=["date"])

monthly=df.groupby("date",as_index=False).agg(total_units=("qty","sum"),parts_with_demand=("qty",lambda x:(x>0).sum()))
monthly.to_csv(OUT/"monthly_demand.csv",index=False)

metrics=df.groupby("part_id").agg(
    total_units=("qty","sum"),
    avg_monthly_demand=("qty","mean"),
    std_monthly_demand=("qty","std"),
    zero_months=("qty",lambda x:(x==0).sum()),
    active_months=("qty",lambda x:(x>0).sum()),
    max_monthly_demand=("qty","max"),
    months_observed=("qty","count")
).reset_index()
metrics["demand_occurrence_pct"]=100*metrics["active_months"]/metrics["months_observed"]
metrics["cv_demand"]=metrics["std_monthly_demand"]/metrics["avg_monthly_demand"].replace(0, pd.NA)
metrics["last_sale_date"]=df[df.qty>0].groupby("part_id").date.max().values
metrics.to_csv(OUT/"part_metrics.csv",index=False)

# Demand intermittency buckets (simple descriptive classification)
metrics["demand_pattern"]=pd.cut(metrics.demand_occurrence_pct,
    bins=[-0.01,20,50,100.01],labels=["Very intermittent (<=20% active)","Intermittent (20-50%)","Frequent (>50%)"])
metrics.to_csv(OUT/"part_metrics.csv",index=False)

plt.figure(figsize=(10,5)); plt.plot(monthly.date,monthly.total_units,marker="o")
plt.title("Total monthly car-parts demand"); plt.xlabel("Month"); plt.ylabel("Units")
plt.tight_layout(); plt.savefig(OUT/"monthly_total_demand.png",dpi=150); plt.close()

plt.figure(figsize=(9,5)); plt.hist(metrics.demand_occurrence_pct,bins=20)
plt.title("Demand occurrence across parts"); plt.xlabel("% months with non-zero demand"); plt.ylabel("Number of parts")
plt.tight_layout(); plt.savefig(OUT/"demand_occurrence_distribution.png",dpi=150); plt.close()

plt.figure(figsize=(9,5)); plt.hist(metrics.zero_months,bins=20)
plt.title("Zero-demand months per part"); plt.xlabel("Zero-demand months (out of observed)"); plt.ylabel("Parts")
plt.tight_layout(); plt.savefig(OUT/"zero_months_distribution.png",dpi=150); plt.close()

print(metrics.describe(include="all"))
print("Charts and tables written to outputs/")
