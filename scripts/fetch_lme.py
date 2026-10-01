"""Download daily LME aluminium prices and stocks from westmetall.com.

Westmetall publishes one HTML table per year:
    https://www.westmetall.com/en/markdaten.php?action=table&field=LME_Al_cash&year=YYYY
Columns: date, cash settlement (USD/t), 3-month (USD/t), LME stock (t).

Usage:
    python scripts/fetch_lme.py              # 2024 to current year
    python scripts/fetch_lme.py 2018 2026    # custom range
"""

import sys
import time
from datetime import date
from io import StringIO
from pathlib import Path

import pandas as pd
import requests

URL = "https://www.westmetall.com/en/markdaten.php"
OUT = Path(__file__).resolve().parent.parent / "data" / "lme_aluminium.csv"
COLUMNS = ["date", "cash", "three_month", "stock"]


def fetch_year(year: int) -> pd.DataFrame:
    params = {"action": "table", "field": "LME_Al_cash", "year": year}
    resp = requests.get(URL, params=params, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
    resp.raise_for_status()
    # thousands="," turns "3,225.50" into 3225.5
    df = pd.read_html(StringIO(resp.text), thousands=",")[0]
    df.columns = COLUMNS
    df = df[df["date"] != "date"]  # the header row repeats inside the table
    df["date"] = pd.to_datetime(df["date"], format="%d. %B %Y")
    return df


def main() -> None:
    start = int(sys.argv[1]) if len(sys.argv) > 1 else 2024
    end = int(sys.argv[2]) if len(sys.argv) > 2 else date.today().year

    frames = []
    for year in range(start, end + 1):
        frames.append(fetch_year(year))
        print(f"{year}: {len(frames[-1])} rows")
        time.sleep(1)  # be polite to a free site

    df = pd.concat(frames).drop_duplicates("date").sort_values("date")
    # Non-trading days can show "-" instead of a number
    for col in COLUMNS[1:]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    OUT.parent.mkdir(exist_ok=True)
    df.to_csv(OUT, index=False)
    print(f"Saved {len(df)} rows ({df['date'].min():%Y-%m-%d} to {df['date'].max():%Y-%m-%d}) -> {OUT}")


if __name__ == "__main__":
    main()
