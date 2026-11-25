from pathlib import Path
import pandas as pd
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"outputs"; OUT.mkdir(exist_ok=True)
parts=pd.read_csv(ROOT/"outputs/part_metrics.csv")
forecast=pd.read_csv(OUT/"future_forecasts.csv")
# Use Croston-SBA 6-month forecasts; average forecast per month is demand-rate proxy.
croston=forecast[forecast.model=="CrostonSBA"].groupby("part_id").forecast_qty.mean().reset_index(name="forecast_monthly_rate")
# Assumptions are deliberately simulated for demonstration only.
rng=np.random.default_rng(42)
croston["assumed_lead_time_days"]=rng.integers(14,46,size=len(croston))
croston["assumed_service_level"]=0.95
croston["assumed_unit_cost"]=rng.uniform(5,150,size=len(croston)).round(2)
croston=croston.merge(parts[["part_id","avg_monthly_demand","std_monthly_demand","total_units"]],on="part_id",how="left")
lead_months=croston.assumed_lead_time_days/30.0
# Approximate safety stock using monthly std scaled by square root of lead-time months.
z=1.645 # approximate 95% service level, one-sided normal z
croston["estimated_lead_time_demand"]=croston.forecast_monthly_rate*lead_months
croston["assumed_safety_stock"]=z*croston.std_monthly_demand.fillna(0)*np.sqrt(np.maximum(lead_months,0))
croston["suggested_reorder_point"]=np.ceil(croston.estimated_lead_time_demand+croston.assumed_safety_stock)
croston["assumed_stock_on_hand"]=np.ceil(croston.forecast_monthly_rate*rng.uniform(0.25,2.0,size=len(croston)))
croston["reorder_flag"]=croston.assumed_stock_on_hand<=croston.suggested_reorder_point
croston["estimated_reorder_qty"]=np.where(croston.reorder_flag,np.maximum(0,np.ceil(2*croston.forecast_monthly_rate-croston.assumed_stock_on_hand)),0)
croston["estimated_inventory_value"]=croston.assumed_stock_on_hand*croston.assumed_unit_cost
croston.to_csv(OUT/"inventory_recommendations_demo.csv",index=False)
print("Reminder: lead time, cost, stock and service level are assumptions—not original dataset fields.")
print(croston[["part_id","forecast_monthly_rate","suggested_reorder_point","assumed_stock_on_hand","reorder_flag","estimated_reorder_qty"]].head())
