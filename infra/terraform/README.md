# Terraform Infrastructure

Terraform is the IaC choice for this project.

## Layout

- `environments/dev/` - first deployable personal development environment.
- `modules/` - reusable AWS modules added as the deployment matures.

## Initial Usage

```shell
./infra/scripts/package_lambda.sh
cd infra/terraform/environments/dev
terraform init
terraform plan -var-file=dev.tfvars
terraform apply -var-file=dev.tfvars
```

Do not commit real `*.tfvars` files or Terraform state. Use `*.tfvars.example` for documented inputs.

For a local structural plan without configured AWS credentials, use temporary skip variables:

```shell
AWS_ACCESS_KEY_ID=dummy AWS_SECRET_ACCESS_KEY=dummy terraform plan \
  -refresh=false \
  -var-file=dev.tfvars.example \
  -var='skip_credentials_validation=true' \
  -var='skip_requesting_account_id=true' \
  -var='skip_metadata_api_check=true'
```

## Near-Term Resource Order

1. DynamoDB tables for approvals, audit events, portfolios, sessions, and memory queue.
2. IAM roles and policies for backend, research-agent, and sentiment MCP Lambdas.
3. Lambda packages and functions.
4. API Gateway HTTP routes to each Lambda-backed FastAPI service.
5. CloudWatch log groups, metrics, alarms, and retention.
6. Angular hosting target.

## Lambda Services

- Backend API: `backend/app/lambda_handler.handler`
- Remote Research Agent: `remote-agents/research-agent/app/lambda_handler.handler`
- Sentiment MCP Server: `mcp-servers/sentiment/app/lambda_handler.handler`

The dev environment expects package artifacts in `infra/build/`.

## Frontend Upload

After `terraform apply`, build Angular with the deployed API Gateway URL and upload it to S3:

```shell
cd infra/terraform/environments/dev
API_BASE=$(terraform output -raw api_base_url)
FRONTEND_BUCKET=$(terraform output -raw frontend_bucket_name)

cd ../../../../frontend
npm run build
printf "window.assetManagementConfig = {\\n  apiBaseUrl: '%s'\\n};\\n" "$API_BASE" \
  > dist/frontend/browser/app-config.js
aws s3 sync dist/frontend/browser "s3://${FRONTEND_BUCKET}" --delete
```

Open the deployed URL from:

```shell
terraform output -raw frontend_website_url
```
