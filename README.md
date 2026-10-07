# Has the US Midwest premium priced in the Section 232 tariffs?

**[View the dashboard →](https://ricardo-sonda.github.io/al-mwp/dashboard/)** The main findings in charts. Rebuild it with `python scripts/build_dashboard.py`.

An independent research project in Python (pandas, statsmodels). It looks at how far the US Midwest aluminium premium priced in the 2025 Section 232 tariffs, whether the futures curve priced them correctly, what they did to LME hedging, and how they redirected North American metal flows. The full analysis is in `notebook.ipynb`.

## The question

> **To what extent has the US Midwest aluminium price absorbed the cost of the Section 232 tariffs, and what explains the part that has not been passed through?**

The project has four strands:

1. **Price: pass-through.** Compare the physical Midwest price (LME + MW premium) with the *landed cost* of importing a tonne. The landed cost is LME + origin premium + freight + tariff. The gap between the two is the import margin. A gap near zero means full pass-through. A persistent gap means the market is coping some other way: running down inventory, substituting domestic or scrap units, or expecting the tariff to be reversed.
2. **Futures: expectations.** Did the MW premium futures curve forecast the premium correctly under the tariff, or did it price a relief that never came?
3. **Risk: hedging.** How does an ad valorem tariff change the LME exposure of US-delivered metal and of an MW premium position?
4. **Volume: flows.** How did US imports by origin and product change around each tariff step, and where did the Canadian tonnes that stopped going to the US go?

## Summary

**Data and pipeline**
- Built a data pipeline in Python (pandas, statsmodels) from the LME, USGS, UN Comtrade (API) and Platts/Fastmarkets-based premium contracts: daily LME prices and stocks, the MW premium futures curve (M01–M15), Rotterdam duty-paid and duty-unpaid premiums, US imports by origin and product, and Canadian exports by destination.
- Rebuilt the missing Rotterdam duty-unpaid premium from the duty-paid series by estimating the effective EU import duty (median 2.7%). The backtest error was about ±13 $/t.
- Extended the monthly MW premium series past its USGS end date using month-end front-month futures, after checking they match the USGS series within 10 $/t (median).
- Found that the MW futures settlements were often stale (back months unchanged on ~80% of days, and the Aug 2026 move showed up two days late and at half size compared with CME). Flagged stale quotes in every test.
- Separated the tariff from the Mar 2026 Strait of Hormuz supply shock by splitting every analysis at the closure date.

**Price: import parity and pass-through**
- Modelled the landed cost of a tonne delivered to the Midwest on two routes (Canada and Rotterdam): LME + origin premium + freight + ad valorem tariff, with freight sensitivity bands. Compared it with the physical Midwest price.
- Showed that the premium passed the tariff through in full. Backing the tariff rate out of the Canada import-parity condition gives 25% in the 25% regime and 50% in the 50% regime, and the premium rose from ~850 to ~2,100 $/t.
- Found that the futures market repriced on the announcement. The front MW contracts rose ~400 $/t (+48%) within about a week of the 50% announcement.

**Futures: did the curve misprice the tariff?**
- Found that the MW curve stayed backwardated through most of the 50% regime (M03 − M01 between −120 and −230 $/t). Backing out the tariff rate the forward premium implied gives ~46% against the statutory 50%: the market was pricing relief.
- Tested the 3-month futures as a forecast against no-change and import-parity benchmarks (Newey–West errors). Before the tariff it was unbiased (+13 $/t over 69 forecasts). Under the 50% tariff it came in below the outcome in all 7 forecasts, by 342 $/t on average (t = 7.5), and did worse than both benchmarks (RMSE 366 vs 252 and 218 $/t).
- Backtested a rule that buys the 3-month contract whenever it trades below Canada import parity: +276 $/t per trade with 10 of 11 trades profitable, against +80 $/t for always being long. This is in-sample, before costs, and from a single regime.
- Read the August 2026 US–Canada tariff episode against the parity model. A Canada-only cut to 25% would lower Canada parity by ~920 $/t, but deferred CME contracts fell only ~270 $/t. This is consistent with Canada not being the marginal supplier to the US.

**Risk: LME hedging under an ad valorem tariff**
- Derived that a tariff charged on value makes US-delivered metal move like (1 + t) tonnes of LME, so a 1:1 LME hedge is too small.
- Estimated minimum-variance hedge ratios (HAC regressions, by regime and on a rolling window): ~1.3 at 50% against 1.2 before the tariff. With a 1:1 hedge, monthly residual risk rose from 50 to 90 $/t (the 90 includes the Gulf shock).
- Showed that the MW futures curve reacts to LME moves 1–2 months late. The weekly beta is ~0 at 1 week and 0.7 at 8 weeks, and this week's LME move predicts the next four weeks of futures moves. A daily delta therefore understates the premium's LME exposure.

**Flows: how trade adjusted**
- US crude aluminium imports fell 25% against the pre-tariff baseline. Imports from Canada fell 38% (224 → 140 kt/month), and Canada's share fell from 75% to 62%. India (+77%) and the UAE (+27%) partly filled the gap.
- Canadian metal was redirected to Europe. The US share of Canadian unwrought exports fell from 94% to 71%, and exports to the Netherlands rose from ~4 to ~43 kt/month.
- Imports shifted from primary metal to semis and scrap. By Q2 2026, scrap imports were up 83% (Canadian scrap doubled) and semis up 51% (Europe, Korea, China). Crude's share of US imports fell from 65% to 45%, and total aluminium imports were back at the pre-tariff level.

## The tariff timeline

The rate depends on the **origin**, not only on the date. Dates and rates are compiled from public reporting; check them against the proclamation or Federal Register text before reusing them.

| Effective | Change | Rate on Canada | Rate on others |
|---|---|---|---|
| 23 Mar 2018 | Section 232 introduced | exempt, then 10% from 1 Jun 2018 | 10% |
| 20 May 2019 | Canada and Mexico exempted | 0% | 10% |
| 16 Aug – 15 Sep 2020 | 10% briefly reimposed on Canadian non-alloyed unwrought metal | 10% (part) | 10% |
| 12 Mar 2025 | All exemptions end; rate raised | 25% | 25% |
| 4 Jun 2025 | Rate doubled (UK kept at 25%) | 50% | 50% (UK 25%) |
| 2 Apr 2026 | Customs-value overhaul for derivatives; no change for unwrought aluminium | 50% | 50% |
| 20–22 Aug 2026 | US signals a cut for Canada to 25%; talks collapse | 50% | 50% |

Two consequences for the model:

- **Canada paid 0% for most of 2019–2025, while other origins paid 10%.** The first event that hit the marginal (Canadian) tonne was 12 March 2025, not June 2025, so both steps are analysed separately.
- **Duty basis.** The model treats the duty on primary metal (HTS 7601) as ad valorem on customs value. Customs value is roughly the FOB price, LME + origin premium, and excludes international freight. The 2 April 2026 overhaul changed how derivatives are valued and does not affect unwrought metal, so it is not a tariff step in the price model. It is marked on the charts for reference.

## Method

**Landed cost by route (USD/t, monthly):**

```
FOB(origin, m)    = LME(m) + P_origin(m)                     # what the tonne is worth where it sits
Landed(origin, m) = FOB(origin, m) + Freight_origin→MW + t_origin(m) × FOB(origin, m)
Gap(origin, m)    = (LME(m) + MWP(m)) − Landed(origin, m)
```

`P_origin` is the premium the tonne gives up by going to the US instead of its best alternative. That alternative differs by route, so the two routes use different European premiums:

- **Rotterdam → Midwest: `P_origin` = DUP.** This is the world-market tonne. Metal in Rotterdam bonded warehouses that is re-exported never clears EU customs, so it never pays the EU's 3% duty. Its opportunity cost is the duty-unpaid price, LME + DUP. Using DP here would charge the US route with an EU duty it never pays (about 3% × (LME + DUP), ≈ 70–90 $/t). Freight is transatlantic plus inland. Europe ships almost no primary metal to the US, so this route is a *would-it-pay* test rather than an observed flow.
- **Canada → Midwest: `P_origin` = DP − Freight_Canada→Rotterdam.** This is the marginal tonne, about 60–75% of US crude imports. Canadian aluminium enters the EU duty-free under CETA, so a Canadian tonne diverted to Europe can be cleared and sold at the *duty-paid* price without paying the duty. Its alternative is therefore LME + DP, *netted back* to Canada by subtracting transatlantic freight. Adding the full Rotterdam premium and then Canada→MW freight on top would price Canadian metal as if it were already in Rotterdam. Freight to the Midwest is short rail or truck haul.

Freight is an assumption with a sensitivity band, because no free series exists. All results are shown at low, mid and high freight. The Canada route has two freight legs: the netback leg (Canada → Rotterdam) and the delivery leg (Canada → Midwest).

**Tariff base.** US duty is charged on the customs value of the actual import, i.e. the transaction price excluding international freight. `FOB` above is a proxy for that value, not the invoice itself.

**Pass-through.** The main measure is the *implied tariff rate*: the rate at which import parity explains the observed premium, solved on each route. It is computed twice: once from the actual monthly premium, and once from the forward premium (M03 on the last trading day, with LME 3M). If the implied rate tracks the statutory rate, the tariff is fully passed through. If the forward rate is below the actual rate, the market expects the landed cost to fall. Price moves around each tariff event are measured on fixed futures contracts (event month +1 and +3, 5 and 20 trading days after the event), not on the rolling M01/M03 series, which switch contract each month.

**Futures as a forecast.** At each month-end, M03 is the market's forecast of the premium two months out. Its error is compared with two benchmarks, no change and Canada import parity at the rate in force on the trade date, with Newey–West standard errors because the forecasts overlap. Results are split into three regimes: pre-tariff, 50% before the Hormuz closure, and 50% after it. Forecasts whose horizon spans a tariff step are excluded. Stale M03 quotes are flagged and reported separately.

**Hedge ratio under an ad valorem tariff.** At Canada parity, ∂MWP/∂LME = t, so the all-in US price moves by 1 + t per unit of LME. This is tested three ways:
- monthly minimum-variance hedge ratios of the all-in price on LME (HAC errors), by regime, on a rolling 12-month window, and pooled with a t × ΔLME interaction;
- weekly changes in a fixed MW futures contract regressed on LME 3M changes over 1, 2, 4 and 8 weeks;
- a lead-lag regression testing whether this week's LME move predicts the next four weeks of futures moves.

**Flows.** Monthly US imports by origin (crude) and by product (crude, semis, scrap), compared with a pre-tariff baseline (Mar 2024 – Feb 2025) in each tariff regime. On the Canadian side, exports of unwrought metal by destination over the same windows.

## Data on hand

| File | Series | Frequency | Coverage | Notes |
|---|---|---|---|---|
| `lme_aluminium.csv` | LME cash, 3M, stocks (westmetall.com) | Daily | Jan 2018 – Oct 2026 | Monthly means match the USGS LME cash column to within 0.5 $/t. |
| `midwest_premium.csv` | MW premium and all-in MW price (USGS, Platts monthly averages) | **Monthly** | Aug 2020 – Jun 2026 | Monthly averages, not daily spot. Premium = all-in MW − LME cash. |
| `midwest_premium_curve.csv` | LME MW premium futures (Platts), M01–M15 | Daily | Mar 2019 – Aug 2026 | Cash-settled on the monthly average of the Platts MW premium. M01 is the trade date's own calendar month, so it is part-fixed and converges to that month's average. M01 at month-end matches the USGS monthly premium within ~10 $/t (median; max 34), which justifies extending the monthly series to Aug 2026. **M01 is not a spot price**: within a month it lags the spot premium, and it switches contract on the first trading day of each month. This is the LME's thinly traded contract; most volume on the same assessment trades on CME (AUP). Since 2024, M02+ are unchanged on ~81% of days. |
| `europe_duty_unpaid_premium.csv` | Rotterdam DUP (investing.com continuous series) | Daily → monthly | Mar 2019 – **Oct 2025** | Ends before the most interesting period. Looks like a rolling front-month futures series rather than the Fastmarkets assessment itself (month-end roll spikes, ~70% unchanged days). Source definition not yet confirmed. |
| `europe_duty_paid_premium.csv` | Rotterdam DP (LME ED final settlement = monthly average of Fastmarkets assessment) | Monthly | Jul 2021 – Aug 2026 | |
| `europe_duty_unpaid_premium_reconstructed.csv` | Rotterdam DUP, observed and then reconstructed from DP | Monthly | Jul 2021 – Aug 2026 | `source` column marks reconstructed months; low/mid/high band. See below. |
| `us_imports_by_country.csv` | US imports by country: crude, semis, scrap (USGS) | Monthly | Aug 2021 – Jun 2026 | Contains `Total` and `Other` rows, so do not sum across countries. Two months are derived from year-to-date differences. |
| `canada_exports_by_country.csv` | Canadian exports by destination, HS 7601 (unwrought) and 7602 (scrap), tonnes and FOB USD (UN Comtrade, from StatCan) | Monthly | 7601: Jan 2018 – Jul 2026; 7602: to Oct 2024 so far | `country == "World"` is the total, so do not sum it with the rest. Comtrade drops the weight in about 9 months for the US and World rows. These are filled from value ÷ interpolated unit value (`qty_imputed`). Exports to the US match US-reported imports from Canada within about 3% in most quarters. |

### Gaps and caveats

- **DUP after Oct 2025: reconstructed.** Duty-paid metal carries the EU import duty (3% on unwrought aluminium, charged on LME + DUP), so `DUP = (DP − r·LME) / (1 + r)`. Here `r` is the *effective* duty rate. It is lower than 3% because part of the metal in Rotterdam comes from duty-free origins. Fitted on the overlap months, r has a median of 2.7% and a 10–90% range of 1.9–3.3%. The backtest error is about ±13 $/t. Feb–May 2025 is the exception: r collapsed to about 0% as metal turned away from the US flooded Europe, and the reconstruction overstates DUP by 50–80 $/t in those months. Reconstructed months are plotted as a dashed line and the band is carried into the landed-cost sensitivity. DUP is needed only for the Rotterdam route; the Canada route uses DP, which is observed through Aug 2026.
- **Freight.** Fixed assumptions with a low/mid/high range. Before 2025 the Canada route sat 80–180 $/t above parity at a 0% tariff, the same size as the freight band, so small post-tariff gaps should not be read as arbitrage.
- **Hormuz shock.** Iran closed the Strait of Hormuz on 2 Mar 2026. It drives the Mar–May 2026 jump in Rotterdam DP (361 → 596 $/t) and the fall in Gulf-origin US imports. For tariff attribution, use months up to Feb 2026; the futures and hedging analyses split the 50% regime at the closure.
- **Stale futures curve.** Daily and weekly results on `midwest_premium_curve.csv` understate and delay moves. Around the Aug 2026 Canada news, the file showed the drop two business days after the CME move and at about half its size. The weekly hedge-ratio tests should be re-run on CME AUP settlements.
- **Aug 2026 premium** is M01 on 28 Aug, so that month is not fully fixed.
- **US-located inventory.** Not on hand; there are no public US-specific stocks.

## Open work

- Re-run the event table and the weekly hedge-ratio tests on CME AUP settlements.
- Build a US import supply stack (FOB value, freight and available volume by origin, against US import demand) to test which origin sets the US price, and run differentiated-tariff scenarios (e.g. Canada 25%, others 50%).
- Compute pass-through on premiums (ΔMWP / Δparity premium) as well as on all-in prices, and the time it takes the gap to close.
- Chart Canadian FOB unit values by destination (who pays the tariff), and set the sign of the import margin against flows with a 1–2 month lag.

## Scripts

- `scripts/fetch_lme.py`: LME prices and stocks
- `scripts/fetch_usgs.py`: USGS Mineral Industry Surveys (MW premium, imports by country)
- `scripts/clean_lme_premiums.py`: LME MW premium curve and Rotterdam DP
- `scripts/clean_duty_unpaid.py`: Rotterdam DUP (investing.com export)
- `scripts/reconstruct_duty_unpaid.py`: extends DUP past Oct 2025 from DP (run after the two cleaning scripts)
- `scripts/fetch_canada_exports.py`: Canadian exports by destination from the UN Comtrade public API (no key needed; one month per call, cached in `data/raw/comtrade`)
- `scripts/build_dashboard.py`: recomputes the headline results from `data/` and writes `dashboard/index.html` from `dashboard/template.html`
