# Azure Deployment Guide

## 🎯 Complete Deployment Instructions

This guide walks through deploying the Energy Project to Azure cloud infrastructure.

## 📋 Pre-Deployment Checklist

- [ ] Azure Account created (free tier)
- [ ] Python 3.8+ installed
- [ ] Git installed
- [ ] Terminal/Command line access
- [ ] Required permissions in Azure (Contributor role)

## Phase 1: Azure Account Setup

### Step 1.1: Create Azure Account

1. Go to [Azure Free Trial](https://azure.microsoft.com/free/)
2. Click "Start free"
3. Sign in with Microsoft account (or create new)
4. Complete verification (phone + credit card)
5. Accept agreement and click "Sign up"

**Benefits:**
- $200 credit for 30 days
- Free services for 12 months
- No auto-renewal after free trial

### Step 1.2: Access Azure Portal

1. Go to [portal.azure.com](https://portal.azure.com)
2. Sign in with your Azure account
3. Select "Subscriptions" to verify account

## Phase 2: Create Azure Resources

### Option A: Manual Creation (Recommended)

#### A1: Create Storage Account

1. Click "Create a resource"
2. Search for "Storage account"
3. Click "Create"
4. Fill in details:
   - **Subscription**: Your subscription
   - **Resource group**: Create new → "energy-project"
   - **Storage account name**: `yourname<unique>`
   - **Region**: East US
   - **Performance**: Standard
   - **Redundancy**: Locally-redundant storage (LRS)
5. Click "Review + Create"
6. Click "Create"

**Copy credentials:**
1. Go to created Storage account
2. Select "Access keys"
3. Copy:
   - Storage account name
   - Key (key1)

#### A2: Create Cosmos DB

1. Click "Create a resource"
2. Search for "Azure Cosmos DB"
3. Click "Create"
4. Select "Serverless" option
5. Fill in details:
   - **Subscription**: Your subscription
   - **Resource group**: "energy-project"
   - **Account name**: `yourname-cosmos`
   - **Location**: East US
   - **API**: Core (SQL)
   - **Capacity mode**: Serverless
6. Click "Review + Create"
7. Click "Create"

**Copy credentials:**
1. Go to created Cosmos DB account
2. Select "Connection String"
3. Copy:
   - Connection string (full)
   - Primary key

### Option B: Azure CLI Deployment (Advanced)

```bash
# Install Azure CLI
# https://learn.microsoft.com/cli/azure/install-azure-cli

# Login
az login

# Create resource group
az group create \
  --name energy-project \
  --location eastus

# Create storage account
STORAGE_ACCOUNT="yourstorageaccount"
az storage account create \
  --name $STORAGE_ACCOUNT \
  --resource-group energy-project \
  --location eastus \
  --sku Standard_LRS \
  --kind StorageV2

# Get storage key
STORAGE_KEY=$(az storage account keys list \
  --resource-group energy-project \
  --account-name $STORAGE_ACCOUNT \
  --query '[0].value' -o tsv)

# Create Cosmos DB
COSMOS_ACCOUNT="youraccount-cosmos"
az cosmosdb create \
  --name $COSMOS_ACCOUNT \
  --resource-group energy-project \
  --kind GlobalDocumentDB

# Get Cosmos endpoint and key
COSMOS_ENDPOINT=$(az cosmosdb show \
  --name $COSMOS_ACCOUNT \
  --resource-group energy-project \
  --query documentEndpoint -o tsv)

COSMOS_KEY=$(az cosmosdb keys list \
  --name $COSMOS_ACCOUNT \
  --resource-group energy-project \
  --query primaryMasterKey -o tsv)

echo "Storage Account: $STORAGE_ACCOUNT"
echo "Storage Key: $STORAGE_KEY"
echo "Cosmos Endpoint: $COSMOS_ENDPOINT"
echo "Cosmos Key: $COSMOS_KEY"
```

## Phase 3: Local Setup

### Step 3.1: Install Dependencies

```bash
# Clone repository (if not already done)
git clone <repository-url>
cd AI-EnergyR6

# Install Python packages
pip install -r requirements_azure.txt
```

### Step 3.2: Configure Credentials

```bash
# Copy template
cp .azure.template .env.azure

# Edit with your credentials
nano .env.azure  # macOS/Linux
# OR
notepad .env.azure  # Windows
```

**Fill in the following:**
```
AZURE_STORAGE_ACCOUNT=yourname<unique>
AZURE_STORAGE_KEY=<your-storage-key>
AZURE_STORAGE_CONTAINER=energy-data

AZURE_COSMOS_ENDPOINT=https://yourname-cosmos.documents.azure.com:443/
AZURE_COSMOS_KEY=<your-cosmos-primary-key>
AZURE_COSMOS_DATABASE=energy-data-db
AZURE_COSMOS_CONTAINER=energy-data
```

**⚠️ Security**: Never commit `.env.azure`. Add to `.gitignore`.

## Phase 4: Infrastructure Initialization

### Step 4.1: Run Setup Script

```bash
python setup_azure.py
```

**This will:**
- ✓ Validate Azure credentials
- ✓ Create blob containers (api-files, csv-data, backup)
- ✓ Create Cosmos DB database and container
- ✓ Upload API configuration files
- ✓ Upload existing CSV files

**Expected output:**
```
============================================================
AZURE SETUP ORCHESTRATION
============================================================

[STEP 1/5] Creating template file...
✓ Created template

[STEP 2/5] Checking Azure credentials...
✓ All Azure credentials configured

[STEP 3/5] Initializing Azure services...
✓ Azure Configuration initialized
✓ Azure Blob Storage initialized
✓ Azure Cosmos DB initialized

[STEP 4/5] Setting up containers...
✓ Blob Storage containers configured

[STEP 5/5] Uploading initial files...
✓ Uploaded 47 API files
✓ Uploaded 365 CSV files

✓ Azure setup verified successfully
✓ Azure setup complete
```

### Step 4.2: Verify Setup

```bash
# Check storage
python -c "from azure_storage import AzureStorage; s = AzureStorage(); files = s.list_files(); print(f'✓ Files in storage: {len(files)}')"

# Check database
python -c "from azure_database import AzureDatabase; d = AzureDatabase(); stats = d.get_table_stats(); print(f'✓ Database stats: {stats}')"
```

## Phase 5: Data Fetching

### Step 5.1: Fetch March-April 2026 Data

```bash
# Run data fetcher
python -c "
from azure_data_fetcher import AzureDataFetcher
fetcher = AzureDataFetcher()
result = fetcher.fetch_and_store_march_april_2026()
print('✓ Data fetch complete')
print(f'  NASA items: {result[\"nasa\"]}')
print(f'  OpenMeteo items: {result[\"openmeteo\"]}')
"
```

**Expected:**
- NASA POWER API: 59 days × ~4 records = ~236 items
- Open-Meteo API: 61 days × 24 hours = ~1,464 items
- Total: ~1,700 items in Cosmos DB

## Phase 6: Report Generation

### Step 6.1: Generate CSV Reports

```bash
# Generate March-April 2026 CSVs
python generate_monthly_csv_azure.py
```

**Output files:**
- `data/weather_2026_03_march.csv`
- `data/weather_2026_04_april.csv`

### Step 6.2: Upload Reports to Blob Storage

```bash
python -c "
from azure_storage import AzureStorage
storage = AzureStorage()
storage.upload_csv_files('data/', 'csv-data')
print('✓ CSV files uploaded to Blob Storage')
"
```

## Phase 7: Testing

### Step 7.1: Run Integration Tests

```bash
python test_azure_integration.py
```

**Expected output:**
```
============================================================
AZURE INTEGRATION TEST SUITE
============================================================

[TEST 1/8] Azure Configuration
✓ Azure clients initialized successfully

[TEST 2/8] Blob Storage Upload
✓ File uploaded successfully

[TEST 3/8] Blob Storage Download
✓ Found test files

[TEST 4/8] Cosmos DB Put Item
✓ Item stored successfully

[TEST 5/8] Cosmos DB Query
✓ Query returned items

[TEST 6/8] Data Fetcher NASA
✓ NASA POWER API connection successful

[TEST 7/8] Data Fetcher Open-Meteo
✓ Open-Meteo API connection successful

[TEST 8/8] CSV Generation
✓ CSV generation successful

============================================================
Tests Passed: 8/8
============================================================
✓ ALL TESTS PASSED
```

## Phase 8: Monitoring & Maintenance

### Step 8.1: Monitor Costs

1. Go to Azure Portal
2. Search for "Cost Management + Billing"
3. Select "Cost analysis"
4. View usage by service

### Step 8.2: Set Budget Alerts

1. In Cost Management, select "Budgets"
2. Click "Create"
3. Set budget: $5 (monthly)
4. Set alert threshold: 80%

### Step 8.3: Backup Data

```bash
# Backup data directory
python -c "
from azure_storage import AzureStorage
storage = AzureStorage()
count = storage.backup_data_directory('data/', 'backup')
print(f'✓ Backed up {count} files')
"
```

## Troubleshooting

### Issue: "Failed to initialize clients"

**Cause**: Azure credentials not found  
**Solution**:
```bash
# Verify .env.azure exists and has credentials
cat .env.azure

# Verify format (no extra spaces)
AZURE_STORAGE_ACCOUNT=correct_format
```

### Issue: "Connection timeout"

**Cause**: Network/firewall issue  
**Solution**:
```bash
# Test connectivity
python -c "import azure_storage; print('✓ Connected')"

# Check internet connection
ping 1.1.1.1
```

### Issue: "InvalidAuthorizationHeader"

**Cause**: Incorrect credentials  
**Solution**:
```bash
# Copy correct keys from Azure Portal
# Storage Account → Access Keys
# Cosmos DB → Connection String
```

### Issue: "Quota exceeded"

**Cause**: Using free tier limits  
**Solution**:
1. Upgrade to paid subscription
2. Or delete old data
3. Or contact Azure support

## Deployment Verification Checklist

- [ ] Azure account created
- [ ] Storage account created and accessible
- [ ] Cosmos DB created and accessible
- [ ] `.env.azure` configured with credentials
- [ ] `setup_azure.py` executed successfully
- [ ] Initial files uploaded to Blob Storage
- [ ] March-April 2026 data fetched
- [ ] CSV reports generated
- [ ] Integration tests passed (8/8)
- [ ] Budget alerts configured
- [ ] Backup created

## 🎉 Deployment Complete!

Your Azure infrastructure is now ready. You can:

1. **Fetch additional data**
   ```bash
   python -c "from azure_data_fetcher import AzureDataFetcher; AzureDataFetcher().fetch_nasa_data(40.7128, -74.0060, '20260301', '20260430')"
   ```

2. **Query data**
   ```bash
   python -c "from azure_database import AzureDatabase; db = AzureDatabase(); print(db.query_by_source('nasa'))"
   ```

3. **Upload new files**
   ```bash
   python -c "from azure_storage import AzureStorage; AzureStorage().upload_file('your_file.csv')"
   ```

## 📞 Support Resources

- [Azure Support](https://support.microsoft.com/azure)
- [Azure Documentation](https://learn.microsoft.com/azure/)
- [Stack Overflow - Azure Tag](https://stackoverflow.com/questions/tagged/azure)
- [Azure SDK Python Issues](https://github.com/Azure/azure-sdk-for-python/issues)

---

**Deployment Date**: [Date]  
**Last Updated**: 2026  
**Status**: Ready for Production
