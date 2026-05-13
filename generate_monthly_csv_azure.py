#!/usr/bin/env python3
"""
Generate Monthly CSV from Azure Data
Creates monthly CSV reports from Azure Cosmos DB data
"""

import csv
import os
from pathlib import Path
from datetime import datetime, timedelta
from azure_database import AzureDatabase


class AzureCSVGenerator:
    """Generate CSV reports from Azure Cosmos DB data"""
    
    def __init__(self, database=None, output_dir='data'):
        """Initialize CSV generator
        
        Args:
            database (AzureDatabase): Database instance
            output_dir (str): Output directory for CSV files
        """
        self.database = database or AzureDatabase()
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def generate_monthly_csv(self, year, month, source=None):
        """Generate CSV for a specific month
        
        Args:
            year (int): Year
            month (int): Month (1-12)
            source (str): Optional data source filter
        
        Returns:
            str: Path to generated CSV file
        """
        # Calculate date range
        start_date = f"{year:04d}-{month:02d}-01"
        
        if month == 12:
            end_date = f"{year+1:04d}-01-01"
        else:
            end_date = f"{year:04d}-{month+1:02d}-01"
        
        # Query data
        print(f"\nGenerating CSV for {year}-{month:02d}...")
        data = self.database.query_by_date_range(
            start_date, 
            end_date,
            source=source,
            limit=100000
        )
        
        if not data:
            print(f"⚠ No data found for {year}-{month:02d}")
            return None
        
        # Generate filename
        if source:
            csv_filename = f"{source}_{year:04d}_{month:02d}_{self._month_name(month).lower()}.csv"
        else:
            csv_filename = f"weather_{year:04d}_{month:02d}_{self._month_name(month).lower()}.csv"
        
        csv_path = self.output_dir / csv_filename
        
        # Write CSV
        try:
            with open(csv_path, 'w', newline='') as csvfile:
                if not data:
                    return None
                
                fieldnames = set()
                for item in data:
                    fieldnames.update(item.keys())
                fieldnames = sorted(list(fieldnames))
                
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for item in data:
                    writer.writerow(item)
            
            print(f"✓ Generated: {csv_path} ({len(data)} records)")
            return str(csv_path)
        except Exception as e:
            print(f"✗ Failed to generate CSV: {str(e)}")
            return None
    
    def generate_range_csv(self, start_year, start_month, end_year, end_month, source=None):
        """Generate CSV for a range of months
        
        Args:
            start_year (int): Start year
            start_month (int): Start month (1-12)
            end_year (int): End year
            end_month (int): End month (1-12)
            source (str): Optional data source filter
        
        Returns:
            list: Paths to generated CSV files
        """
        print("\n" + "="*60)
        print("GENERATING MONTHLY CSV REPORTS")
        print("="*60)
        
        csv_files = []
        current_year = start_year
        current_month = start_month
        
        while (current_year, current_month) <= (end_year, end_month):
            csv_path = self.generate_monthly_csv(current_year, current_month, source)
            if csv_path:
                csv_files.append(csv_path)
            
            # Next month
            if current_month == 12:
                current_year += 1
                current_month = 1
            else:
                current_month += 1
        
        print(f"\n✓ Generated {len(csv_files)} CSV files")
        return csv_files
    
    def generate_march_april_2026_csv(self, source=None):
        """Generate CSV for March-April 2026
        
        Args:
            source (str): Optional data source filter
        
        Returns:
            list: Paths to generated CSV files
        """
        print("\n" + "="*60)
        print("GENERATING MARCH-APRIL 2026 CSV")
        print("="*60)
        
        csv_files = []
        
        # March 2026
        csv_path = self.generate_monthly_csv(2026, 3, source)
        if csv_path:
            csv_files.append(csv_path)
        
        # April 2026
        csv_path = self.generate_monthly_csv(2026, 4, source)
        if csv_path:
            csv_files.append(csv_path)
        
        return csv_files
    
    def generate_all_source_csv(self, year, month):
        """Generate CSV for each data source for a specific month
        
        Args:
            year (int): Year
            month (int): Month (1-12)
        
        Returns:
            list: Paths to generated CSV files
        """
        print(f"\nGenerating CSV by source for {year}-{month:02d}...")
        
        sources = ['nasa', 'openmeteo', 'weatherbit', 'meteostat']
        csv_files = []
        
        for source in sources:
            csv_path = self.generate_monthly_csv(year, month, source)
            if csv_path:
                csv_files.append(csv_path)
        
        return csv_files
    
    @staticmethod
    def _month_name(month):
        """Get month name
        
        Args:
            month (int): Month number (1-12)
        
        Returns:
            str: Month name
        """
        months = [
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        ]
        return months[month - 1] if 1 <= month <= 12 else 'Unknown'
    
    def generate_summary_report(self):
        """Generate summary report of all data
        
        Returns:
            str: Path to summary report
        """
        print("\nGenerating summary report...")
        
        try:
            stats = self.database.get_table_stats()
            
            report_path = self.output_dir / 'DATA_SUMMARY.txt'
            
            with open(report_path, 'w') as f:
                f.write("="*60 + "\n")
                f.write("AZURE DATA SUMMARY REPORT\n")
                f.write("="*60 + "\n\n")
                
                f.write(f"Generated: {datetime.now().isoformat()}\n\n")
                
                f.write("STATISTICS:\n")
                f.write(f"  Total Items: {stats.get('total_items', 0)}\n")
                f.write(f"  Unique Sources: {stats.get('unique_sources', 0)}\n")
                f.write(f"  Sources: {', '.join(stats.get('sources', []))}\n")
                f.write(f"  Date Range: {stats.get('min_date', 'N/A')} to {stats.get('max_date', 'N/A')}\n")
            
            print(f"✓ Generated summary: {report_path}")
            return str(report_path)
        except Exception as e:
            print(f"✗ Failed to generate summary: {str(e)}")
            return None


if __name__ == "__main__":
    generator = AzureCSVGenerator()
    
    print("\n" + "="*60)
    print("AZURE CSV GENERATOR")
    print("="*60)
    
    # Example: Generate March-April 2026 CSV
    csv_files = generator.generate_march_april_2026_csv()
    
    # Example: Generate summary report
    summary = generator.generate_summary_report()
    
    print("\n" + "="*60)
    print("CSV GENERATION COMPLETE")
    print("="*60)
    if csv_files:
        print(f"Generated {len(csv_files)} CSV files in {generator.output_dir}")
