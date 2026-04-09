#!/usr/bin/env python3
import csv, math
from pathlib import Path
from collections import defaultdict
import xgboost as xgb
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import numpy as np
from datetime import datetime, timedelta
from glob import glob

data_dir       = Path("data")
api_files      = sorted([f for f in glob(str(data_dir / "*api.txt")) if "sim-api.txt" not in f])
ml_output_file = Path("data/xg-ml.txt")

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
    
    # Train XGBoost models
    wind_model = xgb.XGBRegressor(n_estimators=100, learning_rate=0.1, max_depth=6, random_state=42, verbosity=0)
    solar_model = xgb.XGBRegressor(n_estimators=100, learning_rate=0.1, max_depth=6, random_state=42, verbosity=0)
    
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
            "source": "XGBoost-ML"
        })
    return predict_data

def generate_html(ml_daily, nasa_daily, metrics_text, total_api_rows):
    """Generate hardcoded xg-ml.html with data from xg-ml.txt"""
    html_file = Path("xg-ml.html")
    
    # Extract data for charts
    dates = []
    pred_wind_min, pred_wind_avg, pred_wind_max = [], [], []
    pred_solar_min, pred_solar_avg, pred_solar_max = [], [], []
    actual_wind_min, actual_wind_avg, actual_wind_max = [], [], []
    actual_solar_min, actual_solar_avg, actual_solar_max = [], [], []
    
    # Parse metrics
    metrics = {"mae_wind": 0, "rmse_wind": 0, "r2_wind": 0, "corr_wind": 0, 
               "mae_solar": 0, "rmse_solar": 0, "r2_solar": 0, "corr_solar": 0}
    
    for line in metrics_text.split("\n"):
        if "MAE (wind-avg):" in line:
            try:
                metrics["mae_wind"] = float(line.split(":")[1].strip())
            except:
                pass
        elif "MAE (solar-avg):" in line:
            try:
                metrics["mae_solar"] = float(line.split(":")[1].strip())
            except:
                pass
        elif line.startswith("RMSE:"):
            try:
                val = float(line.split(":")[1].strip())
                if "Solar" in metrics_text[:metrics_text.find(line)]:
                    metrics["rmse_solar"] = val
                else:
                    metrics["rmse_wind"] = val
            except:
                pass
        elif line.startswith("R²:"):
            try:
                val = float(line.split(":")[1].strip())
                if "Solar" in metrics_text[:metrics_text.find(line)]:
                    metrics["r2_solar"] = val
                else:
                    metrics["r2_wind"] = val
            except:
                pass
        elif line.startswith("Correlation:"):
            try:
                val = float(line.split(":")[1].strip())
                if "Solar" in metrics_text[:metrics_text.find(line)]:
                    metrics["corr_solar"] = val
                else:
                    metrics["corr_wind"] = val
            except:
                pass
    
    # Extract chart data
    for pred_row, actual_row in zip(ml_daily, nasa_daily):
        ts = pred_row["timestamp"]
        # Parse date - handle both formats
        try:
            date_obj = parse_date(ts)
        except:
            # Just a date string
            date_obj = datetime.strptime(ts, "%Y-%m-%d")
        dates.append(date_obj.strftime("%b%d"))
        
        pred_wind_min.append(float(pred_row["wind-min"]))
        pred_wind_avg.append(float(pred_row["wind-avg"]))
        pred_wind_max.append(float(pred_row["wind-max"]))
        pred_solar_min.append(float(pred_row["solar-min"]))
        pred_solar_avg.append(float(pred_row["solar-avg"]))
        pred_solar_max.append(float(pred_row["solar-max"]))
        
        actual_wind_min.append(float(actual_row["wind-min"]))
        actual_wind_avg.append(float(actual_row["wind-avg"]))
        actual_wind_max.append(float(actual_row["wind-max"]))
        actual_solar_min.append(float(actual_row["solar-min"]))
        actual_solar_avg.append(float(actual_row["solar-avg"]))
        actual_solar_max.append(float(actual_row["solar-max"]))
    
    # Format arrays for JavaScript
    dates_str = "['" + "','".join(dates) + "']"
    pred_wind_min_str = "[" + ",".join(f"{v:.2f}" for v in pred_wind_min) + "]"
    pred_wind_avg_str = "[" + ",".join(f"{v:.2f}" for v in pred_wind_avg) + "]"
    pred_wind_max_str = "[" + ",".join(f"{v:.2f}" for v in pred_wind_max) + "]"
    pred_solar_min_str = "[" + ",".join(f"{v:.2f}" for v in pred_solar_min) + "]"
    pred_solar_avg_str = "[" + ",".join(f"{v:.2f}" for v in pred_solar_avg) + "]"
    pred_solar_max_str = "[" + ",".join(f"{v:.2f}" for v in pred_solar_max) + "]"
    actual_wind_min_str = "[" + ",".join(f"{v:.2f}" for v in actual_wind_min) + "]"
    actual_wind_avg_str = "[" + ",".join(f"{v:.2f}" for v in actual_wind_avg) + "]"
    actual_wind_max_str = "[" + ",".join(f"{v:.2f}" for v in actual_wind_max) + "]"
    actual_solar_min_str = "[" + ",".join(f"{v:.2f}" for v in actual_solar_min) + "]"
    actual_solar_avg_str = "[" + ",".join(f"{v:.2f}" for v in actual_solar_avg) + "]"
    actual_solar_max_str = "[" + ",".join(f"{v:.2f}" for v in actual_solar_max) + "]"
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>XGBoost-ML | Energy Data Summary</title>
  <link rel="stylesheet" href="style.css">
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <style>
    /* Exact index.html nav styling */
    .header-nav-link {{
      color: #28a745 !important;
      font-weight: bold;
    }}
    .header-nav-link:hover {{
      color: #218838 !important;
      text-decoration: underline;
    }}
    /* Page styling */
.main-summary {{ margin: 50px 0; }}
@media (max-width: 768px) {{
  .summary-cards {{ grid-template-columns: 1fr; }}
  .summary-card {{ padding: 20px 16px; }}
  .summary-label {{ font-size: 0.85rem; }}
  .summary-value {{ font-size: 2rem; }}
  .metric-desc {{ font-size: 0.8em; }}
  table {{ font-size: 0.8em; }}
  th, td {{ padding: 4px 2px; }}
  .chart-wrapper {{ grid-template-columns: 1fr; gap: 20px; }}
  .chart-title {{ font-size: 1.4em; }}
  canvas {{ height: 300px !important; }}
}}
    .chart-wrapper {{ display: grid; grid-template-columns: 1fr 1fr; gap: 40px; margin: 40px 0; }}
    @media (max-width: 1200px) {{ .chart-wrapper {{ grid-template-columns: 1fr; gap: 30px; }} }}
    .combined-chart-section {{ 
      background: linear-gradient(135deg, rgba(30,39,73,0.9), rgba(10,17,40,0.9));
      border: 1px solid #334155;
      backdrop-filter: blur(15px);
      border-radius: 20px;
      padding: 40px;
      box-shadow: 0 20px 60px rgba(0,0,0,0.4);
    }}
    .chart-title {{ color: #06b6d4 !important; font-size: 1.9em; margin-bottom: 30px; font-weight: 700; }}
    .chart-legend {{ text-align: center; margin-bottom: 25px; font-size: 1.2em; color: #e2e8f0; background: rgba(6,182,212,0.2); padding: 15px 25px; border-radius: 30px; border: 1px solid rgba(6,182,212,0.4); backdrop-filter: blur(10px); }}
    canvas {{ border: 1px solid rgba(51,65,85,0.8); box-shadow: 0 12px 40px rgba(0,0,0,0.3); }}
    .metric-desc {{ font-size: 0.92em; color: #94a3b8; margin-top: 8px; }}
  </style>
</head>
<body>
  <div class="container">
    <header class="header">
      <h1>XGBoost-ML: Predict vs Actual</h1>
      <nav class="header-nav">
        <a href="index.html" class="header-nav-link">🏠 Main</a>
        <a href="rf-ml.html" class="header-nav-link">RF-ML</a>
        <a href="nasa-ml.html" class="header-nav-link">NASA-ML</a>
        <a href="sim-ml.html" class="header-nav-link">Sim-ML</a>
        <a href="ltsm-ml.html" class="header-nav-link">LSTM-ML</a>
      </nav>
    </header>

    <div class="main-summary">
      <div class="summary-cards">
        <div class="summary-card" style="grid-column: 1 / -1;">
          <div class="summary-label">XGBoost Performance & Config</div><table style="width: 100%; border-collapse: collapse; font-size: 0.88em;">
            <thead>
          <tr><th style="text-align: right; padding: 8px 0; color: #94a3b8; font-weight: 600;">Metric</th><th style="text-align: center; padding: 8px 0; color: #94a3b8; font-weight: 600;">Wind</th><th style="text-align: center; padding: 8px 0; color: #94a3b8; font-weight: 600;">Solar</th><th style="text-align: center; padding: 8px 0; color: #94a3b8; font-weight: 600;">Ideal</th><th style="text-align: left; padding: 8px 0; color: #94a3b8; font-weight: 600;">Meaning</th></tr>
            </thead>
            <tbody>
              <tr><td style="text-align: right; padding: 6px 0; border-bottom: 1px solid rgba(255,255,255,0.08);">MAE (ave)</td><td style="text-align: center; color: #f59e0b; font-weight: bold;">{metrics["mae_wind"]:.3f}</td><td style="text-align: center; color: #ef4444; font-weight: bold;">{metrics["mae_solar"]:.3f}</td><td style="text-align: center; color: #10b981;"><0.5</td><td style="text-align: left;">Avg abs error</td></tr>
              <tr><td style="text-align: right; padding: 6px 0; border-bottom: 1px solid rgba(255,255,255,0.08);">RMSE</td><td style="text-align: center; color: #ef4444; font-weight: bold;">{metrics["rmse_wind"]:.3f}</td><td style="text-align: center; color: #ef4444; font-weight: bold;">{metrics["rmse_solar"]:.3f}</td><td style="text-align: center; color: #10b981;"><0.7</td><td style="text-align: left;">RMS outliers</td></tr>
              <tr><td style="text-align: right; padding: 6px 0; border-bottom: 1px solid rgba(255,255,255,0.08);">R² Score</td><td style="text-align: center; color: #ef4444; font-weight: bold;">{metrics["r2_wind"]:.3f}</td><td style="text-align: center; color: #ef4444; font-weight: bold;">{metrics["r2_solar"]:.3f}</td><td style="text-align: center; color: #10b981;">>0.7</td><td style="text-align: left;">Variance explained</td></tr>
              <tr><td style="text-align: right; padding: 6px 0; border-bottom: 1px solid rgba(255,255,255,0.08);">Correlation</td><td style="text-align: center; color: #f59e0b; font-weight: bold;">{metrics["corr_wind"]:.3f}</td><td style="text-align: center; color: #ef4444; font-weight: bold;">{metrics["corr_solar"]:.3f}</td><td style="text-align: center; color: #10b981;">>0.8</td><td style="text-align: left;">Linear agreement</td></tr>

<tr style="border-top: 2px solid rgba(255,255,255,0.1); padding: 8px 0;">
  <td style="padding: 4px 0; font-weight: 600; width: 35%; text-align: right;">Model:</td>
  <td style="text-align: left; font-weight: 600; color: #06b6d4; padding-left: 10px;" colspan="4">XGBoost (eXtreme Gradient Boosting)</td>
 </tr>

 <tr style="padding: 4px 0;">
  <td style="padding: 4px 0; width: 35%; text-align: right;">Training data:</td>
  <td style="text-align: left; color: #06b6d4; font-weight: 600; padding-left: 10px;" colspan="4">2025-01 to 2026-02-20 ({total_api_rows:,} rows, 13 months)</td>
 </tr>

 <tr style="padding: 4px 0 8px 0;">
  <td style="padding: 4px 0; width: 35%; text-align: right;">Predict data:</td>
  <td style="text-align: left; color: #06b6d4; font-weight: 600; padding-left: 10px;" colspan="4">Feb 21–28 2026 (8 days Min/Avg/Max)</td>
 </tr>

            </tbody>
          </table>
          <div style="margin-top: 12px; font-size: 0.82em; color: #94a3b8; text-align: center; padding: 8px; background: rgba(6,182,212,0.1); border-radius: 6px; border: 1px solid rgba(6,182,212,0.2);">
            🟠 Orange=Needs Improvement | 🟢 Green=Target | 🔴 Red=Below Baseline
          </div>
        </div>
      </div>
    </div>

    <div class="combined-chart-section">
      <div class="chart-wrapper">
        <div>
          <h2 class="chart-title">💨 Wind: Predict (Dashed ML) vs Actual (Solid API)</h2>
          <div class="chart-legend">🔴 Red=Min | 🟢 Green=Avg | 🔵 Blue=Max | Dashed=Predict (Data-A) | Solid=Actual (Data-B)</div>
          <canvas id="combined_wind"></canvas>
        </div>
        <div>
          <h2 class="chart-title">☀️ Solar: Predict (Dashed ML) vs Actual (Solid API)</h2>
          <div class="chart-legend">🔴 Red=Min | 🟢 Green=Avg | 🔵 Blue=Max | Dashed=Predict (Data-A) | Solid=Actual (Data-B) | Log Scale</div>
          <canvas id="combined_solar"></canvas>
        </div>
      </div>
    </div>
  </div>

  <script>
    const dates = {dates_str};

    // Predict Data-A ML (Feb 21-28 2026)
    const predict_wind_avg = {pred_wind_avg_str};
    const predict_wind_min = {pred_wind_min_str};
    const predict_wind_max = {pred_wind_max_str};
    const predict_solar_avg = {pred_solar_avg_str};
    const predict_solar_min = {pred_solar_min_str};
    const predict_solar_max = {pred_solar_max_str};

    // Actual Data-B API (Feb 21-28 2026)
    const actual_wind_avg = {actual_wind_avg_str};
    const actual_wind_min = {actual_wind_min_str};
    const actual_wind_max = {actual_wind_max_str};
    const actual_solar_avg = {actual_solar_avg_str};
    const actual_solar_min = {actual_solar_min_str};
    const actual_solar_max = {actual_solar_max_str};

    // Wind: simple solid colors Red Min, Green Avg, Blue Max
    new Chart('combined_wind', {{
      type: 'line',
      data: {{
        labels: dates,
        datasets: [
          // Predict
          {{ label: 'Predict Avg (Data-A)', data: predict_wind_avg, borderColor: '#22c55e', borderWidth: 4, borderDash: [12,6], tension: 0.4 }},
          {{ label: 'Predict Min', data: predict_wind_min, borderColor: '#ef4444', borderWidth: 3, borderDash: [10,6], tension: 0.3 }},
          {{ label: 'Predict Max', data: predict_wind_max, borderColor: '#3b82f6', borderWidth: 3, borderDash: [10,6], tension: 0.3 }},
          // Actual
          {{ label: 'Actual Avg (Data-B)', data: actual_wind_avg, borderColor: '#22c55e', borderWidth: 4, tension: 0.4, backgroundColor: 'rgba(34,197,94,0.15)', fill: true }},
          {{ label: 'Actual Min', data: actual_wind_min, borderColor: '#ef4444', borderWidth: 3, tension: 0.3 }},
          {{ label: 'Actual Max', data: actual_wind_max, borderColor: '#3b82f6', borderWidth: 3, tension: 0.3 }}
        ]
      }},
      options: {{ responsive: true, plugins: {{ legend: {{ position: 'top' }} }}, scales: {{ y: {{ beginAtZero: true, title: {{ display: true, text: 'Wind m/s' }} }} }} }}
    }});

    // Solar: same simple colors, log scale
    new Chart('combined_solar', {{
      type: 'line',
      data: {{
        labels: dates,
        datasets: [
          // Predict
          {{ label: 'Predict Avg (Data-A)', data: predict_solar_avg, borderColor: '#22c55e', borderWidth: 4, borderDash: [12,6], tension: 0.4 }},
          {{ label: 'Predict Min', data: predict_solar_min, borderColor: '#ef4444', borderWidth: 3, borderDash: [10,6], tension: 0.3 }},
          {{ label: 'Predict Max', data: predict_solar_max, borderColor: '#3b82f6', borderWidth: 3, borderDash: [10,6], tension: 0.3 }},
          // Actual
          {{ label: 'Actual Avg (Data-B)', data: actual_solar_avg, borderColor: '#22c55e', borderWidth: 4, tension: 0.4, backgroundColor: 'rgba(34,197,94,0.15)', fill: true }},
          {{ label: 'Actual Min', data: actual_solar_min, borderColor: '#ef4444', borderWidth: 3, tension: 0.3 }},
          {{ label: 'Actual Max', data: actual_solar_max, borderColor: '#3b82f6', borderWidth: 3, tension: 0.3 }}
        ]
      }},
      options: {{ responsive: true, plugins: {{ legend: {{ position: 'top' }} }}, scales: {{ y: {{ type: 'logarithmic', min: 0.01, title: {{ display: true, text: 'Solar Irradiance (log scale)' }} }} }} }}
    }});
  </script>
</body>
</html>
"""
    
    with open(html_file, "w") as f:
        f.write(html_content)

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
    
    print(f"\nTraining XGBoost model using {len(all_data)} total rows from all *api.txt files...")
    wind_model, solar_model, scaler = train_ml_model(all_data)
    
    ml_daily = predict_daily_avgs(wind_model, solar_model, scaler)
    nasa_daily = aggregate_daily_actual(all_data)
    
    # Write to xg-ml.txt
    total_api_rows = len(all_data)
    with open(ml_output_file, "w") as f:
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"# ML page output last updated: {now_str}\n")
        f.write(f"# Summary: Training data = {total_api_rows} | full-api actual = {len(nasa_daily)} | XGBoost predict = {len(ml_daily)}\n")
        f.write("[full-api]\n\n")
        
        # Data-A Header
        f.write("# Data-A: XGBoost-ML Predictions (Feb 21–28 2026)\n")
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
            
            # Capture metrics for HTML generation
            metrics_text = f"Wind Metrics:\nMAE (wind-avg): {mae_wind:.3f}\nRMSE: {rmse_wind:.3f}\nR²: {r2_wind:.3f}\nCorrelation: {corr_wind:.3f}\n\nSolar Metrics:\nMAE (solar-avg): {mae_solar:.3f}\nRMSE: {rmse_solar:.3f}\nR²: {r2_solar:.3f}\nCorrelation: {corr_solar:.3f}"
    
    # Generate HTML with hardcoded data
    metrics_text = ""
    with open(ml_output_file, "r") as f:
        lines = f.readlines()
        in_metrics = False
        for line in lines:
            if "Metrics:" in line:
                in_metrics = True
            if in_metrics:
                metrics_text += line
    
    generate_html(ml_daily, nasa_daily, metrics_text, total_api_rows)

    print(f"✅ xg-ml.txt generated with XGBoost ML (Data-A/B + metrics)")
    print(f"✅ xg-ml.html generated with hardcoded data from xg-ml.txt")

if __name__ == "__main__":
    main()
