# The Discipline Premium

**How much does emotional decision-making cost a long-term investor? Over 31 years of S&P 500 history, the answer is roughly one-third of final wealth.**

This project quantifies *behavioral drag* — the long-run cost of reacting emotionally to market declines. It compares two investors who follow an identical monthly investment plan and are exposed to the identical market. The only difference between them is how they respond to fear.

The finding: the investor who sold in panic during downturns and re-entered only after recoveries ended the period with **34.6% less wealth — about $679,000 — than the investor who simply stayed invested.**

🔗 **[View the project →](https://catherinedeng02.github.io/the-discipline-premium/))**

---

## Why this question

In asset management, a large part of the value delivered to clients is helping them stay disciplined through volatility. This project puts a number on what that discipline is worth, using a transparent, reproducible model rather than anecdote.

The framing draws on behavioral finance: investors are known to sell near market bottoms and buy back after prices have recovered. This project does not try to predict markets — it measures the cost of a known behavioral pattern.

## What the project does

- Pulls 31 years of S&P 500 monthly data (1995–2026) from a programmatic, authoritative source.
- Simulates two investors, both contributing $1,000 every month:
  - **The Buy-and-Hold Benchmark** — follows the plan without interruption and never sells.
  - **The Reactive Investor** — sells to cash when the market falls past a drawdown threshold, and re-enters only after a rebound.
- Measures the wealth gap between them, and isolates it as the cost of emotional decision-making.
- Stress-tests the result across multiple panic thresholds (15%, 20%, 25%).
- Breaks down where the cost is incurred, through three crisis case studies (Dot-Com Crash, Global Financial Crisis, COVID-19 Crash).
- Presents everything as an interactive, institutional-style research note.

## Key results

| Panic threshold | Reactive investor final value | Cost of behavioral drag |
|---|---|---|
| 15% drawdown | $1,137,784 | −42.0% |
| 20% drawdown | $1,281,188 | −34.6% |
| 25% drawdown | $1,385,885 | −29.3% |

The conclusion holds across every threshold tested: emotional investing left the investor poorer in every case.

## Data and method

- **Primary data:** S&P 500 monthly index, 1995–2026, from Yahoo Finance.
- **Validation:** independently cross-checked against the Federal Reserve's FRED database; the two sources agreed to within rounding.
- **Approach:** a month-by-month simulation that uses only information available up to each point in time, avoiding look-ahead bias.

Full assumptions and limitations are documented in the interactive note itself.

## How to reproduce

The entire pipeline is automated end to end.

```
pip install pandas yfinance fredapi requests openpyxl
python3 get_data.py        # pulls and validates the data → sp500_raw.csv
python3 simulation.py      # runs the simulation → results.json
```

Then open `index.html` through a local server to view the research note.
