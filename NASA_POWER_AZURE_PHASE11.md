# NASA POWER Azure Integration - Phase 11 Implementation Summary

## Overview
Complete end-to-end implementation for NASA POWER API data ingestion, local file management, and Azure Blob Storage synchronization.

---

## Components Implemented

### 1. **fetch_nasa_power_update.py** (Enhanced)
**Purpose:** Fetch real NASA POWER API data and update local files

**Key Features:**
- ✅ Retry logic (up to 3 attempts with 2s delays)
- ✅ 5-second timeout for API requests (allows online data detection)
- ✅ Comprehensive error handling with logging
- ✅ Duplicate row detection and skipping
- ✅ Atomic file operations (temp file → rename pattern)
- ✅ Timestamp-based sorting (ascending order)
- ✅ Monthly CSV file creation and updates
- ✅ Metadata tracking (last updated, summary with row count)

**Data Flow:**
```
NASA POWER API → Fetch (with retries) → Parse → Sort → Write local files
                                           ↓
                                    Monthly CSVs
```

**Logging:**
- File: `logs/nasa_power_fetch.log`
- Console output during execution
- Detailed error messages and retry attempts

**API Parameters:**
- Location: Manila, PH (14.5995°N, 120.9842°E)
- Parameters: T2M (temperature), RH2M (humidity), ALLSKY_SFC_SW_DWN (irradiance), WS2M (wind speed)
- End Date: Yesterday (avoids incomplete current day data)
- Timeout: 5 seconds

---

### 2. **nasa_power_azure_sync_enhanced.py** (New)
**Purpose:** Sync NASA POWER data to Azure Blob Storage with verification

**Key Features:**
- ✅ Connection verification to Azure
- ✅ Upload with progress tracking and file size reporting
- ✅ Timestamp extraction from both local and Azure files
- ✅ Detailed comparison with 6 possible states:
  - `SYNCHRONIZED` - Local and Azure timestamps match
  - `LOCAL_AHEAD` - Local has newer data (needs upload)
  - `AZURE_AHEAD` - Azure has newer data (local behind)
  - `AZURE_MISSING` - Initial upload needed
  - `LOCAL_MISSING` - Local file not found
  - `BOTH_MISSING` - Both missing (error state)
- ✅ Atomic upload operations
- ✅ CSV file batch processing
- ✅ Comprehensive logging and error reporting

**Sync Process:**
```
Local Files → Verify → Upload to Azure → Compare Timestamps
   ↓              ↓          ↓                    ↓
nasa-api.txt  Size/valid   Blob Storage    Status Report
Monthly CSVs
```

**Logging:**
- File: `logs/azure_sync.log`
- Console output with progress
- Detailed upload/download results

**Return Format:**
```json
{
  "timestamp": "2026-05-27T...",
  "main_file": {"success": true, "file": "nasa-api.txt", "blob_name": "nasa-api.txt", ...},
  "csv_files": [{...}, {...}],
  "timestamp_comparison": {
    "local": {"success": true, "timestamp": "2026-03-12 19:14:46", "row_count": 10177},
    "azure": {"success": true, "timestamp": "2026-03-12 19:14:46", "row_count": 10177},
    "comparison": "SYNCHRONIZED"
  },
  "total_uploaded": 15,
  "total_failed": 0
}
```

---

### 3. **nasa_api_server.py** (Enhanced Backend)
**Purpose:** Flask backend orchestrating fetch and sync workflow

**Endpoints:**

1. **POST `/run-fetch-nasa-power`**
   - Triggers fetch script
   - Automatically syncs to Azure
   - Returns combined status
   - Timeout: 180 seconds
   - Logging: `logs/nasa_api_server.log`

2. **GET `/nasa-api-compare-timestamps`**
   - Returns timestamp comparison
   - Local vs Azure status
   - Recommended action

3. **GET `/nasa-api-sync-status`** (New)
   - Returns current sync status
   - Local and Azure timestamps
   - Row counts and metadata

**Features:**
- ✅ CORS enabled for cross-origin requests
- ✅ Graceful error handling
- ✅ Comprehensive logging
- ✅ Timeout protection
- ✅ Azure availability check (fallback if SDK missing)

**Workflow:**
```
Browser Request (GUI)
    ↓
Flask Backend (/run-fetch-nasa-power)
    ↓
Step 1: Run fetch_nasa_power_update.py
    ↓
Step 2: Verify fetch success
    ↓
Step 3: Sync to Azure (if available)
    ↓
Step 4: Compare timestamps
    ↓
Return status to GUI
```

---

### 4. **test_nasa_power_e2e.py** (New Test Suite)
**Purpose:** Comprehensive end-to-end testing

**Test Coverage:**

1. **TEST 1: Fetch Data**
   - Runs fetch script
   - Validates return code
   - Checks output messages

2. **TEST 2: Local File Validation**
   - Checks file existence
   - Validates row count and format
   - Verifies metadata (last updated, summary)
   - First/last row inspection

3. **TEST 3: Azure Sync**
   - Tests Azure connection
   - Verifies uploads
   - Checks failure handling

4. **TEST 4: Timestamp Comparison**
   - Local vs Azure timestamps
   - Sync status validation
   - Action recommendations

5. **TEST 5: CSV File Validation**
   - Counts monthly CSV files
   - Validates row formats
   - Checks file integrity

**Run Test:**
```bash
python test_nasa_power_e2e.py
```

**Output:**
- Detailed test results with PASS/FAIL/WARN status
- Summary report with test counts
- Logging to console and file

---

## Configuration Files

### `.env.azure` (Required)
```ini
AZURE_STORAGE_ACCOUNT=your_account_name
AZURE_STORAGE_KEY=your_account_key
AZURE_BLOB_CONTAINER=ai-energy-r6-data
```

### Log Files Created
- `logs/nasa_power_fetch.log` - Fetch operations
- `logs/azure_sync.log` - Azure sync operations
- `logs/nasa_api_server.log` - Backend operations

---

## Data File Structure

### Local Files
```
data/
├── nasa-api.txt                          (Main log file)
├── nasa_2026_03_march.csv
├── nasa_2026_02_february.csv
└── ...other monthly CSVs
```

### Azure Blob Storage
```
ai-energy-r6-data/
├── nasa-api.txt
├── nasa_2026_03_march.csv
├── nasa_2026_02_february.csv
└── ...other monthly CSVs
```

---

## File Format Details

### nasa-api.txt Structure
```
# Data collection last updated: 2026-03-12 19:14:46
# Summary: nasa_power=10177
[nasa_power]
id,timestamp,temperature,humidity,irradiance,wind_speed,source,wind_power_density,solar_energy_yield
1,2026-03-01 06:30:00,28.46,80.0,6.073,3.6,nasa_power,28.58,2.56
2,2026-03-01 07:00:00,28.50,79.5,7.125,3.7,nasa_power,29.45,2.75
...
```

### Monthly CSV Format
```
id,timestamp,temperature,humidity,irradiance,wind_speed,source,wind_power_density,solar_energy_yield
1,2026-03-01 06:30:00,28.46,80.0,6.073,3.6,nasa_power,28.58,2.56
2,2026-03-01 07:00:00,28.50,79.5,7.125,3.7,nasa_power,29.45,2.75
...
```

---

## Error Handling & Retry Logic

### API Fetch Retry Strategy
- **Initial Attempt:** Direct fetch
- **Retry 1-2:** Wait 2 seconds, retry
- **Fallback:** Use previous row values if all retries fail
- **Timeout:** 5 seconds per request

### File Operations
- **Atomic writes:** Temp file → Rename pattern
- **Duplicate detection:** Skip by ID
- **Validation:** Row format checking before insertion

### Azure Sync Errors
- **Connection failed:** Return error to Flask
- **Upload failed:** Mark in results, continue with other files
- **Timestamp mismatch:** Log comparison result
- **Graceful degradation:** Sync failure doesn't block fetch

---

## Performance Characteristics

| Operation | Timeout | Expected Duration |
|-----------|---------|-------------------|
| API Fetch | 180s | 10-30s (varies by API response) |
| Local Write | N/A | <1s |
| Azure Upload | N/A | 1-5s (depends on file size) |
| Timestamp Compare | N/A | <1s |
| Full Sync | 180s | 15-40s |

### Data Volumes
- Main file: ~10,177 rows × ~200 bytes = ~2 MB
- Monthly CSVs: ~15 files × ~700 KB avg = ~10.5 MB
- Total data: ~12.5 MB

---

## Deployment Checklist

- [ ] Set `AZURE_STORAGE_ACCOUNT` in `.env.azure`
- [ ] Set `AZURE_STORAGE_KEY` in `.env.azure`
- [ ] Create `logs/` directory (auto-created)
- [ ] Create Azure Blob container: `ai-energy-r6-data`
- [ ] Install packages: `pip install Flask flask_cors azure-storage-blob python-dotenv requests`
- [ ] Test connection: `python nasa_power_azure_sync_enhanced.py`
- [ ] Run E2E test: `python test_nasa_power_e2e.py`
- [ ] Start Flask: `python nasa_api_server.py`
- [ ] Test via GUI: Click "FETCH DATA (NASA)"

---

## Integration with GUI

### Section 1: Data Acquisition Control
Button: **"FETCH DATA (NASA)"**
- Calls Flask endpoint: `/run-fetch-nasa-power`
- Displays success/error message
- Shows row count and timestamps

### Future: Sync Status Panel
- Display local timestamp
- Display Azure timestamp
- Show sync comparison status
- Indicate next update time

---

## Monitoring & Maintenance

### Daily Checks
- Review `logs/nasa_power_fetch.log` for errors
- Check `logs/azure_sync.log` for upload issues
- Verify timestamp comparison status
- Monitor disk space for monthly CSVs

### Weekly Tasks
- Verify Azure upload success rate
- Check for any API rate limiting issues
- Monitor log file sizes (rotate if needed)

### Monthly Tasks
- Validate total row count growth
- Check for gaps in timestamps
- Review error patterns in logs

---

## Future Enhancements

1. **Scheduled Fetching:** Implement cron/scheduler for daily automatic fetch
2. **Data Download:** Reverse sync to download from Azure if local corrupted
3. **Data Versioning:** Keep multiple versions in Azure
4. **Compression:** Gzip CSVs before upload to reduce storage
5. **Multi-API:** Extend pattern to Meteostat, Open-Meteo, WeatherBit
6. **Dashboard:** Add monitoring UI showing sync status
7. **Alerts:** Email/Slack notifications on sync failures
8. **Backup:** Automatic weekly backup to secondary Azure account

---

## Troubleshooting

### Issue: "No new data to fetch"
**Cause:** Local file already has data up to yesterday
**Solution:** Delete last 24 hours of data rows to test fetch

### Issue: "Failed to connect to Azure"
**Cause:** Missing or incorrect credentials in `.env.azure`
**Solution:** Verify AZURE_STORAGE_ACCOUNT and AZURE_STORAGE_KEY

### Issue: "Timeout" on API fetch
**Cause:** NASA POWER API slow or overloaded
**Solution:** Automatic retry logic will retry 2 more times

### Issue: "File not found: data/nasa-api.txt"
**Cause:** Initial setup before any data fetched
**Solution:** Run initial backfill script first

---

## Document Version
- **Version:** 1.0
- **Date:** May 27, 2026
- **Status:** Phase 11 - Deployment & Scaling (Ongoing)
- **Focus:** NASA POWER API to Azure Blob Storage
