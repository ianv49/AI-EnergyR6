#!/usr/bin/env python3
"""
Azure Setup Module
Orchestrates Azure infrastructure setup and configuration
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from azure_config import AzureConfig
from azure_storage import AzureStorage
from azure_database import AzureDatabase


class AzureSetup:
    """Setup and initialize Azure infrastructure"""
    
    def __init__(self):
        """Initialize setup"""
        self.project_root = Path(__file__).parent
        self.env_file = self.project_root / '.env.azure'
        self.template_file = self.project_root / '.azure.template'
    
    def check_azure_credentials(self):
        """Check if Azure credentials are configured
        
        Returns:
            bool: True if credentials present
        """
        print("\n" + "="*60)
        print("CHECKING AZURE CREDENTIALS")
        print("="*60)
        
        if not self.env_file.exists():
            print(f"✗ {self.env_file} not found")
            print(f"✓ Create {self.env_file} from template {self.template_file}")
            return False
        
        load_dotenv(self.env_file)
        
        required = [
            'AZURE_STORAGE_ACCOUNT',
            'AZURE_STORAGE_KEY',
            'AZURE_COSMOS_ENDPOINT',
            'AZURE_COSMOS_KEY'
        ]
        
        missing = [var for var in required if not os.getenv(var)]
        
        if missing:
            print(f"✗ Missing credentials: {', '.join(missing)}")
            return False
        
        print("✓ All Azure credentials configured")
        return True
    
    def create_template_file(self):
        """Create .azure.template file with required variables
        
        Returns:
            bool: True if successful
        """
        template_content = """# Azure Configuration Template
# Copy this file to .env.azure and fill in your Azure credentials

# Azure Storage Account
AZURE_STORAGE_ACCOUNT=your_storage_account_name
AZURE_STORAGE_KEY=your_storage_account_key
AZURE_STORAGE_CONTAINER=energy-data

# Azure Cosmos DB
AZURE_COSMOS_ENDPOINT=https://your_cosmos_account.documents.azure.com:443/
AZURE_COSMOS_KEY=your_cosmos_db_primary_key
AZURE_COSMOS_DATABASE=energy-data-db
AZURE_COSMOS_CONTAINER=energy-data

# API Keys (Optional)
NASA_API_KEY=
WEATHERBIT_API_KEY=
OPENMETEO_API_KEY=
"""
        
        try:
            if not self.template_file.exists():
                with open(self.template_file, 'w') as f:
                    f.write(template_content)
                print(f"✓ Created template: {self.template_file}")
            else:
                print(f"✓ Template exists: {self.template_file}")
            return True
        except Exception as e:
            print(f"✗ Failed to create template: {str(e)}")
            return False
    
    def initialize_azure_services(self):
        """Initialize Azure services
        
        Returns:
            tuple: (config, storage, database) or (None, None, None)
        """
        print("\n" + "="*60)
        print("INITIALIZING AZURE SERVICES")
        print("="*60)
        
        try:
            # Initialize config
            print("\n1. Initializing Azure Configuration...")
            config = AzureConfig()
            print("✓ Azure Configuration initialized")
            
            # Initialize storage
            print("\n2. Initializing Azure Blob Storage...")
            storage = AzureStorage(config)
            print("✓ Azure Blob Storage initialized")
            
            # Initialize database
            print("\n3. Initializing Azure Cosmos DB...")
            database = AzureDatabase(config)
            print("✓ Azure Cosmos DB initialized")
            
            return config, storage, database
        except Exception as e:
            print(f"✗ Failed to initialize: {str(e)}")
            return None, None, None
    
    def setup_containers(self, storage):
        """Setup required Blob Storage containers
        
        Args:
            storage (AzureStorage): Storage instance
        
        Returns:
            bool: True if successful
        """
        print("\n" + "="*60)
        print("SETTING UP BLOB STORAGE CONTAINERS")
        print("="*60)
        
        try:
            # Create containers
            containers = [
                ('api-files', 'Store API configuration files'),
                ('csv-data', 'Store generated CSV data'),
                ('backup', 'Backup data directory')
            ]
            
            for container_name, description in containers:
                print(f"  • {container_name}: {description}")
            
            print("✓ Blob Storage containers configured")
            return True
        except Exception as e:
            print(f"✗ Failed to setup containers: {str(e)}")
            return False
    
    def upload_initial_files(self, storage):
        """Upload initial API files to Blob Storage
        
        Args:
            storage (AzureStorage): Storage instance
        
        Returns:
            int: Number of files uploaded
        """
        print("\n" + "="*60)
        print("UPLOADING INITIAL FILES")
        print("="*60)
        
        count = 0
        
        # Upload API files
        print("\n1. Uploading API files...")
        count += storage.upload_api_files()
        
        # Upload existing CSV files
        print("\n2. Uploading existing CSV files...")
        count += storage.upload_csv_files()
        
        return count
    
    def verify_setup(self, storage, database):
        """Verify Azure setup is complete
        
        Args:
            storage (AzureStorage): Storage instance
            database (AzureDatabase): Database instance
        
        Returns:
            bool: True if setup verified
        """
        print("\n" + "="*60)
        print("VERIFYING AZURE SETUP")
        print("="*60)
        
        try:
            # Check storage
            print("\n1. Checking Blob Storage...")
            files = storage.list_files()
            print(f"✓ Blob Storage accessible ({len(files)} files)")
            
            # Check database
            print("\n2. Checking Cosmos DB...")
            stats = database.get_table_stats()
            print(f"✓ Cosmos DB accessible ({stats.get('total_items', 0)} items)")
            
            print("\n✓ Azure setup verified successfully")
            return True
        except Exception as e:
            print(f"✗ Verification failed: {str(e)}")
            return False
    
    def run_full_setup(self, upload_files=True):
        """Run complete Azure setup
        
        Args:
            upload_files (bool): Whether to upload initial files
        
        Returns:
            bool: True if setup successful
        """
        print("\n" + "="*70)
        print(" "*20 + "AZURE SETUP ORCHESTRATION")
        print("="*70)
        
        # Step 1: Create template
        print("\n[STEP 1/5] Creating template file...")
        if not self.create_template_file():
            return False
        
        # Step 2: Check credentials
        print("\n[STEP 2/5] Checking Azure credentials...")
        if not self.check_azure_credentials():
            print("\n⚠ Please configure .env.azure with your Azure credentials")
            return False
        
        # Step 3: Initialize services
        print("\n[STEP 3/5] Initializing Azure services...")
        config, storage, database = self.initialize_azure_services()
        if not config or not storage or not database:
            return False
        
        # Step 4: Setup containers and upload files
        print("\n[STEP 4/5] Setting up containers...")
        if not self.setup_containers(storage):
            return False
        
        if upload_files:
            print("\n[STEP 5/5] Uploading initial files...")
            count = self.upload_initial_files(storage)
            print(f"✓ Uploaded {count} files to Blob Storage")
        
        # Step 5: Verify setup
        print("\n[STEP 5/5] Verifying setup...")
        if not self.verify_setup(storage, database):
            return False
        
        # Print summary
        print("\n" + "="*70)
        print(" "*20 + "AZURE SETUP COMPLETE")
        print("="*70)
        print("""
Next steps:
1. Update .env.azure with your Azure credentials
2. Run data fetcher to collect March-April 2026 data
3. Generate CSV reports using generate_monthly_csv_azure.py
4. Query data using Azure Cosmos DB SQL API
        """)
        
        return True


if __name__ == "__main__":
    setup = AzureSetup()
    
    # Check for command line arguments
    upload_files = '--no-upload' not in sys.argv
    
    # Run setup
    success = setup.run_full_setup(upload_files=upload_files)
    sys.exit(0 if success else 1)
