# AWS Deployment Summary

## What Was Created

### 1. Infrastructure Updates
- ✅ Added **Preferences DynamoDB table** to Terraform configuration
- ✅ Updated IAM policies to include preferences table access
- ✅ Added `PREFERENCES_TABLE_NAME` environment variable to backend Lambda
- ✅ Added `Query` permission to DynamoDB IAM policy

### 2. Documentation
- ✅ **AWS_DEPLOYMENT_GUIDE.md** - Comprehensive 500+ line deployment guide
- ✅ **AWS_QUICK_REFERENCE.md** - One-page command reference
- ✅ **AWS_DEPLOYMENT_SUMMARY.md** - This file

### 3. Deployment Scripts
- ✅ **infra/scripts/deploy.sh** - Automated deployment script
- ✅ Updated existing scripts with better error handling

## Files Modified

### Terraform Configuration
- `infra/terraform/environments/dev/main.tf`
  - Added `preferences` to `dynamodb_tables` local
  - Added `aws_dynamodb_table.preferences` resource
  - Updated `backend_dynamodb` IAM policy to include preferences table
  - Added `PREFERENCES_TABLE_NAME` to backend Lambda environment variables
  - Added `Query` action to DynamoDB permissions

## Deployment Options

### Option 1: Automated Deployment (Recommended)
```bash
./infra/scripts/deploy.sh dev
```

### Option 2: Manual Deployment
```bash
# 1. Package Lambda functions
./infra/scripts/package_lambda.sh

# 2. Deploy infrastructure
cd infra/terraform/environments/dev
terraform init
terraform apply -var-file=dev.tfvars

# 3. Deploy frontend
cd ../../../..
./infra/scripts/publish_frontend.sh \
  "$(terraform -chdir=infra/terraform/environments/dev output -raw api_base_url)" \
  "$(terraform -chdir=infra/terraform/environments/dev output -raw frontend_bucket_name)"
```

### Option 3: Step-by-Step (For Learning)
See **AWS_DEPLOYMENT_GUIDE.md** for detailed step-by-step instructions.

## What Gets Deployed

### AWS Resources (30+ total)

#### DynamoDB Tables (6)
1. `asset-management-dev-approvals` - Approval workflow tracking
2. `asset-management-dev-audit-events` - Audit trail
3. `asset-management-dev-portfolios` - Portfolio data
4. `asset-management-dev-sessions` - User sessions
5. `asset-management-dev-memory-queue` - Agent memory queue
6. `asset-management-dev-preferences` - **NEW** User preferences

#### Lambda Functions (3)
1. `asset-management-dev-backend` - Main API (512MB, 30s timeout)
2. `asset-management-dev-research-agent` - Research agent (256MB, 15s timeout)
3. `asset-management-dev-sentiment-mcp` - Sentiment analysis (256MB, 15s timeout)

#### API Gateway (1)
- `asset-management-dev-api` - HTTP API with routes:
  - `ANY /` → Backend
  - `ANY /{proxy+}` → Backend
  - `ANY /a2a/research` → Research Agent
  - `ANY /mcp` → Sentiment MCP

#### S3 Bucket (1)
- `asset-management-dev-frontend` - Static website hosting

#### IAM Roles & Policies (6)
- Lambda execution roles (3)
- DynamoDB access policies (3)

#### CloudWatch Log Groups (3)
- `/aws/lambda/asset-management-dev-backend`
- `/aws/lambda/asset-management-dev-research-agent`
- `/aws/lambda/asset-management-dev-sentiment-mcp`

## Prerequisites Checklist

- [x] AWS CLI installed and configured (`aws configure` already done)
- [ ] Terraform installed (v1.5.0+)
- [ ] Node.js & npm installed (v18+)
- [ ] Python 3.12 or 3.13 installed
- [ ] uv installed (optional but recommended)
- [ ] Docker installed (optional, for Lambda packaging)

## Deployment Time

- **Lambda Packaging**: ~2-3 minutes
- **Terraform Apply**: ~2-3 minutes
- **Frontend Build & Upload**: ~1-2 minutes
- **Total**: ~5-8 minutes

## Cost Estimate

### Development Environment
- **Monthly**: ~$2-5
- **Per Day**: ~$0.10-0.20

### Production Environment
- **Monthly**: ~$150-200
- **Per Day**: ~$5-7

## Post-Deployment

### Get Your URLs
```bash
# Frontend URL
terraform -chdir=infra/terraform/environments/dev output -raw frontend_website_url

# API URL
terraform -chdir=infra/terraform/environments/dev output -raw api_base_url
```

### Test Deployment
```bash
# Test API
API_URL=$(terraform -chdir=infra/terraform/environments/dev output -raw api_base_url)
curl "${API_URL}/health"

# Test Frontend
open "$(terraform -chdir=infra/terraform/environments/dev output -raw frontend_website_url)"
```

### View Logs
```bash
# Backend logs
aws logs tail /aws/lambda/asset-management-dev-backend --follow

# All Lambda logs
aws logs tail /aws/lambda/asset-management-dev-backend --follow &
aws logs tail /aws/lambda/asset-management-dev-research-agent --follow &
aws logs tail /aws/lambda/asset-management-dev-sentiment-mcp --follow &
```

## Troubleshooting

### Common Issues

1. **S3 Bucket Name Conflict**
   - Solution: Specify unique name in `dev.tfvars`
   ```hcl
   frontend_bucket_name = "asset-mgmt-dev-YOUR-UNIQUE-SUFFIX"
   ```

2. **Lambda Package Too Large**
   - Solution: Use Docker for packaging
   ```bash
   USE_DOCKER=true ./infra/scripts/package_lambda.sh
   ```

3. **CORS Errors in Frontend**
   - Solution: Verify CORS configuration in `dev.tfvars`
   ```hcl
   cors_allow_origins = ["*"]
   ```

4. **DynamoDB Access Denied**
   - Solution: Reapply Terraform to update IAM policies
   ```bash
   cd infra/terraform/environments/dev
   terraform apply -var-file=dev.tfvars
   ```

## Cleanup

### Remove All Resources
```bash
# Empty S3 bucket
BUCKET=$(terraform -chdir=infra/terraform/environments/dev output -raw frontend_bucket_name)
aws s3 rm "s3://${BUCKET}" --recursive

# Destroy infrastructure
cd infra/terraform/environments/dev
terraform destroy -var-file=dev.tfvars
```

## Next Steps

1. **Deploy to AWS**
   ```bash
   ./infra/scripts/deploy.sh dev
   ```

2. **Test the Application**
   - Open frontend URL
   - Test rebalancing workflow
   - Configure preferences
   - Monitor logs

3. **Optional Enhancements**
   - Set up custom domain
   - Enable Bedrock for LLM features
   - Configure CloudWatch alarms
   - Set up CI/CD pipeline

4. **Production Deployment**
   - Create production environment
   - Configure custom domain
   - Enable CloudFront
   - Set up monitoring and alerts

## Documentation

- **Full Guide**: `AWS_DEPLOYMENT_GUIDE.md` (500+ lines, comprehensive)
- **Quick Reference**: `AWS_QUICK_REFERENCE.md` (one-page commands)
- **Terraform README**: `infra/terraform/README.md`
- **Startup Guide**: `STARTUP_GUIDE.md` (local development)

## Support

### AWS Console Links
- **Lambda**: https://console.aws.amazon.com/lambda/
- **DynamoDB**: https://console.aws.amazon.com/dynamodb/
- **API Gateway**: https://console.aws.amazon.com/apigateway/
- **S3**: https://console.aws.amazon.com/s3/
- **CloudWatch**: https://console.aws.amazon.com/cloudwatch/

### Useful Commands
```bash
# Get all outputs
terraform -chdir=infra/terraform/environments/dev output

# Check AWS account
aws sts get-caller-identity

# List all resources
aws resourcegroupstaggingapi get-resources \
  --tag-filters Key=Project,Values=asset-management
```

## Summary

✅ **Infrastructure ready** - Terraform configuration updated with preferences table
✅ **Scripts ready** - Automated deployment script created
✅ **Documentation ready** - Comprehensive guides created
✅ **Prerequisites verified** - AWS CLI configured

**You're ready to deploy!** Run `./infra/scripts/deploy.sh dev` to get started.
