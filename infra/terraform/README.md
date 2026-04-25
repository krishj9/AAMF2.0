# Terraform Infrastructure

Terraform is the IaC choice for this project.

## Layout

- `environments/dev/` - first deployable personal development environment.
- `modules/` - reusable AWS modules added as the deployment matures.

## Initial Usage

```shell
cd infra/terraform/environments/dev
terraform init
terraform plan -var-file=dev.tfvars
```

Do not commit real `*.tfvars` files or Terraform state. Use `*.tfvars.example` for documented inputs.

## Near-Term Resource Order

1. DynamoDB tables for approvals, audit events, sessions, and memory queue.
2. IAM role and policy for the orchestrator Lambda.
3. Lambda package and function.
4. API Gateway route to Lambda.
5. CloudWatch log groups, metrics, alarms, and retention.
6. Angular hosting target.
