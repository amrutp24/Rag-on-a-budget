variable "aws_region" {
  description = "The AWS region to deploy to"
  type        = string
  default     = "us-east-1"
}

variable "opensearch_endpoint" {
  description = "The OpenSearch endpoint URL"
  type        = string
}

variable "opensearch_master_user_arn" {
  description = "The ARN of the IAM user that will be the OpenSearch master user"
  type        = string
}