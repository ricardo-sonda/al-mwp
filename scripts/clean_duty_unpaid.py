"""Clean the European duty-unpaid aluminium premium history downloaded by hand from investing.com.

Input:
    data/raw/investing.com/aluminium_premium_duty_unpaid_european_historical_data.csv
    Daily, newest first, USD/t. Open/High/Low always equal Price and Vol. is empty, so only
    Date and Price carry information. About 70% of days are unchanged from the day before.

    A handful of days (mostly the last trading day of a month) drop 5-12% and recover the next
    day, e.g. 290 -> 260 -> 290 on 2024-10-31. They look like contract-roll artifacts in the
    continuous series, so they are flagged as outliers and left out of the monthly average.

Cross-check: the duty-paid (LME ED) minus duty-unpaid spread is 2-3.5% of LME + premium in most
months, in line with the EU's 3% duty on unwrought aluminium.

Outputs:
    data/europe_duty_unpaid_premium_daily.csv  date, premium_usd_t, premium_cpl, outlier
    data/europe_duty_unpaid_premium.csv        date, premium_usd_t, premium_cpl, n_days
                                               (monthly mean of non-outlier days; n_days shows
                                               partial months at either end)

Usage:
    python scripts/clean_duty_unpaid.py
"""

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
IN = ROOT / "data" / "raw" / "investing.com" / "aluminium_premium_duty_unpaid_european_historical_data.csv"
OUT_DAILY = ROOT / "data" / "europe_duty_unpaid_premium_daily.csv"
OUT_MONTHLY = ROOT / "data" / "europe_duty_unpaid_premium.csv"

LB_PER_T = 2204.62262
SPIKE = 0.05  # one-day move, reversed the next day, that counts as an outlier


def to_cpl(usd_t: pd.Series) -> pd.Series:
    return usd_t * 100 / LB_PER_T


def clean_daily() -> pd.DataFrame:
    # utf-8-sig strips the byte-order mark investing.com puts before "Date"
    df = pd.read_csv(IN, encoding="utf-8-sig", usecols=["Date", "Price"], dtype=str)
    df["date"] = pd.to_datetime(df["Date"], format="%m/%d/%Y", errors="coerce")
    df["premium_usd_t"] = pd.to_numeric(df["Price"].str.replace(",", ""), errors="coerce")
    df = df.dropna(subset=["date", "premium_usd_t"]).drop_duplicates("date", keep="last")
    df = df[df["date"].dt.dayofweek < 5].sort_values("date").reset_index(drop=True)

    move_in = df["premium_usd_t"].pct_change()
    move_out = df["premium_usd_t"].pct_change(-1)  # vs the next day
    df["outlier"] = (move_in.abs() > SPIKE) & (move_out.abs() > SPIKE) & (move_in * move_out > 0)
    df["premium_cpl"] = to_cpl(df["premium_usd_t"])
    return df[["date", "premium_usd_t", "premium_cpl", "outlier"]]


def to_monthly(daily: pd.DataFrame) -> pd.DataFrame:
    df = daily[~daily["outlier"]].set_index("date")["premium_usd_t"]
    monthly = df.resample("MS").agg(["mean", "count"]).rename(columns={"mean": "premium_usd_t", "count": "n_days"})
    monthly = monthly[monthly["n_days"] > 0].reset_index()
    monthly["premium_cpl"] = to_cpl(monthly["premium_usd_t"])
    return monthly[["date", "premium_usd_t", "premium_cpl", "n_days"]]


def main() -> None:
    daily = clean_daily()
    flagged = daily[daily["outlier"]]
    print(f"{len(flagged)} outlier days: {', '.join(f'{d:%Y-%m-%d}' for d in flagged['date'])}")
    daily.to_csv(OUT_DAILY, index=False, float_format="%.3f")
    print(f"Saved {len(daily)} days ({daily['date'].min():%Y-%m-%d} to {daily['date'].max():%Y-%m-%d}) -> {OUT_DAILY}")

    monthly = to_monthly(daily)
    monthly.to_csv(OUT_MONTHLY, index=False, float_format="%.3f")
    print(f"Saved {len(monthly)} months ({monthly['date'].min():%Y-%m} to {monthly['date'].max():%Y-%m}) -> {OUT_MONTHLY}")


if __name__ == "__main__":
    main()
