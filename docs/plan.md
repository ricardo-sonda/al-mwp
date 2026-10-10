# Plan: next steps for the Midwest premium / Section 232 project

A handoff file for picking the project up in a new session. Read `README.md` (question, method, data), `notes.md` (the user's running notes; it may have uncommitted edits, don't overwrite it) and this file before changing anything.

Last updated 10 Oct 2026 (LME / Rotterdam control for the forecast test, cells 28–30; Sep-26 / Nov-26 CME contracts added to the risk test; August 2026 event redone on CME, cells 21–22). Late 9 Oct: backtest and the Aug 2026 dashboard panel dropped; parity model limited to after 12 Mar 2025, cells 9–10.

## Context

- **Purpose.** Application project for Hydro's [Summer Internship 2027, Metal Sourcing & Trading (MST), Oslo](https://jobs.hydro.com/Hydro-Office/job/Oslo-Summer-Internship-2027-Metal-Sourcing-&-Trading%2C-Oslo-03-0283/1428803633/). **Deadline 16 Oct 2026.** The listing asks "How will Trump's tariffs influence the global metal flows?" and wants statistical modelling, trading, risk management and Python. MST optimises Hydro's global standard ingot portfolio and manages Hydro's LME price risk.
- **The user** studies Industrial Economics (CS specialisation) at NTNU, with courses in derivatives & real options, financial econometrics, statistical learning and stochastic modelling. They want advanced methods **only where they lead to an insight**, not for show. The README originally put econometrics out of scope; methods 1 and 3 below are the agreed exception.
- **Deliverables.** `notebook.ipynb` (analysis) and `memo.md` (one page, **not started**): landed cost vs actual chart, Canada-share chart, two pass-through numbers, arbitrage summary, "so what for Hydro".

## Notebook map (cell indices as of 10 Oct 2026)

| Cells | Content | Status |
|---|---|---|
| 0–3 | Imports, paths, loading | |
| 4–6 | Landed cost v1 (everything off Rotterdam DP) + takeaway | **Superseded** by cell 7; its "margin still negative" takeaway is an artefact of charging EU duty |
| 7–8 | Landed cost by route (Canada: DP − netback freight; Rotterdam: DUP), gap, pass-through β + takeaway | β is computed on all-in prices (inflated toward 1) |
| 9–10 | **Who sets the price** (added 9 Oct): Canada parity gap and Canada's US export share by regime + takeaway | Done. The parity model holds from 12 Mar 2025 |
| 11–12 | US crude imports by origin + takeaway | |
| 13 | **Note: Hormuz shock** (added 7 Oct) | Has a TODO: event line on the charts |
| 14–16 | US imports by product; semis & scrap by origin | Cell 16's conclusion rests on the 2026 window, partly Hormuz |
| 17 | Canadian HS 7601 exports by destination | |
| 18 | **Note: LME curve is the thin contract; get CME** (added 7 Oct) | |
| 19 | MW curve at month-end: M01 vs M03, slope | |
| 20 | Fixed-contract moves around six events (Δ +5d, +20d), LME curve | 2025 rows stay on the stale LME curve (no liquid CME contract on hand) |
| 21–22 | **August 2026 on CME** (added 10 Oct): Sep/Oct/Nov-26 CME vs the LME curve around 20–24 Aug + takeaway | Done |
| 23 | Tariff rate implied by import parity (actual vs forward) | |
| 24 | **Note: supply stack, needs new data** (added 7 Oct) | Not built |
| 25–27 | **Method 1: did the futures curve misprice the premium?** (added 7 Oct) | Done |
| 28–30 | **Control for method 1** (added 10 Oct): LME futures forecast errors over the same forecasts, Rotterdam DP surprise (no DP futures history), MW miss split via Canada parity + takeaway | Done; DP part is vs no change |
| 31–35 | **Risk: the tariff couples the premium to LME** (rewritten 9 Oct): mechanism and predictions, causal diagram, monthly betas with Rotterdam DP as control, CME Oct-26 futures betas with the CME Oct-26 DP contract as control (added 9 Oct), Sep-26 / Nov-26 cross-contract check (added 10 Oct), takeaway | Done |

Shared objects later cells rely on: `lme_m`, `dp_m`, `mwp_all` (USGS monthly premium to Jun 2026, then month-end M01), `tariff_rate(month, origin)`, `TARIFF_STEPS`, `FREIGHT` + `lo, mid, hi`, `r` (route frame, cell 7), `me` (month-end curve, cell 19), `by_contract` (cell 20), `lme3m_me` (cell 23), `HORMUZ` (cell 26).

## What is established

From the earlier work (details in `notes.md`):
- **Pass-through is about complete in levels.** The implied tariff rate tracks the statutory rate: ~25% in Apr–May 25, ~50% from Jul 25, on both routes.
- **The 50% step was priced on the announcement.** The Jul-25 contract was up 399 $/t five days after 4 Jun; most of the move came from the 30 May announcement.
- **Canada became the marginal tonne under 50% and got redirected.** US imports from Canada fell ~38% (224 → ~140 kt/month). Canadian exports to the Netherlands went from ~4 to ~43 kt/month. The US share of Canadian exports fell from 94% to 71% (92% at 25%, Mar–May 25, so the split came with 50%). Splitting exports means Canada was indifferent between the US and Europe, which is what makes its parity bind. Before 2025 (Canada 0%, others 10%) it was a corner: ~94% to the US and the premium above Canada parity in all 43 months from Jul 2021 (+122 to +350 $/t a year at mid freight). That is Canada earning a rent under a tariff that favours it (cells 9–10); it resolves caveat 4, and explains step 1's β of 0.56: the first 156 of the 331 $/t rise in Canada's landed cost went to wiping out the rent.
- **The curve was in backwardation through most of the 50% regime** (M03 − M01 between −120 and −230 $/t).

From the analyses added on 7 Oct:
- **Method 1 (cells 25–27).** Before the tariff, M03 was an unbiased forecast (+13 $/t, 69 forecasts). Under 50%, before Hormuz, it was too low in **7 of 7** forecasts, by **342 $/t** on average. It did worse than no change (RMSE 366 vs 252) and than Canada parity (218). The three fresh (non-stale) quotes still missed by +240. Since Hormuz there's no bias (−23, n = 4). Reading: a peso problem (priced relief that never came) or a risk premium paid by hedgers.
- **August 2026 (cells 21–22 on CME, and the supply-stack note in cell 24; not on the dashboard).** On CME, Sep/Oct/Nov-26 fell 303/331/332 $/t from 18 to 20 Aug (Sep-26 already −116 on 19 Aug) and were back within 25 $/t by 24 Aug. The LME curve was flat to 21 Aug, then fell a flat 100 $/t on 24 Aug and missed the round trip. By 16 Sep Sep-26 was +17, Oct-26 −50 and Nov-26 −100 against 18 Aug, while LME 3M rose 55 (≈ +28 at t = 50%): the further-out contracts went back to pricing relief. Canada parity falls 921 $/t at a Canada-only 25%; the CME Oct-26 contract fell 298 on 20 Aug and regained 301 on 24 Aug. The 921 is an upper bound, not the forecast: Canada exported ~202 kt/month in all under 50%, below US crude imports (~225 under 50%, ~299 before), so the last tonne would still pay 50%. The "buy M03 below parity" backtest was dropped (rule chosen after seeing the data; 11 trades from one regime).
- **Method 1 control (cells 28–30, 10 Oct).** LME forward for mid t+2 (cash–3M interpolated) vs month t+2 average cash, same 69 / 7 / 4 forecasts. Pre-tariff: unbiased (−0 $/t, RMSE 196 = no change). 50% before Hormuz: also too low, 6 of 7, +111 $/t (~4%), but that is 0.6 usual LME misses vs 3.9 for MW (~22%). DP rose in all 7 windows (+46 $/t over two months; no DP futures, so vs no change). Through parity, t × LME explains 56 and (1 + t) × DP 70 of the 342, leaving ~217 $/t (63%) US-specific, still 2.5× the usual MW miss. The two forecasts spanning Hormuz (Jan, Feb 26) are fully explained by the LME/DP jumps (residuals −70, −240), so the split behaves. Since Hormuz: residual +46, n = 4. Pending: CME Oct-26 DP was 467 on 31 Aug, 557 on 8 Oct (part-fixed); settles end Oct.
- **Risk (cells 31–35, rewritten 9 Oct; replaces the old method 3).** The story: before the tariff, LME and the premium shared only common causes; a duty on value adds a direct link, ∂MWP/∂LME = t. Monthly: the MW premium's LME beta went 0.19 → 0.30 (50%, before Hormuz) while Rotterdam DP's went 0.10 → 0.00, so the rise is US-specific; in the Hormuz months both rose (0.33, 0.26). Pooled: 0.19 + 0.46 × t (s.e. 0.20; 0.33 with ΔDP held fixed), so only about half the link shows up in the monthly physical premium. CME Oct-26 on LME 3M, Jun–Sep 26, without the 20/21/24 Aug tariff news days: β = 0.22 (1 day), 0.43 (5 days), 0.55 (10 days, s.e. 0.10) against a theory of 0.50–0.69. Control, CME Oct-26 Rotterdam DP (from 15 Jun): β = 0.00 / 0.09 / 0.04 (s.e. 0.11); MW − DP = 0.58 (s.e. 0.09) on 10 days, so the futures link is US-specific even after Hormuz. DP rose +35 $/t on 20 Aug (3× its daily s.d.) and fell 11 on 24 Aug, opposite to MW. A 0.5 t LME overlay cuts 10-day risk 110 → 65 $/t but adds risk on daily changes (the contract settles a few days behind LME). 20 Aug: −298 $/t in a day, 12× the usual daily move. Across contracts (10 Oct): Sep-26 (16 Apr – 31 Aug) β = 0.19 / 0.44 / 0.53, Nov-26 (1 Jun – 8 Oct) 0.15 / 0.42 / 0.54 (s.e. 0.10 on 10 days); same dates and LME moves, so a robustness check, not independent tests; no sign of a lower beta further out. Excluding 19 Aug as well (Sep-26 −116) changes no beta by more than 0.02. The lead-lag work from 7 Oct is dropped (peripheral).

## Data caveats (check before trusting a number)

1. **Hormuz shock from 2 Mar 2026** (cell 13). It drives the Mar–May 26 jump in DP (361 → 596 $/t) and the fall in **Gulf-origin** US imports (45 → 31 kt/month, Apr–Jun 26). It does **not** explain the fall in total crude against the pre-tariff baseline, which happened in 2025. For tariff attribution, use months up to Feb 2026.
2. **The LME MW futures curve is stale** (cell 18). M02+ are unchanged on ~81% of days since 2024. The file showed the Aug 2026 Canada-news drop two business days after the CME move, at half its size. Daily and weekly work needs CME AUP settlements (`data/midwest_premium_cme.csv`: Sep, Oct and Nov-26; Barchart allows one contract download a day). In Aug 2026 the curve stayed flat while CME fell ~330 $/t and recovered, then fell a flat 100 on 24 Aug (cells 21–22).
3. **DUP after Oct 2025 is reconstructed from DP** (`scripts/reconstruct_duty_unpaid.py`), with an error of about ±13 $/t, and much worse in Feb–May 2025.
4. **Freight is assumed.** Post-tariff gaps inside the freight band are not arbitrage. The pre-2025 gap (+210 $/t at mid freight, +160 at the highest, positive in all 43 months) is resolved (cells 9–10, 9 Oct): under the two-tier tariff Canada earned a rent and wasn't the price-setter, so the parity model applies only from 12 Mar 2025.
5. **Duty basis.** The README says ad valorem on customs value throughout for HTS 7601. `notes.md` says it was weight-based until Apr 2026. Settle this from the proclamation text. The risk section's positive LME beta fits a duty on value, but the CME data all postdate 2 Apr 2026, and the monthly pre-April evidence is weak.
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
- [ ] Add the 2 Mar 2026 Hormuz event line to the existing charts and split the "Apr–Jun 26" windows (the TODO in cell 13).
- [ ] Mark cell 5 as superseded (cell 8's takeaway is filled in, 9 Oct).
- [ ] Cite freight sources and settle the duty basis from the proclamation text.

### B. Memo (`memo.md`, one page)
- [ ] Two pass-through numbers; landed cost vs actual chart; Canada-share chart; when arbitrage was open or shut, and why.
- [ ] "So what for Hydro": the exposure map (question 2 below), the forecast-bias finding (method 1) and the risk finding (premium positions carry ~t of LME; the overlay can't hedge tariff news).
- [ ] State the limits: Hormuz confound, stale curve, assumed freight.

### C. Needs new data (the user is looking into these)
- [ ] **CME AUP settlements** (Aluminum MW U.S. Transaction Premium Platts). Sep-26, Oct-26 and Nov-26 MW are in (`scripts/clean_comex.py`, used in cells 21 and 31), plus the Oct-26 Rotterdam DP contract (Barchart root IED) as control; the August event is redone on CME. Next, if wanted: contracts that traded around the 2025 steps (e.g. Jul-25, Sep-25) to redo the 2025 event rows. A Sep-26 / Nov-26 DP control would match the new MW contracts. For a real DP leg in the method-1 control (cells 28–30), get the LME ED **daily closing prices** workbook (the counterpart of the MW `UP` file; the repo only has ED final settlements) or a run of past CME IED contracts; no DUP futures are in the repo either. It also unlocks method 2.
- [ ] **US import supply stack** (cell 24 lists the data): FOB value by origin (USITC DataWeb or Comtrade US imports with values; the same API as `scripts/fetch_canada_exports.py`), freight by origin, available volume by origin (exports to the world), and US import demand (USGS). Rank origins by landed cost, cross with demand, and run scenarios: Canada 25% / others 50%, everyone 25%, Gulf back.

### D. Optional methods (not built; good interview material even if unbuilt)
- **Method 2: market-implied probability of tariff relief** (derivatives / stochastic). Treat a cut as a Poisson jump with intensity λ(t): F(T) = P50(T) − Pr(cut by T) · [P50(T) − Pcut(T)]. Bootstrap λ from M01–M06 like a CDS hazard curve. Pcut(T) must come from the supply stack, not Canada parity: a naive Canada-marginal version gave 0–37% per two months and went negative. It also needs CME data. The 20–21 Aug 2026 before/after is the case study: at Aug levels, Canada parity is 2,326 $/t at 50% and 1,405 at 25% (a ~920 $/t gap), while the CME Oct-26 contract fell 298 on 20 Aug (settlements).
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
   - LME: about 1.3–1.5× cover for US-delivered metal, and ~t of LME per tonne inside any premium position (risk section).
   - Regional premiums: CME/LME futures are thin beyond the front months and policy moves come as jumps. The practical tools are contract structure (fixed vs index-linked premium), natural offsets between segments, and destination flexibility.
   - Also: LME time spreads at low stocks, and the low-carbon premium / CBAM (slow-moving; CBAM costs phase in from 2026).
4. **Supply chain.**
   - Qatalum and Hormuz: output, exports and alumina inputs all go through the strait. How fast does Gulf metal return, and to which region? The DP − MWP spread is the one to watch in H1 2027.
   - US–Canada escalation: demand risk for the US extrusion plants.
   - Integrated margin: alumina vs aluminium.

## How to work on the notebook

- **Style.** Constants are in cells 5 and 7: `BLUE #2a78d6`, `ORANGE #eb6834`, `GREEN #1baf7a`, `INK #333333`, `MUTED #8a8a85` (a validated colour-blind-safe palette). Two-panel figures are 11×8 with `height_ratios=[3, 2]`, y-grid `#e5e5e0`, top/right spines off, dotted event lines with rotated labels. Each analysis is followed by a markdown "Takeaway" cell with the numbers.
- **Execution.** The notebook has been run with nbclient. To keep diffs small, the 7 Oct changes executed a copy and transplanted outputs into the new cells only; existing cells kept their stored outputs. A full re-run (`jupyter nbconvert --to notebook --execute --inplace notebook.ipynb`) also works, but rewrites every cell's output. Cells 26, 33 and 34 need `statsmodels`. The 9 Oct risk rewrite was executed the same way. `scripts/fetch_lme.py` with no arguments fetches 2024 onwards and **overwrites** `lme_aluminium.csv`; run `python scripts/fetch_lme.py 2018 2026`.
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
