output "name_prefix" {
  description = "Resource name prefix for this environment."
  value       = local.name_prefix
}

output "dynamodb_table_names" {
  description = "DynamoDB table names for workflow persistence."
  value       = local.dynamodb_tables
}
