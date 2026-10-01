"""Download USGS Aluminum Mineral Industry Surveys and extract monthly prices and imports.

USGS publishes one workbook per month (about two months after the month it covers):
    https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/media/files/mis-YYYYMM-alumi.xlsx
The XLSX goes back to August 2021. Use it rather than the PDF: some PDF issues drop rows
(the June 2026 PDF shows no 2026 prices; the XLSX does).

Two tables are used:
    T6  Midwest U.S. market price (all-in: LME + premium) and LME cash, cents/lb, Platts monthly
        averages. Each issue repeats roughly the last 13 months, so missing issues are covered
        and later issues overwrite earlier ones (revisions win).
    T8  U.S. imports for consumption by country (t): crude metal and alloys (unwrought, HTS 7601),
        semi-fabricated products, scrap, total. Each issue has one month plus year-to-date.
        A month whose issue is missing is rebuilt as YTD(m) - YTD(m-1).

Outputs:
    data/midwest_premium.csv         date, midwest/lme/premium in cents/lb and USD/t, vintage
    data/us_imports_by_country.csv   date, country, crude_t, semis_t, scrap_t, total_t, source

Usage:
    python scripts/fetch_usgs.py              # August 2021 to latest published issue
    python scripts/fetch_usgs.py 2024-01      # from a given issue month
"""

import re
import sys
import time
from datetime import date
from pathlib import Path

import pandas as pd
import requests

URL = (
    "https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/"
    "s3fs-public/media/files/mis-{ym}-alumi.xlsx"
)
ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw" / "usgs"
OUT_PRICES = ROOT / "data" / "midwest_premium.csv"
OUT_IMPORTS = ROOT / "data" / "us_imports_by_country.csv"

LB_PER_T = 2204.62262
MONTHS = {m: i for i, m in enumerate(
    ["january", "february", "march", "april", "may", "june", "july",
     "august", "september", "october", "november", "december"], start=1)}
IMPORT_COLS = ["crude", "semis", "scrap", "total"]


def download(period: pd.Period) -> Path | None:
    """Return the cached workbook for an issue month, downloading it if needed."""
    path = RAW / f"mis-{period.strftime('%Y%m')}-alumi.xlsx"
    if path.exists():
        return path
    resp = requests.get(URL.format(ym=period.strftime("%Y%m")), headers={"User-Agent": "Mozilla/5.0"}, timeout=60)
    if resp.status_code in (403, 404):  # S3 answers 403 for files that don't exist
        return None
    resp.raise_for_status()
    path.write_bytes(resp.content)
    time.sleep(0.5)
    return path


def parse_prices(path: Path) -> pd.DataFrame:
    """Table 6 -> one row per month with the Midwest and LME cash prices (cents/lb)."""
    df = pd.read_excel(path, sheet_name="T6", header=None).dropna(how="all", axis=1)
    df = df.iloc[:, :3]
    df.columns = ["label", "midwest", "lme"]

    rows, year = [], None
    for label, midwest, lme in df.itertuples(index=False):
        label = str(label).strip()
        has_values = pd.notna(pd.to_numeric(midwest, errors="coerce"))
        # Year header: "2025", "2022:" (rows like "2021  138.5" are annual averages, skipped)
        if m := re.fullmatch(r"(\d{4}):?", label):
            if not has_values:
                year = int(m.group(1))
            continue
        # Old layout prefixes the carry-over month with its year: "2021, December"
        if m := re.fullmatch(r"(\d{4}), (\w+)", label):
            year, label = int(m.group(1)), m.group(2)
        month = MONTHS.get(label.lower())
        if month and year and has_values:
            rows.append({"date": pd.Timestamp(year, month, 1), "midwest_cpl": float(midwest), "lme_cash_cpl": float(lme)})
    return pd.DataFrame(rows)


def to_tonnes(value) -> float:
    """'--' means zero, '(2)' and '<0.5' mean less than half a tonne."""
    s = str(value).strip()
    if s in {"--", "-", "–", "(2)", "(3)", "<0.5"}:
        return 0.0
    return pd.to_numeric(s.replace(",", ""), errors="coerce")


def parse_imports(path: Path, period: pd.Period) -> pd.DataFrame:
    """Table 8 -> one row per country with month and year-to-date tonnes by category."""
    df = pd.read_excel(path, sheet_name="T8", header=None).dropna(how="all", axis=1)
    if df.shape[1] == 5:  # some January issues have no year-to-date columns
        df.columns = ["country"] + [f"{c}_month" for c in IMPORT_COLS]
        for c in IMPORT_COLS:
            df[f"{c}_ytd"] = df[f"{c}_month"]
        df = df[["country"] + [f"{c}_{k}" for c in IMPORT_COLS for k in ("month", "ytd")]]
    else:
        df = df.iloc[:, :9]
        df.columns = ["country"] + [f"{c}_{k}" for c in IMPORT_COLS for k in ("month", "ytd")]

    start = df.index[df["country"].astype(str).str.strip() == "Country or locality"][0]
    end = df.index[df["country"].astype(str).str.strip() == "Total"][0]
    df = df.loc[start + 1 : end].copy()
    for col in df.columns[1:]:
        df[col] = df[col].map(to_tonnes)
    df = df.dropna(subset=df.columns[1:], how="all")  # repeated header rows

    # Footnote markers stick to names in older issues: "China3" -> "China"
    df["country"] = df["country"].astype(str).str.strip().str.replace(r"\d+$", "", regex=True)
    df.insert(0, "date", period.to_timestamp())
    return df


def fill_missing_months(imports: pd.DataFrame) -> pd.DataFrame:
    """Rebuild months with no issue from consecutive year-to-date columns."""
    have = set(imports["date"])
    filled = []
    for month in pd.period_range(imports["date"].min(), imports["date"].max(), freq="M"):
        ts, prev = month.to_timestamp(), (month - 1).to_timestamp()
        if ts in have or month.month == 1 or prev not in have:
            continue
        nxt = (month + 1).to_timestamp()
        # This month's YTD isn't published either, so infer it from next month: YTD(m) = YTD(m+1) - month(m+1)
        a = imports[imports["date"] == prev].set_index("country")
        b = imports[imports["date"] == nxt].set_index("country")
        if b.empty:
            continue
        gap = pd.DataFrame(index=a.index.union(b.index))
        for c in IMPORT_COLS:
            ytd = b[f"{c}_ytd"] - b[f"{c}_month"]
            gap[f"{c}_month"] = ytd.sub(a[f"{c}_ytd"], fill_value=0).clip(lower=0)
            gap[f"{c}_ytd"] = ytd
        gap = gap.reset_index().rename(columns={"index": "country"})
        gap.insert(0, "date", ts)
        gap["source"] = "ytd_diff"
        filled.append(gap)
        print(f"{month}: no issue, rebuilt from year-to-date columns")
    return pd.concat([imports, *filled], ignore_index=True)


def main() -> None:
    first = pd.Period(sys.argv[1] if len(sys.argv) > 1 else "2021-08", freq="M")
    last = pd.Period(date.today(), freq="M") - 1
    RAW.mkdir(parents=True, exist_ok=True)

    prices, imports = [], []
    for period in pd.period_range(first, last, freq="M"):
        path = download(period)
        if path is None:
            print(f"{period}: not published")
            continue
        p = parse_prices(path)
        p["vintage"] = str(period)
        prices.append(p)
        imports.append(parse_imports(path, period))
        print(f"{period}: {len(p)} price months, {len(imports[-1])} import rows")

    # Prices: the latest issue's figure for each month wins
    px = pd.concat(prices).sort_values(["date", "vintage"]).drop_duplicates("date", keep="last")
    px["premium_cpl"] = px["midwest_cpl"] - px["lme_cash_cpl"]
    for col in ["midwest", "lme_cash", "premium"]:
        px[f"{col}_usd_t"] = (px[f"{col}_cpl"] * LB_PER_T / 100).round(2)
    px = px[["date", "midwest_cpl", "lme_cash_cpl", "premium_cpl",
             "midwest_usd_t", "lme_cash_usd_t", "premium_usd_t", "vintage"]]
    px.to_csv(OUT_PRICES, index=False, float_format="%.3f")
    print(f"Saved {len(px)} months ({px['date'].min():%Y-%m} to {px['date'].max():%Y-%m}) -> {OUT_PRICES}")

    im = pd.concat(imports, ignore_index=True)
    im["source"] = "month"
    im = fill_missing_months(im)
    im = im[["date", "country"] + [f"{c}_month" for c in IMPORT_COLS] + ["source"]]
    im.columns = ["date", "country"] + [f"{c}_t" for c in IMPORT_COLS] + ["source"]
    im = im.sort_values(["date", "country"])
    im.to_csv(OUT_IMPORTS, index=False, float_format="%.0f")
    print(f"Saved {len(im)} rows ({im['date'].min():%Y-%m} to {im['date'].max():%Y-%m}) -> {OUT_IMPORTS}")


if __name__ == "__main__":
    main()
