# Local Intervention Module Migration Instructions

This file applies the shared intervention-module migration spec to `ncd-copd`.

Source repo type: disease module.

Current comparison templates or intervention templates to review:
- `copd_cr2`
- `copd_cr4`

Existing intervention repos beside this source module:
- `/Users/rory/Models/ncd-copd-inhaledsalbutamol`
- `/Users/rory/Models/ncd-copd-ipratropiuminhaler`
- `/Users/rory/Models/ncd-copd-oralprednisolone`

Known route or target context from the current compiler catalogue:
- target `copd`

Do not treat the list above as proof that the work is finished. It is only the starting inventory for the Codex session working in this repo.

---

# Intervention Module Migration Spec

This spec is for Codex sessions working inside a disease module or risk-factor module. The job is to move intervention-owned Botech graph logic out of the source module and into separate intervention repos, using the asthma CR3 split as the worked example.

The goal is not to make placeholder repos. The goal is that selecting an intervention in the client compiles real intervention-owned graph pieces with the relevant disease or risk-factor module, runs through the current Botech runtime, and produces the same kind of health result the old monolith produced.

## What This Migration Means

An intervention module owns the part of the Botech graph that belongs to one intervention: its coverage scale-up nodes, effect-size inputs, population-in-need logic, resource-population outputs if already present, and the links and subroutine order that make those pieces run.

The disease or risk-factor source module should stop owning intervention-specific graph pieces once they have been moved. It should keep the core epidemiology or core risk-factor method. The intervention module then gets compiled back into the source module or downstream disease module when the user selects that intervention.

For example, asthma CR3 is now made from three intervention repos:

- `/Users/rory/Models/ncd-asthma-lowdosebeclom`
- `/Users/rory/Models/ncd-asthma-highdosebeclom`
- `/Users/rory/Models/ncd-asthma-inhaledshortactingbeta`

Each repo owns one Botech component graph slice, its own intervention contract, and its own parameter placements. The client compiler assembles those three modules with `ncd-asthma` when the user selects CR3.

## Required Files In Each Intervention Repo

Each intervention repo should contain these files unless there is a documented reason it cannot.

`AGENTS.md` should say this is an intervention repo and that health-effect graph logic belongs here, not in the parent disease or risk-factor module.

`README.md` should describe the intervention in plain English, say which source module or target module it plugs into, and name the current known limitation if the path is not fully wired yet.

`intervention.json` should be the small descriptor for the intervention. It should name the intervention id, label, Appendix 3 code if relevant, target module, component ref, interface contract ref, package id if this intervention is one part of a package, and provenance ref.

`interface/<intervention-id>.intervention.contract.v1.json` should be the contract the compiler consumes. It must name the owner repo, target module, component file, baseline and comparison parameter values, scenario parameters with placements, published outputs, resource/costing status, validation rules, and package membership if applicable.

`components/<intervention-id>.component.v1.json` should contain the actual Botech graph slice: nodes, links, and the execution order needed for that intervention piece. It must not be a parameter-only stub if the old model had real graph logic.

`scripts/validate_intervention_contract.py` should fail if the contract points to missing files, unknown component nodes, stale target modules, missing parameter placements, missing execution order, duplicate parameter ids, or a component that cannot be compiled.

`resource_requirements.json` may exist if the intervention has resource inputs. Resource and costing requirements are not health-effect lowering unless that is explicitly part of a future resource/cost module. The current health compiler should not treat resource requirements as disease effects.

## How To Do The Migration

Start from the real source evidence. Read the current source module, the recovered `monolith-reference/model.json` if it exists, the current `model.json`, the source module parameter templates, and any existing intervention repo beside the source module. Do not rebuild the graph from memory.

For each intervention, identify the exact old graph slice. This means the nodes, links, and subroutine order that changed when the old template was applied. Include upstream coverage, target coverage, scale-up year, effect size, population in need, intermediate calculation nodes, final outputs, and any resource-population output that already existed in the graph.

Create or repair the intervention repo under `/Users/rory/Models/<source-module-slug>-<intervention-slug>`. Use the same ownership shape as the CR3 intervention repos. Do not keep intervention graph logic in the disease or risk-factor module just because it is easier.

Write the intervention contract so the compiler can consume it without private knowledge. The contract should say what graph component to insert, which target module it is for, what parameters the baseline uses, what parameters the comparison uses, what outputs are published, and what execution-order metadata the compiler must preserve.

Clean the source module after extraction. Remove intervention-specific parameters, templates, nodes, links, and component metadata from the source module unless the source module still genuinely owns them. A plain disease or risk-factor run should not silently include intervention nodes that now belong to an intervention repo.

Keep package semantics separate from component ownership. If one Appendix 3 template is a package made from multiple interventions, each intervention still gets its own repo and contract. The package is assembled by the compiler from those contracts.

## What Not To Do

Do not create a repo that only repeats the old template values. If the old model had graph nodes and links, the intervention repo must own those graph nodes and links.

Do not add hidden client fallbacks. If the compiler cannot assemble the intervention, it should fail clearly.

Do not hard-code private node ids in the client or compiler if the intervention contract or target module contract should declare them.

Do not leave both the old source-module implementation and the new intervention-module implementation active. That creates double counting and makes the client output untrustworthy.

Do not move core epidemiology, core risk-factor method, demography, HYL, DALYs, resource costing, or ROI calculations into an intervention repo. The intervention repo owns the intervention-specific graph slice only.

## Validation Required Before Calling A Repo Done

Run the intervention repo validator.

Run the source module validator after removing the old intervention-owned surface.

Run the compiler bundle sync in `ncd-client` so the intervention repo is copied into `compiler-inputs/module-release-bundle.v1/modules`.

Compile the baseline and comparison through `scripts/canonical_botech_compiler.py`. The receipt must cite the intervention repo contracts from the synced module bundle, not local `/Users/rory/Models` paths.

Run the compiled model through the current Botech WASM or Rust runtime with hosted unified API data. Baseline must not receive comparison values. Comparison must receive the selected intervention values. The output should move in the expected direction unless there is a documented data or method reason it cannot.

Update `scripts/validate_compiler_runtime.py` or an equivalent validator so the new path cannot regress silently. The validator should check that plain source-module compiles do not still contain extracted intervention nodes.

## Done Means

The intervention repos contain real graph components, contracts, descriptors, and validators.

The parent disease or risk-factor module no longer owns the extracted intervention-specific graph surface.

The client compiler can sync, plan, compile, and run the migrated intervention.

The results page receives the runtime output through the normal compiled-model flow.

There is one user-facing intervention entry for the package or intervention. There should not be duplicate entries caused by internal implementation differences.
