# Azure Infrastructure Guide

## 📋 Overview

This project uses Azure cloud services to store, manage, and query weather data for energy analysis.

**Services Used:**
- **Azure Blob Storage** - File storage for API files and CSV data
- **Azure Cosmos DB (Serverless)** - NoSQL database for weather records

**Cost**: FREE for students + minimal usage charges (~$0-3/month)

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    WEATHER DATA APIs                        │
│  ┌────────────┐  ┌─────────────┐  ┌──────────────┐         │
│  │ NASA       │  │ Open-Meteo  │  │ Weatherbit   │         │
│  │ POWER      │  │ (Free)      │  │ (Optional)   │         │
│  └──────┬─────┘  └──────┬──────┘  └──────┬───────┘         │
│         │                │               │                   │
│         └────────────────┼───────────────┘                   │
│                          │                                    │
│                   ┌──────▼─────────┐                         │
│                   │  azure_data_   │                         │
│                   │   fetcher.py   │                         │
│                   └──────┬─────────┘                         │
│              ┌────────────┴────────────┐                     │
│              │                         │                     │
│         ┌────▼──────────┐   ┌────────▼──────────┐           │
│         │ Azure Blob    │   │ Azure Cosmos DB  │           │
│         │ Storage       │   │ (Serverless)     │           │
│         │               │   │                  │            │
│         │ Containers:   │   │ Database: energy-│            │
│         │ • api-files   │   │ data-db          │            │
│         │ • csv-data    │   │ Container: energy│            │
│         │ • backup      │   │ -data            │            │
│         └────┬──────────┘   └────────┬─────────┘            │
│              │                       │                       │
│              └───────────┬───────────┘                       │
│                          │                                    │
│                 ┌────────▼────────┐                         │
│                 │ CSV Reports &   │                         │
│                 │ Analytics       │                         │
│                 └─────────────────┘                         │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## 📁 File Structure

### Core Modules

| Module | Purpose |
|--------|---------|
| `azure_config.py` | Azure credentials & client initialization |
| `azure_storage.py` | Blob Storage upload/download/list operations |
| `azure_database.py` | Cosmos DB CRUD and query operations |
| `azure_data_fetcher.py` | Weather API integration & data fetching |
| `setup_azure.py` | Infrastructure setup orchestration |
| `generate_monthly_csv_azure.py` | CSV report generation from database |
| `test_azure_integration.py` | Integration test suite |

### Configuration Files

| File | Purpose |
|------|---------|
| `.env.azure` | Azure credentials (keep secret!) |
| `.azure.template` | Configuration template |
| `requirements_azure.txt` | Python dependencies |

### Data Directory

```
data/
├── *.csv                  # Monthly weather data (CSV)
├── *-api.txt              # API configuration files
└── backup/                # Backup of uploaded files
```

## 🔑 Key Features

### 1. Azure Blob Storage
```python
storage = AzureStorage()

# Upload file
storage.upload_file("local_file.csv", "csv-data/file.csv")

# Download file
storage.download_file("csv-data/file.csv", "local_file.csv")

# List files
files = storage.list_files("csv-data/")

# Backup entire directory
storage.backup_data_directory("data/", "backup/")
```

### 2. Azure Cosmos DB
```python
db = AzureDatabase()

# Store single item
db.put_item({
    'source': 'nasa',
    'timestamp': '2026-03-15T12:00:00Z',
    'temperature': 25.5,
    'humidity': 65.0
})

# Query by date range
data = db.query_by_date_range('2026-03-01', '2026-04-30')

# Query by source
data = db.query_by_source('openmeteo', limit=1000)

# Get statistics
stats = db.get_table_stats()
```

### 3. Data Fetching
```python
fetcher = AzureDataFetcher()

# Fetch March-April 2026 data
fetcher.fetch_and_store_march_april_2026(
    latitude=40.7128,    # NYC latitude
    longitude=-74.0060   # NYC longitude
)

# Results stored directly in Cosmos DB
```

### 4. CSV Generation
```python
from generate_monthly_csv_azure import AzureCSVGenerator

generator = AzureCSVGenerator()

# Generate specific month
generator.generate_monthly_csv(2026, 3)

# Generate date range
generator.generate_range_csv(2026, 3, 2026, 4)

# Generate by source
generator.generate_all_source_csv(2026, 3)
```

## 🌐 Weather Data Sources

### NASA POWER API
- **Free**: Yes
- **Authentication**: No API key required
- **Coverage**: Global, hourly data
- **Parameters**: Temperature, Humidity, Pressure, Wind Speed
- **Endpoint**: https://power.larc.nasa.gov/api/v1/aggregate

### Open-Meteo API
- **Free**: Yes
- **Authentication**: No API key required
- **Coverage**: Global, hourly data
- **Parameters**: Temperature, Humidity, Pressure, Wind Speed
- **Endpoint**: https://archive-api.open-meteo.com/v1/archive

### Weatherbit API (Optional)
- **Free**: Limited (requires API key)
- **Authentication**: Yes (API key)
- **Coverage**: Global
- **Parameters**: Daily weather data
- **Endpoint**: https://api.weatherbit.io/v2.0/history/daily

### Meteostat Library (Optional)
- **Free**: Yes
- **Authentication**: No API key required
- **Coverage**: Global weather stations
- **Parameters**: Temperature, Humidity, Wind Speed, Pressure

## 💾 Database Schema

### Cosmos DB Container: `energy-data`

```json
{
    "id": "unique-identifier",
    "source": "nasa|openmeteo|weatherbit|meteostat",
    "timestamp": "2026-03-15T12:00:00Z",
    "temperature": 25.5,
    "humidity": 65.0,
    "pressure": 1013.25,
    "wind_speed": 5.2,
    "source_date": "2026-03-01 to 2026-04-30"
}
```

**Partition Key**: `/source`  
**TTL**: None (unlimited retention)

## 🔒 Security

### Credentials Management

1. **Never commit `.env.azure`** - Add to `.gitignore`
2. **Use `.azure.template`** - Share template, not secrets
3. **Rotate keys regularly** - Azure Portal → Access Keys
4. **Environment-based configuration** - Load from `.env.azure`

```python
import os
from dotenv import load_dotenv

load_dotenv('.env.azure')
storage_key = os.getenv('AZURE_STORAGE_KEY')
```

## 📊 Pricing

### Storage
- **5 GB free** (12 months)
- **$0.018/GB** after free tier
- **Typical usage**: 100-300 MB/year

### Cosmos DB
- **25 GB storage** free
- **$0.25 per million requests** (after free tier)
- **Typical usage**: $0-3/month

### Total Cost
- **Student**: FREE (within free tier)
- **Production**: $5-10/month

## 🚀 Deployment

### Local Development
```bash
# Setup
python setup_azure.py

# Run tests
python test_azure_integration.py

# Fetch data
python -c "from azure_data_fetcher import AzureDataFetcher; AzureDataFetcher().fetch_and_store_march_april_2026()"

# Generate reports
python generate_monthly_csv_azure.py
```

### Production Considerations
- Store credentials in Azure Key Vault
- Use Managed Identities for authentication
- Enable blob versioning for backups
- Monitor costs in Azure Cost Management

## 📈 Monitoring

### Check Storage Usage
```bash
az storage account show-usage \
  --name your_storage_account \
  --resource-group your_resource_group
```

### Check Cosmos DB Usage
```bash
az cosmosdb database show \
  --name your_cosmos_account \
  --resource-group your_resource_group \
  --db-name energy-data-db
```

### Query Database Statistics
```python
db = AzureDatabase()
stats = db.get_table_stats()
print(f"Total items: {stats['total_items']}")
print(f"Sources: {stats['sources']}")
print(f"Date range: {stats['min_date']} to {stats['max_date']}")
```

## 🐛 Troubleshooting

### Connection Issues
```python
# Test connection
from azure_config import AzureConfig
config = AzureConfig()
print("✓ Connected to Azure")
```

### Query Performance
- Cosmos DB: Add indexes for frequently queried fields
- Blob Storage: Use containers for logical organization
- Consider partition strategy for large datasets

### Cost Overruns
- Monitor in Azure Cost Management
- Set budgets and alerts
- Archive old data to Archive tier

## 📚 Resources

- [Azure Storage Documentation](https://learn.microsoft.com/en-us/azure/storage/)
- [Cosmos DB SQL Query Reference](https://learn.microsoft.com/en-us/azure/cosmos-db/sql-query/)
- [Python SDK Examples](https://github.com/Azure/azure-sdk-for-python)
- [Azure Free Tier Details](https://azure.microsoft.com/free/)

## ✨ Best Practices

1. **Backup regularly** - Use Blob Storage backup container
2. **Monitor costs** - Check Azure Cost Management weekly
3. **Archive old data** - Move historical data to Archive tier
4. **Optimize queries** - Use partition keys efficiently
5. **Test before production** - Use test_azure_integration.py
6. **Document changes** - Update this README as needed

---

**Last Updated**: 2026  
**Version**: 1.0.0  
**Status**: Production Ready
