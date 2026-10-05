---
title: Chronic obstructive pulmonary disease epidemiology
module_identifier: ncd-copd
owner: Forecast Health
last_updated: 2026-10-05
status: Executable source module
---

# Chronic obstructive pulmonary disease epidemiology

## Contents

- [Purpose](#purpose)
- [Method](#method)
- [Inputs and outputs](#inputs-and-outputs)
- [Parameters and templates](#parameters-and-templates)
- [Data and evidence](#data-and-evidence)
- [Relationships](#relationships)
- [Assumptions and limitations](#assumptions-and-limitations)
- [Status](#status)

## Purpose

This module models chronic obstructive pulmonary disease (COPD) incidence, prevalence, disability, and cause-specific mortality within the canonical demographic population.

## Method

COPD is a marginal disease process with a COPD episode state and a derived disease-free residual. At each model-year opening, the coordinator sets the residual to the canonical population minus the COPD episode population, by age and sex. During the year, incidence moves people into the COPD episode state. Disease transitions use a continuous-hazard competing-transition calculation. Background mortality then applies to the COPD episode state.

Clinical intervention components can reduce COPD disability through the disease-owned transform. A risk-factor module can modify COPD incidence. The COPD graph publishes raw state and mortality results for post-run health metrics.

## Inputs and outputs

Required inputs are the reconciled opening population at risk and background mortality rates. An incidence modifier is optional. The module publishes COPD episode population, COPD incidence flow, and COPD-specific mortality flow as age-sex arrays.

## Parameters and templates

The source module exposes only `copd_baseline`. The parameter registry declares the COPD disability weight below as a module-owned parameter that is not editable in a scenario; it places its value on node `lrso7mga` in `model.json`. Comparison coverage and effect values belong to selected intervention modules.

## Data and evidence

[`model.json`](model.json) is the executable disease graph. The [module contract](interface/copd-epidemiology-core.module.contract.v1.json) defines composition and runtime semantics. The opening-state recipe defines baseline initialization. The contract identifies Spectrum/OneHealth COPD material and the current module cleanup as default provenance.

Routine care is declared in [`resource_requirements.json`](resource_requirements.json). It holds two ordinary COPD services from the Spectrum/OneHealth treatment costing structure (`ICModData.xlsx`, Treatment Inputs): symptom relief with inhaled salbutamol, `copd-salbutamol-symptom-relief` (five puffs a day for 365 days, 20 doctor and 20 nurse minutes and three outpatient visits a person; rows 2260 to 2263), and exacerbation treatment with oral prednisolone, `copd-oral-prednisolone-exacerbation` (two 20 mg tablets a day for seven days, 42 doctor and 56 nurse minutes and seven outpatient visits; rows 2276 to 2279). Each is applied to the COPD episode state at its baseline coverage in both scenarios. These blocks were previously named as CR2 services. They are not: the CR2 intervention modules, `ncd-copd-inhaledsalbutamol` and `ncd-copd-oralprednisolone`, declare the Appendix 3 CR2 acute-exacerbation course (`Model_Costing_V3-CRD.xlsx`), a different regimen with different quantities. The two are separate services, each declared once, and routine care keeps its source quantities. Prednisolone is priced as `cost-item.prednisolone-tablet-50-mg.unit-cost`, the same item as the CR2 and asthma CR1 intervention modules, at 0.2628 US dollars per tablet, the OneHealth price for `IC_DS_PrednisoloneTablet20Mg`. The services' resource graphs, previously held in the client, are now part of this declaration.

Staff time is priced from one shared salary item per staff type, `cost-item.workforce-salary.<type>`: `nurse`, `generalist-primary-care-doctor`, `specialist`, `therapist` and `counsellor`. A type is the same item in every module that uses it, so a generalist minute costs the same everywhere, and each type can be edited on its own: a specialist can be paid differently from a generalist doctor. The item is an annual salary. Its default is the country's WHO-CHOICE annual salary from the data service for the type's cadre (skill level 4 for doctors and specialists, 3 for nurses and therapists, 2 for counsellors); the cadre is the default source, not the item. A staff minute costs that salary divided by 126,720 working minutes a year (8 hours, 22 days a month, 12 months). The data service uses this convention for its WHO-CHOICE cost per minute, and every clinical staff cost has used it. The per-minute values in the resource graphs are defaults for use without a country. Tobacco policy programme roles are separate staff types, since none is the same job as a clinical one.

### Disability weights

A model state that holds one GBD health state takes that state's weight. A state that combines several GBD sequelae takes the GBD 2019 global average for those sequelae, which is the cause's years lived with disability divided by its prevalent cases. That average weights each severity level by GBD's own severity distribution, which GBD models by location and does not publish as a table. A person with two modelled conditions takes GBD's multiplicative combination, 1 − (1 − w1)(1 − w2).

| Model state | Old | GBD weight | GBD health states and mapping |
|---|---|---|---|
| COPD episode (`COPDEpsd`, node `lrso7mga`) | 0.097–0.217 by region | 0.093 | COPD: asymptomatic 0, mild 0.019, moderate 0.225, severe 0.408, mapped by GBD from GOLD classes I, II and III–IV. GBD 2019 global average: 19.84 million YLDs over 212.3 million cases. |

Until October 2026 the weight was read from the data service observation `COPDEpsd -> Disability`, a Spectrum/OneHealth value by region and age (0.097 to 0.217) without a cited source. Clinical interventions still reduce the weight through `Disability_Effect_Transform`. Sources: GBD 2019 Diseases and Injuries Collaborators, *Lancet* 2020;396:1204–22, appendix 1 (the disability-weight table in each cause section) and appendix 2, table S18 (global prevalence and years lived with disability, 2019); the IHME GBD 2019 disability-weights table; Salomon JA et al., *Lancet Glob Health* 2015;3:e712–23, where the weights were estimated.

### Onset age

COPD incidence and opening prevalence are 0 below age 15. The GBD input is non-zero from birth, at about 1.5e-4 a year for ages 0 to 14 in nearly every country, which is a model floor rather than observed childhood COPD. The incidence node (`Mn5YBbsp`) and the opening-prevalence source ask the data service for `min_age` 15, and the registry declares it as `minimum_onset_age`. From October 2026 the current-smoking relative risk the tobacco module applies to COPD (10.8 men, 12.3 women, the CPS-II mortality ratio from adults aged 30 and over) is 1 below 30; it was applied from 15, and 45% of the COPD cases averted in an Indonesia T1 audit were at ages 15 to 29. Whether an incidence relative risk should replace the mortality ratio is a tobacco-module method question that remains open.

## Relationships

The demographic module supplies canonical population and background mortality. `opening-state-reconciliation` creates the baseline disease partition. Separate repositories own oral prednisolone, inhaled salbutamol, and ipratropium inhaler components. Tobacco and other risk-factor modules can bind to the incidence modifier.

## Assumptions and limitations

The disease-free state is a local residual, not an additional population. The model is a marginal COPD estimate and must be reconciled to the canonical population. Routine care uses the Spectrum/OneHealth salbutamol and oral-prednisolone quantities. Ipratropium maintenance care remains visible as source under review because the current evidence does not provide a stable eligible-share default. Health metrics remain outside this disease module.

## Status

The disease graph, compiler contract, baseline template, intervention extension points, and routine-care declarations are implemented. The source graph requires compiler lowering and is not a standalone national model.
