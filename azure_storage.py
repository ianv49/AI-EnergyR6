#!/usr/bin/env python3
"""
Azure Blob Storage Module
Handles uploading, downloading, and managing files in Azure Blob Storage
"""

import os
from pathlib import Path
from datetime import datetime
from azure_config import AzureConfig


class AzureStorage:
    """Azure Blob Storage operations"""
    
    def __init__(self, config=None):
        """Initialize Azure storage
        
        Args:
            config (AzureConfig): Azure configuration object
        """
        self.config = config or AzureConfig()
        self.blob_client = self.config.get_blob_client()
        self.container_client = self.config.get_blob_container_client()
        self.container_name = self.config.get_container_name()
    
    def upload_file(self, local_path, blob_name=None, metadata=None):
        """Upload a file to Blob Storage
        
        Args:
            local_path (str): Local file path
            blob_name (str): Blob name (if None, uses filename)
            metadata (dict): File metadata
        
        Returns:
            bool: True if successful
        """
        try:
            local_path = Path(local_path)
            if not local_path.exists():
                raise FileNotFoundError(f"File not found: {local_path}")
            
            blob_name = blob_name or str(local_path.name)
            
            with open(local_path, "rb") as data:
                self.container_client.upload_blob(blob_name, data, overwrite=True)
            
            print(f"✓ Uploaded: {local_path.name} → {self.container_name}/{blob_name}")
            return True
        except Exception as e:
            print(f"✗ Upload failed for {local_path}: {str(e)}")
            return False
    
    def upload_directory(self, local_dir, blob_prefix=""):
        """Upload all files from a directory to Blob Storage
        
        Args:
            local_dir (str): Local directory path
            blob_prefix (str): Blob prefix for uploaded files
        
        Returns:
            int: Number of files uploaded
        """
        local_dir = Path(local_dir)
        count = 0
        
        for file_path in local_dir.glob("**/*"):
            if file_path.is_file():
                relative_path = file_path.relative_to(local_dir)
                blob_name = f"{blob_prefix}/{relative_path}".strip("/")
                
                if self.upload_file(file_path, blob_name):
                    count += 1
        
        return count
    
    def download_file(self, blob_name, local_path=None):
        """Download a file from Blob Storage
        
        Args:
            blob_name (str): Blob name
            local_path (str): Local file path (if None, uses blob name)
        
        Returns:
            bool: True if successful
        """
        try:
            local_path = Path(local_path or Path(blob_name).name)
            local_path.parent.mkdir(parents=True, exist_ok=True)
            
            blob_client = self.container_client.get_blob_client(blob_name)
            with open(local_path, "wb") as file_stream:
                file_stream.write(blob_client.download_blob().readall())
            
            print(f"✓ Downloaded: {self.container_name}/{blob_name} → {local_path}")
            return True
        except Exception as e:
            print(f"✗ Download failed for {blob_name}: {str(e)}")
            return False
    
    def list_files(self, prefix="", recursive=False):
        """List files in Blob Storage
        
        Args:
            prefix (str): Blob prefix to filter files
            recursive (bool): Include subdirectories
        
        Returns:
            list: List of blob information
        """
        try:
            files = []
            blobs = self.container_client.list_blobs(name_starts_with=prefix)
            
            for blob in blobs:
                if recursive or '/' not in blob.name.replace(prefix, ''):
                    files.append({
                        'name': blob.name,
                        'size': blob.size,
                        'modified': blob.last_modified
                    })
            
            return files
        except Exception as e:
            print(f"✗ Failed to list files: {str(e)}")
            return []
    
    def delete_file(self, blob_name):
        """Delete a file from Blob Storage
        
        Args:
            blob_name (str): Blob name
        
        Returns:
            bool: True if successful
        """
        try:
            self.container_client.delete_blob(blob_name)
            print(f"✓ Deleted: {self.container_name}/{blob_name}")
            return True
        except Exception as e:
            print(f"✗ Delete failed for {blob_name}: {str(e)}")
            return False
    
    def file_exists(self, blob_name):
        """Check if a file exists in Blob Storage
        
        Args:
            blob_name (str): Blob name
        
        Returns:
            bool: True if file exists
        """
        try:
            self.container_client.get_blob_client(blob_name).get_blob_properties()
            return True
        except:
            return False
    
    def get_file_url(self, blob_name):
        """Generate URL for a file
        
        Args:
            blob_name (str): Blob name
        
        Returns:
            str: File URL
        """
        try:
            return f"https://{self.container_name}.blob.core.windows.net/{blob_name}"
        except Exception as e:
            print(f"✗ Failed to generate URL: {str(e)}")
            return None
    
    def upload_api_files(self, data_dir='data'):
        """Upload all API files to Blob Storage
        
        Args:
            data_dir (str): Data directory containing API files
        
        Returns:
            int: Number of API files uploaded
        """
        print(f"\nUploading API files to Blob Storage...")
        data_dir = Path(data_dir)
        api_files = list(data_dir.glob("*-api.txt"))
        count = 0
        
        for api_file in api_files:
            if self.upload_file(api_file, f"api-files/{api_file.name}"):
                count += 1
        
        print(f"✓ Uploaded {count} API files")
        return count
    
    def upload_csv_files(self, data_dir='data', prefix='csv-data'):
        """Upload all CSV files to Blob Storage
        
        Args:
            data_dir (str): Data directory containing CSV files
            prefix (str): Blob prefix for CSV files
        
        Returns:
            int: Number of CSV files uploaded
        """
        print(f"\nUploading CSV files to Blob Storage...")
        data_dir = Path(data_dir)
        csv_files = list(data_dir.glob("*.csv"))
        count = 0
        
        for csv_file in csv_files:
            if self.upload_file(csv_file, f"{prefix}/{csv_file.name}"):
                count += 1
        
        print(f"✓ Uploaded {count} CSV files")
        return count
    
    def backup_data_directory(self, data_dir='data', backup_prefix='backup'):
        """Backup entire data directory to Blob Storage
        
        Args:
            data_dir (str): Data directory to backup
            backup_prefix (str): Blob backup prefix
        
        Returns:
            int: Number of files backed up
        """
        print(f"\nBacking up data directory to Blob Storage...")
        count = self.upload_directory(data_dir, backup_prefix)
        print(f"✓ Backed up {count} files")
        return count


if __name__ == "__main__":
    storage = AzureStorage()
    
    # Example usage
    print("\n" + "="*60)
    print("AZURE BLOB STORAGE OPERATIONS")
    print("="*60)
    
    # Upload API files
    storage.upload_api_files()
    
    # Upload CSV files
    storage.upload_csv_files()
    
    # List files
    print("\nListing uploaded files:")
    files = storage.list_files()
    for file in files[:5]:
        print(f"  {file['name']} ({file['size']} bytes)")
