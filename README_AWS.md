# AWS Integration Guide

## Overview

This guide walks you through setting up AWS infrastructure for the AI-EnergyR6 project. The integration includes:

- **Amazon S3**: Cloud storage for CSV and API data files
- **DynamoDB**: NoSQL database for fast data retrieval
- **RDS**: Relational database for structured queries (optional)

---

## Prerequisites

1. **AWS Account**: Create an AWS account at https://aws.amazon.com
2. **AWS Credentials**: Generate access keys from AWS IAM console
3. **Python 3.8+**: Installed on your machine
4. **Required packages**:
   ```bash
   pip install boto3 python-dotenv requests meteostat scikit-learn
   ```

---

## Step 1: Create AWS Credentials

### 1.1 Sign in to AWS Console
- Go to https://console.aws.amazon.com
- Sign in with your AWS account

### 1.2 Create IAM User
1. Navigate to **IAM** > **Users**
2. Click **Create user**
3. Set username (e.g., `ai-energy-r6-user`)
4. Select **Access key - Programmatic access**
5. Click **Next**

### 1.3 Set Permissions
1. Select **Attach policies directly**
2. Search for and attach these policies:
   - `AmazonS3FullAccess`
   - `AmazonDynamoDBFullAccess`
   - `AmazonRDSFullAccess` (optional)
3. Click **Next** and **Create user**

### 1.4 Get Access Keys
1. On the confirmation page, click **Show** under "Access key"
2. Copy the **Access Key ID** and **Secret Access Key**
3. Store these securely

---

## Step 2: Configure Local Environment

### 2.1 Create .env File
```bash
cp .env.template .env
```

### 2.2 Update .env with Your Credentials
Edit `.env` and replace placeholder values:

```env
# AWS Credentials (from IAM user)
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_REGION=us-east-1

# AWS S3 Configuration
AWS_S3_BUCKET=ai-energy-r6-data

# AWS DynamoDB Configuration
AWS_DYNAMODB_TABLE=energy-data

# AWS RDS Configuration (optional)
AWS_RDS_ENDPOINT=mydb.c9akciq32.us-east-1.rds.amazonaws.com
AWS_RDS_USER=admin
AWS_RDS_PASSWORD=YourSecurePassword
AWS_RDS_DATABASE=energy_db
```

⚠️ **IMPORTANT**: Never commit `.env` to Git. It contains sensitive credentials.

---

## Step 3: Initialize AWS Resources

### 3.1 Run Setup Script
```bash
python setup_aws.py --full
```

This script will:
1. ✓ Initialize AWS clients
2. ✓ Create S3 bucket
3. ✓ Create DynamoDB table
4. ✓ Upload existing data files
5. ✓ Load data into database
6. ✓ Display statistics

### 3.2 Monitor Setup Progress
The script outputs detailed logs for each step. Look for:
- ✓ Green checks for successful operations
- ✗ Red X for errors (troubleshoot if needed)
- ℹ Blue info for status updates

---

## Step 4: Project Structure

```
ai-energy-r6/
├── aws_config.py           # AWS configuration and initialization
├── aws_storage.py          # S3 storage operations
├── aws_database.py         # DynamoDB operations
├── aws_data_fetcher.py     # Fetch new data from APIs
├── setup_aws.py            # Setup and migration script
├── generate_monthly_csv_aws.py  # CSV generation with AWS
├── .env                    # AWS credentials (local only)
├── .env.template          # Template for .env
├── data/
│   ├── nasa-api.txt       # NASA source data
│   ├── openmet-api.txt    # Open-Meteo source data
│   ├── metstat-api.txt    # Meteostat source data
│   ├── wethrbit-api.txt   # Weatherbit source data
│   └── *.csv              # Monthly data files
└── README_AWS.md          # This guide
```

---

## AWS Architecture

### S3 Bucket Structure
```
ai-energy-r6-data/
├── api-files/
│   ├── nasa-api.txt
│   ├── openmet-api.txt
│   ├── metstat-api.txt
│   └── wethrbit-api.txt
├── csv-data/
│   ├── 2025/
│   │   ├── nasa_2025_01_january.csv
│   │   ├── nasa_2025_02_february.csv
│   │   └── ...
│   └── 2026/
│       ├── nasa_2026_03_march.csv
│       ├── openmeteo_2026_03_march.csv
│       └── ...
├── backup/
│   └── 2026-03-12_15-30-45/
│       └── [full backup of data/]
└── 2026-march-april/
    ├── nasa_2026_03_04.csv
    ├── openmeteo_2026_03_04.csv
    └── ...
```

### DynamoDB Table Schema
- **Table Name**: `energy-data`
- **Primary Key**: `source_timestamp` (Partition Key)
- **Sort Key**: `record_id`
- **Global Secondary Index**: `source-date-index` (for efficient queries)
- **Attributes**:
  - `source`: Data source (nasa, openmeteo, etc.)
  - `timestamp`: ISO format timestamp
  - `temperature`: In Celsius
  - `humidity`: Percentage
  - `irradiance`: Solar irradiance in W/m²
  - `wind_speed`: Wind speed in m/s
  - `wind_power_density`: Calculated wind power
  - `solar_energy_yield`: Calculated solar yield

---

## Usage Examples

### 1. Upload API Files
```python
from aws_storage import AWSStorage

storage = AWSStorage()
storage.upload_api_files('data')
```

### 2. Upload CSV Files
```python
storage.upload_csv_files('data', 'csv-data')
```

### 3. Load Data to DynamoDB
```python
from aws_database import load_csv_to_dynamodb

load_csv_to_dynamodb('data/nasa_2026_03_march.csv', 'nasa')
```

### 4. Query Data from DynamoDB
```python
from aws_database import AWSDatabase

db = AWSDatabase()
records = db.query_by_source_and_date('nasa', '2026-03-15')
for record in records:
    print(f"{record['timestamp']}: {record['temperature']}°C")
```

### 5. Download File from S3
```python
storage.download_file('csv-data/2026/nasa_2026_03_march.csv', 'local_copy.csv')
```

### 6. Generate March-April 2026 Data with AWS
```bash
python generate_monthly_csv_aws.py --march-april-2026 --with-aws
```

### 7. Fetch New Data for 2026
```bash
python aws_data_fetcher.py
```

This will:
- Fetch data from multiple APIs
- Store in CSV files
- Upload to S3
- Load into DynamoDB

---

## Cost Optimization

### S3 Storage
- **Free tier**: 5 GB
- **Standard storage**: $0.023 per GB/month
- **Tip**: Use S3 Lifecycle policies to archive old data

### DynamoDB
- **On-demand pricing** (current): $1.25 per million reads, $6.25 per million writes
- **Free tier**: 25 GB storage, 25 RCU, 25 WCU
- **Tip**: For predictable workloads, use provisioned capacity

### Data Transfer
- **Data IN**: Free
- **Data OUT to Internet**: $0.09 per GB (first 10 TB/month)
- **Tip**: Use CloudFront for cached distributions

### Monthly Estimate
- **CSV files (100 MB)**: ~$0.002
- **Database queries (10M/month)**: ~$8-12
- **Total monthly estimate**: ~$10-15

---

## Monitoring and Debugging

### Check S3 Bucket
```bash
aws s3 ls s3://ai-energy-r6-data --recursive
```

### Check DynamoDB Table
```bash
python -c "from aws_database import AWSDatabase; db = AWSDatabase(); print(db.get_table_stats())"
```

### View CloudWatch Logs
1. Go to AWS Console > CloudWatch > Logs
2. Search for `/aws/dynamodb/` or `/aws/s3/`

### Common Issues

#### 1. "Access Denied" Error
- Verify AWS credentials in `.env`
- Check IAM user has proper permissions
- Ensure bucket/table names match `.env`

#### 2. "The bucket already exists" Error
- Another AWS account owns the bucket name
- Use a unique bucket name in `.env`

#### 3. "NoCredentialsError"
- `.env` file is missing or not loaded
- Verify `python-dotenv` is installed
- Check `.env` file is in project root directory

#### 4. Slow Queries
- Add more read capacity to DynamoDB
- Use GSI for frequently queried attributes
- Implement caching layer

---

## Security Best Practices

### 1. Credentials Management
- ✓ Use `.env` file for local development
- ✓ Use IAM roles for production deployment
- ✓ Rotate access keys regularly
- ✗ Never commit `.env` to Git

### 2. S3 Security
- Enable versioning: `aws s3api put-bucket-versioning --bucket ai-energy-r6-data --versioning-configuration Status=Enabled`
- Enable encryption: `aws s3api put-bucket-encryption --bucket ai-energy-r6-data --server-side-encryption-configuration '{"Rules": [{"ApplyServerSideEncryptionByDefault": {"SSEAlgorithm": "AES256"}}]}'`

### 3. DynamoDB Security
- Enable point-in-time recovery
- Use VPC endpoints for private access
- Enable CloudTrail for audit logging

### 4. Network Security
- Restrict IAM permissions to minimum required
- Use Security Groups to limit access
- Enable VPC Flow Logs

---

## Troubleshooting

### Test Connection
```bash
python -c "from aws_config import AWSConfig; config = AWSConfig(); print('✓ AWS connection successful')"
```

### Verify S3 Access
```bash
python -c "from aws_storage import AWSStorage; s = AWSStorage(); print(s.list_files()[:3])"
```

### Verify DynamoDB Access
```bash
python -c "from aws_database import AWSDatabase; db = AWSDatabase(); print(db.get_table_stats())"
```

### View Logs
All operations log to console with status indicators:
- ✓ Success
- ✗ Error
- ℹ Info
- ⚠ Warning

---

## Next Steps

1. **Configure Monitoring**: Set up CloudWatch alerts
2. **Implement Backup**: Use AWS Backup service
3. **Setup CI/CD**: Use GitHub Actions with AWS deployment
4. **Add Analytics**: Use Athena to query S3 data
5. **Scale Database**: Use DynamoDB global tables for multi-region

---

## Support and Resources

- **AWS Documentation**: https://docs.aws.amazon.com
- **boto3 Documentation**: https://boto3.amazonaws.com/v1/documentation
- **AWS CLI Reference**: https://docs.aws.amazon.com/cli/latest/reference
- **AWS Pricing Calculator**: https://calculator.aws

---

## Summary

✓ AWS infrastructure setup complete
✓ S3 bucket created for data storage
✓ DynamoDB table created for fast queries
✓ Data migration scripts configured
✓ March-April 2026 data fetching enabled

**You're ready to use AWS with your AI-EnergyR6 project!**
