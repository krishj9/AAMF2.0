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
