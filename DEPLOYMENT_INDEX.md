# Deployment Documentation Index

Quick navigation to all deployment-related documentation.

## 🚀 Getting Started

**New to AWS deployment?** Start here:
1. Read [AWS Deployment Summary](#aws-deployment-summary) (5 min read)
2. Follow [AWS Deployment Guide](#aws-deployment-guide) (step-by-step)
3. Use [Quick Reference](#quick-reference) for common commands

**Already familiar?** Jump to:
- [Quick Deploy](#quick-deploy) - One command deployment
- [Quick Reference](#quick-reference) - Command cheat sheet

---

## 📚 Documentation

### AWS Deployment Summary
**File**: `AWS_DEPLOYMENT_SUMMARY.md`

**What it covers:**
- What was created/modified
- Deployment options (3 ways)
- Resource overview
- Prerequisites checklist
- Cost estimates
- Quick troubleshooting

**When to use**: First time deploying or need a quick overview

**Read time**: 5 minutes

---

### AWS Deployment Guide
**File**: `AWS_DEPLOYMENT_GUIDE.md`

**What it covers:**
- Complete prerequisites
- Architecture overview
- Detailed step-by-step deployment
- Post-deployment configuration
- Verification procedures
- Troubleshooting guide
- Cost estimation
- Cleanup procedures
- Advanced topics

**When to use**: Detailed deployment, troubleshooting, or learning

**Read time**: 20-30 minutes

**Sections:**
1. Prerequisites
2. Architecture Overview
3. Quick Start
4. Detailed Deployment Steps
5. Post-Deployment Configuration
6. Verification
7. Troubleshooting
8. Cost Estimation
9. Cleanup

---

### Quick Reference
**File**: `AWS_QUICK_REFERENCE.md`

**What it covers:**
- Common commands (copy-paste ready)
- Deploy, update, test commands
- Log viewing
- DynamoDB operations
- Lambda operations
- S3 operations
- Troubleshooting commands
- Monitoring commands

**When to use**: Daily operations, quick lookups

**Read time**: 2 minutes (reference)

---

### Terraform README
**File**: `infra/terraform/README.md`

**What it covers:**
- Terraform structure
- Module organization
- Initial usage
- Lambda services
- Frontend upload

**When to use**: Understanding Terraform structure

**Read time**: 5 minutes

---

## 🎯 Quick Deploy

### One-Command Deployment
```bash
./infra/scripts/deploy.sh dev
```

This script will:
1. ✅ Check prerequisites
2. ✅ Package Lambda functions
3. ✅ Initialize Terraform
4. ✅ Deploy infrastructure
5. ✅ Deploy frontend
6. ✅ Display URLs and next steps

**Time**: ~5-8 minutes

---

## 📋 Common Tasks

### First Time Deployment
```bash
# 1. Verify prerequisites
aws sts get-caller-identity
terraform version
node --version

# 2. Deploy everything
./infra/scripts/deploy.sh dev

# 3. Get URLs
terraform -chdir=infra/terraform/environments/dev output
```

### Update Backend Code
```bash
# 1. Make changes to backend code
# 2. Repackage and deploy
./infra/scripts/package_lambda.sh
cd infra/terraform/environments/dev
terraform apply -var-file=dev.tfvars -target=module.backend_lambda
```

### Update Frontend
```bash
# 1. Make changes to frontend code
# 2. Rebuild and deploy
cd frontend
npm run build
cd ..
./infra/scripts/publish_frontend.sh \
  "$(terraform -chdir=infra/terraform/environments/dev output -raw api_base_url)" \
  "$(terraform -chdir=infra/terraform/environments/dev output -raw frontend_bucket_name)"
```

### View Logs
```bash
# Backend logs (live)
aws logs tail /aws/lambda/asset-management-dev-backend --follow

# All logs
aws logs tail /aws/lambda/asset-management-dev-backend --follow &
aws logs tail /aws/lambda/asset-management-dev-research-agent --follow &
aws logs tail /aws/lambda/asset-management-dev-sentiment-mcp --follow &
```

### Test Deployment
```bash
# Get API URL
API_URL=$(terraform -chdir=infra/terraform/environments/dev output -raw api_base_url)

# Test health endpoint
curl "${API_URL}/health"

# Test portfolios endpoint
curl "${API_URL}/api/portfolios"

# Open frontend
open "$(terraform -chdir=infra/terraform/environments/dev output -raw frontend_website_url)"
```

### Cleanup
```bash
# Empty S3 bucket
BUCKET=$(terraform -chdir=infra/terraform/environments/dev output -raw frontend_bucket_name)
aws s3 rm "s3://${BUCKET}" --recursive

# Destroy all resources
cd infra/terraform/environments/dev
terraform destroy -var-file=dev.tfvars
```

---

## 🏗️ Architecture

### AWS Services
- **DynamoDB** (6 tables) - Data persistence
- **Lambda** (3 functions) - Backend services
- **API Gateway** (1 HTTP API) - API routing
- **S3** (1 bucket) - Frontend hosting
- **CloudWatch Logs** (3 log groups) - Monitoring
- **IAM** (6 roles/policies) - Permissions

### Resource Naming
Format: `{project}-{environment}-{resource}`

Example:
- `asset-management-dev-backend` (Lambda)
- `asset-management-dev-portfolios` (DynamoDB)
- `asset-management-dev-frontend` (S3)

---

## 💰 Cost Estimates

### Development
- **Monthly**: ~$2-5
- **Daily**: ~$0.10-0.20

### Production
- **Monthly**: ~$150-200
- **Daily**: ~$5-7

**Cost breakdown** in [AWS Deployment Guide](#aws-deployment-guide)

---

## 🔧 Troubleshooting

### Quick Fixes

**S3 Bucket Name Conflict**
```bash
# In dev.tfvars, add:
frontend_bucket_name = "asset-mgmt-dev-YOUR-UNIQUE-SUFFIX"
```

**Lambda Package Too Large**
```bash
USE_DOCKER=true ./infra/scripts/package_lambda.sh
```

**CORS Errors**
```bash
# In dev.tfvars, ensure:
cors_allow_origins = ["*"]
```

**DynamoDB Access Denied**
```bash
cd infra/terraform/environments/dev
terraform apply -var-file=dev.tfvars
```

**More troubleshooting** in [AWS Deployment Guide](#aws-deployment-guide)

---

## 📖 Related Documentation

### Local Development
- `STARTUP_GUIDE.md` - Local development setup
- `docker-compose.yml` - Local Docker setup
- `README_LLM_INTEGRATION.md` - LLM features

### Features
- `PREFERENCES_INTEGRATION_FIX.md` - Preferences system
- `TARGET_ALLOCATION_PREFERENCE_FIX.md` - Preference display
- `REBALANCE_FLOW_VERIFICATION.md` - Rebalancing workflow

### Architecture
- `docs/01-architecture/system-architecture.md` - System design
- `docs/01-architecture/langgraph-orchestration.md` - LangGraph
- `docs/06-architecture/LANGGRAPH_DESIGN_COMPREHENSIVE.md` - Detailed design

---

## 🎓 Learning Path

### Beginner
1. Read `AWS_DEPLOYMENT_SUMMARY.md`
2. Follow `AWS_DEPLOYMENT_GUIDE.md` step-by-step
3. Bookmark `AWS_QUICK_REFERENCE.md`

### Intermediate
1. Review `infra/terraform/README.md`
2. Explore Terraform modules in `infra/terraform/modules/`
3. Customize `dev.tfvars` for your needs

### Advanced
1. Create production environment
2. Set up CI/CD pipeline
3. Configure custom domain
4. Enable CloudWatch alarms

---

## 🆘 Getting Help

### Check Logs
```bash
# Backend errors
aws logs filter-log-events \
  --log-group-name /aws/lambda/asset-management-dev-backend \
  --filter-pattern "ERROR" \
  --max-items 10
```

### Verify Configuration
```bash
# Check AWS credentials
aws sts get-caller-identity

# Check Terraform state
cd infra/terraform/environments/dev
terraform show

# Check deployed resources
aws resourcegroupstaggingapi get-resources \
  --tag-filters Key=Project,Values=asset-management
```

### AWS Console
- Lambda: https://console.aws.amazon.com/lambda/
- DynamoDB: https://console.aws.amazon.com/dynamodb/
- API Gateway: https://console.aws.amazon.com/apigateway/
- S3: https://console.aws.amazon.com/s3/
- CloudWatch: https://console.aws.amazon.com/cloudwatch/

---

## ✅ Deployment Checklist

### Pre-Deployment
- [ ] AWS CLI installed and configured
- [ ] Terraform installed (v1.5.0+)
- [ ] Node.js & npm installed (v18+)
- [ ] Python 3.12/3.13 installed
- [ ] Created `dev.tfvars` from example
- [ ] Reviewed cost estimates

### Deployment
- [ ] Packaged Lambda functions
- [ ] Initialized Terraform
- [ ] Reviewed Terraform plan
- [ ] Applied Terraform configuration
- [ ] Deployed frontend
- [ ] Saved output URLs

### Post-Deployment
- [ ] Tested API health endpoint
- [ ] Tested portfolios endpoint
- [ ] Opened frontend in browser
- [ ] Verified data loads
- [ ] Checked CloudWatch logs
- [ ] Bookmarked URLs

### Optional
- [ ] Set up custom domain
- [ ] Enabled Bedrock for LLM
- [ ] Configured CloudWatch alarms
- [ ] Set up CI/CD pipeline

---

## 📞 Support

**Documentation Issues**: Check the specific guide for detailed troubleshooting

**AWS Issues**: Check CloudWatch Logs and AWS Console

**Terraform Issues**: Run `terraform validate` and check syntax

**Application Issues**: Check `STARTUP_GUIDE.md` for local testing

---

## 🎉 Success!

Once deployed, you'll have:
- ✅ Fully functional backend API on AWS Lambda
- ✅ Static frontend hosted on S3
- ✅ DynamoDB tables for data persistence
- ✅ API Gateway for routing
- ✅ CloudWatch Logs for monitoring

**Next**: Open your frontend URL and start using the application!

```bash
# Get your frontend URL
terraform -chdir=infra/terraform/environments/dev output -raw frontend_website_url
```
