variable "function_name" {
  description = "Lambda function name."
  type        = string
}

variable "description" {
  description = "Lambda function description."
  type        = string
  default     = ""
}

variable "artifact_path" {
  description = "Path to the Lambda deployment package zip."
  type        = string
}

variable "handler" {
  description = "Lambda handler path."
  type        = string
}

variable "runtime" {
  description = "Lambda runtime."
  type        = string
  default     = "python3.13"
}

variable "timeout_seconds" {
  description = "Lambda timeout in seconds."
  type        = number
  default     = 30
}

variable "memory_mb" {
  description = "Lambda memory size in MB."
  type        = number
  default     = 512
}

variable "environment_variables" {
  description = "Environment variables for the Lambda function."
  type        = map(string)
  default     = {}
}

variable "policy_json" {
  description = "Optional IAM policy JSON attached to the Lambda role."
  type        = string
  default     = null
}

variable "attach_policy" {
  description = "Whether to attach the optional IAM policy JSON."
  type        = bool
  default     = false
}

variable "tags" {
  description = "Tags applied to resources."
  type        = map(string)
  default     = {}
}
