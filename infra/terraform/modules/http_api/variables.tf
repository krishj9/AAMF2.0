variable "name" {
  description = "HTTP API name."
  type        = string
}

variable "stage_name" {
  description = "API Gateway stage name."
  type        = string
  default     = "$default"
}

variable "routes" {
  description = "Route definitions keyed by a stable route identifier."
  type = map(object({
    route_key          = string
    lambda_invoke_arn  = string
    lambda_function_arn = string
    lambda_function_name = string
  }))
}

variable "cors_allow_origins" {
  description = "Allowed CORS origins."
  type        = list(string)
  default     = ["*"]
}

variable "tags" {
  description = "Tags applied to resources."
  type        = map(string)
  default     = {}
}
