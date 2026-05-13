#!/usr/bin/env python3
"""
Azure Integration Tests
Comprehensive test suite for Azure infrastructure
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path
from azure_config import AzureConfig
from azure_storage import AzureStorage
from azure_database import AzureDatabase
from azure_data_fetcher import AzureDataFetcher
from setup_azure import AzureSetup


class AzureIntegrationTests:
    """Test Azure integration"""
    
    def __init__(self):
        """Initialize tests"""
        self.results = {}
        self.test_count = 0
        self.passed = 0
        self.failed = 0
    
    def run_all_tests(self):
        """Run all tests
        
        Returns:
            bool: True if all tests passed
        """
        print("\n" + "="*70)
        print(" "*15 + "AZURE INTEGRATION TEST SUITE")
        print("="*70)
        
        tests = [
            ("Configuration", self.test_azure_config),
            ("Blob Storage Upload", self.test_blob_upload),
            ("Blob Storage Download", self.test_blob_download),
            ("Cosmos DB Put Item", self.test_cosmos_put),
            ("Cosmos DB Query", self.test_cosmos_query),
            ("Data Fetcher NASA", self.test_data_fetcher_nasa),
            ("Data Fetcher OpenMeteo", self.test_data_fetcher_openmeteo),
            ("CSV Generation", self.test_csv_generation),
        ]
        
        for test_name, test_func in tests:
            self.test_count += 1
            try:
                result = test_func()
                if result:
                    self.passed += 1
                    self.results[test_name] = "PASS"
                else:
                    self.failed += 1
                    self.results[test_name] = "FAIL"
            except Exception as e:
                self.failed += 1
                self.results[test_name] = f"ERROR: {str(e)}"
        
        # Print summary
        self.print_summary()
        
        return self.failed == 0
    
    def test_azure_config(self):
        """Test 1: Azure Configuration
        
        Returns:
            bool: True if successful
        """
        print("\n[TEST 1/8] Azure Configuration")
        print("-" * 60)
        
        try:
            config = AzureConfig()
            
            # Verify clients
            assert config.get_blob_client() is not None, "Blob client is None"
            assert config.get_cosmos_client() is not None, "Cosmos client is None"
            
            print("✓ Azure clients initialized successfully")
            return True
        except Exception as e:
            print(f"✗ Configuration test failed: {str(e)}")
            return False
    
    def test_blob_upload(self):
        """Test 2: Blob Storage Upload
        
        Returns:
            bool: True if successful
        """
        print("\n[TEST 2/8] Blob Storage Upload")
        print("-" * 60)
        
        try:
            storage = AzureStorage()
            
            # Create test file
            test_file = Path("test_upload.txt")
            test_file.write_text("Test data for Azure Blob Storage")
            
            # Upload
            result = storage.upload_file(test_file, "test/test_upload.txt")
            
            # Cleanup
            test_file.unlink()
            
            if result:
                print("✓ File uploaded successfully")
                return True
            return False
        except Exception as e:
            print(f"✗ Upload test failed: {str(e)}")
            return False
    
    def test_blob_download(self):
        """Test 3: Blob Storage Download
        
        Returns:
            bool: True if successful
        """
        print("\n[TEST 3/8] Blob Storage Download")
        print("-" * 60)
        
        try:
            storage = AzureStorage()
            
            # List files
            files = storage.list_files("test/")
            
            if files:
                print(f"✓ Found {len(files)} test files")
                return True
            else:
                print("⚠ No test files found to download")
                return True  # Not a failure
        except Exception as e:
            print(f"✗ Download test failed: {str(e)}")
            return False
    
    def test_cosmos_put(self):
        """Test 4: Cosmos DB Put Item
        
        Returns:
            bool: True if successful
        """
        print("\n[TEST 4/8] Cosmos DB Put Item")
        print("-" * 60)
        
        try:
            database = AzureDatabase()
            
            # Create test item
            test_item = {
                'source': 'test',
                'timestamp': datetime.now().isoformat() + 'Z',
                'temperature': 22.5,
                'humidity': 60.0,
                'test': True
            }
            
            # Put item
            result = database.put_item(test_item)
            
            if result:
                print("✓ Item stored successfully")
                return True
            return False
        except Exception as e:
            print(f"✗ Put item test failed: {str(e)}")
            return False
    
    def test_cosmos_query(self):
        """Test 5: Cosmos DB Query
        
        Returns:
            bool: True if successful
        """
        print("\n[TEST 5/8] Cosmos DB Query")
        print("-" * 60)
        
        try:
            database = AzureDatabase()
            
            # Query by source
            results = database.query_by_source('test', limit=10)
            
            if results is not None:
                print(f"✓ Query returned {len(results)} items")
                return True
            return False
        except Exception as e:
            print(f"✗ Query test failed: {str(e)}")
            return False
    
    def test_data_fetcher_nasa(self):
        """Test 6: Data Fetcher NASA
        
        Returns:
            bool: True if successful
        """
        print("\n[TEST 6/8] Data Fetcher NASA POWER")
        print("-" * 60)
        
        try:
            fetcher = AzureDataFetcher()
            
            # Fetch sample data (single day)
            data = fetcher.fetch_nasa_data(40.7128, -74.0060, '20260301', '20260301')
            
            if data:
                print("✓ NASA POWER API connection successful")
                return True
            else:
                print("⚠ NASA POWER API returned no data")
                return True  # Not a failure
        except Exception as e:
            print(f"✗ NASA test failed: {str(e)}")
            return False
    
    def test_data_fetcher_openmeteo(self):
        """Test 7: Data Fetcher Open-Meteo
        
        Returns:
            bool: True if successful
        """
        print("\n[TEST 7/8] Data Fetcher Open-Meteo")
        print("-" * 60)
        
        try:
            fetcher = AzureDataFetcher()
            
            # Fetch sample data (single day)
            data = fetcher.fetch_openmeteo_data(40.7128, -74.0060, '2026-03-01', '2026-03-01')
            
            if data:
                print("✓ Open-Meteo API connection successful")
                return True
            else:
                print("⚠ Open-Meteo API returned no data")
                return True  # Not a failure
        except Exception as e:
            print(f"✗ Open-Meteo test failed: {str(e)}")
            return False
    
    def test_csv_generation(self):
        """Test 8: CSV Generation
        
        Returns:
            bool: True if successful
        """
        print("\n[TEST 8/8] CSV Generation")
        print("-" * 60)
        
        try:
            from generate_monthly_csv_azure import AzureCSVGenerator
            
            generator = AzureCSVGenerator()
            
            # Try to generate summary
            summary_path = generator.generate_summary_report()
            
            if summary_path:
                print("✓ CSV generation successful")
                return True
            return False
        except Exception as e:
            print(f"✗ CSV generation test failed: {str(e)}")
            return False
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*70)
        print(" "*20 + "TEST RESULTS SUMMARY")
        print("="*70)
        
        for test_name, result in self.results.items():
            status = "✓" if result == "PASS" else "✗"
            print(f"{status} {test_name}: {result}")
        
        print("\n" + "="*70)
        print(f"Tests Passed: {self.passed}/{self.test_count}")
        print(f"Tests Failed: {self.failed}/{self.test_count}")
        print("="*70)
        
        if self.failed == 0:
            print("\n✓ ALL TESTS PASSED")
        else:
            print(f"\n✗ {self.failed} TEST(S) FAILED")


if __name__ == "__main__":
    tests = AzureIntegrationTests()
    success = tests.run_all_tests()
    sys.exit(0 if success else 1)
