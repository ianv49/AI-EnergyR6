# AI-EnergyR6
https://ianv49.github.io/AI-EnergyR6/

This project develops a cross-platform application for predictive maintenance of renewable energy assets (wind turbines, solar panels, inverters, batteries). It uses IoT sensor data, external weather/solar APIs, and AI/ML models to forecast failures and optimize maintenance schedules.

## 📋 Project Phases

The project is organized into phases for systematic development. Below is the latest status of all phases with detailed sub-steps:

### Phase 1: Environment Setup ✅ Done
- Install PostgreSQL portable binaries
- Initialize database cluster (initdb)
- Start PostgreSQL manually (pg_ctl)
- Connect with psql
- **APIs Used:** None (foundational setup only)

### Phase 2: Database Schema ✅ Done
- Create energy_db database
- Define sensor_data table schema with 11 columns (timestamp, temperature, humidity, irradiance, wind_speed, source, etc.)
- Verify schema with \d sensor_data
- **APIs Used:** None (database foundation only)

### Phase 3: Python Integration ✅ Done
- Install psycopg2 driver for PostgreSQL connectivity
- Create db_ingest.py script for data ingestion
- Connect Python to PostgreSQL database
- Insert test row via Python
- Fetch and display rows via Python
- **APIs Used:** None (local testing only)

### Phase 4: Log Ingestion ✅ Done
- Adapt script to read sensor_logs.txt (local sensor simulation data)
- Insert multiple rows from file into database
- Verify ingestion with query output
- **APIs Used:** None (local file ingestion only)

### Phase 5: Enhancements ✅ Done
- Handle duplicate entries with unique timestamp constraint and ON CONFLICT logic
- Format timestamp output (seconds precision)
- Optional: pretty table output for display
- Row count tracking before/after ingestion
- Skip header line in text file ingestion
- Modularize connection logic into db_connector.py
- Add test_connection.py script for connectivity verification
- Show top/bottom rows in test script output
- **APIs Used:** None (enhancements to local ingestion pipeline)

### Phase 6: Next Steps ✅ Done
- Automate ingestion with batch file or cron job scheduling
- Extend ingestion for CSV and real sensor stream handling
- Dashboard/visualization integration with Flask
- Add permanent log file output (logs/ingestion.log)
- Daily log rotation using TimedRotatingFileHandler
- **APIs Used:** None (automation and logging infrastructure)

### Phase 7: Visualization & Dashboard ✅ Done
- Generate HTML tables from database data (collect1.txt: sim data)
- Build simple Flask web interface with interactive data tables
- Display multiple data sources in separate organized tables
- Implement real-time data refresh capability
- **APIs Used:** SIM (simulated sensor data only, no external APIs yet)


### Phase 8: Real-Time Ingestion ✅ Done
- Simulate sensor streams (append rows every minute) with SIM data ✅ Done (collect1.txt: 9,478 rows)
- Implement manual trigger for on-demand ingestion via Flask API ✅ Done
- Enable continuous ingestion pipeline with scheduled execution ✅ Done
- HTML interface integration for Phase 8 steps and routines ✅ Done
- Backfill scripts for historical data (NASA POWER, Open-Meteo) ✅ Done (collect2.txt: 10,177 rows, collect3.txt: 10,176 rows)
- **APIs Used:** SIM (local simulation), NASA POWER, Open-Meteo


### Phase 9: Web-Sensor Data Integration ⏳ Partial
- Connect to Open-Meteo API for local weather data ✅ Done
- Ingest NASA POWER API for solar irradiance and climate data ✅ Done
- Open-Meteo and NASA POWER backfill scripts for historical data ✅ Done
- Integrate PVOutput API for solar PV system performance **Skip** (no free use of historical API) ⏳ Skipped
- Integrate NOAA Climate Data API **Skip** (not able to fetch API for 2025) ⏳ Skipped
- Integrate Solcast API **Skip** (student API key has very low fetch limit) ⏳ Skipped
- Integrate Meteostat API ⏳ Partial (limited historical data ingested)
- Integrate Weatherbit API ✅ Done (2025 historical data fetched + stored)
- Normalize and store web-sensor data into sensor_data table ✅ Done
- Combine local sensor + web API data for richer analytics ✅ Done
- Ingest Tomorrow.io (real sensor) data ✅ Done (24 rows in collect6.txt)

#### Available Data Sources
| Source | Description | Backfill Scripts | Status | Reason |
|--------|-------------|-----------------|--------|--------|
| sim | Simulated sensor data | N/A (generated locally) | ✅ Active | Testing & validation |
| nasa_power | NASA POWER solar irradiance data | backfill_nasa_*.py, run_nasa_ingestion.py | ✅ Active | Free API, reliable data |
| open_meteo | Open-Meteo weather data | backfill_open_meteo*.py, fetch_open_meteo*.py | ✅ Active | Free API, no key required |
| weatherbit | Weatherbit historical weather data | fetch_weatherbit_2025.py (2025 history) | ✅ Active | Full 2025 history integrated |
| meteostat | Meteostat historical weather data (temp/hum/wind) | backfill_meteostat.py, fetch_meteostat_feb2026.py, ingest_meteostat_feb2026.py | ✅ Limited | Partial 2026 data available |
| tomorrow | Tomorrow.io real web sensor data | fetch_tomorrowio_march2026.py | ✅ Active | 24 rows in collect6.txt |
| solcast | Solcast solar irradiance (GHI/DNI/DHI + wind/temp) | backfill_solcast_feb2026.py | **Skip** | Student API key quota too low |
| pvoutput | PVOutput solar PV system data | backfill_pvoutput*.py (planned) | **Skip** | No free historical data access (401 auth) |
| noaa | NOAA Climate Data | backfill_noaa*.py (planned) | **Skip** | Consistent API timeouts/502 errors |
| tomorrow | Tomorrow.io real web sensor data | fetch_tomorrowio_march2026.py | ✅ Active | 24 rows in collect6.txt |

#### API Status Details
**Active APIs:**
- **NASA POWER** ✅: Free, no authentication required. Provides comprehensive solar irradiance and meteorological data for historical periods.
- **Open-Meteo** ✅: Free API with no API key needed. Delivers hourly historical weather data including temperature, humidity, wind speed, and solar radiation.
- **Weatherbit** ✅: Successfully integrated with full 2025 historical hourly data (10,909 records).
- **Meteostat** ⏳: Limited integration with partial data for early 2026 periods.
- **Tomorrow.io** ✅: Live web sensor data ingest from Tomorrow.io (24 rows in collect6.txt).

**Skipped APIs:**
- **NOAA**: Consistent API timeouts and 502 errors. Unable to fetch 2025 historical data reliably.
- **PVOutput**: No free historical data access. API requires authentication but free tier doesn't support historical data queries (returns 401 Unauthorized).
- **Solcast**: Student API key has quota restrictions too low for full backfills. Limited to minimal requests per month.
- **OpenWeather**: Removed from pipeline due to authorization issues with One Call API 3.0 (401 Unauthorized on historical endpoints).

Here is a list of the API sources mentioned in your `README.md`, along with the data they provide that is relevant to your database schema:

### Actively Used APIs:

1.  **Open-Meteo** ✅ Active
    *   **Status:** Fully operational. Active data source for weather data with complete historical data.
    *   **Data Collected:** Hourly historical weather data for Manila location (2025-present).
    *   **Row Count:** 10,176 rows in collect3.txt
    *   **Database Column Mapping:**
        *   `temperature`
        *   `humidity`
        *   `wind_speed`
        *   `cloudiness`
        *   `uv_index`
        *   `irradiance` (as Shortwave Radiation)

2.  **NASA POWER** ✅ Active
    *   **Status:** Fully operational. Active source for solar and meteorological data.
    *   **Data Collected:** Hourly solar irradiance and climate data for Manila location (2025-present).
    *   **Row Count:** 10,177 rows in collect2.txt
    *   **Database Column Mapping:**
        *   `temperature`
        *   `humidity`
        *   `wind_speed`
        *   `irradiance` (as Direct solar irradiance)

3.  **Weatherbit** ✅ Active
    *   **Status:** Fully integrated with 2025 historical data.
    *   **Data Collected:** Complete 2025 hourly weather data (temperature, humidity, wind speed, irradiance).
    *   **Row Count:** 743 historical records from 2025 in collect7.txt
    *   **Database Column Mapping:**
        *   `temperature`
        *   `humidity`
        *   `wind_speed`
        *   `cloudiness`
        *   `uv_index`
        *   `irradiance` (Solar Radiation)

4.  **Meteostat** ⏳ Partial Implementation
    *   **Status:** Limited integration with partial data for early 2026 periods.
    *   **Data Collected:** Hourly station data for Manila location (2025-01-01 to 2026-03-01).
    *   **Row Count:** 9,438 rows in collect5.txt
    *   **Database Column Mapping:**
        *   `temperature`
        *   `humidity`
        *   `wind_speed`
        *   `sunshine duration` (related to irradiance)

5.  **Tomorrow.io** ✅ Active
    *   **Status:** Real web sensor data ingest complete (March 2026 subset).
    *   **Data Collected:** 24 hourly rows from 2026-03-19 to 2026-03-20.
    *   **Row Count:** 24 rows in collect6.txt
    *   **Database Column Mapping:**
        *   `temperature`
        *   `humidity`
        *   `wind_speed`
        *   `irradiance`
        *   `wind_power_density`
        *   `solar_energy_yield`

### Skipped/Inactive APIs:

6.  **Solcast** ❌ Skip
    *   **Status:** Not operational. Student API key has quota restrictions too low for full backfills.
    *   **Reason:** Student API key quota too low
    *   **Attempted Data:** Solar irradiance forecasts (GHI, DNI, DHI)
    *   **Database Column Mapping:**
        *   `temperature`
        *   `wind_speed`
        *   `irradiance` (as GHI, DNI, and DHI)
        *   `cloudiness`

7.  **PVOutput** ❌ Skip
    *   **Status:** Not operational. No free historical data access available.
    *   **Reason:** API requires authentication but free tier doesn't support historical data queries (returns 401 Unauthorized).
    *   **Attempted Data:** Community-sourced PV system performance data
    *   **Database Column Mapping:**
        *   `temperature`
        *   `wind_speed`
        *   `irradiance` (Solar Radiation)

8.  **NOAA Climate Data** ❌ Skip
    *   **Status:** Not operational. Consistent API timeouts and 502 errors prevent data retrieval.
    *   **Reason:** Consistent API timeouts/502 errors. Unable to fetch 2025 historical data reliably.
    *   **Attempted Data:** Climate data from the National Oceanic and Atmospheric Administration.
    *   **Database Column Mapping:**
        *   `temperature` (Max and Min)
        *   `wind_speed` (in some datasets)
        *   `precipitation` (not a direct column in your DB, but related to cloudiness/humidity)

9.  **OpenWeather** ❌ Removed
    *   **Status:** Removed from pipeline. Authorization issues with One Call API 3.0.
    *   **Reason:** One Call API 3.0 returns 401 Unauthorized on historical endpoints. Legacy implementation removed.
    *   **Note:** Previously simulated data was used, but no real API access available for production use.

#### Database Table Model
The `sensor_data` table stores web sensor data with the following 11 headers:

| Header Label | Data Type | Description | Source API |
|--------------|-----------|-------------|------------|
| Row Number | SERIAL | Auto-incrementing row identifier | Database |
| Timestamp | TIMESTAMP | Date and time of data collection | System/API |
| Temperature (°C) | DECIMAL(5,2) | Air temperature in Celsius | Open-Meteo |
| Humidity (%) | DECIMAL(5,2) | Relative humidity percentage | Open-Meteo |
| Wind Speed (m/s) | DECIMAL(5,2) | Wind speed in meters per second | Open-Meteo |
| Cloudiness (%) | DECIMAL(5,2) | Cloud cover percentage | Open-Meteo |
| UV Index | DECIMAL(3,1) | Ultraviolet index value | Open-Meteo |
| Irradiance (W/m²) | DECIMAL(7,2) | Solar irradiance in watts per square meter | NASA POWER |
| Wind Power Density (W/m²) | DECIMAL(7,2) | Wind power density | Calculated |
| Solar Energy Yield (kWh/m²/day) | DECIMAL(7,3) | Solar energy yield | Calculated |
| Source | VARCHAR(50) | Data source identifier (open_meteo/nasa_power) | System |

### Phase 10: Predictive Analytics ⏳ Pending
- Calculate averages/min/max/moving averages
- Train ML model for forecasting (scikit-learn)
- **ML Models Ranked for Wind/Solar Energy Time-Series Prediction:**
  - **Rank#1: LSTM (Long Short-Term Memory)** → Best for sequential/time-series data like wind/solar; captures long-term dependencies.
  - **Rank#2: GRU (Gated Recurrent Unit)** → Similar to LSTM but lighter and faster; efficient for limited compute.
  - **Rank#3: Random Forest Regressor** → Strong baseline for regression tasks; handles non-linearities and robust to outliers.
  - **Rank#4: XGBoost (Gradient Boosting)** → High accuracy for tabular data; requires careful hyperparameter tuning.
  - **Rank#5: ARIMA / SARIMA** → Classic statistical models for univariate forecasting with seasonality; good baseline.
  - **Rank#6: CNN (1D Convolutional Neural Network)** → Captures local temporal patterns; useful for short-term fluctuations.
  - **Rank#7: Linear Regression with Lag Features** → Simple, interpretable baseline; add lag features (t-1, t-24) and time features.
  - **Rank#8: SVR (Support Vector Regression)** → Effective for small datasets with kernel tricks; less scalable for large time-series.
  - **Rank#9: KNN Regressor** → Instance-based learning; captures local patterns but not ideal for long time-series.
  - **Rank#10: Naive Forecast (Persistence Model)** → Simplest baseline; predicts next value as last observed; useful for sanity checks.
  - Start simple: Linear Regression or Naive Forecast as baselines.
  - Progress to advanced: Random Forest/XGBoost, then LSTM/GRU for best accuracy.
  - Evaluate models using MAE/RMSE on held-out test data.
  - Note: All libraries are open-source (scikit-learn, statsmodels, TensorFlow, PyTorch, Prophet).

### Phase 11: Deployment & Scaling ⏳ Pending
- **Containerize the Application:** Use Docker to package the Flask web application, ingestion scripts, and all dependencies into a portable container.
- **Migrate to a Cloud Database:**
    - **Choose a Cloud Provider:** Select a managed PostgreSQL service (e.g., Amazon RDS, Azure Database for PostgreSQL, Google Cloud SQL, or Supabase).
    - **Use Supabase (Optional):** Supabase provides a hosted PostgreSQL database with a web UI and REST/API access. It can be used as a drop-in replacement for the local database.
    - **Export and Import:** Export the schema and data from the local PostgreSQL database and import it into the new cloud-hosted instance.
    - **Update Configuration:** Update the `.env` file with the new database credentials (host, port, user, password, database) for the cloud instance.
- **Deploy to Cloud:** Deploy the containerized application to a cloud platform like AWS, Azure, GCP, or any container hosting service that supports Docker.