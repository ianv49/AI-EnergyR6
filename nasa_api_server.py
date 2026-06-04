from flask import Flask, jsonify, request
import subprocess
import os
from flask_cors import CORS
from datetime import datetime
try:
    from nasa_power_azure_sync_enhanced import NasaPowerAzureSync
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False
    print("Warning: Azure SDK not available. Azure sync will be disabled.")
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/nasa_api_server.log', mode='a')
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

NASA_API_TXT = os.path.join('data', 'nasa-api.txt')
FETCH_SCRIPT = 'fetch_nasa_power_update.py'

# Ensure logs directory exists
os.makedirs('logs', exist_ok=True)

@app.route('/nasa-api-latest-date', methods=['GET'])
def nasa_api_latest_date():
    latest_date = None
    try:
        with open(NASA_API_TXT, 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#') and not line.startswith('['):
                    parts = line.strip().split(',')
                    if len(parts) > 1:
                        latest_date = parts[1]
                        break
        # The file is in reverse order (latest at top), so we need the first data row
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    return jsonify({'latest_date': latest_date})

@app.route('/run-fetch-nasa-power', methods=['POST'])
def run_fetch_nasa_power():
    """
    NEW WORKFLOW: Azure-first data flow
    1. Upload local nasa-api.txt to Azure (initial sync)
    2. Mirror Azure data to nasa-api-azure.txt (verification)
    3. Fetch new Mar-2026 data from NASA POWER API
    4. Upload to Azure
    5. Mirror updated Azure data to nasa-api-azure.txt
    6. Update monthly CSV (Mar-2026)
    7. Compare timestamps (nasa-api.txt vs nasa-api-azure.txt)
    8. Return status to GUI
    """
    logger.info("=" * 80)
    logger.info("NASA POWER Azure-First Workflow Started")
    logger.info("=" * 80)
    
    results = {
        'workflow': 'Azure-First Data Flow',
        'steps': {},
        'status': 'IN_PROGRESS',
        'message': ''
    }
    
    try:
        if not AZURE_AVAILABLE:
            logger.error("Azure SDK not available")
            results['status'] = 'ERROR'
            results['message'] = 'Azure SDK not available'
            return jsonify(results), 500
        
        sync = NasaPowerAzureSync()
        NASA_API_AZURE = os.path.join('data', 'nasa-api-azure.txt')
        
        # STEP 1: Upload local nasa-api.txt to Azure (initial sync)
        logger.info("\n[STEP 1] Uploading local nasa-api.txt to Azure...")
        try:
            upload_result = sync.upload_nasa_data(NASA_API_TXT, blob_name='nasa-api.txt')
            results['steps']['step_1_upload_local'] = upload_result
            if upload_result['success']:
                logger.info("✓ Step 1 completed: Local file uploaded to Azure")
            else:
                logger.error(f"Step 1 failed: {upload_result['error']}")
                results['status'] = 'ERROR'
                results['message'] = f"Upload failed: {upload_result['error']}"
                return jsonify(results), 500
        except Exception as e:
            logger.error(f"Step 1 exception: {e}")
            results['status'] = 'ERROR'
            results['message'] = f"Step 1 failed: {e}"
            return jsonify(results), 500
        
        # STEP 2: Mirror Azure data to nasa-api-azure.txt
        logger.info("\n[STEP 2] Mirroring Azure data to nasa-api-azure.txt...")
        try:
            mirror_result = sync.mirror_azure_to_local('nasa-api.txt', NASA_API_AZURE)
            results['steps']['step_2_mirror_azure'] = mirror_result
            if mirror_result['success']:
                logger.info("✓ Step 2 completed: Azure data mirrored to local nasa-api-azure.txt")
            else:
                logger.error(f"Step 2 failed: {mirror_result['error']}")
                results['status'] = 'ERROR'
                results['message'] = f"Mirror failed: {mirror_result['error']}"
                return jsonify(results), 500
        except Exception as e:
            logger.error(f"Step 2 exception: {e}")
            results['status'] = 'ERROR'
            results['message'] = f"Step 2 failed: {e}"
            return jsonify(results), 500
        
        # STEP 3: Fetch new Mar-2026 data from NASA POWER API
        logger.info("\n[STEP 3] Fetching Mar-2026 data from NASA POWER API...")
        try:
            fetch_result = subprocess.run(['python', FETCH_SCRIPT], capture_output=True, text=True, timeout=180)
            fetch_output = fetch_result.stdout.strip()
            fetch_error = fetch_result.stderr.strip()
            
            results['steps']['step_3_fetch_nasa_data'] = {
                'return_code': fetch_result.returncode,
                'output': fetch_output,
                'error': fetch_error if fetch_result.returncode != 0 else None
            }
            
            if fetch_result.returncode != 0:
                logger.error(f"Step 3 failed: {fetch_error}")
                results['status'] = 'ERROR'
                results['message'] = f"Fetch failed: {fetch_error}"
                return jsonify(results), 500
            
            logger.info(f"✓ Step 3 completed: {fetch_output}")
        except subprocess.TimeoutExpired:
            logger.error("Step 3 timeout: Fetch script exceeded 180 seconds")
            results['status'] = 'ERROR'
            results['message'] = 'Fetch script timeout'
            return jsonify(results), 500
        except Exception as e:
            logger.error(f"Step 3 exception: {e}")
            results['status'] = 'ERROR'
            results['message'] = f"Step 3 failed: {e}"
            return jsonify(results), 500
        
        # STEP 4: Upload updated nasa-api.txt to Azure
        logger.info("\n[STEP 4] Uploading updated nasa-api.txt to Azure...")
        try:
            upload_result_2 = sync.upload_nasa_data(NASA_API_TXT, blob_name='nasa-api.txt')
            results['steps']['step_4_upload_updated'] = upload_result_2
            if upload_result_2['success']:
                logger.info("✓ Step 4 completed: Updated file uploaded to Azure")
            else:
                logger.error(f"Step 4 failed: {upload_result_2['error']}")
                results['status'] = 'ERROR'
                results['message'] = f"Updated upload failed: {upload_result_2['error']}"
                return jsonify(results), 500
        except Exception as e:
            logger.error(f"Step 4 exception: {e}")
            results['status'] = 'ERROR'
            results['message'] = f"Step 4 failed: {e}"
            return jsonify(results), 500
        
        # STEP 5: Mirror updated Azure data to nasa-api-azure.txt
        logger.info("\n[STEP 5] Mirroring updated Azure data to nasa-api-azure.txt...")
        try:
            mirror_result_2 = sync.mirror_azure_to_local('nasa-api.txt', NASA_API_AZURE)
            results['steps']['step_5_mirror_updated_azure'] = mirror_result_2
            if mirror_result_2['success']:
                logger.info("✓ Step 5 completed: Updated Azure data mirrored to nasa-api-azure.txt")
            else:
                logger.error(f"Step 5 failed: {mirror_result_2['error']}")
                results['status'] = 'WARNING'
                results['message'] = f"Step 5 warning: {mirror_result_2['error']}"
                # Don't return error - continue to next steps
        except Exception as e:
            logger.error(f"Step 5 exception: {e}")
            results['status'] = 'WARNING'
            results['message'] = f"Step 5 warning: {e}"
        
        # STEP 6: Update monthly CSV (Mar-2026)
        logger.info("\n[STEP 6] Updating monthly CSV files...")
        try:
            csv_result = subprocess.run(
                ['python', '-c', 
                 'from fetch_nasa_power_update import update_monthly_csvs; update_monthly_csvs()'],
                capture_output=True, text=True, timeout=60
            )
            csv_output = csv_result.stdout.strip()
            
            results['steps']['step_6_update_csv'] = {
                'return_code': csv_result.returncode,
                'output': csv_output if csv_result.returncode == 0 else csv_result.stderr.strip()
            }
            
            if csv_result.returncode != 0:
                logger.warning(f"Step 6 warning: CSV update returned {csv_result.returncode}")
                # Don't fail - CSVs are secondary
            else:
                logger.info(f"✓ Step 6 completed: Monthly CSVs updated")
        except Exception as e:
            logger.warning(f"Step 6 warning: {e}")
            results['steps']['step_6_update_csv'] = {'error': str(e)}
        
        # STEP 7: Compare timestamps (nasa-api.txt vs nasa-api-azure.txt)
        logger.info("\n[STEP 7] Comparing timestamps between local files...")
        try:
            # Timestamps for nasa-api.txt and nasa-api-azure.txt
            local_ts = sync.get_latest_timestamp_local(NASA_API_TXT)
            azure_mirror_ts = sync.get_latest_timestamp_local(NASA_API_AZURE)
            
            results['steps']['step_7_compare_timestamps'] = {
                'nasa_api_local': local_ts,
                'nasa_api_azure_mirror': azure_mirror_ts,
                'comparison': {}
            }
            
            if local_ts['success'] and azure_mirror_ts['success']:
                if local_ts['timestamp'] == azure_mirror_ts['timestamp']:
                    results['steps']['step_7_compare_timestamps']['comparison'] = 'SYNCHRONIZED'
                    logger.info("✓ Step 7 completed: Files are SYNCHRONIZED")
                elif local_ts['timestamp'] > azure_mirror_ts['timestamp']:
                    results['steps']['step_7_compare_timestamps']['comparison'] = 'LOCAL_AHEAD'
                    logger.warning("⚠ Step 7 warning: Local file is AHEAD of Azure mirror")
                else:
                    results['steps']['step_7_compare_timestamps']['comparison'] = 'AZURE_AHEAD'
                    logger.warning("⚠ Step 7 warning: Azure mirror is AHEAD")
            else:
                results['steps']['step_7_compare_timestamps']['comparison'] = 'ERROR'
                logger.error("Step 7 failed: Could not read timestamps")
        except Exception as e:
            logger.error(f"Step 7 exception: {e}")
            results['steps']['step_7_compare_timestamps'] = {'error': str(e)}
        
        # STEP 8: Return status to GUI
        logger.info("\n[STEP 8] Returning status to GUI...")
        results['status'] = 'SUCCESS'
        results['message'] = 'Azure-first workflow completed successfully'
        results['timestamp'] = datetime.now().isoformat()
        
        logger.info("=" * 80)
        logger.info("NASA POWER Azure-First Workflow Completed Successfully")
        logger.info("=" * 80)
        
        return jsonify(results)
        
    except Exception as e:
        logger.error(f"Workflow error: {e}", exc_info=True)
        results['status'] = 'ERROR'
        results['message'] = f"Workflow failed: {e}"
        return jsonify(results), 500

@app.route('/nasa-api-compare-timestamps', methods=['GET'])
def compare_timestamps():
    """Compare timestamps between nasa-api.txt and nasa-api-azure.txt (mirror verification)"""
    logger.info("Timestamp comparison request: nasa-api.txt vs nasa-api-azure.txt")
    try:
        if not AZURE_AVAILABLE:
            return jsonify({'error': 'Azure SDK not available'}), 500
        
        sync = NasaPowerAzureSync()
        NASA_API_AZURE = os.path.join('data', 'nasa-api-azure.txt')
        
        # Compare local nasa-api.txt with its mirror nasa-api-azure.txt
        local_ts = sync.get_latest_timestamp_local(NASA_API_TXT)
        mirror_ts = sync.get_latest_timestamp_local(NASA_API_AZURE)
        
        comparison = {
            'nasa_api_txt': local_ts,
            'nasa_api_azure_txt': mirror_ts,
            'comparison_result': 'ERROR',
            'validation_status': 'FAILED',
            'timestamp': datetime.now().isoformat()
        }
        
        # Determine if mirror is valid
        if local_ts['success'] and mirror_ts['success']:
            if local_ts['timestamp'] == mirror_ts['timestamp']:
                comparison['comparison_result'] = 'SYNCHRONIZED'
                comparison['validation_status'] = 'VALID_MIRROR'
                logger.info("✓ Mirror is valid: Timestamps match")
            else:
                comparison['comparison_result'] = f"MISMATCH (Local: {local_ts['timestamp']}, Mirror: {mirror_ts['timestamp']})"
                comparison['validation_status'] = 'INVALID_MIRROR'
                logger.warning("⚠ Mirror mismatch detected")
        else:
            comparison['comparison_result'] = 'FILE_READ_ERROR'
            comparison['validation_status'] = 'FAILED'
            logger.error("Failed to read timestamps")
        
        return jsonify(comparison)
    except Exception as e:
        logger.error(f"Timestamp comparison error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/nasa-api-sync-status', methods=['GET'])
def sync_status():
    """Get current sync status (nasa-api.txt vs nasa-api-azure.txt mirror)"""
    logger.info("Sync status request")
    try:
        if not AZURE_AVAILABLE:
            return jsonify({'error': 'Azure SDK not available'}), 500
        
        sync = NasaPowerAzureSync()
        NASA_API_AZURE = os.path.join('data', 'nasa-api-azure.txt')
        
        local = sync.get_latest_timestamp_local(NASA_API_TXT)
        mirror = sync.get_latest_timestamp_local(NASA_API_AZURE)
        
        # Also get Azure blob info
        azure = sync.get_latest_timestamp_from_azure('nasa-api.txt')
        
        return jsonify({
            'local_nasa_api': local,
            'mirror_nasa_api_azure': mirror,
            'azure_blob': azure,
            'mirror_valid': local.get('timestamp') == mirror.get('timestamp') if local['success'] and mirror['success'] else False,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Sync status error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=5001, debug=True)
