# output "lambda_function_name" {
#   description = "The name of the Lambda function"
#   value       = aws_lambda_function.rag_function.function_name
# }

# output "lambda_iam_role_arn" {
#   description = "The ARN of the Lambda execution role"
#   value       = aws_iam_role.lambda_exec_role.arn
# }

# output "s3_bucket_name" {
#   description = "The name of the S3 bucket for Lambda artifacts"
#   value       = aws_s3_bucket.lambda_bucket.id
# }

# output "opensearch_endpoint" {
#   value = aws_opensearch_domain.rag_search.endpoint
# }