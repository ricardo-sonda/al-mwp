"""Clean the LME duty-paid aluminium premium files downloaded by hand into data/raw/lme.

Two workbooks from the LME website:
    UP  LME Aluminium Premium Duty Paid US Midwest (Platts): daily closing prices for the
        monthly futures curve, columns M01..M15 (USD/t). M01 is the contract for the trade
        date's own calendar month, M02 the next month, and so on. The contracts settle on the
        monthly average of the Platts assessment, so M01 converges to that average as the month
        is fixed. On the first trading day of a month M01 equals the previous day's M02 and then
        jumps once the first assessment is in: that is the contract working, not bad data.
        The back of the curve (roughly M07+) is illiquid and often flat or stale.
    ED  LME Aluminium Premium Duty Paid European (Fastmarkets MB): monthly final settlement
        prices (USD/t), one per contract month, i.e. the monthly average of the assessment.

Outputs:
    data/midwest_premium_curve.csv     date, tenor, contract_month, premium_usd_t, premium_cpl
    data/europe_duty_paid_premium.csv  date, premium_usd_t, premium_cpl

Usage:
    python scripts/clean_lme_premiums.py
"""

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw" / "lme"
IN_MIDWEST = RAW / "LME Aluminium Premium Duty Paid US Midwest (Platts) closing prices.xlsx"
IN_EUROPE = RAW / "LME Aluminium Premium Duty Paid European (Fastmarkets MB) Final  Settlement prices.xlsx"
OUT_MIDWEST = ROOT / "data" / "midwest_premium_curve.csv"
OUT_EUROPE = ROOT / "data" / "europe_duty_paid_premium.csv"

LB_PER_T = 2204.62262


def to_cpl(usd_t: pd.Series) -> pd.Series:
    return usd_t * 100 / LB_PER_T


def clean_midwest() -> pd.DataFrame:
    """Wide M01..M15 curve -> one row per trade date and contract month."""
    df = pd.read_excel(IN_MIDWEST, sheet_name="UP", header=0)
    assert df.columns[0] == "USD/mt", f"unexpected unit header: {df.columns[0]}"
    df = df.rename(columns={df.columns[0]: "date"})
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"]).drop_duplicates("date", keep="last")

    df = df.melt(id_vars="date", var_name="tenor", value_name="premium_usd_t")
    df["tenor"] = df["tenor"].str.removeprefix("M").astype(int)
    df["premium_usd_t"] = pd.to_numeric(df["premium_usd_t"], errors="coerce")
    df = df.dropna(subset=["premium_usd_t"])

    # M01 = trade month, M02 = trade month + 1, ...
    trade_month = df["date"].dt.to_period("M")
    df["contract_month"] = (trade_month + (df["tenor"] - 1)).dt.to_timestamp()
    df["premium_cpl"] = to_cpl(df["premium_usd_t"])
    return df[["date", "tenor", "contract_month", "premium_usd_t", "premium_cpl"]].sort_values(["date", "tenor"])


def clean_europe() -> pd.DataFrame:
    """Three metadata rows, then contract month | final settlement."""
    meta = pd.read_excel(IN_EUROPE, sheet_name="ED", header=None, nrows=3, index_col=0)[1]
    assert meta["Currency/unit"] == "USD/mt", f"unexpected unit: {meta['Currency/unit']}"

    df = pd.read_excel(IN_EUROPE, sheet_name="ED", header=None, skiprows=3, names=["date", "premium_usd_t"])
    df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.to_period("M").dt.to_timestamp()
    df["premium_usd_t"] = pd.to_numeric(df["premium_usd_t"], errors="coerce")
    df = df.dropna().drop_duplicates("date", keep="last").sort_values("date")
    df["premium_cpl"] = to_cpl(df["premium_usd_t"])
    return df


def report_gaps(dates: pd.Series, name: str, max_days: int) -> None:
    gaps = dates.drop_duplicates().sort_values().diff().dt.days
    long = dates.drop_duplicates().sort_values()[gaps > max_days]
    if len(long):
        print(f"{name}: {len(long)} gaps longer than {max_days} days, ending on {', '.join(f'{d:%Y-%m-%d}' for d in long)}")


def main() -> None:
    mw = clean_midwest()
    report_gaps(mw["date"], "Midwest", 5)  # 5 = long weekends (Easter, Christmas)
    mw.to_csv(OUT_MIDWEST, index=False, float_format="%.3f")
    print(f"Saved {len(mw)} rows, {mw['date'].nunique()} trade dates "
          f"({mw['date'].min():%Y-%m-%d} to {mw['date'].max():%Y-%m-%d}) -> {OUT_MIDWEST}")

    eu = clean_europe()
    missing = pd.period_range(eu["date"].min(), eu["date"].max(), freq="M").difference(eu["date"].dt.to_period("M"))
    if len(missing):
        print(f"Europe: missing months {', '.join(map(str, missing))}")
    eu.to_csv(OUT_EUROPE, index=False, float_format="%.3f")
    print(f"Saved {len(eu)} months ({eu['date'].min():%Y-%m} to {eu['date'].max():%Y-%m}) -> {OUT_EUROPE}")


if __name__ == "__main__":
    main()
