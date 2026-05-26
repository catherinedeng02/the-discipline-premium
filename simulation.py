"""
Step 2C: Simulation Engine — full results exported to results.json
Project: The Price of Panic — Quantifying the Cost of Emotional Investing
"""

import pandas as pd
import json
from datetime import date

MONTHLY_CONTRIBUTION = 1000
REBOUND_THRESHOLD = 0.15
PANIC_THRESHOLDS = [0.15, 0.20, 0.25]
MAIN_THRESHOLD = 0.20   # the headline scenario used for the main chart

data = pd.read_csv("sp500_raw.csv", parse_dates=["date"])
prices = data["sp500_close"].tolist()
dates = data["date"].tolist()
n = len(prices)
print(f"Loaded {n} months of data: {dates[0].date()} to {dates[-1].date()}\n")


def simulate_benchmark(prices, start=0, end=None):
    if end is None:
        end = len(prices)
    shares = 0.0
    invested = 0.0
    history = []
    for i in range(start, end):
        price = prices[i]
        shares += MONTHLY_CONTRIBUTION / price
        invested += MONTHLY_CONTRIBUTION
        history.append({"i": i, "value": shares * price, "invested": invested})
    return history


def simulate_reactive(prices, panic_threshold, start=0, end=None):
    if end is None:
        end = len(prices)
    shares = 0.0
    cash = 0.0
    invested = 0.0
    state = "INVESTED"
    running_peak = 0.0
    trough_in_cash = 0.0
    history = []
    panic_count = 0
    reenter_count = 0

    for i in range(start, end):
        price = prices[i]
        event = None
        if price > running_peak:
            running_peak = price

        if state == "INVESTED":
            drawdown = (running_peak - price) / running_peak
            if drawdown >= panic_threshold:
                cash += shares * price
                shares = 0.0
                state = "IN_CASH"
                trough_in_cash = price
                event = "PANIC_SELL"
                panic_count += 1
            else:
                shares += MONTHLY_CONTRIBUTION / price
                invested += MONTHLY_CONTRIBUTION
        elif state == "IN_CASH":
            if price < trough_in_cash:
                trough_in_cash = price
            rebound = (price - trough_in_cash) / trough_in_cash
            if rebound >= REBOUND_THRESHOLD:
                cash += MONTHLY_CONTRIBUTION
                invested += MONTHLY_CONTRIBUTION
                shares = cash / price
                cash = 0.0
                state = "INVESTED"
                event = "RE_ENTER"
                reenter_count += 1
            else:
                cash += MONTHLY_CONTRIBUTION
                invested += MONTHLY_CONTRIBUTION

        drawdown_now = (running_peak - price) / running_peak
        history.append({
            "i": i, "value": shares * price + cash,
            "invested": invested, "state": state, "event": event,
            "drawdown": drawdown_now,
        })
    return history, panic_count, reenter_count


def find_index(year, month):
    for i, d in enumerate(dates):
        if d.year == year and d.month == month:
            return i
    return None


# =====================================================================
# RUN ALL SIMULATIONS
# =====================================================================
bh = simulate_benchmark(prices)
bh_final = bh[-1]["value"]
total_contributed = bh[-1]["invested"]

# Main scenario (20%) — used for the main chart
re_main, main_panics, main_reenters = simulate_reactive(prices, MAIN_THRESHOLD)
re_main_final = re_main[-1]["value"]
main_gap = bh_final - re_main_final
main_gap_pct = main_gap / bh_final * 100

print("Benchmark final value:        ${:,.0f}".format(bh_final))
print("Reactive Investor (20%):      ${:,.0f}".format(re_main_final))
print("Cost of panic: ${:,.0f}  ({:.1f}%)\n".format(main_gap, main_gap_pct))

# Sensitivity analysis — all thresholds
sensitivity = []
for threshold in PANIC_THRESHOLDS:
    re_hist, panics, reenters = simulate_reactive(prices, threshold)
    re_f = re_hist[-1]["value"]
    gap = bh_final - re_f
    sensitivity.append({
        "threshold_pct": int(threshold * 100),
        "reactive_final": round(re_f),
        "cost_dollars": round(gap),
        "cost_pct": round(gap / bh_final * 100, 1),
        "panic_count": panics,
    })
    print("Threshold {:.0f}%: cost {:.1f}%".format(threshold * 100, gap / bh_final * 100))

# Crisis case studies
crises_def = [
    ("Dot-Com Crash", 2000, 1, 2003, 12),
    ("Global Financial Crisis", 2007, 10, 2013, 3),
    ("COVID-19 Crash", 2020, 1, 2022, 12),
]
crises = []
for label, sy, sm, ey, em in crises_def:
    start = find_index(sy, sm)
    end = find_index(ey, em)
    if start is None or end is None:
        continue
    bh_c = simulate_benchmark(prices, start, end + 1)
    re_c, panics, reenters = simulate_reactive(prices, MAIN_THRESHOLD, start, end + 1)
    bh_v = bh_c[-1]["value"]
    re_v = re_c[-1]["value"]
    gap = bh_v - re_v
    crises.append({
        "label": label,
        "start": dates[start].date().isoformat(),
        "end": dates[end].date().isoformat(),
        "start_index": start,
        "end_index": end,
        "benchmark_value": round(bh_v),
        "reactive_value": round(re_v),
        "cost_dollars": round(gap),
        "cost_pct": round(gap / bh_v * 100, 1),
        "panic_count": panics,
    })
    print("{}: cost {:.1f}%".format(label, gap / bh_v * 100))

# =====================================================================
# BUILD THE MONTHLY TIMELINE (for the main interactive chart)
# =====================================================================
timeline = []
for i in range(n):
    timeline.append({
        "date": dates[i].date().isoformat(),
        "price": round(prices[i], 2),
        "benchmark_value": round(bh[i]["value"]),
        "reactive_value": round(re_main[i]["value"]),
        "invested": round(bh[i]["invested"]),
        "drawdown_pct": round(re_main[i]["drawdown"] * 100, 1),
        "reactive_state": re_main[i]["state"],
        "event": re_main[i]["event"],
    })

# =====================================================================
# ASSEMBLE AND WRITE results.json
# =====================================================================
results = {
    "meta": {
        "project": "The Price of Panic",
        "data_source": "Yahoo Finance (S&P 500, ^GSPC), validated against FRED",
        "data_retrieved": date.today().isoformat(),
        "period_start": dates[0].date().isoformat(),
        "period_end": dates[-1].date().isoformat(),
        "months": n,
        "monthly_contribution": MONTHLY_CONTRIBUTION,
        "panic_threshold_main": int(MAIN_THRESHOLD * 100),
        "rebound_threshold": int(REBOUND_THRESHOLD * 100),
    },
    "summary": {
        "total_contributed": round(total_contributed),
        "benchmark_final": round(bh_final),
        "reactive_final": round(re_main_final),
        "cost_dollars": round(main_gap),
        "cost_pct": round(main_gap_pct, 1),
        "panic_count": main_panics,
        "reenter_count": main_reenters,
    },
    "sensitivity": sensitivity,
    "crises": crises,
    "timeline": timeline,
}

with open("results.json", "w") as f:
    json.dump(results, f, indent=2)

print("\nresults.json written successfully.")
print("Timeline points:", len(timeline))
print("Crises:", len(crises))
print("Sensitivity scenarios:", len(sensitivity))