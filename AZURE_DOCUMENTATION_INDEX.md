# Azure Documentation Index

## 📚 Complete Documentation for Azure Infrastructure

This index provides quick access to all Azure-related documentation.

---

## 🚀 Getting Started

### [AZURE_QUICKSTART.md](AZURE_QUICKSTART.md)
**Duration**: 15-20 minutes  
**Target**: First-time users

Contents:
- Prerequisites and installation
- Step-by-step setup guide
- Cost estimation
- Verification commands
- Troubleshooting basics

**Start here if**: You're deploying to Azure for the first time.

---

## 📖 Complete Guides

### [AZURE_README.md](AZURE_README.md)
**Duration**: 30-40 minutes  
**Target**: Developers and analysts

Contents:
- Architecture overview
- File structure explanation
- Key features and examples
- Weather data sources
- Database schema
- Security practices
- Monitoring and troubleshooting
- Best practices

**Use this for**: Understanding the complete Azure architecture.

### [AZURE_DEPLOYMENT_GUIDE.md](AZURE_DEPLOYMENT_GUIDE.md)
**Duration**: 45-60 minutes  
**Target**: DevOps and system administrators

Contents:
- Phase-by-phase deployment
- Azure resource creation (manual & CLI)
- Local environment setup
- Infrastructure initialization
- Data fetching procedures
- Report generation
- Testing verification
- Monitoring setup
- Troubleshooting guide

**Use this for**: Complete end-to-end deployment.

---

## 📋 Configuration

### [.azure.template](.azure.template)
Configuration template file containing:
- Azure Storage Account credentials
- Azure Cosmos DB credentials
- Optional API keys

**Usage**:
```bash
cp .azure.template .env.azure
# Edit .env.azure with your credentials
```

### [requirements_azure.txt](requirements_azure.txt)
Python package dependencies:
- azure-storage-blob
- azure-cosmos
- python-dotenv
- requests
- pandas, numpy
- Testing tools

**Usage**:
```bash
pip install -r requirements_azure.txt
```

---

## 💻 Core Modules

### [azure_config.py](azure_config.py)
**Purpose**: Azure credentials management

Key Classes:
- `AzureConfig` - Initialize Azure clients

Key Methods:
- `get_blob_client()` - Get Blob Storage client
- `get_cosmos_client()` - Get Cosmos DB client
- `create_blob_container()` - Create storage container
- `create_cosmos_database_and_container()` - Create database

Example:
```python
from azure_config import AzureConfig
config = AzureConfig()
blob_client = config.get_blob_client()
cosmos_client = config.get_cosmos_client()
```

### [azure_storage.py](azure_storage.py)
**Purpose**: Blob Storage operations

Key Classes:
- `AzureStorage` - Blob Storage operations

Key Methods:
- `upload_file()` - Upload single file
- `download_file()` - Download file
- `list_files()` - List stored files
- `delete_file()` - Delete file
- `upload_api_files()` - Upload API configs
- `upload_csv_files()` - Upload CSV data
- `backup_data_directory()` - Backup directory

Example:
```python
from azure_storage import AzureStorage
storage = AzureStorage()
storage.upload_file("data.csv", "csv-data/data.csv")
files = storage.list_files("csv-data/")
```

### [azure_database.py](azure_database.py)
**Purpose**: Cosmos DB database operations

Key Classes:
- `AzureDatabase` - Cosmos DB operations

Key Methods:
- `put_item()` - Store single item
- `batch_put_items()` - Store multiple items
- `get_item()` - Retrieve item by ID
- `query_by_source()` - Query by data source
- `query_by_source_date()` - Query by source and date
- `query_by_date_range()` - Query by date range
- `get_table_stats()` - Get database statistics
- `delete_item()` - Delete item

Example:
```python
from azure_database import AzureDatabase
db = AzureDatabase()
db.put_item({'source': 'nasa', 'temperature': 25})
data = db.query_by_date_range('2026-03-01', '2026-04-30')
```

### [azure_data_fetcher.py](azure_data_fetcher.py)
**Purpose**: Weather API integration

Key Classes:
- `AzureDataFetcher` - Multi-API data fetching

Key Methods:
- `fetch_nasa_data()` - Fetch from NASA POWER
- `fetch_openmeteo_data()` - Fetch from Open-Meteo
- `fetch_weatherbit_data()` - Fetch from Weatherbit
- `parse_nasa_response()` - Parse NASA response
- `parse_openmeteo_response()` - Parse OpenMeteo response
- `fetch_and_store_march_april_2026()` - Fetch March-April 2026

Example:
```python
from azure_data_fetcher import AzureDataFetcher
fetcher = AzureDataFetcher()
fetcher.fetch_and_store_march_april_2026()
```

### [setup_azure.py](setup_azure.py)
**Purpose**: Infrastructure setup orchestration

Key Classes:
- `AzureSetup` - Setup orchestration

Key Methods:
- `check_azure_credentials()` - Verify credentials
- `create_template_file()` - Create config template
- `initialize_azure_services()` - Initialize clients
- `setup_containers()` - Create storage containers
- `upload_initial_files()` - Upload initial files
- `verify_setup()` - Verify deployment
- `run_full_setup()` - Complete setup

Usage:
```bash
python setup_azure.py
python setup_azure.py --no-upload  # Skip file upload
```

### [generate_monthly_csv_azure.py](generate_monthly_csv_azure.py)
**Purpose**: CSV report generation

Key Classes:
- `AzureCSVGenerator` - CSV generation

Key Methods:
- `generate_monthly_csv()` - Generate single month CSV
- `generate_range_csv()` - Generate date range CSVs
- `generate_march_april_2026_csv()` - Generate specific months
- `generate_all_source_csv()` - Generate by source
- `generate_summary_report()` - Generate summary

Usage:
```bash
python generate_monthly_csv_azure.py
```

### [test_azure_integration.py](test_azure_integration.py)
**Purpose**: Integration testing

Key Classes:
- `AzureIntegrationTests` - Test suite

Test Cases:
1. Azure Configuration
2. Blob Storage Upload
3. Blob Storage Download
4. Cosmos DB Put Item
5. Cosmos DB Query
6. Data Fetcher NASA
7. Data Fetcher Open-Meteo
8. CSV Generation

Usage:
```bash
python test_azure_integration.py
```

---

## 🔍 Quick Reference

### Common Tasks

#### 1. Upload Files to Cloud
```python
from azure_storage import AzureStorage
storage = AzureStorage()
storage.upload_api_files()      # Upload API files
storage.upload_csv_files()      # Upload CSV files
storage.backup_data_directory() # Full backup
```

#### 2. Fetch and Store Data
```python
from azure_data_fetcher import AzureDataFetcher
fetcher = AzureDataFetcher()
fetcher.fetch_and_store_march_april_2026()
```

#### 3. Query Data
```python
from azure_database import AzureDatabase
db = AzureDatabase()
data = db.query_by_date_range('2026-03-01', '2026-04-30')
data = db.query_by_source('nasa')
```

#### 4. Generate Reports
```python
from generate_monthly_csv_azure import AzureCSVGenerator
generator = AzureCSVGenerator()
generator.generate_march_april_2026_csv()
```

#### 5. Run Complete Setup
```bash
python setup_azure.py
```

---

## 📊 Architecture Overview

```
Weather APIs
    ↓
azure_data_fetcher.py
    ↓
[Azure Cosmos DB] ← [Azure Blob Storage]
    ↓
generate_monthly_csv_azure.py
    ↓
CSV Reports
```

---

## 🔐 Security Checklist

- [ ] `.env.azure` in `.gitignore`
- [ ] No credentials in code
- [ ] Credentials stored in `.env.azure` only
- [ ] Azure credentials rotated regularly
- [ ] Access keys never committed to git
- [ ] Test with test credentials first

---

## 📈 Cost Monitoring

### Free Tier Usage
- **Blob Storage**: 5 GB / 12 months
- **Cosmos DB**: 1000 RU free per month
- **Data Transfer**: 15 GB free per month

### Typical Monthly Costs
- **Students**: $0-3/month
- **Small projects**: $5-15/month
- **Production**: $20-50/month

### Cost Reduction Tips
1. Archive old data
2. Use Blob Storage tiers
3. Monitor request patterns
4. Clean up unused resources

---

## 🆘 Troubleshooting Index

| Issue | Guide | Solution |
|-------|-------|----------|
| Connection errors | [AZURE_README.md](AZURE_README.md#-troubleshooting) | Check credentials |
| Setup fails | [AZURE_DEPLOYMENT_GUIDE.md](AZURE_DEPLOYMENT_GUIDE.md#troubleshooting) | Verify prerequisites |
| Costs high | [AZURE_README.md](AZURE_README.md#-monitoring) | Monitor usage |
| Slow queries | [AZURE_README.md](AZURE_README.md#-troubleshooting) | Add indexes |
| Auth errors | [AZURE_QUICKSTART.md](AZURE_QUICKSTART.md#⚠️-troubleshooting) | Verify keys |

---

## 📞 Support & Resources

### Official Documentation
- [Azure Storage Docs](https://learn.microsoft.com/en-us/azure/storage/)
- [Cosmos DB Docs](https://learn.microsoft.com/en-us/azure/cosmos-db/)
- [Python SDK Reference](https://github.com/Azure/azure-sdk-for-python)

### Community Help
- [Azure Support](https://support.microsoft.com/azure)
- [Stack Overflow - Azure](https://stackoverflow.com/questions/tagged/azure)
- [Microsoft Q&A](https://learn.microsoft.com/en-us/answers/topics/azure.html)

---

## 📋 Recommended Reading Order

### For Quick Start (20 minutes)
1. [AZURE_QUICKSTART.md](AZURE_QUICKSTART.md)
2. [requirements_azure.txt](requirements_azure.txt)
3. [.azure.template](.azure.template)

### For Complete Understanding (90 minutes)
1. [AZURE_QUICKSTART.md](AZURE_QUICKSTART.md)
2. [AZURE_README.md](AZURE_README.md)
3. [AZURE_DEPLOYMENT_GUIDE.md](AZURE_DEPLOYMENT_GUIDE.md)
4. Module documentation (azure_storage.py, etc.)

### For Production Deployment (2-3 hours)
1. All above documents
2. [AZURE_DEPLOYMENT_GUIDE.md](AZURE_DEPLOYMENT_GUIDE.md) - Full deployment
3. [test_azure_integration.py](test_azure_integration.py) - Run tests
4. Monitoring setup - Cost Management

---

## 🎯 Next Steps

1. **Read**: Start with [AZURE_QUICKSTART.md](AZURE_QUICKSTART.md)
2. **Setup**: Follow [AZURE_DEPLOYMENT_GUIDE.md](AZURE_DEPLOYMENT_GUIDE.md)
3. **Test**: Run `python test_azure_integration.py`
4. **Monitor**: Setup cost alerts in Azure Portal
5. **Develop**: Use modules to build applications

---

## 📝 Document Maintenance

| Document | Last Updated | Status |
|----------|--------------|--------|
| AZURE_QUICKSTART.md | 2026 | Active |
| AZURE_README.md | 2026 | Active |
| AZURE_DEPLOYMENT_GUIDE.md | 2026 | Active |
| AZURE_DOCUMENTATION_INDEX.md | 2026 | Active |
| requirements_azure.txt | 2026 | Active |
| .azure.template | 2026 | Active |

---

**Documentation Version**: 1.0.0  
**Last Updated**: 2026  
**Status**: Complete and Production Ready
