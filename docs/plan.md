# Plan: next steps for the Midwest premium / Section 232 project

A handoff file for picking the project up in a new session. Read `README.md` (question, method, data), `notes.md` (the user's running notes; it may have uncommitted edits, don't overwrite it) and this file before changing anything.

Last updated 7 Oct 2026.

## Context

- **Purpose.** Application project for Hydro's [Summer Internship 2027, Metal Sourcing & Trading (MST), Oslo](https://jobs.hydro.com/Hydro-Office/job/Oslo-Summer-Internship-2027-Metal-Sourcing-&-Trading%2C-Oslo-03-0283/1428803633/). **Deadline 16 Oct 2026.** The listing asks "How will Trump's tariffs influence the global metal flows?" and wants statistical modelling, trading, risk management and Python. MST optimises Hydro's global standard ingot portfolio and manages Hydro's LME price risk.
- **The user** studies Industrial Economics (CS specialisation) at NTNU, with courses in derivatives & real options, financial econometrics, statistical learning and stochastic modelling. They want advanced methods **only where they lead to an insight**, not for show. The README originally put econometrics out of scope; methods 1 and 3 below are the agreed exception.
- **Deliverables.** `notebook.ipynb` (analysis) and `memo.md` (one page, **not started**): landed cost vs actual chart, Canada-share chart, two pass-through numbers, arbitrage summary, "so what for Hydro".

## Notebook map (cell indices as of 7 Oct 2026)

| Cells | Content | Status |
|---|---|---|
| 0–3 | Imports, paths, loading | |
| 4–6 | Landed cost v1 (everything off Rotterdam DP) + takeaway | **Superseded** by cell 7; its "margin still negative" takeaway is an artefact of charging EU duty |
| 7–8 | Landed cost by route (Canada: DP − netback freight; Rotterdam: DUP), gap, pass-through β | β is computed on all-in prices (inflated toward 1). Cell 8 takeaway still "to fill in" |
| 9–10 | US crude imports by origin + takeaway | |
| 11 | **Note: Hormuz shock** (added 7 Oct) | Has a TODO: event line on the charts |
| 12–14 | US imports by product; semis & scrap by origin | Cell 14's conclusion rests on the 2026 window, partly Hormuz |
| 15 | Canadian HS 7601 exports by destination | |
| 16 | **Note: LME curve is the thin contract; get CME** (added 7 Oct) | |
| 17 | MW curve at month-end: M01 vs M03, slope | |
| 18 | Fixed-contract moves around six events (Δ +5d, +20d) | Uses stale LME settlements; re-run on CME |
| 19 | Tariff rate implied by import parity (actual vs forward) | |
| 20 | **Note: supply stack, needs new data** (added 7 Oct) | Not built |
| 21–23 | **Method 1: did the futures curve misprice the premium?** (added 7 Oct) | Done |
| 24–26 | **Method 3: hedge ratio under an ad valorem tariff** (added 7 Oct) | Done; weekly parts need CME |

Shared objects later cells rely on: `lme_m`, `dp_m`, `mwp_all` (USGS monthly premium to Jun 2026, then month-end M01), `tariff_rate(month, origin)`, `TARIFF_STEPS`, `FREIGHT` + `lo, mid, hi`, `r` (route frame, cell 7), `me` (month-end curve, cell 17), `by_contract` (cell 18), `lme3m_me` (cell 19), `HORMUZ` (cell 22).

## What is established

From the earlier work (details in `notes.md`):
- **Pass-through is about complete in levels.** The implied tariff rate tracks the statutory rate: ~25% in Apr–May 25, ~50% from Jul 25, on both routes.
- **The 50% step was priced on the announcement.** The Jul-25 contract was up 399 $/t five days after 4 Jun; most of the move came from the 30 May announcement.
- **Canada was the marginal tonne and got redirected.** US imports from Canada fell ~38% (224 → ~140 kt/month). Canadian exports to the Netherlands went from ~4 to ~43 kt/month. The US share of Canadian exports fell from 94% to 71%.
- **The curve was in backwardation through most of the 50% regime** (M03 − M01 between −120 and −230 $/t).

From the analyses added on 7 Oct:
- **Method 1 (cells 21–23).** Before the tariff, M03 was an unbiased forecast (+13 $/t, 69 forecasts). Under 50%, before Hormuz, it was too low in **7 of 7** forecasts, by **342 $/t** on average. It did worse than no change (RMSE 366 vs 252) and than Canada parity (218). The three fresh (non-stale) quotes still missed by +240. Since Hormuz there's no bias (−23, n = 4). The rule "buy M03 when below Canada parity" fired 11 times, all after Jun 2025, at +276 $/t per trade, so it is really a bet on one regime. Reading: a peso problem (priced relief that never came) or a risk premium paid by hedgers.
- **Method 3 (cells 24–26).** The residual monthly risk of a 1:1 LME hedge on US-delivered metal rose from **50 to 90 $/t**. The monthly hedge ratio is 1.32–1.36 at 50% against a theory of 1 + t = 1.5, but it was already 1.22 pre-tariff, ~1.6 in the 2021 rally and ~1.0 in 2024. So it isn't only the tariff. Pooled premium LME beta = 0.21 + 0.54 × t (s.e. 0.28). The weekly MW curve picks up LME moves with a lag: β ≈ 0 within a week, 0.70 over 8 weeks (50%, before Hormuz). This week's LME move predicts the next 4 weeks of MW futures moves (pre-tariff 0.18, s.e. 0.04). The weekly results are on stale LME settlements and must be re-run on CME.

## Data caveats (check before trusting a number)

1. **Hormuz shock from 2 Mar 2026** (cell 11). It drives the Mar–May 26 jump in DP (361 → 596 $/t) and the fall in **Gulf-origin** US imports (45 → 31 kt/month, Apr–Jun 26). It does **not** explain the fall in total crude against the pre-tariff baseline, which happened in 2025. For tariff attribution, use months up to Feb 2026.
2. **The LME MW futures curve is stale** (cell 16). M02+ are unchanged on ~81% of days since 2024. The file showed the Aug 2026 Canada-news drop two business days after the CME move, at half its size. Daily and weekly work needs CME AUP settlements.
3. **DUP after Oct 2025 is reconstructed from DP** (`scripts/reconstruct_duty_unpaid.py`), with an error of about ±13 $/t, and much worse in Feb–May 2025.
4. **Freight is assumed.** Before 2025 the Canada route sat 80–180 $/t above parity at a 0% tariff, the same size as the freight band. This baseline needs explaining before small post-tariff gaps can be read as arbitrage.
5. **Duty basis.** The README says ad valorem on customs value throughout for HTS 7601. `notes.md` says it was weight-based until Apr 2026. Settle this from the proclamation text. Method 3 fits ad valorem, but the evidence is weak.
6. **Aug 2026 premium** = M01 on 28 Aug, so the month is not fully fixed.
7. **β in cell 7 is computed on all-in prices**, so LME sits on both sides and pulls it toward 1. Recompute it on premiums (ΔMWP / Δparity premium).

## Market context (Oct 2026)

- **Hormuz.** Iran closed the strait on 2 Mar 2026. Qatalum (50% Hydro, 648 kt/yr) shut on 3 Mar for lack of gas, and has run at ~60% since 12 Mar. EGA (Al Taweelah) and Alba were hit. Gulf supply is ~9% of the world's. A ceasefire then partly reopened the strait (Hydro Q2 report). Mozal (~570 kt, Europe-oriented) went into care and maintenance in the same period.
- **US–Canada.** On 20 Aug 2026 the US signalled a cut for Canada from 50% to 25%. The CME Sep contract fell 8.2% to 95 c/lb, and Oct/Nov fell more than 12%. The deal collapsed on 21–22 Aug. Escalation followed (from `notes.md`: Section 338 tariffs, Canadian counter-tariffs, a 29 Sep import ban, October layoffs in cross-border auto lines).
- **Alcoa's argument** (14 Sep). The US needs ~4 Mt/yr of imports and Canada can supply ~3 Mt, so a Canada-only cut wouldn't lower the MW premium much.
- **Europe.** On 21 Aug, Rotterdam DP was 460–465 and DUP 420–470 $/t. Producers expected DP to firm and DUP to soften if Canadian metal went back to the US (Fastmarkets, 24 Aug).
- **Hydro Q2 2026.** Metal Markets adjusted EBITDA was NOK 32m vs 276m a year earlier, on weaker sourcing and trading results (MST's own P&L). Extrusions rose to NOK 1,463m, helped by North American recycling. Bauxite & Alumina fell to NOK 522m from 1,521m on lower alumina prices. The average Q2 MW premium was ~$2,518/t, against $2,292 in Q1 (earnings call).
- **Hydro's exposures relevant here.** Norwegian smelters sell into Europe (DP); Alouette 20% (Québec, the Canada → US route); Qatalum 50% (Hormuz); US extrusion and recycling plants buy at LME + MWP.

## To do, in priority order

### A. Fixes already listed in `notes.md` (do first; no new data)
- [ ] Recompute pass-through as ΔMWP / Δparity premium (cell 7). Use short windows (e.g. Jul–Sep 25 for step 2) and report the time for the gap to close.
- [ ] Chart Canadian FOB unit value by destination; this is the incidence question, "who pays the tariff". The unit value to the US fell from ~LME + 450–600 to ~LME + 0–250 at 50%, then jumped in mid-2026. Caveats: contract lags, product mix, odd Netherlands unit values.
- [ ] Set the sign of the gap against flows with a 1–2 month lag (the core of the arbitrage summary).
- [ ] Decompose monthly gap changes into ΔMWP, ΔDP/DUP, ΔLME × t and Δtariff.
- [ ] Add the 2 Mar 2026 Hormuz event line to the existing charts and split the "Apr–Jun 26" windows (the TODO in cell 11).
- [ ] Mark cell 5 as superseded and fill in cell 8's takeaway.
- [ ] Cite freight sources and settle the duty basis from the proclamation text.

### B. Memo (`memo.md`, one page)
- [ ] Two pass-through numbers; landed cost vs actual chart; Canada-share chart; when arbitrage was open or shut, and why.
- [ ] "So what for Hydro": the exposure map (question 2 below), the forecast-bias finding (method 1) and the hedge-ratio finding (method 3).
- [ ] State the limits: Hormuz confound, stale curve, assumed freight.

### C. Needs new data (the user is looking into these)
- [ ] **CME AUP settlements** (Aluminum MW U.S. Transaction Premium Platts). Then re-run the cell 18 event table and cell 25 parts B and C, and it unlocks method 2.
- [ ] **US import supply stack** (cell 20 lists the data): FOB value by origin (USITC DataWeb or Comtrade US imports with values; the same API as `scripts/fetch_canada_exports.py`), freight by origin, available volume by origin (exports to the world), and US import demand (USGS). Rank origins by landed cost, cross with demand, and run scenarios: Canada 25% / others 50%, everyone 25%, Gulf back.

### D. Optional methods (not built; good interview material even if unbuilt)
- **Method 2: market-implied probability of tariff relief** (derivatives / stochastic). Treat a cut as a Poisson jump with intensity λ(t): F(T) = P50(T) − Pr(cut by T) · [P50(T) − Pcut(T)]. Bootstrap λ from M01–M06 like a CDS hazard curve. Pcut(T) must come from the supply stack, not Canada parity: a naive Canada-marginal version gave 0–37% per two months and went negative. It also needs CME data. The 20–21 Aug 2026 before/after is the case study: at Aug levels, Canada parity is 2,326 $/t at 50% and 1,405 at 25% (a ~920 $/t gap), while the CME deferred contracts fell only ~270.
- **Method 4: band threshold autoregression on the import margin** (law of one price with trade costs). The gap wanders inside a band set by trade costs and reverts outside it. The band width estimates the trade cost that the freight assumptions can't (caveat 4); the half-life answers "how long does the gap take to close". Monthly data has weak power, so use it as a robustness check.
- **Method 5: real-option value of destination flexibility** (derivatives & real options). An uncommitted tonne is an option on S = netback_US − netback_EU. Model S as mean-reverting with policy jumps, fit it to the monthly history, and compare E[max(S, 0)] with E[S]. This gives the cost of committing tonnes to a fixed-destination 2027 term contract (Q4 is contract season). Add-on: a partial-adjustment regression of Canada's US share on the lagged gap; the adjustment speed ≈ 1 / average contract length, which explains the sticky ~140 kt/month still going to the US.
- **LME time spreads against stocks** (Working storage curve). LME stocks fell from ~560 kt to ~240 kt. Cash, 3M and stocks are already on hand.
- **Skip:** machine-learning forecasts of the premium (~70 monthly observations, several breaks), large VARs, GARCH on stale futures.

## Next questions for MST (for the memo's "so what" and the interview)

1. **Which origin sets the US price?** If not Canada, a Canada-only cut is a windfall for Canadian smelters (Alouette included), not a price cut for US buyers. With every origin at 50% the data can't tell; it only matters under a differentiated tariff.
2. **Is Hydro net long or short a Canada tariff cut?** This is inferred from public information; check volumes in the annual report.
   - European sales would likely gain, because Canadian metal returns to the US and DP firms.
   - Alouette gains.
   - US extrusion plants pass the metal price through, so only timing effects.
   - US recyclers likely lose, because the scrap-to-billet spread scales with the MW premium.
3. **Which spreads can be hedged?**
   - LME: about 1.3–1.5× cover for US-delivered metal (method 3).
   - Regional premiums: CME/LME futures are thin beyond the front months and policy moves come as jumps. The practical tools are contract structure (fixed vs index-linked premium), natural offsets between segments, and destination flexibility.
   - Also: LME time spreads at low stocks, and the low-carbon premium / CBAM (slow-moving; CBAM costs phase in from 2026).
4. **Supply chain.**
   - Qatalum and Hormuz: output, exports and alumina inputs all go through the strait. How fast does Gulf metal return, and to which region? The DP − MWP spread is the one to watch in H1 2027.
   - US–Canada escalation: demand risk for the US extrusion plants.
   - Integrated margin: alumina vs aluminium.

## How to work on the notebook

- **Style.** Constants are in cells 5 and 7: `BLUE #2a78d6`, `ORANGE #eb6834`, `GREEN #1baf7a`, `INK #333333`, `MUTED #8a8a85` (a validated colour-blind-safe palette). Two-panel figures are 11×8 with `height_ratios=[3, 2]`, y-grid `#e5e5e0`, top/right spines off, dotted event lines with rotated labels. Each analysis is followed by a markdown "Takeaway" cell with the numbers.
- **Execution.** The notebook has been run with nbclient. To keep diffs small, the 7 Oct changes executed a copy and transplanted outputs into the new cells only; existing cells kept their stored outputs. A full re-run (`jupyter nbconvert --to notebook --execute --inplace notebook.ipynb`) also works, but rewrites every cell's output. Cells 22 and 25 need `statsmodels`.
- **Data rules.** Don't sum `Total` / `Other` (US imports) or `World` (Canada exports) rows with countries. The monthly MW premium is USGS to Jun 2026 and then month-end M01 (`mwp_all`). DP starts Jul 2021, so parity-based series start there.

## Sources

- [Hydro: Summer Internship 2027, MST](https://jobs.hydro.com/Hydro-Office/job/Oslo-Summer-Internship-2027-Metal-Sourcing-&-Trading%2C-Oslo-03-0283/1428803633/)
- [Hydro Q2 2026 results](https://www.hydro.com/en/global/media/news/2026/hydros-second-quarter-2026-operational-strength-delivering-solid-results/)
- [Hydro Q2 2026 earnings call transcript (Investing.com)](https://ph.investing.com/news/transcripts/earnings-call-transcript-norsk-hydro-posts-solid-q2-2026-results-as-shares-rise-93CH-2502596)
- [SMM: Qatalum shifts from full shutdown to 60% capacity](https://news.metal.com/newscontent/103806228-qatalum-shifts-from-full-shutdown-to-60-capacity-operational-update-amid-strait-of-hormuz-disruption)
- [CNBC: Aluminum prices rise after Iran attacks Gulf smelters (30 Mar 2026)](https://www.cnbc.com/2026/03/30/iran-attacks-aluminum-producers-shockwaves-market-metals.html)
- [Fastmarkets: European market watchful of proposed US-Canada tariff reduction (24 Aug 2026)](https://www.fastmarkets.com/insights/european-aluminium-market-watchful-of-proposed-us-canada-tariff-reduction/)
- [AlCircle: Alcoa says Canada tariff cut alone won't bring US premium down (14 Sep 2026)](https://www.alcircle.com/news/alcoa-says-canada-tariff-cut-alone-won-t-bring-us-aluminium-premium-down-121173)
- [AEGIS Hedging: Metals First Look, 21 Aug 2026](https://aegis-hedging.com/insights/metals/daily-first-look/2026-08-21)
- [Mysteel: how regional premiums reshaped markets](https://www.mysteel.net/news/5138322-eu-canada-and-asia-aluminium-prices-why-3-386t-benchmark-can-cost-5-792t-read-how-regional-premiums-reshaped-markets)
