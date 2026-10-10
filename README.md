---
title: Chronic obstructive pulmonary disease epidemiology
module_identifier: ncd-copd
owner: Forecast Health
last_updated: 2026-10-10
status: Executable source module
---

# Chronic obstructive pulmonary disease epidemiology

## Contents

- [Purpose](#purpose)
- [Method](#method)
- [Inputs and outputs](#inputs-and-outputs)
- [Parameters and templates](#parameters-and-templates)
- [Interventions and Appendix 3 codes](#interventions-and-appendix-3-codes)
- [Data and evidence](#data-and-evidence)
- [Relationships](#relationships)
- [Assumptions and limitations](#assumptions-and-limitations)
- [Status](#status)

## Purpose

This module models chronic obstructive pulmonary disease (COPD) incidence, prevalence, disability and COPD deaths within the canonical demographic population. It is the disease model that the COPD clinical interventions and the tobacco module act on.

## Method

COPD is a marginal disease process: the module models one disease and treats everyone else as a disease-free residual. It has one disease state, the COPD episode state (`COPDEpsd`). At each model-year opening the coordinator sets the residual to the canonical population minus the COPD episode population, by sex and single year of age. During the year, incidence moves people from the residual into the COPD state, and COPD deaths remove people from it. Transitions use a continuous-hazard competing-transition calculation. People do not recover from COPD in the model.

Incidence, opening prevalence and the COPD death rate are Global Burden of Disease (GBD) estimates served by the data service for the selected country, by sex and age. Incidence is the annual rate in the disease-free population. The death rate is the annual hazard of dying of COPD for a person with COPD, before calibration.

### Calibration to observed deaths

The [opening-state contract](data/copd-opening-state.contract.v3.json) declares a rate calibration that the shared `opening-state-reconciliation` preflight applies before the first model year. It produces one result, used by the baseline and every comparison.

The target is WHO Global Health Estimates (GHE) 2021: COPD deaths divided by population, by sex and GHE age band (0–4, 5–14, 15–29, 30–49, 50–59, 60–69, 70 and over), applied to the opening population. Within each band the target is spread over single ages by the GBD age pattern of COPD deaths, which is the GBD death rate among people with COPD times GBD COPD prevalence. The COPD death hazard is then scaled by sex and single age, up to at most 3 a year, so the opening year's COPD deaths equal the target.

People with COPD also die of other causes. The preflight fits, by GBD five- or ten-year age band, a multiple of the partition's other-cause death rate between 1 and 4 that keeps observed COPD prevalence stationary from one year to the next. This is the survivor relative mortality: people with COPD die of other causes more often than people without it, and the model represents that without counting those deaths as COPD deaths. The disease-free residual has a multiple of 1.

### Onset age

COPD incidence and opening prevalence are 0 below age 15. The GBD input is non-zero from birth, at about 1.5e-4 a year for ages 0 to 14 in nearly every country; that is a model floor rather than observed childhood COPD, and COPD and its smoking evidence concern adults. The incidence node (`Mn5YBbsp`), the opening-prevalence source and the calibration's incidence and prevalence inputs all ask the data service for `min_age` 15, and the registry declares the value as `minimum_onset_age`.

### Disability weights

A model state that holds one GBD health state takes that state's weight. A state that combines several GBD sequelae takes the GBD 2019 global average for those sequelae, which is the cause's years lived with disability (YLDs) divided by its prevalent cases. That average weights each severity level by GBD's own severity distribution, which GBD models by location and does not publish as a table. A person with two modelled conditions takes GBD's multiplicative combination, 1 − (1 − w1)(1 − w2).

| Model state | Earlier weight | GBD weight | GBD health states and mapping |
|---|---|---|---|
| COPD episode (`COPDEpsd`, node `lrso7mga`) | 0.097–0.217 by region | 0.093 | COPD: asymptomatic 0, mild 0.019, moderate 0.225, severe 0.408, mapped by GBD from GOLD classes I, II and III–IV. GBD 2019 global average: 19.84 million YLDs over 212.3 million cases. |

The earlier weight was a Spectrum/OneHealth value by region and age with no cited source. Clinical interventions reduce the weight through the disease-owned `Disability_Effect_Transform` (see Interventions and Appendix 3 codes). Sources: GBD 2019 Diseases and Injuries Collaborators, *Lancet* 2020;396:1204–22, appendix 1 (the disability-weight table in each cause section) and appendix 2, table S18 (global prevalence and years lived with disability, 2019); the IHME GBD 2019 disability-weights table; Salomon JA et al., *Lancet Glob Health* 2015;3:e712–23, where the weights were estimated.

## Inputs and outputs

Required inputs are the reconciled opening population at risk and background mortality from the demographic module. An incidence modifier is optional; the tobacco module supplies one. The module publishes the COPD episode population, the COPD incidence flow and the COPD death flow as sex-by-age arrays, and the disability weight that the health metrics use. Healthy years lived, years of life lost and disability-adjusted life years are calculated by the metric modules, not here.

## Parameters and templates

The module has one template, `copd_baseline`, which sets no values; the baseline comes from the parameter registry and the graph. It is also the only comparison template the module permits, so every difference between scenarios comes from a selected intervention or risk-factor module.

The [parameter registry](parameters/registry.v1.json) declares two module-owned parameters. Neither is editable in a scenario.

| Parameter | Value | Meaning |
|---|---|---|
| `copd_disability_weight` | 0.093 | COPD disability weight, GBD 2019 (above). Placed on node `lrso7mga`. |
| `minimum_onset_age` | 15 | First age with COPD incidence or prevalence. Placed on the incidence node `Mn5YBbsp`. |

Coverage and effect values belong to the intervention modules.

## Interventions and Appendix 3 codes

WHO's Appendix 3 lists two COPD interventions. CR2 is acute treatment of COPD exacerbations with an inhaled bronchodilator (salbutamol) and oral steroids. CR4 is long-term management of COPD with inhaled bronchodilators. Three intervention modules act on this model: `ncd-copd-inhaledsalbutamol`, `ncd-copd-ipratropiuminhaler` and `ncd-copd-oralprednisolone`.

The compiler builds a code's package from the intervention contracts that name that package in their `appendix3_package`. The result, and what the client catalogue lists for each code, is:

| Code | Compiler package | Modules the compiler runs and costs | Modules the client catalogue names |
|---|---|---|---|
| CR2 | `ncd-copd-cr2` | `ncd-copd-oralprednisolone` | inhaled salbutamol, oral prednisolone |
| CR4 | `ncd-copd-cr4` | `ncd-copd-inhaledsalbutamol`, `ncd-copd-ipratropiuminhaler` | inhaled salbutamol, ipratropium inhaler, oral prednisolone |

The catalogue lists come from the Appendix 3 template registry and only supply names and labels; the compiler's package decides what runs and what is costed. A CR2 analysis therefore contains oral prednisolone alone, and a CR4 analysis contains salbutamol and ipratropium but not prednisolone. The UNDP costing workbook (`Model_Costing_V3-CRD.xlsx`) defines CR2 as salbutamol and prednisolone and CR4 as salbutamol and ipratropium, so the compiled CR4 matches the workbook and the compiled CR2 lacks salbutamol.

Each intervention module works the same way. Let n be the share of people with COPD who need the service, c0 the country's current coverage, ct the coverage in year t and d the proportional reduction in disability for a person treated. The module's effect in year t is n × (ct − c0) × d. The `Disability_Effect_Transform` sums the effects of the selected modules and multiplies the COPD disability weight by 1 minus that sum. In the baseline ct equals c0, so the effect is 0. In the comparison coverage moves to the target, 0.95 by default, in one step at runtime index 1, the second year of the time horizon.

The interventions change disability only. They do not change COPD incidence, deaths or prevalence, so a CR2 or CR4 analysis averts years lived with disability but no deaths.

| Module | Code | Share in need n | Disability reduction d | Current coverage c0 (data-service route) |
|---|---|---|---|---|
| `ncd-copd-oralprednisolone` | CR2 | 0.12 | 0.337 | `/api/data/baseline-coverage/copd_oral_prednisolone_baseline_coverage` |
| `ncd-copd-inhaledsalbutamol` | CR4 | 1 | 0.148 | `/api/data/baseline-coverage/inhaled_salbutamol_baseline_coverage` |
| `ncd-copd-ipratropiuminhaler` | CR4 | country value from the data service | 0.169 | `/api/data/baseline-coverage/ipratropium_inhaler_baseline_coverage` |

Each intervention module's README gives its coverage source and resource quantities. Oral prednisolone coverage for COPD is a separate parameter from oral prednisolone coverage for asthma (`asthma_oral_prednisolone_baseline_coverage`), so each disease keeps its own current coverage.

## Data and evidence

[`model.json`](model.json) is the executable disease graph. The [module contract](interface/copd-epidemiology-core.module.contract.v1.json) defines composition and runtime semantics. The [opening-state recipe](data/copd-opening-balance-seed.recipe.v1.json) places observed GBD COPD prevalence (from age 15) in the COPD state at the opening and leaves the disease rates to the calibration above. The module contract names Spectrum/OneHealth COPD defaults as the source of its epidemiology inputs; the data service serves them as GBD estimates.

### Routine care

Routine care is the COPD care that people already receive, costed in both scenarios. It is declared in [`resource_requirements.json`](resource_requirements.json) as three services applied to the COPD episode population. Each service costs the COPD population × its share in need × its current coverage. Current coverage is one value for both scenarios, editable on the Scenarios page, and its default is the selected country's value from the same data-service route as the matching intervention.

| Service | Share in need | Coverage route | Quantities a person a year |
|---|---|---|---|
| Symptom relief with inhaled salbutamol, `copd-salbutamol-symptom-relief` | 1 | `inhaled_salbutamol_baseline_coverage` | 5 puffs a day for 365 days; 20 doctor minutes; 20 nurse minutes; 3 outpatient visits |
| Exacerbation treatment with oral prednisolone, `copd-oral-prednisolone-exacerbation` | 0.12 | `copd_oral_prednisolone_baseline_coverage` | two 20 mg tablets a day for 7 days; 42 doctor minutes; 56 nurse minutes; 7 outpatient visits |
| Maintenance with ipratropium inhaler, `copd-ipratropium-maintenance` | 0 | `ipratropium_inhaler_baseline_coverage` | none declared |

The salbutamol and prednisolone quantities are the Spectrum/OneHealth treatment costing rows (`ICModData.xlsx`, Treatment Inputs, rows 2260 to 2263 for salbutamol and 2276 to 2279 for prednisolone). They are ordinary care and differ from the Appendix 3 CR2 acute course that the intervention modules declare. The ipratropium service is marked as source under review: its share in need is 0 because no stable eligible-share default is available, so it adds no cost.

Prices are in US dollars from the OneHealth Tool: salbutamol 0.0099 a puff (`IC_DS_SalbutamolInhaler100Mcg`) and prednisolone 0.2628 a 20 mg tablet (`IC_DS_PrednisoloneTablet20Mg`). Prednisolone is priced through the shared item `cost-item.prednisolone-tablet-50-mg.unit-cost`, the same item the CR2 and asthma CR1 intervention modules use. An outpatient visit takes the country's health-centre outpatient cost from the data service.

Staff time is priced from one shared salary item per staff type, `cost-item.workforce-salary.<type>`: `nurse`, `generalist-primary-care-doctor`, `specialist`, `therapist` and `counsellor`. A type is the same item in every module that uses it, so a generalist minute costs the same everywhere, and each type can be edited on its own. The item is an annual salary. Its default is the country's WHO-CHOICE annual salary from the data service for the type's cadre (skill level 4 for doctors and specialists, 3 for nurses and therapists, 2 for counsellors). A staff minute costs that salary divided by 126,720 working minutes a year (8 hours, 22 days a month, 12 months), the convention the data service uses for its WHO-CHOICE cost per minute. The per-minute values in the resource graphs are defaults for use without a country.

## Relationships

The demographic module supplies the canonical population and background mortality. `opening-state-reconciliation` creates the opening partition and fits the calibration. The three intervention modules above insert their components into this graph.

The tobacco module binds to the incidence modifier. It multiplies COPD incidence by the ratio of comparison to baseline population mean risk, using the data service's current-smoking relative risk for COPD (10.8 for men and 12.3 for women, the CPS-II mortality ratio) and its own former-smoker risk schedule. The data service sets that relative risk to 1 below age 30, because the CPS-II cohort it comes from was of adults aged 30 and over. The tobacco module README describes the method.

## Assumptions and limitations

- The model is a marginal estimate of COPD. The disease-free state is a local residual, not an additional population, and the module must be reconciled to the canonical population.
- People with COPD never recover in the model. Prevalence is held at its observed level by the fitted other-cause relative mortality, which is bounded between 1 and 4; where a bound binds, prevalence drifts.
- Only the opening year is calibrated to WHO GHE 2021 deaths. Later years follow the scaled rates, so COPD deaths change with the population and with incidence, not with any observed trend.
- The death target (WHO GHE 2021) and the age pattern, incidence and prevalence (GBD) come from different sources, so the fitted death hazard reconciles two estimates rather than reproducing either exactly.
- The disability weight is one global average. It does not vary by country or by the severity mix of a country's COPD.
- The interventions reduce disability only. The model has no route by which treatment lowers COPD deaths, so the deaths averted by CR2 and CR4 are zero by construction.
- The intervention effect sizes (0.148, 0.169 and 0.337) and the prednisolone share in need (0.12) are carried over from the Spectrum/OneHealth COPD model. The modules cite no primary study for them.
- The compiled CR2 and CR4 packages differ from the client catalogue and from the costing workbook, as described under Interventions and Appendix 3 codes. A CR2 result omits salbutamol's effect and cost; a CR4 result omits prednisolone.
- Routine ipratropium maintenance carries no cost until an eligible-share default is available.

## Status

The disease graph, compiler contract, baseline template, calibration declaration, intervention extension points and routine-care declarations are implemented. The source graph needs compiler lowering and is not a standalone national model. The packaging of CR2 and CR4 does not yet match the Appendix 3 registry.
