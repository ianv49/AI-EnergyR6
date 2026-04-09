#!/usr/bin/env python3
import csv, math
from pathlib import Path
from collections import defaultdict
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import numpy as np
from datetime import datetime, timedelta
from glob import glob

data_dir       = Path("data")
api_files      = sorted([f for f in glob(str(data_dir / "*api.txt")) if "sim-api.txt" not in f])
ml_output_file = Path("data/rf-ml.txt")

def load_csv_skip_comments(file_path):
    with open(file_path, newline="") as f:
        lines = [line for line in f if not line.strip().startswith("#") and not line.strip().startswith("[")]
        reader = csv.DictReader(lines)
        rows = []
        for row in reader:
            clean = {k.strip(): v.strip() for k,v in row.items()}
            rows.append(clean)
        return rows, [h.strip() for h in reader.fieldnames]

def parse_date(ts):
    # Handle ISO format (2026-03-19T09:00:00Z) and standard format (2026-03-19 09:00:00)
    ts = ts.strip()
    if 'T' in ts:
        # ISO format: remove 'Z' and replace 'T' with space
        ts = ts.replace('Z', '').replace('T', ' ')
    return datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")

def create_features(row):
    dt = parse_date(row["timestamp"])
    day_of_year = dt.timetuple().tm_yday
    hour = dt.hour
    day_of_week = dt.weekday()
    month = dt.month
    return [day_of_year, hour, day_of_week, month, float(row["temperature"]), float(row["humidity"])]

def train_ml_model(hourly_data):
    # Train data: Jan 1 2025 to Feb 20 2026
    train_data = [r for r in hourly_data if parse_date(r["timestamp"]).date() <= parse_date("2026-02-20 23:59:59").date()]
    
    X = []
    y_wind = []
    y_solar = []
    for row in train_data:
        features = create_features(row)
        X.append(features)
        y_wind.append(float(row["wind_speed"]))
        y_solar.append(float(row["irradiance"]))
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Train models
    wind_model = RandomForestRegressor(n_estimators=100, random_state=42)
    solar_model = RandomForestRegressor(n_estimators=100, random_state=42)
    
    wind_model.fit(X_scaled, y_wind)
    solar_model.fit(X_scaled, y_solar)
    
    return wind_model, solar_model, scaler

def predict_daily_avgs(model_wind, model_solar, scaler):
    # Predict for Feb 21-28 2026
    dates = ["2026-02-21", "2026-02-22", "2026-02-23", "2026-02-24", "2026-02-25", "2026-02-26", "2026-02-27", "2026-02-28"]
    predict_data = []
    
    for i, date in enumerate(dates, 1):
        # Generate 24 hourly timestamps for this date
        daily_hourly = []
        for hour in range(24):
            ts = f"{date} {hour:02d}:00:00"
            dummy_row = {"timestamp": ts, "temperature": "30.0", "humidity": "80.0", "wind_speed": "0", "irradiance": "0"}
            features = create_features(dummy_row)
            daily_hourly.append(features)
        
        X_daily = scaler.transform(daily_hourly)
        wind_preds = model_wind.predict(X_daily)
        solar_preds = model_solar.predict(X_daily)
        
        wind_min, wind_avg, wind_max = min(wind_preds), np.mean(wind_preds), max(wind_preds)
        solar_min, solar_avg, solar_max = min(solar_preds), np.mean(solar_preds), max(solar_preds)
        
        predict_data.append({
            "id": str(i),
            "timestamp": date,
            "wind-min": f"{wind_min:.2f}",
            "wind-avg": f"{wind_avg:.2f}",
            "wind-max": f"{wind_max:.2f}",
            "solar-min": f"{solar_min:.2f}",
            "solar-avg": f"{solar_avg:.2f}",
            "solar-max": f"{solar_max:.2f}",
            "source": "RF-ML"
        })
    return predict_data

def aggregate_daily_actual(hourly_data):
    daily = defaultdict(list)
    for row in hourly_data:
        ts = row["timestamp"].strip()
        # Extract date - handle both formats: YYYY-MM-DD HH:MM:SS and YYYY-MM-DDTHH:MM:SSZ
        date = ts.split('T')[0] if 'T' in ts else ts.split()[0]
        if "2026-02-21" <= date <= "2026-02-28":
            daily[date].append(row)

    results = []
    for i, date in enumerate(sorted(daily.keys()), start=1):
        rows = daily[date]
        wind_vals = [float(r["wind_speed"]) for r in rows]
        solar_vals = [float(r["irradiance"]) for r in rows]
        wind_min = min(wind_vals)
        wind_avg = sum(wind_vals)/len(wind_vals)
        wind_max = max(wind_vals)
        solar_min = min(solar_vals)
        solar_avg = sum(solar_vals)/len(solar_vals)
        solar_max = max(solar_vals)
        results.append({
            "id": str(i),
            "timestamp": date,
            "wind-min": f"{wind_min:.2f}",
            "wind-avg": f"{wind_avg:.2f}",
            "wind-max": f"{wind_max:.2f}",
            "solar-min": f"{solar_min:.2f}",
            "solar-avg": f"{solar_avg:.2f}",
            "solar-max": f"{solar_max:.2f}",
            "source": "full-API"
        })
    return results

def main():
    # Load all API files
    all_data = []
    for api_file in api_files:
        try:
            data, _ = load_csv_skip_comments(api_file)
            all_data.extend(data)
            print(f"Loaded {len(data)} rows from {Path(api_file).name}")
        except Exception as e:
            print(f"⚠️ Skipped {Path(api_file).name}: {e}")
    
    print(f"\nTraining ML model using {len(all_data)} total rows from all *api.txt files...")
    wind_model, solar_model, scaler = train_ml_model(all_data)
    
    ml_daily = predict_daily_avgs(wind_model, solar_model, scaler)
    nasa_daily = aggregate_daily_actual(all_data)
    
    # Write to ml-nasa-output.txt - FIXED SPACING
    with open(ml_output_file, "w") as f:
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"# ML page output last updated: {now_str}\n")
        f.write(f"# Summary: full-api actual = {len(nasa_daily)} | RF predict = {len(ml_daily)}\n")
        f.write("[full-api]\n\n")
        
        # Data-A Header
        f.write("# Data-A: RF-ML Predictions (Feb 21–28 2026)\n")
        f.write("id,timestamp,wind-min,wind-avg,wind-max,solar-min,solar-avg,solar-max,source\n")
        for row in ml_daily:
            f.write(f"{row['id']},{row['timestamp']},{row['wind-min']},{row['wind-avg']},{row['wind-max']},{row['solar-min']},{row['solar-avg']},{row['solar-max']},{row['source']}\n")
        f.write("\n")
        
        # Data-B Header
        f.write("# Data-B: REAL-API Power Daily Averages (Feb 21–28 2026)\n")
        f.write("id,timestamp,wind-min,wind-avg,wind-max,solar-min,solar-avg,solar-max,source\n")
        for row in nasa_daily:
            f.write(f"{row['id']},{row['timestamp']},{row['wind-min']},{row['wind-avg']},{row['wind-max']},{row['solar-min']},{row['solar-avg']},{row['solar-max']},{row['source']}\n")
        f.write("\n")
        
        # Metrics
        f.write("# Metrics: Prediction vs API Actual (Feb 21–28 2026)\n")
        pred_map = {r["timestamp"]: r for r in ml_daily}
        actual_map = {r["timestamp"]: r for r in nasa_daily}
        common_dates = sorted(set(pred_map.keys()) & set(actual_map.keys()))

        if not common_dates:
            f.write("No overlapping dates between ML predictions and NASA data.\n")
        else:
            # Wind metrics
            y_pred_wind = [float(pred_map[d]["wind-avg"]) for d in common_dates]
            y_true_wind = [float(actual_map[d]["wind-avg"]) for d in common_dates]
            mae_wind = mean_absolute_error(y_true_wind, y_pred_wind)
            rmse_wind = math.sqrt(mean_squared_error(y_true_wind, y_pred_wind))
            r2_wind = r2_score(y_true_wind, y_pred_wind)
            corr_wind = np.corrcoef(y_true_wind, y_pred_wind)[0,1]
            
            # Solar metrics
            y_pred_solar = [float(pred_map[d]["solar-avg"]) for d in common_dates]
            y_true_solar = [float(actual_map[d]["solar-avg"]) for d in common_dates]
            mae_solar = mean_absolute_error(y_true_solar, y_pred_solar)
            rmse_solar = math.sqrt(mean_squared_error(y_true_solar, y_pred_solar))
            r2_solar = r2_score(y_true_solar, y_pred_solar)
            corr_solar = np.corrcoef(y_true_solar, y_pred_solar)[0,1]
            
            f.write("Wind Metrics:\n")
            f.write(f"MAE (wind-avg): {mae_wind:.3f}\n")
            f.write(f"RMSE: {rmse_wind:.3f}\n")
            f.write(f"R²: {r2_wind:.3f}\n")
            f.write(f"Correlation: {corr_wind:.3f}\n")
            f.write("\n")
            f.write("Solar Metrics:\n")
            f.write(f"MAE (solar-avg): {mae_solar:.3f}\n")
            f.write(f"RMSE: {rmse_solar:.3f}\n")
            f.write(f"R²: {r2_solar:.3f}\n")
            f.write(f"Correlation: {corr_solar:.3f}\n")

    print(f"✅ rf-ml.txt generated with RF ML (Data-A/B + metrics)")

if __name__ == "__main__":
    main()
