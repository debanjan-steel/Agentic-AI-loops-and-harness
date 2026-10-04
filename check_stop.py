import os
import pandas as pd

if not os.path.exists("experiments.csv"):
    print("CONTINUE")
    exit(0)

df = pd.read_csv("experiments.csv")
if len(df) == 0:
    print("CONTINUE")
    exit(0)

latest = df.iloc[-1]
val_mape = float(latest["val_mape"])
attempt = int(latest["attempt"])

if val_mape < 5.0:
    print("SUCCESS")
elif attempt >= 10:
    print("STOP")
else:
    print("CONTINUE")
