#!/usr/bin/env python3
"""
Generate monthly CSV files for 2025 data from raw API files.
Creates separate CSV files for each month: data/[source]_2025_[month].csv
"""

import os
from datetime import datetime

# Define raw data files mapping
RAW_FILES = {
    'nasa': 'data/nasa-api.txt',
    'openmeteo': 'data/openmet-api.txt',
    'meteostat': 'data/metstat-api.txt',
    'weatherbit': 'data/wethrbit-api.txt'
}

MONTHS = {
    1: 'january', 2: 'february', 3: 'march', 4: 'april',
    5: 'may', 6: 'june', 7: 'july', 8: 'august',
    9: 'september', 10: 'october', 11: 'november', 12: 'december'
}

def parse_raw_file(filepath):
    """Parse raw data file and extract CSV data."""
    rows = []
    headers = None
    
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            
            # Skip metadata
            if line.startswith('#') or line.startswith('['):
                continue
            
            # Extract headers
            if line.startswith('id,'):
                headers = line.split(',')
                continue
            
            # Skip empty lines
            if not line:
                continue
            
            # Parse data rows
            cols = line.split(',')
            if headers and len(cols) == len(headers):
                rows.append(dict(zip(headers, cols)))
    
    return headers, rows

def filter_by_month(rows, source, month):
    """Filter rows for a specific month in 2025."""
    filtered = []
    
    for row in rows:
        ts = row.get('timestamp', '')
        
        # Handle different timestamp formats
        if 'T' in ts:
            ts = ts.replace('T', ' ')
        
        try:
            dt = datetime.strptime(ts[:10], '%Y-%m-%d')
            if dt.year == 2025 and dt.month == month:
                filtered.append(row)
        except:
            pass
    
    return filtered

def write_csv_month(source, month, month_name, headers, rows):
    """Write monthly CSV file."""
    filename = f"data/{source}_2025_{month:02d}_{month_name}.csv"
    
    filtered_rows = filter_by_month(rows, source, month)
    
    if not filtered_rows:
        print(f"  No data for {month_name}")
        return
    
    with open(filename, 'w') as f:
        # Write header
        f.write(','.join(headers) + '\n')
        
        # Write data rows
        for row in filtered_rows:
            values = [row.get(h, '') for h in headers]
            f.write(','.join(values) + '\n')
    
    print(f"  Created {filename} ({len(filtered_rows)} rows)")

def main():
    print("Generating monthly CSV files for 2025...\n")
    
    for source, filepath in RAW_FILES.items():
        print(f"Processing {source.upper()} ({filepath})...")
        
        if not os.path.exists(filepath):
            print(f"  ERROR: File not found: {filepath}\n")
            continue
        
        headers, rows = parse_raw_file(filepath)
        
        if not headers:
            print(f"  ERROR: Could not parse {filepath}\n")
            continue
        
        # Generate files for each month
        for month in range(1, 13):
            month_name = MONTHS[month]
            write_csv_month(source, month, month_name, headers, rows)
        
        print()
    
    print("✓ Done! Monthly CSV files generated in data/ directory")

if __name__ == '__main__':
    main()
