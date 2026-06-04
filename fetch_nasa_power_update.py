import csv
from datetime import datetime, timedelta
import os
import requests
import logging
import sys

# --- LOGGING CONFIG ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('logs/nasa_power_fetch.log', mode='a')
    ]
)
logger = logging.getLogger(__name__)

# --- CONFIG ---
TXT_PATH = 'data/nasa-api.txt'
CSV_DIR = 'data'
LOGS_DIR = 'logs'
SCHEMA = ['id','timestamp','temperature','humidity','irradiance','wind_speed','source','wind_power_density','solar_energy_yield']

LAT = 14.5995  # Manila, PH
LON = 120.9842
NASA_API_URL = 'https://power.larc.nasa.gov/api/temporal/hourly/point'
API_TIMEOUT = 5  # seconds
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds

# Ensure logs directory exists
os.makedirs(LOGS_DIR, exist_ok=True)

# --- 1. Find last entry date/time ---
def get_last_entry():
    """Get the last data row from nasa-api.txt"""
    try:
        if not os.path.exists(TXT_PATH):
            logger.error(f"File not found: {TXT_PATH}")
            raise FileNotFoundError(f"File not found: {TXT_PATH}")
        
        last_row = None
        with open(TXT_PATH, 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#') and not line.startswith('['):
                    last_row = line.strip()
        
        if not last_row:
            logger.error('No data rows found in nasa-api.txt!')
            raise Exception('No data rows found!')
        
        parts = last_row.split(',')
        if len(parts) < 9:
            logger.error(f"Invalid data row format: {last_row}")
            raise Exception('Invalid data row format')
        
        dt = datetime.strptime(parts[1], '%Y-%m-%d %H:%M:%S')
        last_id = int(parts[0])
        logger.info(f"Last entry: ID={last_id}, Timestamp={parts[1]}")
        return last_id, dt, parts
    except Exception as e:
        logger.error(f"Error getting last entry: {e}")
        raise

# --- 2. Get yesterday's date (last completed day) ---
def get_end_date():
    """Get yesterday's date to avoid requesting incomplete current day data"""
    today = datetime.now().date()
    end_date = today - timedelta(days=1)
    logger.info(f"Fetch end date set to: {end_date}")
    return end_date

# --- 3. Fetch from NASA POWER API with retry logic ---
def fetch_nasa_power_rows(start_dt, end_dt, start_id, last_row_values):
    """Fetch data from NASA POWER API with retry logic and error handling"""
    rows = []
    dt = start_dt + timedelta(hours=1)
    id_ = start_id + 1
    prev_row = last_row_values[:]
    
    # NASA POWER API parameters
    params = {
        'latitude': LAT,
        'longitude': LON,
        'start': dt.strftime('%Y%m%d'),
        'end': end_dt.strftime('%Y%m%d'),
        'community': 'RE',
        'parameters': 'T2M,RH2M,ALLSKY_SFC_SW_DWN,WS2M',
        'format': 'JSON',
        'user': 'AI-EnergyR6'
    }
    
    # Fetch with retry logic
    api_data = {}
    retry_count = 0
    while retry_count < MAX_RETRIES:
        try:
            logger.info(f"Fetching NASA POWER API (attempt {retry_count + 1}/{MAX_RETRIES})...")
            resp = requests.get(NASA_API_URL, params=params, timeout=API_TIMEOUT)
            resp.raise_for_status()
            api_response = resp.json()
            
            if 'properties' not in api_response or 'parameter' not in api_response['properties']:
                logger.warning(f"Unexpected API response structure: {api_response}")
                raise ValueError("Invalid API response structure")
            
            data = api_response['properties']['parameter']
            api_data = {
                'T2M': data.get('T2M', {}),
                'RH2M': data.get('RH2M', {}),
                'ALLSKY_SFC_SW_DWN': data.get('ALLSKY_SFC_SW_DWN', {}),
                'WS2M': data.get('WS2M', {})
            }
            logger.info(f"✓ NASA POWER API fetch successful!")
            break
        except requests.exceptions.Timeout:
            retry_count += 1
            logger.warning(f"API timeout (attempt {retry_count}/{MAX_RETRIES}). Retrying in {RETRY_DELAY}s...")
            if retry_count < MAX_RETRIES:
                import time
                time.sleep(RETRY_DELAY)
        except requests.exceptions.ConnectionError as e:
            retry_count += 1
            logger.warning(f"Connection error: {e} (attempt {retry_count}/{MAX_RETRIES}). Retrying in {RETRY_DELAY}s...")
            if retry_count < MAX_RETRIES:
                import time
                time.sleep(RETRY_DELAY)
        except Exception as e:
            retry_count += 1
            logger.warning(f"API error: {e} (attempt {retry_count}/{MAX_RETRIES}). Using fallback (copy previous row)...")
            if retry_count < MAX_RETRIES:
                import time
                time.sleep(RETRY_DELAY)
    
    if not api_data:
        logger.warning("Failed to fetch from NASA POWER API after retries. Will use previous row fallback for all new hours.")
    
    # Generate rows for each hour from start_dt+1 to end_dt
    while dt <= end_dt:
        key = dt.strftime('%Y%m%d%H')
        try:
            temp = round(float(api_data.get('T2M', {}).get(key, prev_row[2])), 2)
            hum = round(float(api_data.get('RH2M', {}).get(key, prev_row[3])), 2)
            irr_val = round(float(api_data.get('ALLSKY_SFC_SW_DWN', {}).get(key, prev_row[4])), 3)
            wind = round(float(api_data.get('WS2M', {}).get(key, prev_row[5])), 2)
        except (ValueError, TypeError, IndexError) as e:
            logger.warning(f"Error parsing data for {key}: {e}. Using previous row values.")
            temp = float(prev_row[2])
            hum = float(prev_row[3])
            irr_val = float(prev_row[4])
            wind = float(prev_row[5])
        
        src = 'nasa_power'
        wind_pow = float(prev_row[7])
        solar_yield = float(prev_row[8])
        row = [str(id_), dt.strftime('%Y-%m-%d %H:%M:%S'), temp, hum, irr_val, wind, src, wind_pow, solar_yield]
        rows.append(row)
        prev_row = row
        dt += timedelta(hours=1)
        id_ += 1
    
    logger.info(f"Generated {len(rows)} data rows")
    return rows

# --- 4. Append to nasa-api.txt with validation ---
def append_to_txt(rows):
    """Append rows to nasa-api.txt, removing duplicates and updating metadata"""
    try:
        if not rows:
            logger.warning("No rows to append")
            return False
        
        # Read existing lines
        existing_lines = []
        if os.path.exists(TXT_PATH):
            with open(TXT_PATH, 'r') as f:
                existing_lines = f.readlines()
            logger.info(f"Read {len(existing_lines)} existing lines from {TXT_PATH}")
        
        # Remove old summary and last updated lines
        filtered_lines = [line for line in existing_lines 
                         if not line.startswith('# Data collection last updated:') 
                         and not line.startswith('# Summary:')]
        
        # Extract existing data row IDs to avoid duplicates
        existing_ids = set()
        for line in filtered_lines:
            if line.strip() and not line.startswith('#') and not line.startswith('['):
                parts = line.strip().split(',')
                if parts:
                    try:
                        existing_ids.add(int(parts[0]))
                    except ValueError:
                        pass
        
        logger.info(f"Found {len(existing_ids)} existing row IDs")
        
        # Add new rows, skipping duplicates
        new_data_lines = []
        skipped_count = 0
        for row in rows:
            try:
                row_id = int(row[0])
                if row_id not in existing_ids:
                    new_data_lines.append(','.join(map(str, row)) + '\n')
                    existing_ids.add(row_id)
                else:
                    skipped_count += 1
            except (ValueError, IndexError) as e:
                logger.warning(f"Skipping invalid row: {row}. Error: {e}")
        
        logger.info(f"Added {len(new_data_lines)} new rows, skipped {skipped_count} duplicates")
        
        # Combine all data rows
        all_data_rows = [line for line in filtered_lines 
                        if line.strip() and not line.startswith('#') and not line.startswith('[')] + new_data_lines
        
        # Sort by timestamp (ascending order)
        try:
            all_data_rows.sort(key=lambda x: x.split(',')[1])
            logger.info(f"Sorted {len(all_data_rows)} data rows by timestamp")
        except Exception as e:
            logger.error(f"Error sorting rows: {e}")
        
        # Keep comment/header lines
        comment_lines = [line for line in filtered_lines if line.startswith('#') or line.startswith('[')]
        
        # Write file atomically
        temp_path = TXT_PATH + '.tmp'
        try:
            with open(temp_path, 'w') as f:
                for line in comment_lines:
                    f.write(line)
                for line in all_data_rows:
                    f.write(line)
                # Add metadata
                now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                f.write(f'# Data collection last updated: {now_str}\n')
                f.write(f'# Summary: nasa_power={len(all_data_rows)}\n')
            
            # Replace original file
            if os.path.exists(TXT_PATH):
                os.remove(TXT_PATH)
            os.rename(temp_path, TXT_PATH)
            
            logger.info(f"✓ Updated {TXT_PATH} with {len(all_data_rows)} total rows")
            return True
        except Exception as e:
            logger.error(f"Error writing file: {e}")
            if os.path.exists(temp_path):
                os.remove(temp_path)
            return False
    except Exception as e:
        logger.error(f"Error in append_to_txt: {e}")
        return False

# --- 5. Update monthly CSVs with validation ---
def update_monthly_csvs(rows):
    """Update monthly CSV files with new rows"""
    try:
        if not rows:
            logger.warning("No rows to add to monthly CSVs")
            return False
        
        csv_updates = {}
        for row in rows:
            try:
                dt = datetime.strptime(row[1], '%Y-%m-%d %H:%M:%S')
                y = dt.year
                m = dt.month
                fname = f'nasa_{y}_{str(m).zfill(2)}_{dt.strftime("%B").lower()}.csv'
                fpath = os.path.join(CSV_DIR, fname)
                
                # Track updates
                if fpath not in csv_updates:
                    csv_updates[fpath] = {'count': 0, 'is_new': not os.path.exists(fpath)}
                
                # Append to CSV
                file_exists = os.path.exists(fpath)
                with open(fpath, 'a', newline='') as f:
                    writer = csv.writer(f)
                    if not file_exists:
                        writer.writerow(SCHEMA)
                    writer.writerow(row)
                
                csv_updates[fpath]['count'] += 1
            except Exception as e:
                logger.warning(f"Error updating CSV for row {row}: {e}")
        
        # Log summary
        for fpath, info in csv_updates.items():
            status = "created" if info['is_new'] else "updated"
            logger.info(f"✓ CSV {status}: {os.path.basename(fpath)} ({info['count']} rows)")
        
        logger.info(f"✓ Updated {len(csv_updates)} monthly CSV files")
        return True
    except Exception as e:
        logger.error(f"Error in update_monthly_csvs: {e}")
        return False

if __name__ == '__main__':
    logger.info("=" * 80)
    logger.info("NASA POWER API Data Fetch - Started")
    logger.info("=" * 80)
    
    try:
        # Get last entry from local file
        last_id, last_dt, last_row_values = get_last_entry()
        
        # Calculate date range
        end_date = get_end_date()
        end_dt = datetime.combine(end_date, datetime.max.time())
        
        # Check if there's new data to fetch
        if last_dt >= end_dt:
            logger.info("✓ Data is up to date. No new data to fetch.")
            print('No new data to fetch.')
            exit(0)
        
        logger.info(f"Fetching data from {last_dt} to {end_dt}")
        
        # Fetch data from NASA POWER API
        rows = fetch_nasa_power_rows(last_dt, end_dt, last_id, last_row_values)
        
        if not rows:
            logger.warning("No rows fetched from NASA POWER API")
            print('No rows fetched from NASA POWER API')
            exit(1)
        
        logger.info(f"✓ Fetched {len(rows)} new rows")
        print(f'Fetched {len(rows)} new rows.')
        
        # Append to local file
        if not append_to_txt(rows):
            logger.error("Failed to append data to nasa-api.txt")
            print('Failed to append data to nasa-api.txt')
            exit(1)
        
        print('Appended to nasa-api.txt')
        
        # Update monthly CSVs
        if not update_monthly_csvs(rows):
            logger.error("Failed to update monthly CSVs")
            print('Failed to update monthly CSVs')
            exit(1)
        
        print('Updated monthly CSVs.')
        
        logger.info("=" * 80)
        logger.info("NASA POWER API Data Fetch - Completed Successfully")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        print(f'Error: {e}')
        exit(1)
