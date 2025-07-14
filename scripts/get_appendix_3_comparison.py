#!/usr/bin/env python3
"""
Script to compare latest model results with Appendix 3 reference data.
Runs compare_latest_results.py for null vs c2 and null vs c4, then compares
the outputs with the reference values from data/copd_impact_a3.csv.
"""

import subprocess
import sys
import csv
from pathlib import Path
import re

def run_comparison(baseline, comparison):
    """
    Run compare_latest_results.py and capture the output.
    
    Args:
        baseline: Baseline scenario name
        comparison: Comparison scenario name
        
    Returns:
        Dict mapping country ISO3 to difference value
    """
    cmd = [
        sys.executable,
        "scripts/compare_latest_results.py",
        "--baseline", baseline,
        "--comparison", comparison
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        output = result.stdout
        
        # Parse the output to extract country and difference values
        results = {}
        lines = output.strip().split('\n')
        
        # Skip header lines and find data
        data_started = False
        for line in lines:
            if line.startswith('-' * 40):
                if data_started:
                    break  # End of data section
                else:
                    data_started = True
                    continue
                    
            if data_started and '\t' in line:
                parts = line.split('\t')
                if len(parts) == 2:
                    country = parts[0].strip()
                    try:
                        value = float(parts[1].replace(',', ''))
                        results[country] = value
                    except ValueError:
                        continue
        
        return results
        
    except subprocess.CalledProcessError as e:
        print(f"Error running comparison: {e}")
        print(f"Error output: {e.stderr}")
        return {}

def load_appendix_3_data():
    """
    Load reference data from copd_impact_a3.csv.
    
    Returns:
        Dict with structure: {country: {'CR2': value, 'CR4': value}}
    """
    csv_path = Path("data/copd_impact_a3.csv")
    if not csv_path.exists():
        print(f"Error: {csv_path} not found")
        return {}
    
    data = {}
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            iso3 = row['ISO3']
            if iso3:
                cr2_str = row['CR2'].replace(',', '')
                cr4_str = row['CR4'].replace(',', '')
                data[iso3] = {
                    'CR2': float(cr2_str) if cr2_str and cr2_str != '0' else 0,
                    'CR4': float(cr4_str) if cr4_str and cr4_str != '0' else 0
                }
    
    return data

def main():
    print("Comparing latest model results with Appendix 3 reference data")
    print("=" * 70)
    
    # Run comparisons
    print("\nRunning null vs copd_cr2_scenario comparison...")
    c2_results = run_comparison("copd_null_scenario", "copd_cr2_scenario")
    
    print("\nRunning null vs copd_cr4_scenario comparison...")
    c4_results = run_comparison("copd_null_scenario", "copd_cr4_scenario")
    
    # Load reference data
    print("\nLoading Appendix 3 reference data...")
    appendix_3_data = load_appendix_3_data()
    
    if not c2_results and not c4_results:
        print("Error: No results from model comparisons")
        return
        
    if not appendix_3_data:
        print("Error: No reference data loaded")
        return
    
    # Compare results
    print("\n" + "=" * 70)
    print("Comparison Results (Model/Reference Ratio)")
    print("=" * 70)
    print(f"{'Country':<10} {'CR2 Model':<15} {'CR2 Ref':<15} {'CR2 Ratio':<12} {'CR4 Model':<15} {'CR4 Ref':<15} {'CR4 Ratio':<12}")
    print("-" * 95)
    
    # Find common countries
    all_countries = set()
    all_countries.update(c2_results.keys())
    all_countries.update(c4_results.keys())
    all_countries.update(appendix_3_data.keys())
    
    total_c2_model = 0
    total_c2_ref = 0
    total_c4_model = 0
    total_c4_ref = 0
    c2_count = 0
    c4_count = 0
    
    for country in sorted(all_countries):
        c2_model = c2_results.get(country, 0)
        c4_model = c4_results.get(country, 0)
        
        ref_data = appendix_3_data.get(country, {})
        c2_ref = ref_data.get('CR2', 0)
        c4_ref = ref_data.get('CR4', 0)
        
        # Calculate ratios
        c2_ratio = c2_model / c2_ref if c2_ref != 0 else float('inf') if c2_model != 0 else 0
        c4_ratio = c4_model / c4_ref if c4_ref != 0 else float('inf') if c4_model != 0 else 0
        
        # Format output
        c2_model_str = f"{c2_model:,.0f}" if c2_model != 0 else "-"
        c4_model_str = f"{c4_model:,.0f}" if c4_model != 0 else "-"
        c2_ref_str = f"{c2_ref:,.0f}" if c2_ref != 0 else "-"
        c4_ref_str = f"{c4_ref:,.0f}" if c4_ref != 0 else "-"
        c2_ratio_str = f"{c2_ratio:.4f}" if c2_ratio not in [0, float('inf')] else "-"
        c4_ratio_str = f"{c4_ratio:.4f}" if c4_ratio not in [0, float('inf')] else "-"
        
        print(f"{country:<10} {c2_model_str:<15} {c2_ref_str:<15} {c2_ratio_str:<12} {c4_model_str:<15} {c4_ref_str:<15} {c4_ratio_str:<12}")
        
        # Update totals
        if c2_model != 0 and c2_ref != 0:
            total_c2_model += c2_model
            total_c2_ref += c2_ref
            c2_count += 1
            
        if c4_model != 0 and c4_ref != 0:
            total_c4_model += c4_model
            total_c4_ref += c4_ref
            c4_count += 1
    
    # Summary statistics
    print("-" * 95)
    print("\nSummary Statistics:")
    print("-" * 30)
    
    if c2_count > 0:
        overall_c2_ratio = total_c2_model / total_c2_ref
        print(f"CR2 - Countries compared: {c2_count}")
        print(f"CR2 - Total Model HYL: {total_c2_model:,.0f}")
        print(f"CR2 - Total Ref HYL: {total_c2_ref:,.0f}")
        print(f"CR2 - Overall Ratio: {overall_c2_ratio:.4f}")
    
    if c4_count > 0:
        overall_c4_ratio = total_c4_model / total_c4_ref
        print(f"\nCR4 - Countries compared: {c4_count}")
        print(f"CR4 - Total Model HYL: {total_c4_model:,.0f}")
        print(f"CR4 - Total Ref HYL: {total_c4_ref:,.0f}")
        print(f"CR4 - Overall Ratio: {overall_c4_ratio:.4f}")

if __name__ == "__main__":
    main()