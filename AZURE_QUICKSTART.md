# Azure Quick Start Guide

## 🚀 Getting Started with Azure

This guide will help you set up the Azure infrastructure for the Energy Project.

### Prerequisites

- Python 3.8+
- Azure Account (Free tier available for students)
- git

### Step 1: Install Dependencies

```bash
pip install -r requirements_azure.txt
```

### Step 2: Create Azure Resources

#### Option A: Manual Setup (Recommended for Learning)

1. **Create Azure Storage Account**
   - Go to https://portal.azure.com
   - Click "Create a resource" → "Storage account"
   - Choose free tier (5 GB for 12 months)
   - Note your account name and access key

2. **Create Azure Cosmos DB**
   - Click "Create a resource" → "Azure Cosmos DB"
   - Select "Serverless" pricing (pay-per-request)
   - Create database: `energy-data-db`
   - Create container: `energy-data` with partition key: `/source`

#### Option B: Azure CLI (Advanced)

```bash
# Install Azure CLI
# https://learn.microsoft.com/en-us/cli/azure/install-azure-cli

# Login to Azure
az login

# Create resource group
az group create --name energy-project --location eastus

# Create storage account
az storage account create \
  --name yourstorageaccount \
  --resource-group energy-project \
  --location eastus \
  --sku Standard_LRS

# Create Cosmos DB
az cosmosdb create \
  --name your-cosmos-account \
  --resource-group energy-project \
  --kind GlobalDocumentDB
```

### Step 3: Configure Credentials

1. Copy the template:
   ```bash
   cp .azure.template .env.azure
   ```

2. Edit `.env.azure` with your Azure credentials:
   ```
   AZURE_STORAGE_ACCOUNT=your_account_name
   AZURE_STORAGE_KEY=your_access_key
   AZURE_COSMOS_ENDPOINT=https://your_account.documents.azure.com:443/
   AZURE_COSMOS_KEY=your_primary_key
   ```

### Step 4: Run Setup

```bash
python setup_azure.py
```

This will:
- ✓ Verify Azure credentials
- ✓ Create blob storage containers
- ✓ Initialize Cosmos DB database
- ✓ Upload initial files

### Step 5: Fetch Data

```bash
python -c "from azure_data_fetcher import AzureDataFetcher; AzureDataFetcher().fetch_and_store_march_april_2026()"
```

### Step 6: Generate Reports

```bash
python generate_monthly_csv_azure.py
```

## 📊 Cost Estimation

| Service | Free Tier | Additional Cost |
|---------|-----------|-----------------|
| Blob Storage | 5 GB (12 months) | $0.018/GB after |
| Cosmos DB | 25 GB storage | $0.25 per million requests |
| **Total (Student)** | **FREE** | **$0-3/month** |

## 🔍 Verify Setup

```bash
# List uploaded files
python -c "from azure_storage import AzureStorage; s = AzureStorage(); print('Files:', len(s.list_files()))"

# Check database stats
python -c "from azure_database import AzureDatabase; d = AzureDatabase(); print(d.get_table_stats())"

# Run integration tests
python test_azure_integration.py
```

## 🗂️ Project Structure

```
├── azure_config.py           # Azure credentials & initialization
├── azure_storage.py          # Blob Storage operations
├── azure_database.py         # Cosmos DB operations
├── azure_data_fetcher.py     # Weather API integration
├── setup_azure.py            # Infrastructure setup
├── generate_monthly_csv_azure.py  # CSV report generation
├── test_azure_integration.py # Test suite
├── .azure.template          # Configuration template
├── requirements_azure.txt    # Python dependencies
└── data/                     # Data directory
    ├── *.csv                 # Weather data (CSV)
    └── *-api.txt             # API configuration files
```

## 📚 Available Functions

### Storage Operations
```python
from azure_storage import AzureStorage

storage = AzureStorage()
storage.upload_file("local_file.txt", "blob_name")
storage.download_file("blob_name", "local_file.txt")
storage.list_files("prefix/")
```

### Database Operations
```python
from azure_database import AzureDatabase

db = AzureDatabase()
db.put_item({'source': 'nasa', 'temperature': 25})
results = db.query_by_date_range('2026-03-01', '2026-04-30')
stats = db.get_table_stats()
```

### Data Fetching
```python
from azure_data_fetcher import AzureDataFetcher

fetcher = AzureDataFetcher()
fetcher.fetch_and_store_march_april_2026()
```

## ⚠️ Troubleshooting

### Connection Error
```
"Failed to initialize clients"
```
**Solution**: Check `.env.azure` file exists and contains correct credentials.

### Authentication Error
```
"InvalidAuthorizationHeader"
```
**Solution**: Verify Azure Storage Key or Cosmos DB Primary Key.

### Import Error
```
"No module named 'azure'"
```
**Solution**: Run `pip install -r requirements_azure.txt`

## 📖 Additional Resources

- [Azure Storage Documentation](https://learn.microsoft.com/en-us/azure/storage/)
- [Cosmos DB Documentation](https://learn.microsoft.com/en-us/azure/cosmos-db/)
- [Azure Free Tier](https://azure.microsoft.com/free/)
- [Python SDK Examples](https://github.com/Azure/azure-sdk-for-python)

## ✅ Next Steps

1. ✓ Configure Azure credentials
2. ✓ Run setup_azure.py
3. ✓ Fetch March-April 2026 data
4. ✓ Generate monthly CSV reports
5. ✓ Run integration tests

Happy coding! 🎉
