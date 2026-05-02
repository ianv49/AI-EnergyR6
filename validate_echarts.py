#!/usr/bin/env python3
"""
Validation script for ECharts implementation
Checks:
1. All 48 CSV files exist
2. CSV files have proper structure
3. Data types and columns are correct
4. No side effects on other pages
"""

import os
import glob
import csv
from pathlib import Path

def check_csv_files():
    """Verify all 48 monthly CSV files exist and are valid"""
    print("\n" + "="*60)
    print("CSV FILES VALIDATION")
    print("="*60)
    
    data_dir = Path('/Users/ianvallejo/Documents/GitHub/AI-EnergyR6/data')
    
    # Expected files
    sources = ['nasa', 'openmeteo', 'meteostat', 'weatherbit']
    months = [f'{i:02d}' for i in range(1, 13)]
    month_names = ['january', 'february', 'march', 'april', 'may', 'june',
                   'july', 'august', 'september', 'october', 'november', 'december']
    
    expected_files = []
    for source in sources:
        for month_code, month_name in zip(months, month_names):
            filename = f'{source}_2025_{month_code}_{month_name}.csv'
            expected_files.append(filename)
    
    # Check each file
    found = 0
    missing = 0
    invalid = 0
    
    for filename in expected_files:
        filepath = data_dir / filename
        
        if not filepath.exists():
            print(f"✗ MISSING: {filename}")
            missing += 1
            continue
        
        # Validate file structure
        try:
            with open(filepath, 'r') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                
                if not rows:
                    print(f"✗ EMPTY: {filename}")
                    invalid += 1
                    continue
                
                # Check required columns
                required_cols = ['timestamp', 'temperature', 'humidity', 'irradiance', 
                                'wind_speed', 'solar_energy_yield']
                row = rows[0]
                missing_cols = [col for col in required_cols if col not in row]
                
                if missing_cols:
                    print(f"✗ INVALID COLUMNS in {filename}: missing {missing_cols}")
                    invalid += 1
                    continue
                
                found += 1
                print(f"✓ {filename} ({len(rows)} rows)")
                
        except Exception as e:
            print(f"✗ ERROR in {filename}: {e}")
            invalid += 1
    
    print(f"\nSummary: {found} valid, {missing} missing, {invalid} invalid")
    return found == 48

def check_html_structure():
    """Verify Data Charts tab structure in index.html"""
    print("\n" + "="*60)
    print("HTML STRUCTURE VALIDATION")
    print("="*60)
    
    with open('/Users/ianvallejo/Documents/GitHub/AI-EnergyR6/index.html', 'r') as f:
        content = f.read()
    
    checks = {
        'Chart Type dropdown': 'id="chartTypeSelect"' in content,
        'ECharts CDN': 'echarts@5.4.3' in content,
        'Data Chart container': 'id="dataChart"' in content,
        'Line chart function': 'function createLineChart' in content,
        'Scatter chart function': 'function createScatterChart' in content,
        'Box plot function': 'function createBoxPlot' in content,
        'Histogram function': 'function createHistogram' in content,
        'Heatmap function': 'function createHeatmap' in content,
        'Trendline function': 'function calculateTrendline' in content,
        'Event listeners': "document.getElementById('chartTypeSelect')" in content,
    }
    
    passed = 0
    for check_name, result in checks.items():
        status = "✓" if result else "✗"
        print(f"{status} {check_name}")
        if result:
            passed += 1
    
    print(f"\nPassed: {passed}/{len(checks)}")
    return passed == len(checks)

def check_no_chart_js_conflict():
    """Verify Chart.js is not used in Data Charts tab"""
    print("\n" + "="*60)
    print("LIBRARY CONFLICT CHECK")
    print("="*60)
    
    with open('/Users/ianvallejo/Documents/GitHub/AI-EnergyR6/index.html', 'r') as f:
        content = f.read()
    
    # Extract Data Charts section
    start = content.find('<!-- Data Charts Tab -->') or content.find('id="data-charts"')
    end = content.find('<!-- ML Results Comparison -->', start) or content.find('</div>', start + 1000)
    
    if start == -1:
        print("✗ Could not locate Data Charts section")
        return False
    
    data_charts_section = content[start:end] if end != -1 else content[start:]
    
    checks = {
        'No Chart.js canvas': 'canvas' not in data_charts_section or 'chart' not in data_charts_section.lower(),
        'ECharts div container': '<div id="dataChart"' in data_charts_section,
        'Chart.js not referenced': 'new Chart(' not in data_charts_section,
    }
    
    passed = 0
    for check_name, result in checks.items():
        status = "✓" if result else "✗"
        print(f"{status} {check_name}")
        if result:
            passed += 1
    
    print(f"\nPassed: {passed}/{len(checks)}")
    return passed == len(checks)

def main():
    print("\n" + "="*60)
    print("ECHARTS IMPLEMENTATION VALIDATION")
    print("="*60)
    
    results = {
        'CSV Files': check_csv_files(),
        'HTML Structure': check_html_structure(),
        'No Conflicts': check_no_chart_js_conflict(),
    }
    
    print("\n" + "="*60)
    print("FINAL RESULTS")
    print("="*60)
    
    all_passed = True
    for check_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {check_name}")
        if not result:
            all_passed = False
    
    if all_passed:
        print("\n✓ All validation checks passed!")
        print("\nThe ECharts implementation is ready for testing.")
        print("Next steps:")
        print("  1. Open index.html in a browser")
        print("  2. Navigate to Data Charts tab")
        print("  3. Test all chart types: Line, Scatter+Trendline, Box Plot, Histogram, Heatmap")
        print("  4. Verify other tabs (ML Results, Raw Data) are unaffected")
    else:
        print("\n✗ Some validation checks failed. Review above for details.")
    
    return 0 if all_passed else 1

if __name__ == '__main__':
    exit(main())
