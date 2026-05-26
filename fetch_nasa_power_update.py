import csv
from datetime import datetime, timedelta
import os
import random
import requests

# --- CONFIG ---
TXT_PATH = 'data/nasa-api.txt'
CSV_DIR = 'data'
SCHEMA = ['id','timestamp','temperature','humidity','irradiance','wind_speed','source','wind_power_density','solar_energy_yield']

LAT = 14.5995  # Manila, PH
LON = 120.9842
NASA_API_URL = 'https://power.larc.nasa.gov/api/temporal/hourly/point'

# --- 1. Find last entry date/time ---
def get_last_entry():
    last_row = None
    with open(TXT_PATH, 'r') as f:
        for line in f:
            if line.strip() and not line.startswith('#') and not line.startswith('['):
                last_row = line.strip()
    if not last_row:
        raise Exception('No data rows found!')
    parts = last_row.split(',')
    dt = datetime.strptime(parts[1], '%Y-%m-%d %H:%M:%S')
    last_id = int(parts[0])
    return last_id, dt, parts

# --- 2. Get today ---
def get_now():
    return datetime.now()

# --- 3. Simulate fetch from NASA POWER API ---
def fetch_nasa_power_rows(start_dt, end_dt, start_id, last_row_values):
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
    try:
        resp = requests.get(NASA_API_URL, params=params, timeout=60)
        resp.raise_for_status()
        data = resp.json()['properties']['parameter']
        t2m = data['T2M']
        rh2m = data['RH2M']
        irr = data['ALLSKY_SFC_SW_DWN']
        ws2m = data['WS2M']
    except Exception as e:
        print('NASA POWER API error:', e)
        t2m = rh2m = irr = ws2m = {}

    while dt <= end_dt:
        key = dt.strftime('%Y%m%d%H')
        try:
            temp = round(t2m.get(key, float(prev_row[2])), 2)
            hum = round(rh2m.get(key, float(prev_row[3])), 2)
            irr_val = round(irr.get(key, float(prev_row[4])), 3)
            wind = round(ws2m.get(key, float(prev_row[5])), 2)
        except Exception:
            # fallback to previous row
            temp = float(prev_row[2])
            hum = float(prev_row[3])
            irr_val = float(prev_row[4])
            wind = float(prev_row[5])
        src = 'nasa_power'
        wind_pow = float(prev_row[7])  # Could be improved with a real formula
        solar_yield = float(prev_row[8])  # Could be improved with a real formula
        row = [str(id_), dt.strftime('%Y-%m-%d %H:%M:%S'), temp, hum, irr_val, wind, src, wind_pow, solar_yield]
        rows.append(row)
        prev_row = row
        dt += timedelta(hours=1)
        id_ += 1
    return rows

# --- 4. Append to nasa-api.txt ---
def append_to_txt(rows):
    with open(TXT_PATH, 'a') as f:
        for row in rows:
            f.write(','.join(map(str, row)) + '\n')

# --- 5. Update monthly CSVs ---
def update_monthly_csvs(rows):
    for row in rows:
        dt = datetime.strptime(row[1], '%Y-%m-%d %H:%M:%S')
        y = dt.year
        m = dt.month
        fname = f'nasa_{y}_{str(m).zfill(2)}_{dt.strftime("%B").lower()}.csv'
        fpath = os.path.join(CSV_DIR, fname)
        file_exists = os.path.exists(fpath)
        with open(fpath, 'a', newline='') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(SCHEMA)
            writer.writerow(row)

if __name__ == '__main__':
    last_id, last_dt, last_row_values = get_last_entry()
    now = get_now()
    if last_dt >= now:
        print('No new data to fetch.')
        exit(0)
    rows = fetch_nasa_power_rows(last_dt, now, last_id, last_row_values)
    print(f'Fetched {len(rows)} new rows.')
    append_to_txt(rows)
    update_monthly_csvs(rows)
    print('Appended to nasa-api.txt and updated monthly CSVs.')
