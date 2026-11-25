from pathlib import Path
import pandas as pd
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
df=pd.read_csv(ROOT/"data/processed/sales_monthly.csv",parse_dates=["date"])
OUT=ROOT/"outputs"; OUT.mkdir(exist_ok=True)
H=6 # hold out final six months
ALPHA=0.2

def naive(y,h):
    return np.repeat(y[-1] if len(y) else 0.,h)
def moving_average(y,h,k=3):
    v=np.mean(y[-k:]) if len(y) else 0.
    return np.repeat(v,h)
def ses(y,h,alpha=ALPHA):
    if len(y)==0: return np.zeros(h)
    level=float(y[0])
    for obs in y[1:]: level=alpha*float(obs)+(1-alpha)*level
    return np.repeat(level,h)
def croston(y,h,alpha=0.1,sba=False):
    y=np.asarray(y,dtype=float)
    nonzero=np.where(y>0)[0]
    if len(nonzero)==0: return np.zeros(h)
    demand=float(y[nonzero[0]])
    interval=1.0
    last=nonzero[0]
    for idx in nonzero[1:]:
        demand=alpha*float(y[idx])+(1-alpha)*demand
        interval=alpha*float(idx-last)+(1-alpha)*interval
        last=idx
    rate=demand/max(interval,1e-9)
    if sba: rate*= (1-alpha/2)
    return np.repeat(max(0,rate),h)

def metrics(actual,forecast):
    actual=np.asarray(actual,dtype=float); forecast=np.asarray(forecast,dtype=float)
    err=actual-forecast
    return {"MAE":np.mean(np.abs(err)),"WAPE":np.sum(np.abs(err))/max(np.sum(np.abs(actual)),1e-9),
            "Bias_actual_minus_forecast":np.mean(err)}

methods={"Naive":naive,"MovingAverage3":moving_average,"SES":ses,
         "Croston":lambda y,h:croston(y,h,sba=False),
         "CrostonSBA":lambda y,h:croston(y,h,sba=True)}
rows=[]
for part,g in df.sort_values("date").groupby("part_id"):
    y=g.qty.to_numpy(dtype=float)
    if len(y)<=H: continue
    train,actual=y[:-H],y[-H:]
    for name,fn in methods.items():
        pred=fn(train,H)
        m=metrics(actual,pred)
        rows.append({"part_id":part,"model":name,**m})
results=pd.DataFrame(rows)
results.to_csv(OUT/"forecast_metrics_by_part.csv",index=False)
summary=results.groupby("model",as_index=False).agg(
    mean_part_MAE=("MAE","mean"),
    median_part_MAE=("MAE","median"),
    mean_part_WAPE=("WAPE","mean"),
    median_part_WAPE=("WAPE","median"),
    mean_bias=("Bias_actual_minus_forecast","mean")
)
# Aggregate WAPE: total absolute error divided by total actual across part-model pairs
summary.to_csv(OUT/"forecast_model_summary.csv",index=False)
print(summary.sort_values("mean_part_WAPE"))

# Forecast 6 future periods using all available history. Aggregate forecasts and part-level output.
future_rows=[]
for part,g in df.sort_values("date").groupby("part_id"):
    y=g.qty.to_numpy(dtype=float)
    for name,fn in methods.items():
        forecast=fn(y,6)
        for step,val in enumerate(forecast,1):
            future_rows.append({"part_id":part,"model":name,"forecast_month_ahead":step,
                               "forecast_qty":max(0,float(val))})
future=pd.DataFrame(future_rows)
future.to_csv(OUT/"future_forecasts.csv",index=False)
print("Forecast outputs saved.")
