# NCD COPD Module

This repository contains the COPD disease epidemiology module for the botech NCD module system. The current source surface is the core COPD graph in `model.json`, the module contract in `interface/`, the COPD parameter registry in `parameters/registry.v1.json`, and the baseline template in `parameters/templates/`.

The COPD source module now owns core epidemiology only. Clinical intervention health-effect graph slices for oral prednisolone, inhaled salbutamol, and ipratropium inhaler live in their separate intervention repositories. Tobacco or other risk-factor effects are not owned here; COPD declares an optional incidence-modifier input that a source-owned risk-factor relationship can bind through the compiler.

The repository command surface is `scripts/orchestrator_scenarios.py`. It exposes `catalog`, `templates`, and `materialize`. A materialized COPD artifact is not a standalone proof run: COPD requires compiler lowering for demographic opening balances and background mortality before botech-rust can prove a full linked runtime execution.

Run the repository validator with:

```bash
python scripts/validate_module_contract.py
```
