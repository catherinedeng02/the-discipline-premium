"""
Step 1: Data Acquisition
Project: The Price of Panic — Quantifying the Cost of Emotional Investing

Primary source : Yahoo Finance (S&P 500 index, ticker ^GSPC) — long history
Validation     : FRED (Federal Reserve Bank of St. Louis), series SP500
"""

import yfinance as yf
import pandas as pd
from fredapi import Fred
from datetime import date

# ---- Configuration ----
FRED_API_KEY = "8c204cb1d6bc8f2a49ecff602e6d77cb"   # <-- replace with your FRED API key
START_DATE = "1995-01-01"            # study window start
TICKER = "^GSPC"                     # S&P 500 index on Yahoo Finance

# =====================================================================
# 1. PRIMARY DATA — pull S&P 500 from Yahoo Finance
# =====================================================================
print("Pulling S&P 500 from Yahoo Finance...")
raw = yf.download(TICKER, start=START_DATE, interval="1mo", auto_adjust=True)

# Keep only the closing price, give it a clean name
df = raw[["Close"]].copy()
df.columns = ["sp500_close"]
df.index.name = "date"

# Resample to month-end to guarantee a clean monthly series
monthly = df.resample("ME").last().dropna()

print("Pulled", len(monthly), "monthly data points")
print("Date range:", monthly.index.min().date(), "to", monthly.index.max().date())

# =====================================================================
# 2. CROSS-VALIDATION — compare against FRED for the overlapping period
# =====================================================================
print("\n--- Cross-validation against FRED ---")
try:
    fred = Fred(api_key=FRED_API_KEY)
    fred_raw = fred.get_series("SP500")
    fred_monthly = fred_raw.to_frame(name="fred_close").resample("ME").last().dropna()

    # Align the two sources on their common dates
    merged = monthly.join(fred_monthly, how="inner")
    merged["pct_diff"] = (
        (merged["sp500_close"] - merged["fred_close"]).abs()
        / merged["fred_close"] * 100
    )

    print("Overlapping months compared:", len(merged))
    print("Average difference between sources: {:.3f}%".format(merged["pct_diff"].mean()))
    print("Maximum difference between sources: {:.3f}%".format(merged["pct_diff"].max()))
    if merged["pct_diff"].max() < 2.0:
        print("Result: PASS — the two independent sources agree closely.")
    else:
        print("Result: REVIEW — sources differ more than expected.")
except Exception as e:
    print("Cross-validation skipped (FRED issue):", e)

# =====================================================================
# 3. DATA QUALITY CHECK
# =====================================================================
print("\n--- Data Quality Check ---")
print("Total monthly data points:", len(monthly))
print("Missing values:", monthly["sp500_close"].isna().sum())

# Sanity check: do we have the three major crises in the window?
years = monthly.index.year
for crisis_year in [2000, 2008, 2020]:
    has_it = (years == crisis_year).any()
    print(f"  Covers {crisis_year} crisis period: {'YES' if has_it else 'NO'}")

# =====================================================================
# 4. SAVE RAW DATA — audit trail
# =====================================================================
output_file = "sp500_raw.csv"
monthly.to_csv(output_file)
print(f"\nSaved monthly data to '{output_file}'")
print("Primary source: Yahoo Finance (^GSPC)")
print("Data retrieved on:", date.today().isoformat())

# ---- Preview ----
print("\n--- First 3 months ---")
print(monthly.head(3))
print("\n--- Last 3 months ---")
print(monthly.tail(3))
