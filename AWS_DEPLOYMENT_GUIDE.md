# AWS Deployment Guide

Complete guide for deploying the Asset Management Multi-Agent Platform to AWS.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Architecture Overview](#architecture-overview)
3. [Quick Start](#quick-start)
4. [Detailed Deployment Steps](#detailed-deployment-steps)
5. [Post-Deployment Configuration](#post-deployment-configuration)
6. [Verification](#verification)
7. [Troubleshooting](#troubleshooting)
8. [Cost Estimation](#cost-estimation)
9. [Cleanup](#cleanup)

---

## Prerequisites

### Required Tools

- **AWS CLI** (v2.x or later)
  ```bash
  aws --version
  # aws-cli/2.x.x Python/3.x.x
  ```

- **Terraform** (v1.5.0 or later)
  ```bash
  terraform version
  # Terraform v1.5.0 or later
  ```

- **Node.js & npm** (v18.x or later)
  ```bash
  node --version  # v18.x or later
  npm --version   # v9.x or later
  ```

- **Python** (3.12 or 3.13)
  ```bash
  python3 --version  # Python 3.12 or 3.13
  ```

- **uv** (Python package installer - optional but recommended)
  ```bash
  uv --version
  # Or install: curl -LsSf https://astral.sh/uv/install.sh | sh
  ```

- **Docker** (optional, for Lambda packaging)
  ```bash
  docker --version
  ```

### AWS Configuration

✅ **AWS credentials configured** (you mentioned this is done)

Verify your configuration:
```bash
aws sts get-caller-identity
```

Expected output:
```json
{
    "UserId": "AIDAXXXXXXXXXXXXXXXXX",
    "Account": "123456789012",
    "Arn": "arn:aws:iam::123456789012:user/your-username"
}
```

### AWS Permissions Required

Your IAM user/role needs permissions for:
- **DynamoDB**: CreateTable, DescribeTable, TagResource
- **Lambda**: CreateFunction, UpdateFunctionCode, UpdateFunctionConfiguration
- **IAM**: CreateRole, AttachRolePolicy, PassRole
- **API Gateway**: CreateApi, CreateRoute, CreateIntegration
- **S3**: CreateBucket, PutObject, PutBucketPolicy, PutBucketWebsite
- **CloudWatch Logs**: CreateLogGroup, PutRetentionPolicy

---

## Architecture Overview

### AWS Services Used

```
┌─────────────────────────────────────────────────────────────┐
│                         AWS Cloud                            │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐         ┌──────────────────────────┐      │
│  │   S3 Bucket  │         │   API Gateway (HTTP)     │      │
│  │   (Frontend) │         │   /api/* → Backend       │      │
│  │   Static     │         │   /a2a/research → Agent  │      │
│  │   Website    │         │   /mcp → Sentiment       │      │
│  └──────────────┘         └──────────────────────────┘      │
│         │                            │                        │
│         │                            ▼                        │
│         │                  ┌──────────────────┐              │
│         │                  │  Lambda Functions │              │
│         │                  ├──────────────────┤              │
│         │                  │ • Backend API    │              │
│         │                  │ • Research Agent │              │
│         │                  │ • Sentiment MCP  │              │
│         │                  └──────────────────┘              │
│         │                            │                        │
│         │                            ▼                        │
│         │                  ┌──────────────────┐              │
│         │                  │   DynamoDB       │              │
│         │                  ├──────────────────┤              │
│         │                  │ • Approvals      │              │
│         │                  │ • Audit Events   │              │
│         │                  │ • Portfolios     │              │
│         │                  │ • Sessions       │              │
│         │                  │ • Memory Queue   │              │
│         │                  │ • Preferences    │              │
│         │                  └──────────────────┘              │
│         │                            │                        │
│         │                            ▼                        │
│         │                  ┌──────────────────┐              │
│         │                  │  CloudWatch Logs │              │
│         │                  │  (Monitoring)    │              │
│         │                  └──────────────────┘              │
│         │                                                     │
└─────────┴─────────────────────────────────────────────────────┘
          │
          ▼
    ┌──────────┐
    │  Users   │
    │ (Browser)│
    └──────────┘
```

### Resource Naming Convention

All resources are prefixed with: `{project_name}-{environment}-`

Example for dev environment:
- DynamoDB: `asset-management-dev-approvals`
- Lambda: `asset-management-dev-backend`
- S3: `asset-management-dev-frontend`
- API Gateway: `asset-management-dev-api`

---

## Quick Start

For experienced users who want to deploy immediately:

```bash
# 1. Package Lambda functions
./infra/scripts/package_lambda.sh

# 2. Create tfvars file
cd infra/terraform/environments/dev
cp dev.tfvars.example dev.tfvars
# Edit dev.tfvars with your settings

# 3. Deploy infrastructure
terraform init
terraform plan -var-file=dev.tfvars
terraform apply -var-file=dev.tfvars

# 4. Deploy frontend
cd ../../../..
./infra/scripts/publish_frontend.sh \
  "$(terraform -chdir=infra/terraform/environments/dev output -raw api_base_url)" \
  "$(terraform -chdir=infra/terraform/environments/dev output -raw frontend_bucket_name)"

# 5. Get frontend URL
terraform -chdir=infra/terraform/environments/dev output -raw frontend_website_url
```

---

## Detailed Deployment Steps

### Step 1: Package Lambda Functions

Lambda functions need to be packaged with their dependencies.

```bash
# From project root
./infra/scripts/package_lambda.sh
```

**What this does:**
- Installs Python dependencies for each service
- Creates deployment packages in `infra/build/`
- Generates three zip files:
  - `backend.zip` (~50MB)
  - `research-agent.zip` (~20MB)
  - `sentiment-mcp.zip` (~20MB)

**Options:**
```bash
# Use Docker for consistent builds (recommended for production)
USE_DOCKER=true ./infra/scripts/package_lambda.sh

# Use local Python (faster for development)
USE_DOCKER=false ./infra/scripts/package_lambda.sh

# Specify Python version
PYTHON_VERSION=3.13 ./infra/scripts/package_lambda.sh
```

**Verify packages:**
```bash
ls -lh infra/build/*.zip
# Should show three zip files
```

### Step 2: Configure Terraform Variables

Create your environment-specific configuration:

```bash
cd infra/terraform/environments/dev
cp dev.tfvars.example dev.tfvars
```

Edit `dev.tfvars`:

```hcl
# AWS Region
aws_region = "us-east-1"  # Change to your preferred region

# Project Configuration
project_name = "asset-management"
environment  = "dev"

# Lambda Configuration
lambda_runtime = "python3.13"

# CORS Configuration
cors_allow_origins = ["*"]  # For production, specify exact origins

# Optional: Custom S3 bucket name
# frontend_bucket_name = "my-custom-frontend-bucket-name"
```

**Important Notes:**
- S3 bucket names must be globally unique
- If you don't specify `frontend_bucket_name`, it will be auto-generated
- For production, restrict CORS to your domain only

### Step 3: Initialize Terraform

```bash
# Still in infra/terraform/environments/dev
terraform init
```

**Expected output:**
```
Initializing modules...
Initializing the backend...
Initializing provider plugins...
- Finding latest version of hashicorp/aws...
- Installing hashicorp/aws v5.x.x...

Terraform has been successfully initialized!
```

### Step 4: Review Deployment Plan

```bash
terraform plan -var-file=dev.tfvars
```

**What to look for:**
- ✅ 6 DynamoDB tables to be created
- ✅ 3 Lambda functions to be created
- ✅ 1 API Gateway to be created
- ✅ 1 S3 bucket to be created
- ✅ IAM roles and policies
- ✅ CloudWatch log groups

**Expected resource count:**
```
Plan: 30+ to add, 0 to change, 0 to destroy.
```

### Step 5: Deploy Infrastructure

```bash
terraform apply -var-file=dev.tfvars
```

Type `yes` when prompted.

**Deployment time:** ~2-3 minutes

**Expected output:**
```
Apply complete! Resources: 30+ added, 0 changed, 0 destroyed.

Outputs:

api_base_url = "https://xxxxxxxxxx.execute-api.us-east-1.amazonaws.com"
dynamodb_table_names = {
  "approvals" = "asset-management-dev-approvals"
  "audit_events" = "asset-management-dev-audit-events"
  "memory_queue" = "asset-management-dev-memory-queue"
  "portfolios" = "asset-management-dev-portfolios"
  "preferences" = "asset-management-dev-preferences"
  "sessions" = "asset-management-dev-sessions"
}
frontend_bucket_name = "asset-management-dev-frontend"
frontend_website_url = "http://asset-management-dev-frontend.s3-website-us-east-1.amazonaws.com"
lambda_function_names = {
  "backend" = "asset-management-dev-backend"
  "research_agent" = "asset-management-dev-research-agent"
  "sentiment_mcp" = "asset-management-dev-sentiment-mcp"
}
```

**Save these outputs!** You'll need them for the next steps.

### Step 6: Deploy Frontend

Build and upload the Angular frontend:

```bash
# From project root
cd ../../../../  # Back to project root

# Option A: Use the automated script (recommended)
./infra/scripts/publish_frontend.sh \
  "$(terraform -chdir=infra/terraform/environments/dev output -raw api_base_url)" \
  "$(terraform -chdir=infra/terraform/environments/dev output -raw frontend_bucket_name)"

# Option B: Manual steps
cd frontend
npm ci
npm run build

# Create app-config.js with API URL
API_BASE=$(terraform -chdir=../infra/terraform/environments/dev output -raw api_base_url)
printf "window.assetManagementConfig = {\n  apiBaseUrl: '%s'\n};\n" "$API_BASE" \
  > dist/frontend/browser/app-config.js

# Upload to S3
BUCKET=$(terraform -chdir=../infra/terraform/environments/dev output -raw frontend_bucket_name)
aws s3 sync dist/frontend/browser/ "s3://${BUCKET}/" --delete
```

**Expected output:**
```
> frontend@0.0.0 build
> ng build

✔ Building...
Application bundle generation complete.

upload: dist/frontend/browser/index.html to s3://asset-management-dev-frontend/index.html
upload: dist/frontend/browser/main.js to s3://asset-management-dev-frontend/main.js
...
Uploaded frontend to s3://asset-management-dev-frontend/
```

---

## Post-Deployment Configuration

### Get Your Application URL

```bash
terraform -chdir=infra/terraform/environments/dev output -raw frontend_website_url
```

Example output:
```
http://asset-management-dev-frontend.s3-website-us-east-1.amazonaws.com
```

### Configure Custom Domain (Optional)

To use a custom domain like `app.yourdomain.com`:

1. **Create CloudFront distribution** (for HTTPS)
2. **Configure Route53** (for DNS)
3. **Update CORS settings** in `dev.tfvars`

See [Custom Domain Setup](#custom-domain-setup) for details.

### Enable Bedrock Access (For LLM Features)

If you want to use LLM-enhanced features:

1. **Request Bedrock model access:**
   - Go to AWS Console → Bedrock → Model access
   - Request access to Claude models
   - Wait for approval (~5 minutes)

2. **Update Lambda IAM role:**
   ```bash
   # Add Bedrock permissions to backend Lambda
   aws iam attach-role-policy \
     --role-name asset-management-dev-backend-role \
     --policy-arn arn:aws:iam::aws:policy/AmazonBedrockFullAccess
   ```

3. **Enable LLM features** in backend environment variables:
   ```hcl
   # In main.tf, add to backend_lambda environment_variables:
   REBALANCING_AGENT_LLM_ENABLED = "true"
   RESEARCH_AGENT_LLM_ENABLED = "true"
   # ... etc
   ```

---

## Verification

### 1. Test Backend API

```bash
API_URL=$(terraform -chdir=infra/terraform/environments/dev output -raw api_base_url)

# Health check
curl "${API_URL}/health"
```

**Expected response:**
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "environment": "dev"
}
```

### 2. Test Portfolios Endpoint

```bash
curl "${API_URL}/api/portfolios"
```

**Expected response:**
```json
[
  {
    "client_profile": {
      "client_id": "client_demo",
      "display_label": "Demo Investor",
      ...
    },
    ...
  }
]
```

### 3. Test Frontend

Open the frontend URL in your browser:

```bash
# Get URL
terraform -chdir=infra/terraform/environments/dev output -raw frontend_website_url

# Or open directly (macOS)
open "$(terraform -chdir=infra/terraform/environments/dev output -raw frontend_website_url)"
```

**What to verify:**
- ✅ Page loads without errors
- ✅ "Asset Management" title visible
- ✅ Portfolio data loads
- ✅ Market simulation stream works
- ✅ Can generate rebalance recommendations
- ✅ Can access preferences page

### 4. Check CloudWatch Logs

```bash
# Backend logs
aws logs tail /aws/lambda/asset-management-dev-backend --follow

# Research agent logs
aws logs tail /aws/lambda/asset-management-dev-research-agent --follow

# Sentiment MCP logs
aws logs tail /aws/lambda/asset-management-dev-sentiment-mcp --follow
```

### 5. Check DynamoDB Tables

```bash
# List portfolios
aws dynamodb scan \
  --table-name asset-management-dev-portfolios \
  --max-items 5

# List preferences
aws dynamodb scan \
  --table-name asset-management-dev-preferences \
  --max-items 5
```

---

## Troubleshooting

### Issue: Lambda Package Too Large

**Error:**
```
Error: error creating Lambda Function: InvalidParameterValueException: 
Unzipped size must be smaller than 262144000 bytes
```

**Solution:**
```bash
# Use Docker for smaller packages
USE_DOCKER=true ./infra/scripts/package_lambda.sh

# Or increase Lambda memory (allows larger packages)
# In main.tf, change memory_mb to 1024 or higher
```

### Issue: S3 Bucket Name Already Exists

**Error:**
```
Error: error creating S3 Bucket: BucketAlreadyExists: 
The requested bucket name is not available
```

**Solution:**
```bash
# In dev.tfvars, specify a unique bucket name:
frontend_bucket_name = "asset-mgmt-dev-frontend-YOUR-UNIQUE-SUFFIX"
```

### Issue: Frontend Shows "Failed to Load"

**Symptoms:**
- Frontend loads but shows errors
- Console shows CORS errors
- API requests fail

**Solution:**
```bash
# 1. Verify API URL in app-config.js
aws s3 cp s3://YOUR-BUCKET/app-config.js -

# 2. Check CORS configuration
# In dev.tfvars, ensure cors_allow_origins includes "*" or your domain

# 3. Redeploy frontend
./infra/scripts/publish_frontend.sh \
  "$(terraform -chdir=infra/terraform/environments/dev output -raw api_base_url)" \
  "$(terraform -chdir=infra/terraform/environments/dev output -raw frontend_bucket_name)"
```

### Issue: Lambda Timeout

**Error in logs:**
```
Task timed out after 30.00 seconds
```

**Solution:**
```hcl
# In main.tf, increase timeout_seconds:
module "backend_lambda" {
  ...
  timeout_seconds = 60  # Increase from 30
  ...
}
```

### Issue: DynamoDB Access Denied

**Error:**
```
AccessDeniedException: User is not authorized to perform: dynamodb:GetItem
```

**Solution:**
```bash
# Verify IAM policy includes all tables
terraform plan -var-file=dev.tfvars
# Look for aws_iam_policy_document.backend_dynamodb

# If preferences table is missing, it was added in this guide
terraform apply -var-file=dev.tfvars
```

### Issue: Cannot Access Bedrock Models

**Error:**
```
AccessDeniedException: Could not access model
```

**Solution:**
1. Request model access in AWS Console → Bedrock
2. Add Bedrock permissions to Lambda role
3. Wait 5-10 minutes for permissions to propagate

---

## Cost Estimation

### Monthly Costs (Development Environment)

**Assumptions:**
- 1,000 API requests/day
- 100 MB data transfer/day
- Minimal usage (dev/testing)

| Service | Usage | Cost |
|---------|-------|------|
| **Lambda** | 30,000 requests/month, 512MB, 5s avg | ~$0.50 |
| **API Gateway** | 30,000 requests/month | ~$0.03 |
| **DynamoDB** | On-demand, minimal reads/writes | ~$1.00 |
| **S3** | 1 GB storage, 1,000 requests | ~$0.05 |
| **CloudWatch Logs** | 1 GB logs/month | ~$0.50 |
| **Data Transfer** | 3 GB/month | ~$0.27 |
| **Total** | | **~$2.35/month** |

### Production Costs (Estimated)

**Assumptions:**
- 100,000 API requests/day
- 10 GB data transfer/day
- Active usage

| Service | Usage | Cost |
|---------|-------|------|
| **Lambda** | 3M requests/month, 512MB, 5s avg | ~$50 |
| **API Gateway** | 3M requests/month | ~$3 |
| **DynamoDB** | On-demand, moderate reads/writes | ~$25 |
| **S3** | 10 GB storage, 100K requests | ~$1 |
| **CloudWatch Logs** | 50 GB logs/month | ~$25 |
| **Data Transfer** | 300 GB/month | ~$27 |
| **CloudFront** (optional) | 300 GB/month | ~$25 |
| **Total** | | **~$156/month** |

**Cost Optimization Tips:**
- Use CloudWatch Logs retention (7-30 days)
- Enable DynamoDB auto-scaling for predictable workloads
- Use S3 lifecycle policies for old data
- Consider Reserved Capacity for Lambda in production

---

## Cleanup

### Remove All AWS Resources

```bash
# 1. Empty S3 bucket (required before deletion)
BUCKET=$(terraform -chdir=infra/terraform/environments/dev output -raw frontend_bucket_name)
aws s3 rm "s3://${BUCKET}" --recursive

# 2. Destroy infrastructure
cd infra/terraform/environments/dev
terraform destroy -var-file=dev.tfvars
```

Type `yes` when prompted.

**What gets deleted:**
- ✅ All DynamoDB tables (data will be lost!)
- ✅ All Lambda functions
- ✅ API Gateway
- ✅ S3 bucket
- ✅ IAM roles and policies
- ✅ CloudWatch log groups

**Cleanup verification:**
```bash
# Should return empty or error
aws dynamodb list-tables --query 'TableNames[?contains(@, `asset-management-dev`)]'
aws lambda list-functions --query 'Functions[?contains(FunctionName, `asset-management-dev`)]'
```

---

## Advanced Topics

### Custom Domain Setup

1. **Create ACM certificate** (in us-east-1 for CloudFront):
   ```bash
   aws acm request-certificate \
     --domain-name app.yourdomain.com \
     --validation-method DNS \
     --region us-east-1
   ```

2. **Create CloudFront distribution:**
   ```hcl
   # Add to main.tf
   resource "aws_cloudfront_distribution" "frontend" {
     # ... configuration
   }
   ```

3. **Update Route53:**
   ```hcl
   resource "aws_route53_record" "frontend" {
     zone_id = var.route53_zone_id
     name    = "app.yourdomain.com"
     type    = "A"
     alias {
       name    = aws_cloudfront_distribution.frontend.domain_name
       zone_id = aws_cloudfront_distribution.frontend.hosted_zone_id
     }
   }
   ```

### CI/CD Pipeline

Example GitHub Actions workflow:

```yaml
name: Deploy to AWS

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
      
      - name: Package Lambda functions
        run: ./infra/scripts/package_lambda.sh
      
      - name: Deploy infrastructure
        run: |
          cd infra/terraform/environments/dev
          terraform init
          terraform apply -auto-approve -var-file=dev.tfvars
      
      - name: Deploy frontend
        run: ./infra/scripts/publish_frontend.sh ...
```

### Multi-Environment Setup

Create separate environments:

```bash
# Staging environment
cp -r infra/terraform/environments/dev infra/terraform/environments/staging
# Edit staging/main.tf and staging.tfvars

# Production environment
cp -r infra/terraform/environments/dev infra/terraform/environments/prod
# Edit prod/main.tf and prod.tfvars
```

---

## Support

### Documentation
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [AWS Lambda Developer Guide](https://docs.aws.amazon.com/lambda/)
- [API Gateway Developer Guide](https://docs.aws.amazon.com/apigateway/)

### Logs and Monitoring
- CloudWatch Logs: AWS Console → CloudWatch → Log groups
- Lambda Metrics: AWS Console → Lambda → Functions → Monitoring
- API Gateway Metrics: AWS Console → API Gateway → APIs → Monitoring

### Getting Help
- Check CloudWatch Logs for errors
- Review Terraform plan output
- Verify IAM permissions
- Check AWS service quotas

---

## Summary

You've successfully deployed the Asset Management Multi-Agent Platform to AWS! 🎉

**What you deployed:**
- ✅ 3 Lambda functions (Backend, Research Agent, Sentiment MCP)
- ✅ 6 DynamoDB tables (Approvals, Audit Events, Portfolios, Sessions, Memory Queue, Preferences)
- ✅ 1 API Gateway (HTTP API)
- ✅ 1 S3 bucket (Static website hosting)
- ✅ CloudWatch Logs (Monitoring)

**Next steps:**
1. Open your frontend URL
2. Test the rebalancing workflow
3. Configure user preferences
4. Monitor CloudWatch Logs
5. Set up custom domain (optional)
6. Enable Bedrock for LLM features (optional)

**Estimated monthly cost:** ~$2-5 for development, ~$150-200 for production
