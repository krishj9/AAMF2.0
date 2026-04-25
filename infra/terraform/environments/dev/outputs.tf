output "name_prefix" {
  description = "Resource name prefix for this environment."
  value       = local.name_prefix
}

output "dynamodb_table_names" {
  description = "DynamoDB table names for workflow persistence."
  value       = local.dynamodb_tables
}

output "api_base_url" {
  description = "API Gateway HTTP API base URL."
  value       = module.http_api.api_endpoint
}

output "lambda_function_names" {
  description = "Lambda function names."
  value = {
    backend        = module.backend_lambda.function_name
    research_agent = module.research_agent_lambda.function_name
    sentiment_mcp  = module.sentiment_mcp_lambda.function_name
  }
}

output "cloudwatch_log_group_names" {
  description = "CloudWatch log group names."
  value = {
    backend        = module.backend_lambda.log_group_name
    research_agent = module.research_agent_lambda.log_group_name
    sentiment_mcp  = module.sentiment_mcp_lambda.log_group_name
  }
}

output "frontend_bucket_name" {
  description = "S3 bucket hosting the Angular frontend."
  value       = aws_s3_bucket.frontend.bucket
}

output "frontend_website_endpoint" {
  description = "S3 website endpoint for the Angular frontend."
  value       = aws_s3_bucket_website_configuration.frontend.website_endpoint
}

output "frontend_website_url" {
  description = "HTTP URL for the Angular frontend."
  value       = "http://${aws_s3_bucket_website_configuration.frontend.website_endpoint}"
}
