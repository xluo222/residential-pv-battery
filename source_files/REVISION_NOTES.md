# Revision Notes for the Residential PV–Battery Manuscript

## Purpose and file status

The original manuscript remains unchanged in [main.tex](main.tex).

Two new synchronized drafts were created:

- [main_revised_ieee.tex](main_revised_ieee.tex): corrected IEEE-style LaTeX draft.
- [manuscript_revised.md](manuscript_revised.md): readable Markdown version of the revised draft.

The revised files correct statements that can be verified directly from the repository, narrow unsupported claims, add the implemented mathematical formulation, and clearly disclose unresolved issues. **They are not submission-ready yet.** The current numerical results must be regenerated after preprocessing and model revisions.

## Overall recommendation

**Current decision:** Major revision required before submission to an IEEE PES journal.

The topic is relevant, but the current study is a seasonal representative-day screening exercise, not a full economic-feasibility or annual battery-sizing study. The strongest publication path is to convert the model to a chronological annual analysis, harmonize all data definitions, rerun the model, add uncertainty and sensitivity analysis, and then update the manuscript with the new results.

Also verify the exact target journal. “IEEE PES Transactions on Renewables” is not a complete journal title. If the intended venue is *IEEE Transactions on Sustainable Energy*, download and follow that journal’s current author instructions before final formatting.

---

# 1. Corrections already applied in the revised drafts

| Priority | Original location | Problem | Adjustment made |
|---|---|---|---|
| Critical | [Original document class](main.tex#L1) | The original uses the IFAC conference class at 14 pt, not an IEEE journal template. | Changed the revision draft to the generic IEEE journal class. The exact target-journal template still needs confirmation. |
| Critical | [Original title command](main.tex#L5) | `\maketitle` appears before `\begin{document}` and before title/author definitions. | Moved title generation to the correct position after `\begin{document}` and the title/author definitions. |
| Major | [Duplicate caption setup](main.tex#L2), [second caption setup](main.tex#L15) | The `caption` package is loaded twice with conflicting options and is generally not recommended with IEEEtran. | Removed both package declarations from the revised IEEE draft. |
| Critical | [PV description](main.tex#L76) | The paper says 6 kW and 25°, but the saved PVWatts response records 12 kW and 30°. | Revised the data section to report the repository-backed 12 kW and 30° values. |
| Critical | [Archived PV capacity](../savings_model/pvwatts_raw_response.json#L5), [archived tilt](../savings_model/pvwatts_raw_response.json#L6) | These are the parameters that generated the saved PV profile. | Cited these implemented values in the revised methodology. |
| Critical | [Candidate sizes in original methods](main.tex#L147) | The methods list 16 kWh, while the code and later discussion use 18 kWh. | Corrected the set to 4, 6, 10, 12, 14, 18, and 20 kWh, matching the code. |
| Major | [Load-profile caption](main.tex#L72) | The figure is called Fourier-smoothed, but the plotted and optimized series use arithmetic hourly means. | Corrected the caption and data description. |
| Major | [Original annual-result description](main.tex#L150), [annual table rows](main.tex#L165) | A single representative seasonal day multiplied by 365 is not an annual simulation. | Removed “annual net benefit” from the revised results and retained only representative-day metrics plus the annualized capital charge. |
| Major | Original cost-minimization section | The paper describes the model only in prose and omits the complete optimization formulation. | Added the objective, variables, state equation, power and state limits, energy balance, PV-only restriction, cyclic condition, capital recovery factor, and net-benefit equation. |
| Major | Original title and conclusions | “Economic feasibility of PV-battery colocation” implies that both PV and battery investment costs are evaluated. The code assumes PV already exists and excludes PV cost. | Narrowed the title and conclusions to incremental battery sizing for an existing PV system. |
| Major | Original results interpretation | The manuscript calls 12 kWh the summer optimum without emphasizing its near-tie with 14 kWh. | Added the $0.004/day difference and stated that it is not a robust preference without sensitivity analysis. |
| Major | Original discussion | It says late-summer export credits can exceed retail import rates. The saved maximum is about $0.474/kWh, below the $0.716/kWh summer peak import rate. | Replaced the claim with a direct comparison of the saved export and peak import rates. |
| Minor | [Duplicated export-credit paragraph](main.tex#L116) | The opening explanation appears twice. | Removed the duplication in the revised draft. |
| Minor | [Citation placeholder](main.tex#L46) | “(Stanford paper)” is an informal placeholder. | Removed the placeholder; the associated paper remains cited normally. |
| Minor | Throughout the original | Grammar problems include “was ran,” subject–verb disagreement, missing spaces, and repetitive wording. | Rewrote the affected passages in concise technical prose. |
| Minor | Original results | “Table 2” is hard-coded. | Replaced hard-coded numbering with a LaTeX cross-reference. |

---

# 2. Blocking technical revisions requiring a rerun

These changes affect the numerical validity of the reported 12 kWh and 10 kWh screening results. They cannot be fixed through editing alone.

## 2.1 Harmonize seasonal month definitions

The data pipeline currently combines different definitions of summer and winter:

- Load preprocessing uses June–August for summer and December–February for winter in [fourier_load.py](../savings_model/fourier_load.py#L44).
- PV preprocessing uses June–October for summer and November–May for winter in [solar_generation_profiles.py](../savings_model/solar_generation_profiles.py#L100).
- Export-credit preprocessing uses June–August for summer and December–February for winter in [export_prices.py](../savings_model/export_prices.py#L23-L29).
- Import prices use a summer or winter weekday function selected outside the timestamped data rather than applying one authoritative calendar definition.

**Required action:** Choose season definitions from the applicable SDG&E tariff, use the same date classification for load, PV, import prices, and export credits, regenerate all CSV files and figures, and rerun both optimization cases.

**Preferred action:** Avoid separate seasonal files and construct one timestamp-aligned annual table in which each hour receives its actual season, day type, import price, and export credit.

## 2.2 Apply a consistent weekday/weekend treatment

The current representative profiles are not filtered consistently:

- Load averages all days in each three-month season.
- PV is filtered to nominal weekdays in [solar_generation_profiles.py](../savings_model/solar_generation_profiles.py#L97-L107).
- Export credits average all available dates.
- The optimization applies weekday import-price schedules.

In addition, the PVWatts typical-year values are assigned to a synthetic 2025 calendar. A weekday label on a typical meteorological year is not inherently meaningful unless the calendar mapping is justified.

**Required action:** Either:

1. build a chronological annual model and apply weekday/weekend tariffs by timestamp, or
2. build internally consistent representative weekday and weekend profiles and weight each one by the number of corresponding days.

Do not state that all profiles are weekday profiles until the pipeline actually applies the same day-type filter to every source.

## 2.3 Decide whether the intended PV size is 6 kW or 12 kW

The original manuscript says 6 kW in [main.tex](main.tex#L76), but the generation call requests 12 kW in [solar_generation_profiles.py](../savings_model/solar_generation_profiles.py#L84), and the archived response confirms 12 kW in [pvwatts_raw_response.json](../savings_model/pvwatts_raw_response.json#L5).

**Required action:** Make an explicit research decision:

- If 12 kW is intended, justify that size for the modeled load and run PV-size sensitivity cases.
- If 6 kW is intended, request or generate a 6 kW PVWatts profile and recompute every table, figure, and result.

The revised draft currently reports 12 kW only because that is what generated the saved results; it should not be treated as a final design choice.

## 2.4 Replace seasonal “optimal sizes” with one annual investment decision

A homeowner purchases one battery for all seasons. Separate 12 kWh summer and 10 kWh winter selections do not directly answer the investment question.

**Required action:** Optimize dispatch over all 8760 hours and select one capacity using annual operating savings minus annualized ownership cost. At minimum, use appropriately weighted representative days for summer weekdays, summer weekends, winter weekdays, and winter weekends.

Do not multiply either representative-day net benefit by 365. That would repeat one seasonal day over the full year and produce a misleading annual estimate.

## 2.5 Expand or optimize the battery-capacity search

The current code evaluates only seven sizes in [summer_cost_optimization.py](../savings_model/summer_cost_optimization.py#L170) and [winter_cost_optimization.py](../savings_model/winter_cost_optimization.py#L170). The grid skips 8 kWh and 16 kWh and jumps from 14 to 18 kWh.

**Required action:** Use one of these approaches:

- evaluate a fine grid, such as 0–25 kWh in 0.25 or 0.5 kWh increments;
- formulate capacity as a planning variable if the cost and power relations remain linear; or
- evaluate actual commercial battery configurations and report the corresponding usable energy and inverter ratings.

Include a zero-battery candidate explicitly. For a feasibility claim, “do not install storage” must be a possible investment decision.

---

# 3. Major methodological revisions

## 3.1 Add battery degradation and replacement economics

The current model assumes unchanged energy capacity, power, and efficiency for ten years. Cycling and calendar aging may materially change storage value.

At minimum, add sensitivity cases for:

- annual capacity fade;
- cycle-throughput cost or degradation cost per discharged kWh;
- end-of-life usable-capacity threshold;
- replacement timing, if applicable;
- residual value at the analysis horizon.

For a stronger paper, include a degradation state or use an empirically supported throughput model.

## 3.2 Correct and document incentive treatment

The code subtracts a flat $200/kWh incentive in [summer_cost_optimization.py](../savings_model/summer_cost_optimization.py#L19-L25) and [winter_cost_optimization.py](../savings_model/winter_cost_optimization.py#L19-L25). Eligibility, incentive category, budget availability, and interaction with federal tax credits are not demonstrated.

**Required action:**

- cite the official SGIP source and applicable 2026 category;
- state whether the modeled household qualifies;
- cap or structure the incentive exactly as required by the program;
- distinguish rebates from tax credits;
- either implement the federal credit or remove text implying that it is included; and
- include with-incentive and without-incentive sensitivity cases.

The revised draft states that no separate federal credit is implemented.

## 3.3 Represent total ownership cost consistently

The current model sets fixed installation cost to zero in [summer_cost_optimization.py](../savings_model/summer_cost_optimization.py#L16) and [winter_cost_optimization.py](../savings_model/winter_cost_optimization.py#L16).

A fixed cost may not change the best positive capacity when comparing only battery sizes, but it changes the decision between installing and not installing a battery. Therefore it cannot be omitted from a full feasibility claim.

Add or justify:

- fixed installation and permitting costs;
- inverter or hybrid-inverter cost;
- operation and maintenance cost;
- replacement cost;
- taxes and financing treatment;
- residual value; and
- any relevant utility fixed charges.

PV capital cost must also be included if the final paper continues to claim feasibility of a new combined PV–battery system. Otherwise, retain the narrower “battery added to existing PV” framing.

## 3.4 Validate dispatch behavior

The linear model does not explicitly prevent simultaneous charging and discharging or simultaneous importing and exporting. Such behavior may be naturally discouraged by efficiency losses and price relationships, but that should be verified rather than assumed.

**Required action:**

- save hourly dispatch for every tested capacity;
- assert energy-balance and state-transition residuals within a stated tolerance;
- check all hours for simultaneous charge/discharge and import/export;
- report solver name, version, status, and optimality tolerance;
- fail the script if the solver status is not optimal or acceptably optimal; and
- compare with a mixed-integer non-simultaneity formulation for selected cases.

The present scripts call the default solver without checking status in [summer_cost_optimization.py](../savings_model/summer_cost_optimization.py#L111) and [winter_cost_optimization.py](../savings_model/winter_cost_optimization.py#L111).

## 3.5 Clarify the export restriction

The implemented constraint is

$$
c_t+g_t^{\mathrm{exp}}\le p_t^{\mathrm{PV}}.
$$

It appears in [summer_cost_optimization.py](../savings_model/summer_cost_optimization.py#L95-L97) and [winter_cost_optimization.py](../savings_model/winter_cost_optimization.py#L95-L97). It prevents direct grid charging and prevents exports from exceeding contemporaneous PV production. Consequently, stored battery energy cannot be exported after sunset under the model.

**Required action:** Confirm that this reflects the intended interconnection and compensation rules. Then align every statement in the paper with the implemented architecture. If battery export is allowed and compensated, model the source of exported energy and the applicable tariff explicitly.

## 3.6 Add inverter and interconnection limits

The present model scales charge and discharge power as half of battery capacity but does not represent:

- PV inverter AC rating;
- battery inverter rating independent of energy capacity;
- shared-inverter limits for DC coupling;
- point-of-common-coupling import/export limits;
- clipping; or
- conversion losses beyond battery charge/discharge efficiency.

Add the relevant limits or state that the system is an idealized AC-balance model. Cite the 0.5C assumption and test alternatives.

## 3.7 Add household and weather variability

One synthetic EnergyPlus home and one typical meteorological year cannot establish a robust regional recommendation.

Recommended minimum extensions:

- low, base, and high residential load profiles already available in the repository;
- multiple PV-to-load ratios;
- multiple weather years or uncertainty bands;
- bootstrap or scenario analysis for hourly load and solar; and
- results reported as distributions or robust ranges rather than one point estimate.

## 3.8 Add benchmarks

Compare optimized dispatch against at least:

1. PV without a battery;
2. a self-consumption rule that charges from PV surplus and discharges to load;
3. a TOU rule-based controller; and
4. perfect-foresight optimization.

This will show the value of optimization itself rather than only the value of storage.

---

# 4. Sensitivity analyses expected for a journal paper

At minimum, report one-at-a-time and selected multi-parameter sensitivities for:

| Parameter | Suggested range or scenarios |
|---|---|
| PV size | Include 6 kW, 8 kW, 10 kW, and 12 kW or normalize by annual load |
| Battery cost | Low/base/high installed $/kWh |
| Fixed installation cost | Zero and evidence-based installed-cost scenarios |
| Incentive | No incentive and eligible SGIP cases |
| Discount rate | For example, 3%, 7%, and 10% |
| Lifetime | For example, 8, 10, and 15 years |
| Round-trip efficiency | Evidence-based low/base/high values |
| C-rate | Commercially realistic alternatives |
| Degradation | None, moderate, and high degradation |
| Import tariff | Current tariff plus plausible escalation or alternative SDG&E plans |
| Export credit | Individual years rather than only a 2026–2028 average |
| Load | Low/base/high homes and different electrification levels |
| Backup reserve | 0%, 20%, and another justified minimum state of charge |

Present a break-even battery installed cost and a robustness interval for the selected capacity. Given the current summer difference of only $0.004/day between 12 and 14 kWh, a single deterministic point estimate is not persuasive.

---

# 5. Data and reproducibility revisions

## 5.1 Add primary data citations

The existing [references.bib](references.bib) mainly contains related literature. Add official sources for:

- OEDI/ResStock or the exact residential load dataset;
- EnergyPlus and the building archetype;
- NREL PVWatts Version 8 and NSRDB;
- the exact SDG&E tariff and effective date;
- CPUC/SDG&E NBT export-credit data;
- the SGIP incentive assumption;
- battery installed cost;
- battery life, efficiency, and C-rate assumptions; and
- the IEEE target journal’s required data/software statement, if applicable.

Every externally sourced number should have a citation adjacent to the claim.

## 5.2 Correct the PVWatts fallback behavior

When no API key is present, [solar_generation_profiles.py](../savings_model/solar_generation_profiles.py) loads the archived JSON file and silently ignores the function arguments. A user could request 6 kW while unknowingly receiving the saved 12 kW output.

**Required action:** Read and validate the archived input parameters against the requested arguments, or make the fallback function accept no configurable arguments and clearly report the archived configuration.

## 5.3 Create a reproducible pipeline

The scripts depend on being launched from the savings_model directory and use duplicated summer/winter optimization code.

Recommended changes:

- create one configuration file for location, season rules, tariff, PV, battery, and financial assumptions;
- combine the duplicated optimization scripts into one tested module;
- construct paths relative to the module or repository root;
- add a pinned dependency file;
- save solver and package versions;
- add unit tests for tariff mapping, seasonal mapping, energy balance, and annualization;
- create one command that regenerates all profiles, optimization outputs, figures, and manuscript tables; and
- record data provenance and checksums for downloaded inputs.

---

# 6. Section-by-section manuscript revisions still needed

## Title

Current revised title deliberately says “representative-day screening” and “existing residential PV system.” After implementing an annual model, replace it with a stronger title such as:

> *Economic Sizing of Residential PV–Battery Storage Under Time-of-Use and Net-Billing Tariffs: A San Diego Case Study*

Use that title only if the paper actually performs annual sizing and complete incremental battery economics.

## Abstract

After rerunning the model:

- replace all provisional values;
- report one annual selected capacity, not separate seasonal purchases;
- report the annual baseline, annual operating savings, annualized cost, and annual net benefit;
- state the dataset period, PV size, and uncertainty/sensitivity scope; and
- quantify the principal robustness result.

Avoid causal language unless the analysis directly supports it.

## Introduction

The original introduction spends too much space explaining basic PV-cell physics and too little space defining the research gap.

Revise it to:

1. establish the policy and tariff context with primary citations;
2. synthesize rather than list related papers;
3. identify what existing sizing studies do not address;
4. state the research question and testable contributions; and
5. distinguish resilience value from the bill-savings objective used here.

Remove unsupported claims such as the uncited “75% reduction” unless verified from an official source.

## Data

Add a compact parameter table containing:

- load source and building archetype;
- location and coordinates;
- analysis year or typical-year treatment;
- PV size and PVWatts inputs;
- tariff name and effective date;
- export-credit vintage;
- season and day-type definitions;
- battery efficiency, C-rate, and usable SOC range; and
- economic assumptions and sources.

Explain all timestamp conventions, including whether hour 1 is 00:00–00:59 or 01:00–01:59, and verify alignment among load, PV, tariff, and export-credit series.

## Methods

Retain the equations added to [main_revised_ieee.tex](main_revised_ieee.tex), then extend them for:

- the annual time horizon;
- capacity as a planning variable or fine-grid parameter;
- degradation;
- inverter/interconnection limits;
- any backup reserve;
- source-specific export eligibility; and
- annual cash-flow or net-present-value treatment.

Explicitly distinguish the operating-cost objective from the separate capacity-ranking calculation.

## Results

Replace the two seasonal “optimal size” figures with journal-level results such as:

- annual net benefit versus capacity;
- annual energy-flow breakdown by capacity;
- monthly bill savings and state-of-charge behavior;
- sensitivity tornado or heat map;
- break-even installed cost;
- robustness across homes/weather scenarios; and
- comparison with rule-based dispatch.

Include units in every axis and table heading. Report enough precision to be reproducible but do not imply accuracy beyond the assumptions.

## Discussion

Separate:

- mechanisms that explain the result;
- comparison with prior literature;
- implications for customers and policy;
- sensitivity and uncertainty;
- limitations; and
- generalizability.

Do not infer broad U.S. homeowner guidance from one San Diego building case.

## Conclusion

The original manuscript does not have a separately labeled conclusion section. Keep the concise conclusion added in the revision, but update it only after the annual rerun. It should state what was demonstrated, quantify the robust result, and avoid repeating the abstract.

## References

Correct and complete the bibliography:

- verify every title, author list, year, volume, pages, and DOI;
- change the NBER item to an appropriate report/working-paper BibTeX type;
- use DOI values rather than DOI URLs where required;
- add missing primary data, tariff, policy, software, and parameter sources; and
- follow the exact IEEE bibliography style for the target journal.

---

# 7. Recommended implementation and writing sequence

1. **Confirm scope:** incremental battery added to existing PV, or full PV-plus-battery investment.
2. **Confirm PV design:** 6 kW or 12 kW, then document and validate all PVWatts inputs.
3. **Unify timestamps:** create one annual hourly dataframe containing load, PV, import price, export price, season, and day type.
4. **Refactor optimization:** one model, one set of assumptions, explicit solver checks, and a zero-battery option.
5. **Add annual economics:** degradation, complete battery ownership cost, incentives, and one annual capacity decision.
6. **Run validation:** constraint residuals, dispatch sanity checks, benchmark controllers, and independent spot checks.
7. **Run sensitivity/uncertainty cases:** costs, tariffs, PV size, load, efficiency, degradation, and weather.
8. **Regenerate outputs:** all CSV files, plots, tables, and result statements from code.
9. **Update both manuscripts:** replace provisional values in the LaTeX and Markdown files.
10. **Complete editorial review:** citations, target-journal template, grammar, figure quality, author affiliations, acknowledgments, funding, conflicts, and data/code availability.

---

# 8. Submission-readiness checklist

## Model and data

- [ ] One authoritative seasonal and tariff calendar is used.
- [ ] Weekday/weekend handling is consistent.
- [ ] PV capacity and tilt are intentional and verified.
- [ ] Load, PV, prices, and export credits are timestamp-aligned.
- [ ] One annual battery capacity is selected.
- [ ] Zero battery is an investment option.
- [ ] Capacity search is sufficiently fine or endogenous.
- [ ] Solver status and constraint residuals are checked.
- [ ] Simultaneous operating modes are ruled out or demonstrated absent.
- [ ] Degradation and complete ownership costs are represented or sensitized.
- [ ] Incentive eligibility is documented.
- [ ] Results are benchmarked and tested across uncertainty scenarios.

## Manuscript

- [ ] Every numerical assumption has a primary citation.
- [ ] The title matches the actual scope.
- [ ] Contributions are explicit and novel relative to prior work.
- [ ] Equations exactly match the final code.
- [ ] Tables and figures are generated from final outputs.
- [ ] Annual claims come from an annual model.
- [ ] Limitations and generalizability are stated accurately.
- [ ] The exact IEEE journal template is used.
- [ ] Author affiliations and any employer disclaimer are approved.
- [ ] Data/code availability, funding, acknowledgments, and conflicts are included as required.
- [ ] The final PDF passes the journal’s formatting and PDF checks.

## Bottom line

The revised drafts are a safer and more accurate representation of the current repository than the original manuscript. However, the present 12 kWh summer and 10 kWh winter values should be treated as **provisional screening outputs**, not publication-ready optimal sizing recommendations. The main scientific revision is an annual, timestamp-consistent, uncertainty-aware investment model selecting one battery capacity.
