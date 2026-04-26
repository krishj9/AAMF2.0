# AWS Deployment Quick Reference

One-page reference for common AWS deployment tasks.

## 🚀 Quick Deploy

```bash
# One-command deployment
./infra/scripts/deploy.sh dev
```

## 📋 Common Commands

### Deploy Infrastructure
```bash
# Package Lambda functions
./infra/scripts/package_lambda.sh

# Deploy with Terraform
cd infra/terraform/environments/dev
terraform init
terraform apply -var-file=dev.tfvars

# Deploy frontend
cd ../../../..
./infra/scripts/publish_frontend.sh \
  "$(terraform -chdir=infra/terraform/environments/dev output -raw api_base_url)" \
  "$(terraform -chdir=infra/terraform/environments/dev output -raw frontend_bucket_name)"
```

### Get URLs
```bash
# API Gateway URL
terraform -chdir=infra/terraform/environments/dev output -raw api_base_url

# Frontend URL
terraform -chdir=infra/terraform/environments/dev output -raw frontend_website_url

# All outputs
terraform -chdir=infra/terraform/environments/dev output
```

### Update Lambda Code
```bash
# Repackage and redeploy
./infra/scripts/package_lambda.sh
cd infra/terraform/environments/dev
terraform apply -var-file=dev.tfvars -target=module.backend_lambda
```

### Update Frontend
```bash
# Rebuild and redeploy
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

# Backend logs (last 10 minutes)
aws logs tail /aws/lambda/asset-management-dev-backend --since 10m

# Research agent logs
aws logs tail /aws/lambda/asset-management-dev-research-agent --follow

# Sentiment MCP logs
aws logs tail /aws/lambda/asset-management-dev-sentiment-mcp --follow
```

### Test Endpoints
```bash
# Get API URL
API_URL=$(terraform -chdir=infra/terraform/environments/dev output -raw api_base_url)

# Health check
curl "${API_URL}/health"

# List portfolios
curl "${API_URL}/api/portfolios"

# Get preferences
curl "${API_URL}/api/preferences/client_demo"

# Market stream (SSE)
curl -N "${API_URL}/api/market/stream"
```

### DynamoDB Operations
```bash
# List all tables
aws dynamodb list-tables --query 'TableNames[?contains(@, `asset-management-dev`)]'

# Scan portfolios
aws dynamodb scan --table-name asset-management-dev-portfolios --max-items 5

# Scan preferences
aws dynamodb scan --table-name asset-management-dev-preferences --max-items 5

# Get specific item
aws dynamodb get-item \
  --table-name asset-management-dev-portfolios \
  --key '{"account_id": {"S": "acct_demo"}}'

# Delete item
aws dynamodb delete-item \
  --table-name asset-management-dev-preferences \
  --key '{"client_id": {"S": "client_demo"}}'
```

### Lambda Operations
```bash
# List functions
aws lambda list-functions --query 'Functions[?contains(FunctionName, `asset-management-dev`)]'

# Get function configuration
aws lambda get-function-configuration \
  --function-name asset-management-dev-backend

# Update environment variable
aws lambda update-function-configuration \
  --function-name asset-management-dev-backend \
  --environment "Variables={SEED_DEFAULT_PORTFOLIOS=false}"

# Invoke function directly
aws lambda invoke \
  --function-name asset-management-dev-backend \
  --payload '{"rawPath": "/health", "requestContext": {"http": {"method": "GET"}}}' \
  response.json
cat response.json
```

### S3 Operations
```bash
# List bucket contents
BUCKET=$(terraform -chdir=infra/terraform/environments/dev output -raw frontend_bucket_name)
aws s3 ls "s3://${BUCKET}/"

# Download file
aws s3 cp "s3://${BUCKET}/app-config.js" -

# Upload file
aws s3 cp local-file.html "s3://${BUCKET}/file.html"

# Sync directory
aws s3 sync ./dist "s3://${BUCKET}/" --delete

# Empty bucket
aws s3 rm "s3://${BUCKET}" --recursive
```

## 🧹 Cleanup

### Destroy Everything
```bash
# Empty S3 bucket first
BUCKET=$(terraform -chdir=infra/terraform/environments/dev output -raw frontend_bucket_name)
aws s3 rm "s3://${BUCKET}" --recursive

# Destroy infrastructure
cd infra/terraform/environments/dev
terraform destroy -var-file=dev.tfvars
```

### Destroy Specific Resources
```bash
# Destroy only Lambda
terraform destroy -var-file=dev.tfvars -target=module.backend_lambda

# Destroy only DynamoDB table
terraform destroy -var-file=dev.tfvars -target=aws_dynamodb_table.preferences
```

## 🔍 Troubleshooting

### Check Lambda Errors
```bash
# Get recent errors
aws logs filter-log-events \
  --log-group-name /aws/lambda/asset-management-dev-backend \
  --filter-pattern "ERROR" \
  --max-items 10

# Get specific time range
aws logs filter-log-events \
  --log-group-name /aws/lambda/asset-management-dev-backend \
  --start-time $(date -u -d '1 hour ago' +%s)000 \
  --filter-pattern "ERROR"
```

### Check API Gateway Logs
```bash
# Enable logging first (if not already enabled)
API_ID=$(aws apigatewayv2 get-apis --query 'Items[?Name==`asset-management-dev-api`].ApiId' --output text)
aws apigatewayv2 get-stages --api-id "${API_ID}"
```

### Verify IAM Permissions
```bash
# Check Lambda execution role
aws iam get-role --role-name asset-management-dev-backend-role

# List attached policies
aws iam list-attached-role-policies --role-name asset-management-dev-backend-role

# Get policy document
POLICY_ARN=$(aws iam list-attached-role-policies --role-name asset-management-dev-backend-role --query 'AttachedPolicies[0].PolicyArn' --output text)
aws iam get-policy-version --policy-arn "${POLICY_ARN}" --version-id v1
```

### Test CORS
```bash
API_URL=$(terraform -chdir=infra/terraform/environments/dev output -raw api_base_url)

curl -X OPTIONS "${API_URL}/api/portfolios" \
  -H "Origin: http://localhost:4200" \
  -H "Access-Control-Request-Method: GET" \
  -v
```

## 📊 Monitoring

### CloudWatch Metrics
```bash
# Lambda invocations (last hour)
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Invocations \
  --dimensions Name=FunctionName,Value=asset-management-dev-backend \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Sum

# Lambda errors
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Errors \
  --dimensions Name=FunctionName,Value=asset-management-dev-backend \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Sum

# DynamoDB consumed capacity
aws cloudwatch get-metric-statistics \
  --namespace AWS/DynamoDB \
  --metric-name ConsumedReadCapacityUnits \
  --dimensions Name=TableName,Value=asset-management-dev-portfolios \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Sum
```

### Cost Monitoring
```bash
# Get current month costs
aws ce get-cost-and-usage \
  --time-period Start=$(date +%Y-%m-01),End=$(date +%Y-%m-%d) \
  --granularity MONTHLY \
  --metrics BlendedCost \
  --group-by Type=SERVICE

# Get Lambda costs
aws ce get-cost-and-usage \
  --time-period Start=$(date +%Y-%m-01),End=$(date +%Y-%m-%d) \
  --granularity MONTHLY \
  --metrics BlendedCost \
  --filter file://<(echo '{"Dimensions":{"Key":"SERVICE","Values":["AWS Lambda"]}}')
```

## 🔐 Security

### Rotate Credentials
```bash
# Create new access key
aws iam create-access-key --user-name your-username

# Delete old access key
aws iam delete-access-key --user-name your-username --access-key-id OLD_KEY_ID
```

### Enable MFA
```bash
# List MFA devices
aws iam list-mfa-devices --user-name your-username

# Enable virtual MFA
aws iam enable-mfa-device \
  --user-name your-username \
  --serial-number arn:aws:iam::ACCOUNT:mfa/your-username \
  --authentication-code1 CODE1 \
  --authentication-code2 CODE2
```

## 📚 Resources

- **Full Guide**: `AWS_DEPLOYMENT_GUIDE.md`
- **Terraform Docs**: `infra/terraform/README.md`
- **Startup Guide**: `STARTUP_GUIDE.md`
- **AWS Console**: https://console.aws.amazon.com/

## 💡 Tips

- Use `--profile` flag to switch AWS accounts: `aws --profile prod ...`
- Use `--region` flag to override default region: `aws --region us-west-2 ...`
- Use `--output json` for machine-readable output: `aws ... --output json | jq`
- Use `--query` for filtering: `aws ... --query 'Items[0].Name'`
- Use `--dry-run` to test commands without executing: `aws ... --dry-run`
