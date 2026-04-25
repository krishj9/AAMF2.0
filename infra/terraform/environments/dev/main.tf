locals {
  name_prefix = "${var.project_name}-${var.environment}"

  dynamodb_tables = {
    approvals    = "${local.name_prefix}-approvals"
    audit_events = "${local.name_prefix}-audit-events"
    portfolios   = "${local.name_prefix}-portfolios"
    sessions     = "${local.name_prefix}-sessions"
    memory_queue = "${local.name_prefix}-memory-queue"
  }
}

resource "aws_dynamodb_table" "approvals" {
  name         = local.dynamodb_tables.approvals
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "approval_id"

  attribute {
    name = "approval_id"
    type = "S"
  }

  ttl {
    attribute_name = "ttl"
    enabled        = true
  }
}

resource "aws_dynamodb_table" "audit_events" {
  name         = local.dynamodb_tables.audit_events
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "event_id"

  attribute {
    name = "event_id"
    type = "S"
  }

  ttl {
    attribute_name = "ttl"
    enabled        = true
  }
}

resource "aws_dynamodb_table" "portfolios" {
  name         = local.dynamodb_tables.portfolios
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "account_id"

  attribute {
    name = "account_id"
    type = "S"
  }
}

resource "aws_dynamodb_table" "sessions" {
  name         = local.dynamodb_tables.sessions
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "session_id"

  attribute {
    name = "session_id"
    type = "S"
  }

  ttl {
    attribute_name = "ttl"
    enabled        = true
  }
}

resource "aws_dynamodb_table" "memory_queue" {
  name         = local.dynamodb_tables.memory_queue
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "task_id"

  attribute {
    name = "task_id"
    type = "S"
  }

  ttl {
    attribute_name = "ttl"
    enabled        = true
  }
}
