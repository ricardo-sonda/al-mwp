"""Fetch Canada's monthly aluminium exports by destination from the UN Comtrade public API.

Source: UN Comtrade "preview" endpoint, which needs no API key (one month and max 500 rows
per call, rate limited, so a full history takes a few minutes; months are cached). Canada
(reporter 124) reports monthly; the figures are Statistics Canada's customs exports, so they
mirror the US import side of the same trade.

    https://comtradeapi.un.org/public/v1/preview/C/M/HS?reporterCode=124&period=...&cmdCode=7601&flowCode=X

HS codes (pass more with --hs):
    7601  unwrought aluminium (primary ingot, T-bar, slab, billet) - the default
    7602  aluminium waste and scrap
    7604  bars, rods and profiles     7606  plates, sheets, strip

Comtrade fills some quantities with its own estimates (isQtyEstimated); those rows are kept and
flagged. Values are FOB in USD.

Output:
    data/canada_exports_by_country.csv
        date, hs, partner_code, country, iso3, tonnes, fob_usd, usd_per_t, qty_estimated, qty_imputed
    qty_imputed: Comtrade gave a value but no weight (about 10 months for the US and World rows);
    tonnes = value / that destination's unit value interpolated from neighbouring months.
    partner_code 0 / country "World" is Canada's reported total: do not sum it with the rest.

Usage:
    python scripts/fetch_canada_exports.py                      # 7601, Jan 2018 to latest
    python scripts/fetch_canada_exports.py --hs 7601 7602 --start 2021-01
"""

import argparse
import json
import time
import urllib.error
import urllib.request
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw" / "comtrade"
OUT = ROOT / "data" / "canada_exports_by_country.csv"

API = "https://comtradeapi.un.org/public/v1/preview/C/M/HS"
PARTNERS = "https://comtradeapi.un.org/files/v1/app/reference/partnerAreas.json"
CANADA = 124
PAUSE = 2.0  # seconds between calls; the preview endpoint allows roughly one per second


class QuotaExceeded(Exception):
    """HTTP 403: the daily preview quota is used up (resets after ~24h; re-run to resume)."""


def get_json(url: str, retries: int = 6) -> dict:
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(url, timeout=90) as r:
                body = json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 403:
                raise QuotaExceeded(url) from e
            if e.code != 429:
                raise
            body = {"statusCode": 429}
        if body.get("statusCode") == 429:
            time.sleep(PAUSE * (attempt + 2))
            continue
        return body
    raise RuntimeError(f"still rate limited after {retries} tries: {url}")


def fetch_month(hs: str, period: str) -> list[dict]:
    """One call per HS code and month: the preview endpoint takes a single period.

    Non-empty months are cached in data/raw/comtrade; empty ones (not yet published) are retried
    on the next run.
    """
    cache = RAW / f"canada_x_{hs}_{period}.json"
    if cache.exists():
        return json.loads(cache.read_text())
    body = get_json(f"{API}?reporterCode={CANADA}&period={period}&cmdCode={hs}&flowCode=X")
    rows = body.get("data") or []
    if body.get("count", 0) >= 500:
        raise RuntimeError(f"hit the 500-row cap for {hs} {period}")
    if rows:
        RAW.mkdir(parents=True, exist_ok=True)
        cache.write_text(json.dumps(rows))
    time.sleep(PAUSE)
    return rows


def partner_names() -> pd.DataFrame:
    cache = RAW / "partner_areas.json"
    if not cache.exists():
        RAW.mkdir(parents=True, exist_ok=True)
        cache.write_text(json.dumps(get_json(PARTNERS)["results"]))
    ref = pd.DataFrame(json.loads(cache.read_text()))
    return ref.rename(columns={"PartnerCode": "partner_code", "PartnerDesc": "country",
                               "PartnerCodeIsoAlpha3": "iso3"})[["partner_code", "country", "iso3"]]


def impute_tonnes(out: pd.DataFrame) -> pd.DataFrame:
    """Fill missing weights as value / unit value, interpolating each destination's USD/t in time.

    Only rows with a value but no weight are filled; they get qty_imputed = True.
    """
    out = out.sort_values("date").copy()
    out["qty_imputed"] = out["tonnes"].isna() & (out["fob_usd"] > 0)
    uv = (out.groupby(["hs", "partner_code"])[["date", "usd_per_t"]]
          .apply(lambda g: g.set_index("date")["usd_per_t"].interpolate(method="time", limit_direction="both"))
          .reset_index(name="uv_interp"))
    out = out.merge(uv, on=["hs", "partner_code", "date"], how="left")
    fill = out["qty_imputed"] & out["uv_interp"].notna()
    out.loc[fill, "tonnes"] = out.loc[fill, "fob_usd"] / out.loc[fill, "uv_interp"]
    out.loc[fill, "usd_per_t"] = out.loc[fill, "uv_interp"]
    left = out["qty_imputed"] & ~fill
    if left.any():
        print(f"{left.sum()} rows with a value but no weight could not be imputed (no other month for that destination)")
    return out.drop(columns="uv_interp")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--hs", nargs="+", default=["7601"])
    ap.add_argument("--start", default="2018-01")
    args = ap.parse_args()

    periods = pd.period_range(args.start, pd.Timestamp.today(), freq="M").strftime("%Y%m").tolist()
    rows, offline = [], False
    for hs in args.hs:
        for period in periods:
            cached = RAW / f"canada_x_{hs}_{period}.json"
            if offline and not cached.exists():
                continue
            try:
                rows += fetch_month(hs, period)
            except QuotaExceeded:
                print(f"Daily Comtrade quota used up at HS {hs} {period}; saving what is cached. Re-run tomorrow to resume.")
                offline = True
        print(f"HS {hs}: {len(rows)} rows so far")

    df = pd.DataFrame(rows)
    # keep the plain customs total: no second partner, all transport modes and customs procedures
    df = df[(df["partner2Code"] == 0) & (df["motCode"] == 0) & (df["customsCode"] == "C00")]
    df = df.drop_duplicates(["period", "cmdCode", "partnerCode"])
    df = df.merge(partner_names(), left_on="partnerCode", right_on="partner_code", how="left")
    df["country"] = df["country"].fillna(df["partnerCode"].astype(str))

    # Comtrade sometimes drops the weight (null or 0) while keeping the value, mostly for the US
    # and World rows. Fall back to altQty (also kg), then flag what is still missing for imputation.
    kg = df["netWgt"].where(df["netWgt"] > 0)
    kg = kg.fillna(df["altQty"].where((df["altQty"] > 0) & (df["altQtyUnitCode"].isin([-1, 8]))))
    out = pd.DataFrame({
        "date": pd.to_datetime(df["period"].astype(str), format="%Y%m"),
        "hs": df["cmdCode"],
        "partner_code": df["partnerCode"],
        "country": df["country"],
        "iso3": df["iso3"],
        "tonnes": kg / 1000,
        "fob_usd": df["primaryValue"],
        "qty_estimated": df["isQtyEstimated"],
    })
    out["usd_per_t"] = out["fob_usd"] / out["tonnes"]
    out = impute_tonnes(out)
    out = out.sort_values(["hs", "date", "tonnes"], ascending=[True, True, False])
    out.to_csv(OUT, index=False, float_format="%.3f")

    world = out[out["partner_code"] == 0]
    print(f"Saved {len(out)} rows, {out['date'].min():%Y-%m} to {out['date'].max():%Y-%m}, "
          f"{out['partner_code'].nunique() - 1} destinations -> {OUT}")
    missing = sorted(set(periods) - set(world["date"].dt.strftime("%Y%m")))
    if missing:
        print(f"No data yet for: {', '.join(missing)}")


if __name__ == "__main__":
    main()
