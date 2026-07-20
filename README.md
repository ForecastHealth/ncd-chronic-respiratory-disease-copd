---
title: Chronic obstructive pulmonary disease epidemiology
module_identifier: ncd-copd
owner: Forecast Health
last_updated: 2026-07-19
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

COPD is a marginal disease process with a COPD episode state and a derived disease-free residual. Observed COPD prevalence informs the opening episode population. The residual state receives the remaining demographic population. During each model year, incidence moves people into the COPD episode state. Disease transitions use a continuous-hazard competing-transition calculation. Background mortality is then applied to the remaining living population.

Clinical intervention components can reduce COPD disability through the disease-owned transform. A risk-factor module can modify COPD incidence. The COPD graph publishes raw state and mortality results for post-run health metrics.

## Inputs and outputs

Required inputs are the reconciled opening population at risk and background mortality rates. An incidence modifier is optional. The module publishes COPD episode population, COPD incidence flow, and COPD-specific mortality flow as age-sex arrays.

## Parameters and templates

The source module exposes only `copd_baseline`. The disease parameter registry is empty because comparison coverage and effect values belong to selected intervention modules.

## Data and evidence

[`model.json`](model.json) is the executable disease graph. The [module contract](interface/copd-epidemiology-core.module.contract.v1.json) defines composition and runtime semantics. The opening-state recipe defines baseline initialization. The contract identifies Spectrum/OneHealth COPD material and the current module cleanup as default provenance.

## Relationships

The demographic module supplies canonical population and background mortality. `opening-state-reconciliation` creates the baseline disease partition. Separate repositories own oral prednisolone, inhaled salbutamol, and ipratropium inhaler components. Tobacco and other risk-factor modules can bind to the incidence modifier.

## Assumptions and limitations

The disease-free state is a local residual, not an additional population. The model is a marginal COPD estimate and must be reconciled to the canonical population. Clinical resource requirements and health metrics remain outside this disease module.

## Status

The disease graph, compiler contract, baseline template, and intervention extension points are implemented. The source graph requires compiler lowering and is not a standalone national model.
