#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
STALE_PATHS = (
    "build",
    "scenarios",
    "scenario-templates",
    "modular-composition",
    "validation_suite",
    "resources",
    "assurance",
)
STALE_SCRIPT_NAMES = {
    "apply_scenario.py",
    "create_economic_analyses.py",
    "run_economic_analyses.py",
    "upload_project.py",
    "validate_scenario.py",
    "fetch_analytics.py",
    "process_analytics.py",
}
STALE_MODEL_NODE_IDS = {"Births", "BXOLckIN", "oGP2Nze1", "PjHF9FHh", "DXhAVyOP", "HaYRxeQQ", "mrGezI4c"}
STALE_MODEL_LINK_IDS = {"8g0Xnawu", "pfDEgvPv", "B48YPJzw", "DbLhgNYh"}
JSON_PATH_RE = re.compile(r"^\$\.(nodes|links)\[\?\(@\.id=='([^']+)'\)\]\.(.+)$")


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def strings_in(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        result: list[str] = []
        for item in value.values():
            result.extend(strings_in(item))
        return result
    if isinstance(value, list):
        result: list[str] = []
        for item in value:
            result.extend(strings_in(item))
        return result
    return []


def resolve_json_path(model: dict[str, Any], ref: str) -> bool:
    match = JSON_PATH_RE.match(ref)
    if not match:
        return False
    section, entry_id, tail = match.groups()
    entries = model.get(section, [])
    target = next((entry for entry in entries if entry.get("id") == entry_id), None)
    if target is None:
        return False
    for part in tail.split("."):
        if not isinstance(target, dict) or part not in target:
            return False
        target = target[part]
    return True


def git_tracked_files() -> set[str]:
    result = subprocess.run(["git", "ls-files"], cwd=REPO_ROOT, check=True, text=True, capture_output=True)
    return set(result.stdout.splitlines())


def validate() -> list[str]:
    errors: list[str] = []
    tracked = git_tracked_files()
    for stale_path in STALE_PATHS:
        if (REPO_ROOT / stale_path).exists():
            fail(errors, f"{stale_path}/ still exists; COPD cleanup should use parameters/templates and scripts/orchestrator_scenarios.py")
        stale_tracked = [path for path in tracked if path == stale_path or path.startswith(stale_path + "/")]
        if stale_tracked:
            fail(errors, f"Tracked stale path remains under {stale_path}/")
    for script_name in STALE_SCRIPT_NAMES:
        if (REPO_ROOT / "scripts" / script_name).exists():
            fail(errors, f"scripts/{script_name} still exists; this is not part of the current command surface")
    if (REPO_ROOT / "templates").exists():
        fail(errors, "top-level templates/ still exists; templates should live in parameters/templates")

    model_path = REPO_ROOT / "model.json"
    if not model_path.exists():
        fail(errors, "Missing model.json")
        return errors
    model = load(model_path)
    node_ids = [node.get("id") for node in model.get("nodes", [])]
    link_ids = [link.get("id") for link in model.get("links", [])]
    if len(node_ids) != len(set(node_ids)):
        fail(errors, "model.json has duplicate node ids")
    if len(link_ids) != len(set(link_ids)):
        fail(errors, "model.json has duplicate link ids")
    node_set = set(node_ids)
    link_set = set(link_ids)
    data_fetcher_requirements = set()
    for section in ("nodes", "links"):
        for item in model.get(section, []):
            generate_array = item.get("generate_array") or {}
            method = generate_array.get("method")
            if not method or method in {"single_value", "linear_with_arbitrary_length"}:
                continue
            parameters = generate_array.get("parameters") or {}
            fetcher = generate_array.get("data_fetcher_label")
            if not fetcher and method not in {"epidemiology", "get_observation", "healthy_disability", "yll_weights", "mortality"}:
                continue
            disease = parameters.get("disease")
            measure = parameters.get("measure")
            observation = parameters.get("observation")
            if method == "epidemiology":
                data_fetcher_requirements.add(("epidemiology", disease, measure, None))
            elif method == "get_observation":
                data_fetcher_requirements.add((f"{fetcher}.get_observation" if fetcher else "get_observation", None, None, observation))
            else:
                data_fetcher_requirements.add((method, None, None, None))
    stale_nodes = STALE_MODEL_NODE_IDS & node_set
    if stale_nodes:
        fail(errors, f"model.json still contains stale monolith/risk-factor nodes: {sorted(stale_nodes)}")
    stale_links = STALE_MODEL_LINK_IDS & link_set
    if stale_links:
        fail(errors, f"model.json still contains stale risk-factor multiplier links: {sorted(stale_links)}")
    for link in model.get("links", []):
        if link.get("source") not in node_set:
            fail(errors, f"Link {link.get('id')} points to missing source {link.get('source')}")
        if link.get("target") not in node_set:
            fail(errors, f"Link {link.get('id')} points to missing target {link.get('target')}")
    subroutine_edge_refs = set()
    subroutine_node_refs = set()
    for subroutine in model.get("subroutines", []):
        subroutine_edge_refs.update(subroutine.get("included_edges", []))
        subroutine_node_refs.update(subroutine.get("included_source_nodes", []))
    for edge_id in sorted(subroutine_edge_refs - link_set):
        fail(errors, f"Subroutine references missing link {edge_id}")
    for node_id in sorted(subroutine_node_refs - node_set):
        fail(errors, f"Subroutine references missing node {node_id}")
    for text_value in strings_in(model):
        if "Asthma" in text_value or "asthma" in text_value:
            fail(errors, f"COPD model still contains stale asthma text: {text_value}")
            break

    intervention_tokens = ("Salbutamol", "Prednisolone", "Ipratropium", "salbutamol", "prednisolone", "ipratropium")
    for text_value in strings_in(model):
        if any(token in text_value for token in intervention_tokens):
            fail(errors, f"COPD model still contains extracted intervention text: {text_value}")
            break
    extracted_nodes = set(['8kLiklUp', 'ResourcePopulationReached_InhaledSalbutamol', 'ResourcePopulationReached_IpratropiumInhaler', 'ResourcePopulationReached_OralPrednisolone', 'U37bYeyB', 'jWfqJ3Yv', 'lrsnalk2', 'lrsnavq2', 'lrsngpv8', 'lrsngte4', 'lrsnhyyd', 'lrsni0s5', 'lrsnjkmt', 'lrsnjnt3', 'lrsnjr1s', 'lrso22do', 'lrso24ss', 'lrso28l8', 'lrst0woc', 'lrst14z6', 'lrst1pq2', 'lrst79uc', 'lrst7n8a', 'lrst7nh0'])
    extracted_links = set(['2UnmNJH5', '2cqXSWkb', '6aVqOh7C', '9Fe9k1UV', 'EfuyA2u1', 'FNrIUP2V', 'LIyy1ky9', 'MnpPqwz9', 'OvOhBeTK', 'QFKsJ7KA', 'R4Vwfikm', 'RFqzZF5Z', 'ResourceAbs_InhaledSalbutamol_Base_1', 'ResourceAbs_InhaledSalbutamol_Coverage', 'ResourceAbs_InhaledSalbutamol_PIN', 'ResourceAbs_IpratropiumInhaler_Base_1', 'ResourceAbs_IpratropiumInhaler_Coverage', 'ResourceAbs_IpratropiumInhaler_PIN', 'ResourceAbs_OralPrednisolone_Base_1', 'ResourceAbs_OralPrednisolone_Coverage', 'ResourceAbs_OralPrednisolone_PIN', 'TjND1e9T', 'WE3nlFuI', 'cpORh46w', 'ee0hmMQf', 'g71GXNvq', 'gO6Yvodp', 'gwDbhWLO', 'lZsxgkeD', 'plB7iwsy', 'rSVQNns4', 'sS2uov2j', 'tJkWGHk3', 'tgy0fCCF', 'u3I26S1y', 'ydn35Gq6'])
    if extracted_nodes & node_set:
        fail(errors, f"COPD model still contains extracted intervention nodes: {sorted(extracted_nodes & node_set)}")
    if extracted_links & link_set:
        fail(errors, f"COPD model still contains extracted intervention links: {sorted(extracted_links & link_set)}")

    background_link = next((link for link in model.get("links", []) if link.get("id") == "cz2LeDKw"), None)
    if not background_link:
        fail(errors, "Missing COPD background mortality link cz2LeDKw")
    elif background_link.get("generate_array"):
        fail(errors, "COPD background mortality link still fetches demographic mortality directly instead of relying on compiler lowering")
    elif background_link.get("compiler_binding", {}).get("kind") != "declared_input":
        fail(errors, "COPD background mortality link is not marked as a declared compiler input")

    module_files = sorted((REPO_ROOT / "interface").glob("*.module.contract.v1.json"))
    if len(module_files) != 1:
        fail(errors, f"Expected exactly one module contract, found {len(module_files)}")
        return errors
    module = load(module_files[0])
    module_id = module.get("module_id")
    repo_id = module.get("owner", {}).get("repo_id")
    if module.get("schema") != "botech.module-contract.v1":
        fail(errors, f"{module_files[0]} has wrong module contract schema")
    if module_id != "copd_epidemiology_core":
        fail(errors, "Module contract module_id is not copd_epidemiology_core")
    if module.get("runtime_role") != "compiled_together":
        fail(errors, "COPD should be marked compiled_together because it declares demographic substrate inputs")
    declared_inputs = {item.get("channel_id") for item in module.get("declared_inputs", [])}
    for required_input in {"population_at_risk_opening", "background_mortality_rate", "incidence_modifier"}:
        if required_input not in declared_inputs:
            fail(errors, f"Module contract is missing declared input {required_input}")
    declared_input_by_id = {item.get("channel_id"): item for item in module.get("declared_inputs", [])}
    for channel_id, link_id in (("background_mortality_rate", "cz2LeDKw"), ("incidence_modifier", "uSWdM5kH")):
        declared_input = declared_input_by_id.get(channel_id, {})
        if "binding" not in declared_input:
            fail(errors, f"Declared input {channel_id} has no target-side binding")
        bound_link = next((link for link in model.get("links", []) if link.get("id") == link_id), None)
        if not bound_link:
            fail(errors, f"Declared input {channel_id} binding points to missing link {link_id}")
        elif bound_link.get("compiler_binding", {}).get("kind") != "declared_input":
            fail(errors, f"Declared input {channel_id} is not represented by compiler_binding on link {link_id}")
        elif channel_id == "incidence_modifier" and bound_link.get("compiler_binding", {}).get("channel_id") != "incidence_modifier":
            fail(errors, "COPD incidence modifier compiler binding does not name the incidence_modifier channel")
    published_bindings = []
    published_outputs = {
        item.get("channel_id"): item
        for item in module.get("published_outputs", [])
    }
    incidence_output = published_outputs.get("copd_incidence_flow", {})
    if incidence_output.get("units") != "people":
        fail(errors, "copd_incidence_flow must be published in people")
    if incidence_output.get("binding") != {
        "edge_id": "compiler::copd::incidence_from_disease_free_population"
    }:
        fail(
            errors,
            "copd_incidence_flow must bind the compiler-generated disease-free-population-to-incidence edge",
        )
    for output in module.get("published_outputs", []):
        binding = output.get("binding", {})
        if "node_id" in binding:
            published_bindings.append(binding["node_id"])
        if "node_ids" in binding:
            published_bindings.extend(binding["node_ids"])
    for node_id in published_bindings:
        if node_id not in node_set:
            fail(errors, f"Published output binds to missing node {node_id}")
    for extension in module.get("intervention_extension_points", []):
        node_id = extension.get("node_id") or (extension.get("binding") or {}).get("node_id")
        if node_id not in node_set:
            fail(errors, f"Intervention extension point binds to missing node {node_id}")
        if extension.get("channel_id") == "copd_disability_effect_transform" and node_id != "lrwz1ikj":
            fail(errors, "COPD disability intervention extension point does not bind lrwz1ikj")
    declared_data_requirements = set()
    for requirement in module.get("runtime_data_requirements", []):
        data_type = requirement.get("data_type")
        parameters = requirement.get("parameters") or {}
        disease = parameters.get("disease")
        measure = parameters.get("measure")
        observation = parameters.get("observation")
        declared_data_requirements.add((data_type, disease, measure, observation))
    for requirement in sorted(data_fetcher_requirements):
        if requirement not in declared_data_requirements:
            fail(errors, f"Model data dependency is not declared in runtime_data_requirements: {requirement}")

    tests = module.get("validation", {}).get("internal_validity_tests", [])
    if "python scripts/validate_module_contract.py" not in tests:
        fail(errors, "Module contract validation command does not point at scripts/validate_module_contract.py")
    recipe_ref = module.get("state_initialization", {}).get("recipe_ref")
    if not recipe_ref or not (REPO_ROOT / recipe_ref).exists():
        fail(errors, "Module contract state initialization recipe is missing")
    else:
        recipe = load(REPO_ROOT / recipe_ref)
        if recipe.get("module_id") != module_id:
            fail(errors, "State initialization recipe module_id does not match module contract")
        population_source = recipe.get("population_source", {})
        if population_source.get("data_type") != "fhdb.population":
            fail(errors, "State initialization recipe does not consume the canonical population source")
        durable_states = recipe.get("durable_states", [])
        prevalence_sources = [item.get("prevalence_source", {}) for item in durable_states]
        if not any(
            source.get("data_type") == "fhdb.epidemiology"
            and source.get("parameters", {}).get("disease") == "COPD"
            and source.get("parameters", {}).get("measure") == "prevalence"
            for source in prevalence_sources
        ):
            fail(errors, "State initialization recipe does not declare COPD prevalence")
        recipe_targets = {
            item.get("target_node_id")
            for group in ("durable_states", "transient_states", "zero_states")
            for item in recipe.get(group, [])
        }
        recipe_targets.add(recipe.get("residual_state", {}).get("target_node_id"))
        recipe_targets.discard(None)
        if recipe_targets != set(module.get("state_initialization", {}).get("targets", [])):
            fail(errors, "State initialization recipe targets do not match the module contract")
        residual_target = recipe.get("residual_state", {}).get("target_node_id")
        for target in recipe_targets:
            if target not in node_set and target != residual_target:
                fail(errors, f"State initialization recipe targets missing model node {target}")
        epidemiology_requirements = {
            ((item.get("parameters", {}) or {}).get("disease"), (item.get("parameters", {}) or {}).get("measure"))
            for item in module.get("runtime_data_requirements", [])
            if item.get("data_type") == "epidemiology"
        }
        if ("COPD", "prevalence") not in epidemiology_requirements:
            fail(errors, "Module runtime data requirements do not declare COPD prevalence for state initialization")

    registry_path = REPO_ROOT / "parameters" / "registry.v1.json"
    if not registry_path.exists():
        fail(errors, "Missing parameters/registry.v1.json")
        return errors
    registry = load(registry_path)
    if registry.get("schema") != "botech.parameter-registry.v1":
        fail(errors, "parameters/registry.v1.json has wrong schema")
    if registry.get("module_id") != module_id:
        fail(errors, "Parameter registry module_id does not match module contract")
    if registry.get("owner", {}).get("repo_id") != repo_id:
        fail(errors, "Parameter registry owner repo_id does not match module contract")
    registry_ids = [item.get("parameter_id") for item in registry.get("parameters", [])]
    if len(registry_ids) != len(set(registry_ids)):
        fail(errors, "Parameter registry has duplicate parameter_id values")
    registry_set = set(registry_ids)
    if any("tobacco" in str(parameter_id).lower() for parameter_id in registry_set):
        fail(errors, "COPD registry contains tobacco-owned parameter ids")
    if any(parameter_id in {"country", "start_year", "end_year"} for parameter_id in registry_set):
        fail(errors, "Runtime context appears as scenario-editable registry parameters")

    for parameter_id in registry_set:
        if any(token in str(parameter_id) for token in ("salbutamol", "prednisolone", "ipratropium")):
            fail(errors, f"COPD registry still contains extracted intervention parameter {parameter_id}")
    for text in strings_in(registry):
        if any(token in text for token in ("Salbutamol", "Prednisolone", "Ipratropium", "salbutamol", "prednisolone", "ipratropium")):
            fail(errors, f"Parameter registry still references extracted intervention surface: {text}")
            break
    for text in strings_in(registry):
        if any(token in text for token in ("build/", "scenarios/", "scenario-templates", "modular-composition")):
            fail(errors, f"Parameter registry still references removed source: {text}")
            break
    for item in registry.get("parameters", []):
        for placement in item.get("placement_refs", []):
            if placement.get("kind") != "json_path":
                fail(errors, f"Parameter {item.get('parameter_id')} has unsupported placement kind {placement.get('kind')}")
            elif not resolve_json_path(model, placement.get("ref", "")):
                fail(errors, f"Parameter {item.get('parameter_id')} placement does not resolve: {placement.get('ref')}")

    template_root = REPO_ROOT / "parameters" / "templates"
    template_files = sorted(template_root.glob("*.template.v1.json"))
    required_templates = {"copd_baseline"}
    template_ids = set()
    if not template_files:
        fail(errors, "Missing parameters/templates/*.template.v1.json")
    for template_file in template_files:
        template = load(template_file)
        template_id = template.get("template_id")
        template_ids.add(template_id)

        if template_id in {"copd_cr2", "copd_cr4"}:
            fail(errors, f"{template_file} is an extracted intervention template and should not remain source-owned")
        if template.get("schema") != "botech.scenario-template.v1":
            fail(errors, f"{template_file} has wrong template schema")
        if template.get("module_id") != module_id:
            fail(errors, f"{template_file} module_id does not match registry")
        if template.get("owner", {}).get("repo_id") != repo_id:
            fail(errors, f"{template_file} owner repo_id does not match registry")
        if template.get("parameter_registry_ref") != "parameters/registry.v1.json":
            fail(errors, f"{template_file} does not point to parameters/registry.v1.json")
        for text in strings_in(template):
            if any(token in text for token in ("build/", "scenarios/", "scenario-templates", "tobacco")):
                fail(errors, f"{template_file} contains stale or cross-module reference: {text}")
                break
        for value in template.get("parameter_values", []):
            parameter_id = value.get("parameter_id")
            if parameter_id not in registry_set:
                fail(errors, f"{template_file} references unknown parameter_id {parameter_id}")
    missing = required_templates - template_ids
    if missing:
        fail(errors, f"Missing required COPD templates: {sorted(missing)}")

    link_files = sorted((REPO_ROOT / "contracts" / "links").glob("*.link.contract.v1.json"))
    for link_file in link_files:
        link = load(link_file)
        if link.get("schema") != "botech.link-contract.v1":
            fail(errors, f"{link_file} has wrong link schema")
        source_repo = link.get("source", {}).get("repo_id")
        if source_repo and source_repo != repo_id:
            fail(errors, f"{link_file} is not source-owned by this repository")

    command_script = REPO_ROOT / "scripts" / "orchestrator_scenarios.py"
    if not command_script.exists():
        fail(errors, "Missing scripts/orchestrator_scenarios.py command surface")
    else:
        for command, expected_schema in (("catalog", "botech.parameter-registry.v1"), ("templates", "botech.module-template-registry.v1")):
            result = subprocess.run([sys.executable, str(command_script), command], cwd=REPO_ROOT, text=True, capture_output=True)
            if result.returncode != 0:
                fail(errors, f"Command surface `{command}` failed: {result.stderr.strip() or result.stdout.strip()}")
                continue
            try:
                payload = json.loads(result.stdout)
            except json.JSONDecodeError as exc:
                fail(errors, f"Command surface `{command}` did not emit valid JSON: {exc}")
                continue
            if payload.get("schema") != expected_schema:
                fail(errors, f"Command surface `{command}` emitted schema {payload.get('schema')} not {expected_schema}")

    return errors


def main() -> int:
    errors = validate()
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print("Module contract validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
