#!/usr/bin/env python3
"""
NASA POWER Azure Sync Module - ENHANCED
Handles uploading NASA POWER data to Azure Blob Storage and comparing timestamps
With comprehensive error handling, logging, and atomic operations
"""

import os
from pathlib import Path
from datetime import datetime
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv
import logging
import sys

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('logs/azure_sync.log', mode='a')
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables from .env.azure file
load_dotenv(dotenv_path='.env.azure')

# Ensure logs directory exists
os.makedirs('logs', exist_ok=True)


class NasaPowerAzureSync:
    """Sync NASA POWER data with Azure Blob Storage"""
    
    def __init__(self):
        """Initialize Azure Blob Storage connection"""
        logger.info("Initializing Azure Blob Storage connection...")
        self.storage_account = os.getenv('AZURE_STORAGE_ACCOUNT')
        self.storage_key = os.getenv('AZURE_STORAGE_KEY')
        self.container_name = os.getenv('AZURE_BLOB_CONTAINER', 'ai-energy-r6-data')
        
        if not self.storage_account or not self.storage_key:
            logger.error("Azure credentials not found in .env.azure")
            raise ValueError(
                "Azure Storage credentials not found. "
                "Please set AZURE_STORAGE_ACCOUNT and AZURE_STORAGE_KEY in .env.azure"
            )
        
        try:
            # Initialize blob client
            self.blob_service_client = BlobServiceClient(
                account_url=f"https://{self.storage_account}.blob.core.windows.net",
                credential=self.storage_key
            )
            self.container_client = self.blob_service_client.get_container_client(self.container_name)
            
            # Verify connection
            self.container_client.get_container_properties()
            logger.info(f"✓ Connected to Azure Blob Storage: {self.storage_account}/{self.container_name}")
        except Exception as e:
            logger.error(f"Failed to connect to Azure: {e}")
            raise
    
    def upload_nasa_data(self, local_file_path, blob_name=None):
        """Upload NASA POWER data file to Azure with verification
        
        Args:
            local_file_path (str): Local file path (e.g., data/nasa-api.txt or CSV)
            blob_name (str): Name in Azure (if None, uses filename)
        
        Returns:
            dict: Upload result with success status and details
        """
        try:
            local_path = Path(local_file_path)
            if not local_path.exists():
                logger.error(f"File not found: {local_file_path}")
                return {'success': False, 'error': f'File not found: {local_file_path}', 'file': local_file_path}
            
            blob_name = blob_name or str(local_path.name)
            file_size = local_path.stat().st_size
            
            logger.info(f"Uploading {local_path.name} ({file_size} bytes) to Azure as {blob_name}...")
            
            with open(local_path, "rb") as data:
                self.container_client.upload_blob(blob_name, data, overwrite=True)
            
            logger.info(f"✓ Successfully uploaded: {blob_name}")
            return {
                'success': True,
                'file': str(local_path.name),
                'blob_name': blob_name,
                'size': file_size,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Upload failed for {local_file_path}: {e}")
            return {'success': False, 'error': str(e), 'file': local_file_path}
    
    def get_latest_timestamp_from_azure(self, blob_name='nasa-api.txt'):
        """Get latest data timestamp from Azure blob
        
        Args:
            blob_name (str): Blob name in Azure
        
        Returns:
            dict: Result with timestamp and metadata
        """
        try:
            blob_client = self.container_client.get_blob_client(blob_name)
            blob_data = blob_client.download_blob().readall().decode('utf-8')
            
            # Parse the blob to find latest timestamp
            lines = blob_data.strip().split('\n')
            data_rows = [line for line in lines if line.strip() and not line.startswith('#') and not line.startswith('[')]
            
            if data_rows:
                # Get the last row (most recent)
                last_row = data_rows[-1].split(',')
                if len(last_row) > 1:
                    latest_timestamp = last_row[1]
                    logger.info(f"✓ Latest timestamp in Azure ({blob_name}): {latest_timestamp}")
                    return {
                        'success': True,
                        'timestamp': latest_timestamp,
                        'row_count': len(data_rows),
                        'blob': blob_name
                    }
            
            logger.warning(f"No data rows found in Azure blob: {blob_name}")
            return {'success': False, 'error': 'No data rows found', 'blob': blob_name}
        except Exception as e:
            logger.error(f"Failed to get timestamp from Azure blob {blob_name}: {e}")
            return {'success': False, 'error': str(e), 'blob': blob_name}
    
    def get_latest_timestamp_local(self, local_file_path):
        """Get latest data timestamp from local file
        
        Args:
            local_file_path (str): Local file path
        
        Returns:
            dict: Result with timestamp and metadata
        """
        try:
            local_path = Path(local_file_path)
            if not local_path.exists():
                logger.error(f"Local file not found: {local_file_path}")
                return {'success': False, 'error': f'File not found', 'file': local_file_path}
            
            with open(local_path, 'r') as f:
                lines = f.readlines()
            
            # Parse to find latest timestamp
            data_rows = [line for line in lines if line.strip() and not line.startswith('#') and not line.startswith('[')]
            
            if data_rows:
                # Get the last row (most recent)
                last_row = data_rows[-1].split(',')
                if len(last_row) > 1:
                    latest_timestamp = last_row[1]
                    logger.info(f"✓ Latest timestamp local ({local_file_path}): {latest_timestamp}")
                    return {
                        'success': True,
                        'timestamp': latest_timestamp,
                        'row_count': len(data_rows),
                        'file': str(local_path.name)
                    }
            
            logger.warning(f"No data rows found in local file: {local_file_path}")
            return {'success': False, 'error': 'No data rows found', 'file': local_file_path}
        except Exception as e:
            logger.error(f"Failed to get timestamp from local file {local_file_path}: {e}")
            return {'success': False, 'error': str(e), 'file': local_file_path}
    
    def mirror_azure_to_local(self, azure_blob_name, local_file_path):
        """Mirror (download) Azure blob data to local file
        
        Args:
            azure_blob_name (str): Azure blob name (e.g., 'nasa-api.txt')
            local_file_path (str): Local file path to write mirror (e.g., 'data/nasa-api-azure.txt')
        
        Returns:
            dict: Mirror result with success status and metadata
        """
        try:
            logger.info(f"Mirroring {azure_blob_name} from Azure to {local_file_path}...")
            
            # Download blob from Azure
            blob_client = self.container_client.get_blob_client(azure_blob_name)
            blob_data = blob_client.download_blob().readall()
            
            # Ensure directory exists
            local_path = Path(local_file_path)
            local_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write to local file atomically (temp file → rename pattern)
            temp_path = local_path.with_suffix('.tmp')
            with open(temp_path, 'wb') as f:
                f.write(blob_data)
            
            # Atomic rename
            temp_path.replace(local_path)
            
            file_size = len(blob_data)
            logger.info(f"✓ Successfully mirrored {azure_blob_name} ({file_size} bytes) to {local_file_path}")
            
            return {
                'success': True,
                'azure_blob': azure_blob_name,
                'local_file': str(local_path.name),
                'size': file_size,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to mirror {azure_blob_name} to {local_file_path}: {e}")
            return {'success': False, 'error': str(e), 'azure_blob': azure_blob_name, 'local_file': local_file_path}
    
    def compare_timestamps(self, local_file_path, azure_blob_name='nasa-api.txt'):
        """Compare latest timestamps between local and Azure
        
        Args:
            local_file_path (str): Local file path
            azure_blob_name (str): Azure blob name
        
        Returns:
            dict: Detailed comparison results
        """
        logger.info(f"Comparing timestamps: {local_file_path} <-> {azure_blob_name}")
        
        local_result = self.get_latest_timestamp_local(local_file_path)
        azure_result = self.get_latest_timestamp_from_azure(azure_blob_name)
        
        comparison = {
            'local': local_result,
            'azure': azure_result,
            'comparison': 'ERROR',
            'action_needed': False
        }
        
        # Determine comparison status
        if local_result['success'] and azure_result['success']:
            local_ts = local_result['timestamp']
            azure_ts = azure_result['timestamp']
            
            if local_ts > azure_ts:
                comparison['comparison'] = 'LOCAL_AHEAD'
                comparison['action_needed'] = True
                logger.info(f"ℹ Local data is more recent (LOCAL_AHEAD)")
            elif local_ts < azure_ts:
                comparison['comparison'] = 'AZURE_AHEAD'
                logger.warning(f"⚠ Azure data is more recent (AZURE_AHEAD)")
            else:
                comparison['comparison'] = 'SYNCHRONIZED'
                logger.info(f"✓ Data is synchronized")
        elif local_result['success'] and not azure_result['success']:
            comparison['comparison'] = 'AZURE_MISSING'
            comparison['action_needed'] = True
            logger.info(f"ℹ Azure blob missing, local data needs initial upload")
        elif azure_result['success'] and not local_result['success']:
            comparison['comparison'] = 'LOCAL_MISSING'
            logger.error(f"✗ Local file missing")
        else:
            comparison['comparison'] = 'BOTH_MISSING'
            logger.error(f"✗ Both local and Azure data missing")
        
        return comparison
    
    def sync_nasa_data(self, data_dir='data'):
        """Sync all NASA POWER data files to Azure
        
        Args:
            data_dir (str): Local data directory
        
        Returns:
            dict: Comprehensive sync results
        """
        logger.info("=" * 80)
        logger.info("Starting NASA POWER Azure Sync")
        logger.info("=" * 80)
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'main_file': None,
            'csv_files': [],
            'timestamp_comparison': None,
            'total_uploaded': 0,
            'total_failed': 0
        }
        
        try:
            # Upload main nasa-api.txt
            main_file = os.path.join(data_dir, 'nasa-api.txt')
            if os.path.exists(main_file):
                logger.info("\n--- Uploading Main File ---")
                results['main_file'] = self.upload_nasa_data(main_file)
                if results['main_file']['success']:
                    results['total_uploaded'] += 1
                else:
                    results['total_failed'] += 1
            
            # Upload all nasa monthly CSVs
            logger.info("\n--- Uploading Monthly CSV Files ---")
            csv_count = 0
            for filename in sorted(os.listdir(data_dir)):
                if filename.startswith('nasa_') and filename.endswith('.csv'):
                    csv_path = os.path.join(data_dir, filename)
                    csv_result = self.upload_nasa_data(csv_path)
                    results['csv_files'].append(csv_result)
                    if csv_result['success']:
                        results['total_uploaded'] += 1
                    else:
                        results['total_failed'] += 1
                    csv_count += 1
            
            logger.info(f"✓ Processed {csv_count} CSV files")
            
            # Compare timestamps
            logger.info("\n--- Comparing Timestamps ---")
            if os.path.exists(main_file):
                results['timestamp_comparison'] = self.compare_timestamps(main_file)
            
            logger.info("=" * 80)
            logger.info(f"NASA POWER Azure Sync Complete")
            logger.info(f"Total Uploaded: {results['total_uploaded']}, Failed: {results['total_failed']}")
            logger.info("=" * 80)
            
            return results
        except Exception as e:
            logger.error(f"Sync failed with error: {e}", exc_info=True)
            results['error'] = str(e)
            return results


def main():
    """Test the Azure sync functionality"""
    try:
        sync = NasaPowerAzureSync()
        
        # Sync all NASA data
        print("\n=== Syncing NASA POWER data to Azure ===")
        results = sync.sync_nasa_data()
        
        print("\n=== Sync Results Summary ===")
        print(f"Total Uploaded: {results['total_uploaded']}")
        print(f"Total Failed: {results['total_failed']}")
        
        if results['timestamp_comparison']:
            comp = results['timestamp_comparison']
            print(f"\n=== Timestamp Comparison ===")
            print(f"Local:  {comp['local'].get('timestamp', 'N/A')}")
            print(f"Azure:  {comp['azure'].get('timestamp', 'N/A')}")
            print(f"Status: {comp['comparison']}")
    
    except Exception as e:
        logger.error(f"Error: {e}")
        print(f"✗ Error: {e}")
        print("\nNote: Ensure .env.azure file has AZURE_STORAGE_ACCOUNT and AZURE_STORAGE_KEY")


if __name__ == '__main__':
    main()
