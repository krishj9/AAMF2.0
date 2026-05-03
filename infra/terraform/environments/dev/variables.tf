variable "aws_region" {
  description = "AWS region for the dev environment."
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project tag and resource name prefix."
  type        = string
  default     = "asset-management"
}

variable "environment" {
  description = "Deployment environment name."
  type        = string
  default     = "dev"

  validation {
    condition     = contains(["dev", "test", "staging", "main"], var.environment)
    error_message = "Environment must be one of: dev, test, staging, main."
  }
}

variable "lambda_runtime" {
  description = "Python runtime for Lambda functions."
  type        = string
  default     = "python3.13"
}

variable "lambda_artifact_dir" {
  description = "Directory containing Lambda zip artifacts."
  type        = string
  default     = "../../../build"
}

variable "cors_allow_origins" {
  description = "Allowed CORS origins for the HTTP API."
  type        = list(string)
  default     = ["*"]
}

variable "frontend_bucket_name" {
  description = "Optional S3 bucket name for the Angular static website."
  type        = string
  default     = null
}

variable "skip_credentials_validation" {
  description = "Skip AWS credential validation for local structural plans."
  type        = bool
  default     = false
}

variable "skip_requesting_account_id" {
  description = "Skip AWS account ID lookup for local structural plans."
  type        = bool
  default     = false
}

variable "skip_metadata_api_check" {
  description = "Skip EC2 metadata API credential checks for local structural plans."
  type        = bool
  default     = false
}

variable "api_token" {
  description = "Shared API token required in x-api-token header for all API requests."
  type        = string
  sensitive   = true
}
