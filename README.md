---
title: Chronic obstructive pulmonary disease epidemiology
module_identifier: ncd-copd
owner: Forecast Health
last_updated: 2026-10-11
status: Executable source module
---

# Chronic obstructive pulmonary disease epidemiology

## Contents

- [Purpose](#purpose)
- [Inputs and outputs](#inputs-and-outputs)
- [Method](#method)
- [Routine care](#routine-care)
- [Parameters](#parameters)
- [Data and evidence](#data-and-evidence)
- [Validation](#validation)
- [Assumptions and limitations](#assumptions-and-limitations)
- [Relationships](#relationships)
- [Status](#status)

## Purpose

This module models chronic obstructive pulmonary disease (COPD) in a national population. It tracks new cases, the number of people living with COPD, the disability they carry and the deaths caused by COPD, by sex and single year of age.

It is the disease model on which the COPD treatment modules and the tobacco module act. Treatment reduces the disability of people with COPD. Tobacco control changes the number of new cases.

## Inputs and outputs

The module reads two inputs from the demographic module: the opening population by sex and single year of age (people), and background mortality (the annual probability of death from all causes). It can also read an incidence multiplier, a dimensionless factor by sex and age that the tobacco module supplies.

It publishes, by sex and single year of age, the number of people with COPD, the annual flow of new COPD cases and the annual flow of COPD deaths (all in people). It also publishes the COPD disability weight, a number between 0 (full health) and 1 (equivalent to death). Healthy years lived, years of life lost and disability-adjusted life years (DALYs) are calculated by the metric modules, not by this module.

## Method

### Disease states

The module models one disease and treats everyone without it as a disease-free remainder. This is called a marginal disease model. It has one disease state, the COPD episode state (`COPDEpsd`).

At the start of each model year the platform sets the disease-free remainder equal to the national population minus the people with COPD, by sex and single year of age. During the year new cases move people from the disease-free remainder into the COPD state, and COPD deaths remove people from the COPD state. The two flows are calculated together from continuous annual hazards, so that each flow competes with the other for the same people. People do not recover from COPD in the model.

The incidence rate, the opening prevalence and the COPD death rate are Global Burden of Disease (GBD) estimates for the selected country, by sex and age, served by the Forecast Health data service. The incidence rate is the annual rate of new cases in the disease-free population. The death rate is the annual hazard of dying of COPD for a person with COPD.

### Onset age

COPD incidence and opening prevalence are set to 0 below age 15. The GBD inputs are non-zero from birth, at about 1.5e-4 a year for ages 0 to 14 in nearly every country. That value is a floor in the GBD model, not observed childhood COPD, and COPD and the evidence on smoking and COPD concern adults. The minimum onset age (`minimum_onset_age`, 15 years) is applied to the incidence node (`Mn5YBbsp`), to the opening prevalence and to the incidence and prevalence inputs of the calibration.

### Calibration to observed deaths

Before the first model year, the shared opening-state reconciliation module adjusts the COPD death rate so that the model reproduces observed COPD deaths in the opening year. The adjustment is made once and used by the baseline and every comparison.

The target is the World Health Organization (WHO) Global Health Estimates (GHE) 2021: COPD deaths divided by population, by sex and GHE age band (0–4, 5–14, 15–29, 30–49, 50–59, 60–69, and 70 and over), applied to the opening population. Within each band the target deaths are spread over single years of age in proportion to the GBD age pattern of COPD deaths, which is the GBD COPD death rate among people with COPD multiplied by GBD COPD prevalence.

The COPD death hazard is then scaled for each sex and single year of age so that opening-year COPD deaths equal the target. Let $h_{s,a}$ be the GBD COPD death hazard for sex $s$ and age $a$ (per year) and $k_{s,a}$ the fitted scaling factor (dimensionless). The hazard used in the model is

$$
h^{*}_{s,a} = \min\left(3,\; k_{s,a}\, h_{s,a}\right),
$$

so the scaled hazard is at most 3 a year.

People with COPD also die of other causes, more often than people without COPD. The reconciliation fits, for each GBD age band of five or ten years, a relative mortality $m_b$ (dimensionless) for people with COPD in band $b$. People with COPD die of causes other than COPD at $m_b$ times the population's other-cause death rate, and these deaths are not counted as COPD deaths. The factor is fitted between 1 and 4 so that observed COPD prevalence is carried forward unchanged from one year to the next. The disease-free remainder has a factor of 1.

### Disability

A disability weight measures the health loss of a condition on a scale from 0 (full health) to 1 (equivalent to death). The COPD state takes one disability weight, 0.093 (`copd_disability_weight`).

GBD divides COPD into four health states with their own weights: asymptomatic 0, mild 0.019, moderate 0.225 and severe 0.408. GBD maps these from the Global Initiative for Chronic Obstructive Lung Disease (GOLD) classes I, II and III–IV. The model has one COPD state, so it takes the GBD 2019 global average weight. Let $Y$ be global COPD years lived with disability (YLDs) in 2019 and $P$ global prevalent COPD cases in 2019. The average weight is

$$
\bar{w} = \frac{Y}{P} = \frac{19.84 \text{ million}}{212.3 \text{ million}} = 0.093.
$$

This average weights each severity level by GBD's own severity distribution, which GBD models by location and does not publish as a table. The Spectrum/OneHealth COPD model, from which the graph is taken, used weights of 0.097 to 0.217 by region and age with no cited source; this module does not use them.

A person with two modelled conditions takes GBD's multiplicative combination of the two weights. With $w_1$ and $w_2$ the two weights, the combined weight is

$$
w = 1 - (1 - w_1)(1 - w_2).
$$

### Treatment packages

Three treatment modules act on this model: inhaled salbutamol (`ncd-copd-inhaledsalbutamol`), the ipratropium inhaler (`ncd-copd-ipratropiuminhaler`) and oral prednisolone (`ncd-copd-oralprednisolone`). They belong to two interventions in Appendix 3 of the WHO Global Action Plan for the Prevention and Control of Noncommunicable Diseases, the WHO menu of recommended interventions. In WHO's wording, CR2 is "acute treatment of COPD exacerbations with inhaled bronchodilators and oral steroids", and CR4 is "long-term management of COPD with inhaled bronchodilator".

The compiler is the platform component that assembles the selected modules into one runnable model. It builds a code's package from the treatment contracts that name that package, in their `appendix3_package` field or, for a module in more than one package, in `appendix3_packages`. The client catalogue takes its names and labels from the Appendix 3 template registry, which lists the same modules.

| Code | Compiler package | Modules the compiler runs and costs |
|---|---|---|
| CR2 | `ncd-copd-cr2` | `ncd-copd-inhaledsalbutamol`, `ncd-copd-oralprednisolone` |
| CR4 | `ncd-copd-cr4` | `ncd-copd-inhaledsalbutamol`, `ncd-copd-ipratropiuminhaler` |

CR2 is the inhaled bronchodilator salbutamol with the oral steroid prednisolone. CR4 is salbutamol with the inhaled bronchodilator ipratropium. These are also the packages of the United Nations Development Programme (UNDP) costing workbook (`Model_Costing_V3-CRD.xlsx`). Salbutamol belongs to both. When CR2 and CR4 are selected together, the compiler runs and costs salbutamol once, at the one target coverage both packages give it.

### Effect of treatment on disability

Each treatment module reduces the disability of people with COPD, and all three have the same structure. For a treatment $j$, let $n_j$ be the share of people with COPD who need it, $c_{j,0}$ the country's current coverage, $c_{j,t}$ the coverage in year $t$, and $d_j$ the proportional reduction in disability for a person treated (all dimensionless, from 0 to 1). The treatment's effect in year $t$ is

$$
E_{j,t} = n_j \left(c_{j,t} - c_{j,0}\right) d_j .
$$

The disease's disability transform (`Disability_Effect_Transform`) sums the effects of the selected treatments and reduces the COPD disability weight $w$ to

$$
w_t = w \left(1 - \sum_j E_{j,t}\right).
$$

In the baseline the coverage stays at current coverage, so every effect is 0. In the comparison the coverage moves to the target, 0.95 by default, in one step at runtime index 1. Runtime index 0 is the first year of the time horizon, so index 1 is the second year.

The treatments change disability only. They do not change COPD incidence, deaths or prevalence, so a treatment analysis averts years lived with disability but no deaths. The default values are:

| Treatment module | Appendix 3 code | Share in need $n_j$ | Disability reduction $d_j$ | Current coverage $c_{j,0}$ |
|---|---|---|---|---|
| `ncd-copd-oralprednisolone` | CR2 | 0.12 | 0.337 | country value, `/api/data/baseline-coverage/copd_oral_prednisolone_baseline_coverage` |
| `ncd-copd-inhaledsalbutamol` | CR2 and CR4 | 1 | 0.148 | country value, `/api/data/baseline-coverage/inhaled_salbutamol_baseline_coverage` |
| `ncd-copd-ipratropiuminhaler` | CR4 | country value from the data service | 0.169 | country value, `/api/data/baseline-coverage/ipratropium_inhaler_baseline_coverage` |

Each treatment module's README gives its coverage source and resource quantities. COPD oral prednisolone coverage is a separate parameter from asthma oral prednisolone coverage (`asthma_oral_prednisolone_baseline_coverage`), so each disease keeps its own current coverage.

## Routine care

Routine care is the COPD care that people already receive. It is costed in both the baseline and the comparison. The module declares three routine services in `resource_requirements.json`, each applied to the COPD population. For a service, let $P$ be the number of people with COPD, $n$ the share who need the service and $c_0$ its current coverage. The number of people receiving the service each year is

$$
R = P \, n \, c_0 .
$$

Each person receiving the service uses the quantities below each year, and the cost is the number of people times the quantities times the unit prices. The current coverage is one value for both scenarios and can be edited on the Scenarios page. Its default is the selected country's value from the same data-service route as the matching treatment module.

| Service | Share in need | Coverage parameter | Quantities per person per year |
|---|---|---|---|
| Symptom relief with inhaled salbutamol, `copd-salbutamol-symptom-relief` | 1 | `inhaled_salbutamol_baseline_coverage` | 5 puffs a day for 365 days; 20 doctor minutes; 20 nurse minutes; 3 outpatient visits |
| Exacerbation treatment with oral prednisolone, `copd-oral-prednisolone-exacerbation` | 0.12 | `copd_oral_prednisolone_baseline_coverage` | two 20 mg tablets a day for 7 days; 42 doctor minutes; 56 nurse minutes; 7 outpatient visits |
| Maintenance with ipratropium inhaler, `copd-ipratropium-maintenance` | 0 | `ipratropium_inhaler_baseline_coverage` | none declared |

The salbutamol and prednisolone quantities are the Spectrum/OneHealth treatment costing rows (`ICModData.xlsx`, Treatment Inputs, rows 2260 to 2263 for salbutamol and 2276 to 2279 for prednisolone). They describe ordinary care and differ from the Appendix 3 CR2 acute course that the treatment modules declare. The ipratropium service is marked as source under review. Its share in need is 0 because no stable default for the eligible share is available, so it adds no cost.

Prices are in US dollars from the OneHealth Tool, the United Nations costing tool for health sector plans. Salbutamol costs US$0.0099 a puff (`IC_DS_SalbutamolInhaler100Mcg`) and prednisolone US$0.2628 a 20 mg tablet (`IC_DS_PrednisoloneTablet20Mg`). Prednisolone is priced through the shared item `cost-item.prednisolone-tablet-50-mg.unit-cost`, the same item that the COPD oral prednisolone module and the asthma treatment module for Appendix 3 code CR1 use. An outpatient visit takes the country's health-centre outpatient cost from the data service.

Staff time is priced from one shared salary item per staff type, `cost-item.workforce-salary.<type>`, where the type is `nurse`, `generalist-primary-care-doctor`, `specialist`, `therapist` or `counsellor`. A type is the same item in every module that uses it, so a generalist minute costs the same everywhere, and each type can be edited on its own. The item is an annual salary. Its default is the country's annual salary from WHO-CHOICE (WHO CHOosing Interventions that are Cost-Effective), served by the data service for the type's skill level: 4 for doctors and specialists, 3 for nurses and therapists, and 2 for counsellors. Let $S$ be the annual salary in US dollars. A staff minute costs

$$
\frac{S}{126{,}720},
$$

where 126,720 is the number of working minutes in a year (8 hours a day, 22 days a month, 12 months). This is the convention the data service uses for its WHO-CHOICE cost per minute. The per-minute values written in the resource graphs are defaults for use without a selected country.

## Parameters

The module has one scenario template, `copd_baseline`, which sets no values. The baseline comes from the parameter registry (`parameters/registry.v1.json`) and the disease graph. It is also the only comparison template the module permits, so every difference between baseline and comparison comes from a selected treatment or risk-factor module.

The registry declares two parameters owned by this module. Neither can be edited in a scenario.

| Parameter | Meaning | Baseline default | Comparison default | Range | Source |
|---|---|---|---|---|---|
| COPD disability weight, `copd_disability_weight` | Disability weight of the COPD state, placed on node `lrso7mga` | 0.093 | 0.093 | 0–1 | GBD 2019 global average |
| Minimum onset age, `minimum_onset_age` | First age with COPD incidence or prevalence, in years, placed on the incidence node `Mn5YBbsp` | 15 | 15 | 0–100 | Module method |

Coverage and effect parameters belong to the treatment modules, and routine-care coverage uses the same parameters.

## Data and evidence

| Input | Source | Route |
|---|---|---|
| COPD incidence, prevalence and death rate by sex and age | GBD, as served by the Forecast Health data service | `fhdb.epidemiology`, disease COPD; incidence and prevalence from age 15 |
| Death target | WHO Global Health Estimates 2021, COPD deaths by sex and GHE age band | `who_ghe.cause_death_rate`, cause `copd` |
| All-cause mortality | Forecast Health data service | `fhdb.mortality` |
| Disability weight | GBD 2019 | Registry value |
| Routine-care quantities | Spectrum/OneHealth treatment costing rows, `ICModData.xlsx` | `resource_requirements.json` |
| Drug prices | OneHealth Tool | Shared cost items |
| Staff salaries and visit costs | WHO-CHOICE, as served by the data service | Shared cost items |

The executable disease graph is `model.json`. The module contract (`interface/copd-epidemiology-core.module.contract.v1.json`) defines how the platform composes and runs the module. The opening-state recipe (`data/copd-opening-balance-seed.recipe.v1.json`) places observed GBD COPD prevalence from age 15 in the COPD state at the start of the first year. The opening-state contract (`data/copd-opening-state.contract.v3.json`) declares the calibration. The module contract names Spectrum/OneHealth COPD defaults as the source of its epidemiology inputs; the data service serves them as GBD estimates.

The disability weights are from: GBD 2019 Diseases and Injuries Collaborators. Global burden of 369 diseases and injuries in 204 countries and territories, 1990–2019. *Lancet* 2020;396:1204–22, appendix 1 (the disability-weight table in each cause section) and appendix 2, table S18 (global prevalence and years lived with disability, 2019); the Institute for Health Metrics and Evaluation (IHME) GBD 2019 disability-weights table; and Salomon JA et al. Disability weights for the Global Burden of Disease 2013 study. *Lancet Glob Health* 2015;3:e712–23, where the weights were estimated.

## Validation

Opening-year COPD deaths equal the WHO GHE 2021 target by construction, except in sex and age cells where the hazard reaches its limit of 3 a year. Prevalence stays at its observed GBD level from year to year by construction, except in age bands where the other-cause relative mortality reaches 1 or 4. The module has no comparison against data that were not used to fit it.

## Assumptions and limitations

- The model is a marginal model of COPD. The disease-free state is a remainder, not an additional population, and the module must be reconciled to the national population each year.
- People with COPD never recover in the model. Prevalence is held at its observed level by the fitted other-cause relative mortality, which lies between 1 and 4. Where a bound binds, prevalence drifts away from its observed level.
- Only the opening year is calibrated to WHO GHE 2021 deaths. Later years follow the scaled rates, so COPD deaths change with the population and with incidence, not with any observed trend.
- The death target (WHO GHE 2021) and the age pattern, incidence and prevalence (GBD) come from different sources. The fitted death hazard reconciles two estimates and reproduces neither exactly.
- The disability weight is one global average. It does not vary by country or by the severity mix of a country's COPD.
- The treatments reduce disability only. The model has no route by which treatment lowers COPD deaths, so the deaths averted by CR2 and CR4 are zero by construction.
- The treatment effect sizes (0.148, 0.169 and 0.337) and the prednisolone share in need (0.12) are taken from the Spectrum/OneHealth COPD model. The modules cite no primary study for them.
- Salbutamol is one module with one effect and one resource declaration, the CR2 acute-exacerbation course, in both packages. A CR4 analysis therefore costs salbutamol as that course, not as daily long-term use.
- Routine ipratropium maintenance carries no cost because its share in need is 0.

## Relationships

The demographic module supplies the national population and background mortality. The opening-state reconciliation module creates the opening population by state and fits the calibration.

The tobacco module binds to the incidence multiplier. It multiplies COPD incidence by the ratio of the comparison to the baseline population mean relative risk. It uses the data service's relative risk of COPD for current smokers (10.8 for men and 12.3 for women, the mortality ratio from the Cancer Prevention Study II, CPS-II) and its own risk schedule for former smokers. The data service sets that relative risk to 1 below age 30, because the CPS-II cohort was of adults aged 30 and over. The tobacco module README describes the method.

The three treatment modules described under Method insert their components into this graph and join their effects to the disability transform.

## Status

The disease graph, compiler contract, baseline template, calibration declaration, treatment extension points and routine-care declarations are implemented. The source graph needs compiler lowering and is not a standalone national model. CR2 runs salbutamol and prednisolone, and CR4 runs salbutamol and ipratropium, as WHO and the costing workbook define them.
