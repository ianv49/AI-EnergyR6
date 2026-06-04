#!/usr/bin/env python3
"""
Quick Start Guide for NASA POWER Azure Integration

This guide explains how to set up and use Azure Blob Storage with your NASA POWER data pipeline.
"""

print("""
╔════════════════════════════════════════════════════════════════════════════╗
║          NASA POWER - AZURE BLOB STORAGE INTEGRATION GUIDE                 ║
╚════════════════════════════════════════════════════════════════════════════╝

📋 SETUP INSTRUCTIONS:

1. CREATE AZURE STORAGE ACCOUNT (Free Tier):
   - Go to: https://portal.azure.com
   - Create Storage Account (free tier: 5 GB blob storage)
   - Note: storage_account_name, account_key

2. CREATE BLOB CONTAINER:
   - In Azure Portal → Storage Account → Containers
   - Create container named: ai-energy-r6-data

3. CONFIGURE CREDENTIALS:
   - Copy .env.azure.template to .env.azure
   - Fill in your Azure credentials:
     AZURE_STORAGE_ACCOUNT=your_storage_account_name
     AZURE_STORAGE_KEY=your_storage_account_key
     AZURE_BLOB_CONTAINER=ai-energy-r6-data

4. INSTALL AZURE SDK:
   pip install azure-storage-blob python-dotenv

═════════════════════════════════════════════════════════════════════════════

🔄 HOW IT WORKS:

1. FETCH NASA DATA (Manual or scheduled):
   - Click "FETCH DATA (NASA)" in GUI.html
   - Backend runs fetch_nasa_power_update.py
   - Downloads data from NASA POWER API

2. SYNC TO AZURE (Automatic after fetch):
   - nasa_api_server.py calls NasaPowerAzureSync
   - Uploads nasa-api.txt to Azure
   - Uploads all monthly NASA CSVs to Azure
   - Compares timestamps between local and Azure

3. CHECK SYNCHRONIZATION STATUS:
   - Endpoint: GET /nasa-api-compare-timestamps
   - Returns:
     {
       "local_timestamp": "2026-03-12 19:14:46",
       "azure_timestamp": "2026-03-12 19:14:46",
       "comparison": "SYNCHRONIZED"
     }

═════════════════════════════════════════════════════════════════════════════

📊 TIMESTAMP COMPARISON RESULTS:

- SYNCHRONIZED:  Local and Azure have the same latest timestamp ✓
- LOCAL_AHEAD:   Local has newer data (needs upload) ⬆️
- AZURE_AHEAD:   Azure has newer data (local is behind) ⬇️
- AZURE_MISSING: Azure blob doesn't exist (initial upload needed) ❌
- LOCAL_MISSING: Local file not found ❌
- BOTH_MISSING:  Neither local nor Azure has data ❌

═════════════════════════════════════════════════════════════════════════════

🚀 QUICK TEST:

1. Ensure Flask backend is running:
   python nasa_api_server.py

2. Test timestamp comparison:
   curl http://127.0.0.1:5001/nasa-api-compare-timestamps

3. Trigger fetch and sync:
   Click "FETCH DATA (NASA)" in GUI.html
   Or: curl -X POST http://127.0.0.1:5001/run-fetch-nasa-power

═════════════════════════════════════════════════════════════════════════════

💡 NOTES:

- Data is automatically synced after each fetch
- All monthly CSV files are uploaded alongside nasa-api.txt
- Azure Free Tier: 5 GB storage, perfect for your data
- First 12 months: Free Azure services
- Monitor your usage in Azure Portal

═════════════════════════════════════════════════════════════════════════════
""")
