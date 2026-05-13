#!/usr/bin/env python3
"""
Azure Configuration and Initialization Module
Handles Azure credentials, Blob Storage setup, and Cosmos DB configuration
"""

from azure.storage.blob import BlobServiceClient
from azure.cosmos import CosmosClient
import os
import json
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env.azure file
load_dotenv(dotenv_path='.env.azure')

class AzureConfig:
    """Azure Configuration and credential management"""
    
    def __init__(self, region='East US'):
        """Initialize Azure configuration
        
        Args:
            region (str): Azure region for services
        """
        self.region = region
        self.storage_account = os.getenv('AZURE_STORAGE_ACCOUNT')
        self.storage_key = os.getenv('AZURE_STORAGE_KEY')
        self.blob_container = os.getenv('AZURE_BLOB_CONTAINER', 'ai-energy-r6-data')
        self.cosmos_endpoint = os.getenv('AZURE_COSMOS_ENDPOINT')
        self.cosmos_key = os.getenv('AZURE_COSMOS_KEY')
        self.cosmos_database = os.getenv('AZURE_COSMOS_DATABASE', 'energy_db')
        self.cosmos_container = os.getenv('AZURE_COSMOS_CONTAINER', 'energy-data')
        
        self._validate_credentials()
        self._initialize_clients()
    
    def _validate_credentials(self):
        """Validate Azure credentials are available"""
        if not self.storage_account or not self.storage_key:
            raise ValueError(
                "Azure Storage credentials not found. Please set AZURE_STORAGE_ACCOUNT and "
                "AZURE_STORAGE_KEY environment variables or in .env.azure file"
            )
        if not self.cosmos_endpoint or not self.cosmos_key:
            raise ValueError(
                "Azure Cosmos DB credentials not found. Please set AZURE_COSMOS_ENDPOINT and "
                "AZURE_COSMOS_KEY environment variables or in .env.azure file"
            )
        print(f"✓ Azure credentials validated")
    
    def _initialize_clients(self):
        """Initialize Azure service clients"""
        try:
            # Initialize Blob Storage client
            self.blob_client = BlobServiceClient(
                account_url=f"https://{self.storage_account}.blob.core.windows.net",
                credential=self.storage_key
            )
            
            # Initialize Cosmos DB client
            self.cosmos_client = CosmosClient(self.cosmos_endpoint, self.cosmos_key)
            
            # Get database and container references
            self.cosmos_database_client = self.cosmos_client.get_database_client(self.cosmos_database)
            self.cosmos_container_client = self.cosmos_database_client.get_container_client(self.cosmos_container)
            
            print(f"✓ Azure clients initialized for region: {self.region}")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Azure clients: {str(e)}")
    
    def create_blob_container(self):
        """Create Blob Storage container if it doesn't exist"""
        try:
            self.blob_client.get_container_client(self.blob_container).get_container_properties()
            print(f"✓ Blob Storage container '{self.blob_container}' already exists")
        except:
            try:
                self.blob_client.create_container(name=self.blob_container)
                print(f"✓ Created Blob Storage container: {self.blob_container}")
            except Exception as e:
                print(f"⚠ Error creating Blob Storage container: {str(e)}")
    
    def create_cosmos_database_and_container(self):
        """Create Cosmos DB database and container if they don't exist"""
        try:
            self.cosmos_database_client.read()
            print(f"✓ Cosmos DB database '{self.cosmos_database}' already exists")
        except:
            try:
                self.cosmos_client.create_database(self.cosmos_database)
                print(f"✓ Created Cosmos DB database: {self.cosmos_database}")
            except Exception as e:
                print(f"⚠ Error creating database: {str(e)}")
        
        try:
            self.cosmos_container_client.read()
            print(f"✓ Cosmos DB container '{self.cosmos_container}' already exists")
            return True
        except:
            try:
                self.cosmos_database_client.create_container(
                    id=self.cosmos_container,
                    partition_key_path="/source_timestamp",
                    offer_throughput=400  # Minimum for serverless
                )
                print(f"✓ Created Cosmos DB container: {self.cosmos_container}")
                return True
            except Exception as e:
                print(f"⚠ Error creating container: {str(e)}")
                return False
    
    def get_blob_client(self):
        """Get Blob Storage client"""
        return self.blob_client
    
    def get_blob_container_client(self):
        """Get Blob Storage container client"""
        return self.blob_client.get_container_client(self.blob_container)
    
    def get_cosmos_client(self):
        """Get Cosmos DB client"""
        return self.cosmos_client
    
    def get_cosmos_container_client(self):
        """Get Cosmos DB container client"""
        return self.cosmos_container_client
    
    def get_container_name(self):
        """Get Blob Storage container name"""
        return self.blob_container
    
    def get_cosmos_container_name(self):
        """Get Cosmos DB container name"""
        return self.cosmos_container


def setup_azure_environment():
    """Setup and initialize Azure environment"""
    print("\n" + "="*60)
    print("AZURE ENVIRONMENT SETUP")
    print("="*60)
    
    try:
        config = AzureConfig()
        config.create_blob_container()
        config.create_cosmos_database_and_container()
        
        print("\n" + "="*60)
        print("✓ Azure environment setup completed successfully")
        print("="*60)
        print(f"  Blob Container: {config.blob_container}")
        print(f"  Cosmos Database: {config.cosmos_database}")
        print(f"  Cosmos Container: {config.cosmos_container}")
        print(f"  Region: {config.region}")
        print("="*60 + "\n")
        
        return config
    except Exception as e:
        print(f"\n✗ Azure setup failed: {str(e)}")
        raise


if __name__ == "__main__":
    setup_azure_environment()
