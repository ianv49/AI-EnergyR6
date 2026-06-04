#!/usr/bin/env python3
"""
End-to-End Test Script for NASA POWER Azure Integration
Tests: Fetch → Validate → Sync → Compare workflow
"""

import os
import sys
import logging
from datetime import datetime
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class NasaPowerE2ETest:
    """End-to-end testing for NASA POWER Azure integration"""
    
    def __init__(self):
        self.nasa_txt = 'data/nasa-api.txt'
        self.data_dir = 'data'
        self.test_results = {
            'fetch': None,
            'local_validation': None,
            'azure_sync': None,
            'timestamp_comparison': None,
            'csv_validation': None
        }
    
    def test_fetch_data(self):
        """Test: Fetch data from NASA POWER API"""
        logger.info("\n" + "=" * 80)
        logger.info("TEST 1: Fetch Data from NASA POWER API")
        logger.info("=" * 80)
        
        try:
            import subprocess
            logger.info("Running fetch_nasa_power_update.py...")
            result = subprocess.run(['python', 'fetch_nasa_power_update.py'], 
                                  capture_output=True, text=True, timeout=180)
            
            if result.returncode == 0:
                logger.info(f"✓ Fetch successful: {result.stdout}")
                self.test_results['fetch'] = {
                    'status': 'PASSED',
                    'output': result.stdout
                }
                return True
            else:
                logger.error(f"✗ Fetch failed: {result.stderr}")
                self.test_results['fetch'] = {
                    'status': 'FAILED',
                    'error': result.stderr
                }
                return False
        except subprocess.TimeoutExpired:
            logger.error("✗ Fetch timeout (>180s)")
            self.test_results['fetch'] = {'status': 'TIMEOUT'}
            return False
        except Exception as e:
            logger.error(f"✗ Fetch error: {e}")
            self.test_results['fetch'] = {'status': 'ERROR', 'error': str(e)}
            return False
    
    def test_local_file_validation(self):
        """Test: Validate local nasa-api.txt integrity"""
        logger.info("\n" + "=" * 80)
        logger.info("TEST 2: Validate Local File Integrity")
        logger.info("=" * 80)
        
        try:
            if not os.path.exists(self.nasa_txt):
                logger.error(f"✗ File not found: {self.nasa_txt}")
                self.test_results['local_validation'] = {'status': 'FAILED', 'error': 'File not found'}
                return False
            
            with open(self.nasa_txt, 'r') as f:
                lines = f.readlines()
            
            # Check structure
            logger.info(f"Total lines: {len(lines)}")
            
            # Validate header
            if not any(line.startswith('# Data collection last updated:') for line in lines):
                logger.warning("⚠ Missing 'last updated' metadata")
            
            if not any(line.startswith('# Summary:') for line in lines):
                logger.warning("⚠ Missing 'summary' metadata")
            
            # Count data rows
            data_rows = [line for line in lines if line.strip() and not line.startswith('#') and not line.startswith('[')]
            logger.info(f"Data rows: {len(data_rows)}")
            
            if not data_rows:
                logger.error("✗ No data rows found")
                self.test_results['local_validation'] = {'status': 'FAILED', 'error': 'No data rows'}
                return False
            
            # Validate first and last rows
            try:
                first_row = data_rows[0].strip().split(',')
                last_row = data_rows[-1].strip().split(',')
                
                if len(first_row) != 9 or len(last_row) != 9:
                    logger.error(f"✗ Invalid row format (expected 9 columns)")
                    self.test_results['local_validation'] = {'status': 'FAILED', 'error': 'Invalid row format'}
                    return False
                
                logger.info(f"First row: ID={first_row[0]}, TS={first_row[1]}")
                logger.info(f"Last row:  ID={last_row[0]}, TS={last_row[1]}")
                
                logger.info("✓ Local file validation passed")
                self.test_results['local_validation'] = {
                    'status': 'PASSED',
                    'total_rows': len(data_rows),
                    'first_timestamp': first_row[1],
                    'last_timestamp': last_row[1]
                }
                return True
            except Exception as e:
                logger.error(f"✗ Row parsing error: {e}")
                self.test_results['local_validation'] = {'status': 'FAILED', 'error': str(e)}
                return False
        
        except Exception as e:
            logger.error(f"✗ Validation error: {e}")
            self.test_results['local_validation'] = {'status': 'ERROR', 'error': str(e)}
            return False
    
    def test_azure_sync(self):
        """Test: Sync to Azure Blob Storage"""
        logger.info("\n" + "=" * 80)
        logger.info("TEST 3: Sync to Azure Blob Storage")
        logger.info("=" * 80)
        
        try:
            from nasa_power_azure_sync_enhanced import NasaPowerAzureSync
            
            logger.info("Initializing Azure sync...")
            sync = NasaPowerAzureSync()
            
            logger.info("Running sync...")
            sync_results = sync.sync_nasa_data()
            
            if 'error' in sync_results:
                logger.error(f"✗ Sync error: {sync_results['error']}")
                self.test_results['azure_sync'] = {'status': 'FAILED', 'error': sync_results['error']}
                return False
            
            uploaded = sync_results.get('total_uploaded', 0)
            failed = sync_results.get('total_failed', 0)
            
            logger.info(f"Uploaded: {uploaded}, Failed: {failed}")
            
            if failed > 0:
                logger.warning(f"⚠ {failed} files failed to upload")
            
            logger.info("✓ Azure sync completed")
            self.test_results['azure_sync'] = {
                'status': 'PASSED',
                'total_uploaded': uploaded,
                'total_failed': failed
            }
            return True
        
        except ImportError:
            logger.error("✗ Azure SDK not available")
            self.test_results['azure_sync'] = {'status': 'SKIPPED', 'reason': 'SDK not installed'}
            return False
        except Exception as e:
            logger.error(f"✗ Sync error: {e}")
            self.test_results['azure_sync'] = {'status': 'ERROR', 'error': str(e)}
            return False
    
    def test_timestamp_comparison(self):
        """Test: Compare timestamps between local and Azure"""
        logger.info("\n" + "=" * 80)
        logger.info("TEST 4: Timestamp Comparison (Local vs Azure)")
        logger.info("=" * 80)
        
        try:
            from nasa_power_azure_sync_enhanced import NasaPowerAzureSync
            
            sync = NasaPowerAzureSync()
            comparison = sync.compare_timestamps(self.nasa_txt)
            
            local_ts = comparison['local'].get('timestamp', 'N/A')
            azure_ts = comparison['azure'].get('timestamp', 'N/A')
            comp_status = comparison['comparison']
            
            logger.info(f"Local:  {local_ts}")
            logger.info(f"Azure:  {azure_ts}")
            logger.info(f"Status: {comp_status}")
            
            if comp_status in ['SYNCHRONIZED', 'LOCAL_AHEAD']:
                logger.info("✓ Timestamp comparison passed")
                self.test_results['timestamp_comparison'] = {
                    'status': 'PASSED',
                    'comparison': comp_status,
                    'local_timestamp': local_ts,
                    'azure_timestamp': azure_ts
                }
                return True
            else:
                logger.warning(f"⚠ Status: {comp_status}")
                self.test_results['timestamp_comparison'] = {
                    'status': 'WARNING',
                    'comparison': comp_status
                }
                return False
        
        except ImportError:
            logger.error("✗ Azure SDK not available")
            self.test_results['timestamp_comparison'] = {'status': 'SKIPPED', 'reason': 'SDK not installed'}
            return False
        except Exception as e:
            logger.error(f"✗ Comparison error: {e}")
            self.test_results['timestamp_comparison'] = {'status': 'ERROR', 'error': str(e)}
            return False
    
    def test_csv_files(self):
        """Test: Validate monthly CSV files"""
        logger.info("\n" + "=" * 80)
        logger.info("TEST 5: Validate Monthly CSV Files")
        logger.info("=" * 80)
        
        try:
            csv_files = [f for f in os.listdir(self.data_dir) 
                        if f.startswith('nasa_') and f.endswith('.csv')]
            
            logger.info(f"Found {len(csv_files)} CSV files")
            
            if not csv_files:
                logger.warning("⚠ No CSV files found")
                self.test_results['csv_validation'] = {
                    'status': 'WARNING',
                    'csv_count': 0
                }
                return True
            
            valid_count = 0
            invalid_count = 0
            
            for csv_file in sorted(csv_files):
                try:
                    csv_path = os.path.join(self.data_dir, csv_file)
                    with open(csv_path, 'r') as f:
                        lines = f.readlines()
                    
                    if len(lines) < 2:
                        logger.warning(f"⚠ {csv_file}: No data rows")
                        invalid_count += 1
                    else:
                        valid_count += 1
                        logger.info(f"✓ {csv_file}: {len(lines)-1} rows")
                except Exception as e:
                    logger.error(f"✗ {csv_file}: {e}")
                    invalid_count += 1
            
            logger.info(f"CSV Validation: {valid_count} valid, {invalid_count} invalid")
            
            self.test_results['csv_validation'] = {
                'status': 'PASSED',
                'total_csv': len(csv_files),
                'valid': valid_count,
                'invalid': invalid_count
            }
            return valid_count > 0
        
        except Exception as e:
            logger.error(f"✗ CSV validation error: {e}")
            self.test_results['csv_validation'] = {'status': 'ERROR', 'error': str(e)}
            return False
    
    def run_all_tests(self):
        """Run all tests"""
        logger.info("\n\n")
        logger.info("#" * 80)
        logger.info("# NASA POWER Azure Integration - E2E Test Suite")
        logger.info("#" * 80)
        
        results = []
        
        # Test 1: Fetch
        results.append(('Fetch Data', self.test_fetch_data()))
        
        # Test 2: Local Validation
        results.append(('Local File Validation', self.test_local_file_validation()))
        
        # Test 3: Azure Sync
        results.append(('Azure Sync', self.test_azure_sync()))
        
        # Test 4: Timestamp Comparison
        results.append(('Timestamp Comparison', self.test_timestamp_comparison()))
        
        # Test 5: CSV Validation
        results.append(('CSV Files', self.test_csv_files()))
        
        # Summary
        logger.info("\n\n")
        logger.info("=" * 80)
        logger.info("TEST SUMMARY")
        logger.info("=" * 80)
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for test_name, result in results:
            status = "✓ PASSED" if result else "✗ FAILED"
            logger.info(f"{test_name:.<40} {status}")
        
        logger.info("=" * 80)
        logger.info(f"Total: {passed}/{total} tests passed")
        logger.info("=" * 80)
        
        return passed == total


def main():
    tester = NasaPowerE2ETest()
    success = tester.run_all_tests()
    
    # Detailed results
    print("\n\nDETAILED RESULTS:")
    print("=" * 80)
    for test_name, result in tester.test_results.items():
        print(f"\n{test_name.upper()}:")
        if isinstance(result, dict):
            for key, value in result.items():
                print(f"  {key}: {value}")
        else:
            print(f"  {result}")
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
