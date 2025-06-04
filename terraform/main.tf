resource "aws_s3_bucket" "lambda_bucket" {
  bucket = "rag-lambda-artifacts"
}

# data "archive_file" "lambda_package" {
#   type        = "zip"
#   source_file = "${path.module}/../lambda/handler.py"
#   output_path = "${path.module}/rag-lambda.zip"
#}

resource "aws_s3_object" "lambda_zip" {
  bucket = aws_s3_bucket.lambda_bucket.id
  key    = "rag-lambda.zip"
  source = "rag-lambda.zip"#data.archive_file.lambda_package.output_path
  source_hash = filebase64sha256("rag-lambda.zip")#data.archive_file.lambda_package.output_base64sha256
}


resource "aws_iam_role" "lambda_exec_role" {
  name = "rag_lambda_exec_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect = "Allow",
      Principal = {
        Service = "lambda.amazonaws.com"
      },
      Action = "sts:AssumeRole"
    }]
  })

  inline_policy {
    name = "AllowInvokeBedrock"

    policy = jsonencode({
      Version = "2012-10-17",
      Statement = [
        {
          Effect = "Allow",
          Action = "bedrock:InvokeModel",
          Resource = [
            "arn:aws:bedrock:${var.aws_region}::foundation-model/amazon.titan-embed-text-v2:0",
            "arn:aws:bedrock:${var.aws_region}::foundation-model/anthropic.claude-v2:1",
            "*"
          ]
        }
      ]
    })
  }
}

resource "aws_iam_role_policy_attachment" "lambda_basic_execution" {
  role       = aws_iam_role.lambda_exec_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_lambda_function" "rag_function" {
  function_name = "rag-handler"
  role          = aws_iam_role.lambda_exec_role.arn
  handler       = "handler.lambda_handler"
  runtime       = "python3.12"

  s3_bucket = aws_s3_bucket.lambda_bucket.bucket
  s3_key    = "rag-lambda.zip"

  memory_size = 1024
  timeout     = 30

  environment {
    variables = {
      REGION     = var.aws_region
      OPENSEARCH = var.opensearch_endpoint
    }
  }
}

resource "aws_opensearch_domain" "rag_search" {
  domain_name           = "rag-opensearch"
  engine_version        = "OpenSearch_2.11"

  cluster_config {
    instance_type  = "t3.small.search"
    instance_count = 1
  }

  ebs_options {
    ebs_enabled = true
    volume_size = 10
  }

  encrypt_at_rest {
    enabled = true
  }


  node_to_node_encryption {
    enabled = true
  }
  domain_endpoint_options {
    enforce_https = true
  }


  advanced_security_options {
    enabled                        = true
    internal_user_database_enabled = false

    master_user_options {
      master_user_arn = var.opensearch_master_user_arn
    }
  }

  access_policies = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect = "Allow",
      Principal = {
        "AWS": [
          var.opensearch_master_user_arn,
          aws_iam_role.lambda_exec_role.arn,
          "arn:aws:iam::${data.aws_caller_identity.current.account_id}:user/iamadmin"
        ]
      },
      Action = ["es:*"],
      Resource = "arn:aws:es:${var.aws_region}:${data.aws_caller_identity.current.account_id}:domain/rag-opensearch/*"
    }]
  })
}

resource "aws_apigatewayv2_api" "rag_api" {
  name          = "rag-api"
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_integration" "lambda_integration" {
  api_id             = aws_apigatewayv2_api.rag_api.id
  integration_type   = "AWS_PROXY"
  integration_uri    = aws_lambda_function.rag_function.invoke_arn
  integration_method = "POST"
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "default_route" {
  api_id    = aws_apigatewayv2_api.rag_api.id
  route_key = "POST /query"
  target    = "integrations/${aws_apigatewayv2_integration.lambda_integration.id}"
}

resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.rag_api.id
  name        = "$default"
  auto_deploy = true
}

resource "aws_lambda_permission" "allow_apigw" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.rag_function.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.rag_api.execution_arn}/*/*"
}
