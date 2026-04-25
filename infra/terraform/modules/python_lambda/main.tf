resource "aws_cloudwatch_log_group" "this" {
  name              = "/aws/lambda/${var.function_name}"
  retention_in_days = 14
  tags              = var.tags
}

data "aws_iam_policy_document" "assume_role" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "this" {
  name               = "${var.function_name}-role"
  assume_role_policy = data.aws_iam_policy_document.assume_role.json
  tags               = var.tags
}

data "aws_iam_policy_document" "logs" {
  statement {
    actions = [
      "logs:CreateLogStream",
      "logs:PutLogEvents",
    ]
    resources = ["${aws_cloudwatch_log_group.this.arn}:*"]
  }
}

resource "aws_iam_role_policy" "logs" {
  name   = "${var.function_name}-logs"
  role   = aws_iam_role.this.id
  policy = data.aws_iam_policy_document.logs.json
}

resource "aws_iam_role_policy" "extra" {
  count  = var.attach_policy ? 1 : 0
  name   = "${var.function_name}-extra"
  role   = aws_iam_role.this.id
  policy = var.policy_json
}

resource "aws_lambda_function" "this" {
  function_name    = var.function_name
  description      = var.description
  role             = aws_iam_role.this.arn
  filename         = var.artifact_path
  source_code_hash = filebase64sha256(var.artifact_path)
  handler          = var.handler
  runtime          = var.runtime
  timeout          = var.timeout_seconds
  memory_size      = var.memory_mb
  tags             = var.tags

  environment {
    variables = var.environment_variables
  }

  depends_on = [
    aws_cloudwatch_log_group.this,
    aws_iam_role_policy.logs,
    aws_iam_role_policy.extra,
  ]
}
