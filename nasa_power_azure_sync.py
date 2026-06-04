#!/usr/bin/env python3
"""
NASA POWER Azure Sync Module
Handles uploading NASA POWER data to Azure Blob Storage and comparing timestamps
"""

import os
from pathlib import Path
from datetime import datetime
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv

# Load environment variables from .env.azure file
load_dotenv(dotenv_path='.env.azure')


class NasaPowerAzureSync:
    """Sync NASA POWER data with Azure Blob Storage"""
    
    def __init__(self):
        """Initialize Azure Blob Storage connection"""
        self.storage_account = os.getenv('AZURE_STORAGE_ACCOUNT')
        self.storage_key = os.getenv('AZURE_STORAGE_KEY')
        self.container_name = os.getenv('AZURE_BLOB_CONTAINER', 'ai-energy-r6-data')
        
        if not self.storage_account or not self.storage_key:
            raise ValueError(
                "Azure Storage credentials not found. "
                "Please set AZURE_STORAGE_ACCOUNT and AZURE_STORAGE_KEY in .env.azure"
            )
        
        # Initialize blob client
        self.blob_service_client = BlobServiceClient(
            account_url=f"https://{self.storage_account}.blob.core.windows.net",
            credential=self.storage_key
        )
        self.container_client = self.blob_service_client.get_container_client(self.container_name)
        print(f"✓ Connected to Azure Blob Storage: {self.storage_account}/{self.container_name}")
    
    def upload_nasa_data(self, local_file_path, blob_name=None):
        """Upload NASA POWER data file to Azure
        
        Args:
            local_file_path (str): Local file path (e.g., data/nasa-api.txt or CSV)
            blob_name (str): Name in Azure (if None, uses filename)
        
        Returns:
            bool: True if successful
        """
        try:
            local_path = Path(local_file_path)
            if not local_path.exists():
                print(f"✗ File not found: {local_file_path}")
                return False
            
            blob_name = blob_name or str(local_path.name)
            
            with open(local_path, "rb") as data:
                self.container_client.upload_blob(blob_name, data, overwrite=True)
            
            print(f"✓ Uploaded to Azure: {local_path.name} → {blob_name}")
            return True
        except Exception as e:
            print(f"✗ Upload failed: {e}")
            return False
    
    def get_latest_timestamp_from_azure(self, blob_name='nasa-api.txt'):
        """Get latest data timestamp from Azure blob
        
        Args:
            blob_name (str): Blob name in Azure
        
        Returns:
            str: Latest timestamp or None if file not found/empty
        """
        try:
            blob_client = self.container_client.get_blob_client(blob_name)
            blob_data = blob_client.download_blob().readall().decode('utf-8')
            
            # Parse the blob to find latest timestamp
            lines = blob_data.strip().split('\n')
            data_rows = [line for line in lines if line.strip() and not line.startswith('#') and not line.startswith('[')]
            
            if data_rows:
                # Get the last row (most recent due to descending order or ascending)
                last_row = data_rows[-1].split(',')
                if len(last_row) > 1:
                    latest_timestamp = last_row[1]
                    print(f"✓ Latest timestamp in Azure ({blob_name}): {latest_timestamp}")
                    return latest_timestamp
            
            print(f"✗ No data rows found in Azure blob: {blob_name}")
            return None
        except Exception as e:
            print(f"✗ Failed to get timestamp from Azure: {e}")
            return None
    
    def get_latest_timestamp_local(self, local_file_path):
        """Get latest data timestamp from local file
        
        Args:
            local_file_path (str): Local file path
        
        Returns:
            str: Latest timestamp or None if file not found/empty
        """
        try:
            local_path = Path(local_file_path)
            if not local_path.exists():
                print(f"✗ Local file not found: {local_file_path}")
                return None
            
            with open(local_path, 'r') as f:
                lines = f.readlines()
            
            # Parse to find latest timestamp
            data_rows = [line for line in lines if line.strip() and not line.startswith('#') and not line.startswith('[')]
            
            if data_rows:
                # Get the last row (most recent)
                last_row = data_rows[-1].split(',')
                if len(last_row) > 1:
                    latest_timestamp = last_row[1]
                    print(f"✓ Latest timestamp local ({local_file_path}): {latest_timestamp}")
                    return latest_timestamp
            
            print(f"✗ No data rows found in local file: {local_file_path}")
            return None
        except Exception as e:
            print(f"✗ Failed to get timestamp from local file: {e}")
            return None
    
    def compare_timestamps(self, local_file_path, azure_blob_name='nasa-api.txt'):
        """Compare latest timestamps between local and Azure
        
        Args:
            local_file_path (str): Local file path
            azure_blob_name (str): Azure blob name
        
        Returns:
            dict: Comparison results
        """
        local_ts = self.get_latest_timestamp_local(local_file_path)
        azure_ts = self.get_latest_timestamp_from_azure(azure_blob_name)
        
        result = {
            'local_timestamp': local_ts,
            'azure_timestamp': azure_ts,
            'local_file': local_file_path,
            'azure_blob': azure_blob_name,
            'comparison': None
        }
        
        if local_ts and azure_ts:
            if local_ts > azure_ts:
                result['comparison'] = 'LOCAL_AHEAD'
                print(f"ℹ Local data is more recent (needs upload to Azure)")
            elif local_ts < azure_ts:
                result['comparison'] = 'AZURE_AHEAD'
                print(f"ℹ Azure data is more recent (local is behind)")
            else:
                result['comparison'] = 'SYNCHRONIZED'
                print(f"✓ Data is synchronized!")
        elif local_ts and not azure_ts:
            result['comparison'] = 'AZURE_MISSING'
            print(f"ℹ Azure blob missing, local data needs initial upload")
        elif azure_ts and not local_ts:
            result['comparison'] = 'LOCAL_MISSING'
            print(f"ℹ Local file missing")
        else:
            result['comparison'] = 'BOTH_MISSING'
            print(f"✗ Both local and Azure data missing")
        
        return result
    
    def sync_nasa_data(self, data_dir='data'):
        """Sync all NASA POWER data files to Azure
        
        Args:
            data_dir (str): Local data directory
        
        Returns:
            dict: Sync results
        """
        results = {
            'main_file': None,
            'csv_files': [],
            'timestamp_comparison': None
        }
        
        # Upload main nasa-api.txt
        main_file = os.path.join(data_dir, 'nasa-api.txt')
        if os.path.exists(main_file):
            results['main_file'] = self.upload_nasa_data(main_file)
        
        # Upload all nasa monthly CSVs
        for filename in os.listdir(data_dir):
            if filename.startswith('nasa_') and filename.endswith('.csv'):
                csv_path = os.path.join(data_dir, filename)
                self.upload_nasa_data(csv_path)
                results['csv_files'].append(filename)
        
        # Compare timestamps
        if os.path.exists(main_file):
            results['timestamp_comparison'] = self.compare_timestamps(main_file)
        
        print(f"\n✓ Sync complete: {len(results['csv_files'])} CSV files uploaded")
        return results


def main():
    """Test the Azure sync functionality"""
    try:
        sync = NasaPowerAzureSync()
        
        # Sync all NASA data
        print("\n=== Syncing NASA POWER data to Azure ===")
        results = sync.sync_nasa_data()
        
        print("\n=== Timestamp Comparison ===")
        if results['timestamp_comparison']:
            comp = results['timestamp_comparison']
            print(f"Local:  {comp['local_timestamp']}")
            print(f"Azure:  {comp['azure_timestamp']}")
            print(f"Status: {comp['comparison']}")
    
    except Exception as e:
        print(f"✗ Error: {e}")
        print("\nNote: Ensure .env.azure file has AZURE_STORAGE_ACCOUNT and AZURE_STORAGE_KEY")


if __name__ == '__main__':
    main()
