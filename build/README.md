# COPD Scenario Build System

This system allows you to compose COPD scenario files from reusable components, reducing duplication and making scenarios easier to maintain.

## Structure

```
build/
├── components/                    # Reusable parameter components
│   ├── copd_base.json            # Country parameter (included in all scenarios)
│   ├── copd_clinical_inhaled_salbutamol.json
│   ├── copd_clinical_ipratropium_inhaler.json
│   ├── copd_clinical_oral_prednisolone.json
│   └── copd_tobacco_interventions.json
├── configs/                       # YAML configuration files for scenarios
│   ├── copd_baseline.yml
│   └── copd_null.yml
├── build_scenario.py             # Build script
└── README.md                     # This file
```

## Usage

### Build a Single Scenario

```bash
python3 build_scenario.py configs/copd_baseline.yml
python3 build_scenario.py configs/copd_null.yml
```

### Build All Scenarios

```bash
python3 build_scenario.py --all
```

## COPD Intervention Components

- **Clinical Interventions**: 
  - Inhaled Salbutamol (bronchodilator for all COPD patients)
  - Ipratropium Inhaler (anticholinergic for 21% of patients)
  - Oral Prednisolone (corticosteroid for severe cases, 12% of patients)

- **Tobacco Interventions**: 
  - Protection, cessation counseling, warning labels, mass media, advertising bans
  - Unique tobacco tax parameter for price increases

## Configuration Format

Each YAML configuration file specifies:
- **metadata**: Label, description, and authors
- **components**: List of component JSON files to include
- **overrides**: Parameter values to override after merging components
- **output**: Where to save the generated scenario

Example configuration (`configs/copd_baseline.yml`):

```yaml
metadata:
  label: "COPD - Default Scenario"
  description: "A scenario where there is no change in the coverage of any intervention"
  authors: []

components:
  - copd_base.json
  - copd_clinical_inhaled_salbutamol.json
  - copd_clinical_ipratropium_inhaler.json
  - copd_clinical_oral_prednisolone.json
  - copd_tobacco_interventions.json

overrides: {}

output: ../scenarios/copd_baseline.json
```

## Workflow

1. **Create/Edit YAML config**: Define which components to include and any overrides
2. **Build scenario**: Run `python3 build_scenario.py configs/your_scenario.yml`
3. **Optional manual editing**: Further customize the generated JSON if needed
4. **Maintain**: When base parameters change, update component files and rebuild all scenarios with `--all`

## Creating New COPD Scenarios

1. Create a new YAML file in `configs/`:
   ```yaml
   metadata:
     label: "COPD CR2 Scenario"
     description: "COPD scenario with specific intervention scaling"
   
   components:
     - copd_base.json
     - copd_clinical_inhaled_salbutamol.json
     - copd_clinical_ipratropium_inhaler.json
     - copd_clinical_oral_prednisolone.json
     - copd_tobacco_interventions.json
   
   overrides:
     "Inhaled Salbutamol Target Coverage":
       value: 0.80
     "Ipratropium Inhaler Target Coverage":
       value: 0.65
   
   output: ../scenarios/copd_cr2.json
   ```

2. Build it:
   ```bash
   python3 build_scenario.py configs/copd_cr2.yml
   ```

## Benefits

- **DRY**: Country parameter paths defined once
- **Maintainable**: Update intervention parameters in one place
- **Composable**: Mix and match components as needed
- **Traceable**: Clear inheritance from components to final scenarios