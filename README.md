# RAG on a Budget

A small retrieval-augmented generation (RAG) setup on AWS. A question comes in through API Gateway, a Lambda function embeds it with Amazon Titan, finds the closest documents in OpenSearch, and asks Claude on Bedrock to answer using those documents.

Written up in [Building RAG on a Budget Using AWS Lambda, Bedrock & OpenSearch](https://amruteng.medium.com/building-rag-on-a-budget-using-aws-lambda-bedrock-opensearch-1f17d46b7b17).

## How it works

- **Embeddings:** Amazon Titan Text Embeddings V2 (`amazon.titan-embed-text-v2:0`), 1024 dimensions
- **Vector search:** an OpenSearch domain with one `t3.small.search` node and a 10 GB volume, using a k-NN index called `documents`
- **Answers:** Claude 2.1 on Bedrock (`anthropic.claude-v2:1`), using the top 3 matching documents as context
- **API:** API Gateway HTTP API, `POST /query`
- **Infrastructure:** Terraform

The "budget" part is the single small OpenSearch node instead of OpenSearch Serverless, whose minimum capacity costs far more. A `t3.small.search` node is also covered by the AWS free tier on new accounts.

## What's in the repo

```
.
├── lambda/
│   └── handler.py           # embeds the question, searches OpenSearch, calls Claude
├── scripts/
│   ├── create_index.py      # creates the k-NN index
│   ├── embed_documents.py   # embeds and indexes three sample documents
│   ├── delete.py            # deletes the index (set the endpoint in the file first)
│   └── sanity.py            # checks that Titan embeddings work from your machine
└── terraform/
    ├── main.tf              # S3 bucket, Lambda, IAM role, OpenSearch domain, API Gateway
    ├── variables.tf
    ├── rag-lambda.zip       # prebuilt Lambda package: handler.py plus requests and requests_aws4auth
    └── ...
```

Terraform deploys `rag-lambda.zip` as committed. If you change `handler.py`, rebuild the zip with the handler and its dependencies before applying.

## Before you deploy

A few values in `terraform/main.tf` are specific to my account. Change them first:

- The S3 bucket name, `rag-lambda-artifacts`. Bucket names are global, so this one is taken.
- The OpenSearch access policy allows an IAM user called `iamadmin`. Replace it with a user or role in your account, or remove it.

You also need Bedrock model access for Titan Text Embeddings V2 and Claude 2.1 in your region.

## Deploy

The Lambda needs the OpenSearch endpoint, but Terraform is what creates the domain, so the first deploy takes two applies.

```bash
cd terraform
terraform init

# 1. Create everything. The endpoint isn't known yet, so pass a placeholder.
#    The OpenSearch domain takes 15 to 20 minutes.
terraform apply \
  -var "opensearch_master_user_arn=<your IAM user or role ARN>" \
  -var "opensearch_endpoint=https://placeholder"

# 2. Get the real endpoint and apply again so the Lambda gets it.
ENDPOINT="https://$(aws opensearch describe-domain --domain-name rag-opensearch \
  --query 'DomainStatus.Endpoint' --output text)"
terraform apply \
  -var "opensearch_master_user_arn=<your IAM user or role ARN>" \
  -var "opensearch_endpoint=$ENDPOINT"
```

The domain has fine-grained access control turned on, so the Lambda's role, `rag_lambda_exec_role`, also has to be mapped to an OpenSearch role (for example `all_access`) in OpenSearch Dashboards under Security, Roles. Without that, searches return 403.

Then create the index and load the sample documents, using the same AWS profile as the master user:

```bash
export REGION=us-east-1
export OPENSEARCH="$ENDPOINT"
export AWS_PROFILE=<your profile>

python scripts/create_index.py
python scripts/embed_documents.py
```

The scripts need `boto3`, `requests` and `requests-aws4auth`.

## Asking a question

```bash
curl -X POST https://<api-id>.execute-api.us-east-1.amazonaws.com/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is OpenSearch?"}'
```

The response is `{"answer": "..."}`.

## Troubleshooting

| Problem | Cause and fix |
| --- | --- |
| `403 Forbidden` from OpenSearch | The caller isn't in the domain's access policy, or the Lambda role isn't mapped to an OpenSearch role. |
| `AccessDeniedException` from Bedrock | Model access isn't enabled for Titan or Claude in that region. |
| Vector dimension mismatch | The index is 1024 dimensions, Titan V2's default. Embeddings of another size won't match. |
| `No module named 'requests'` in Lambda | The deployed zip is missing dependencies. Rebuild `rag-lambda.zip` with them. |
| Claude rejects the prompt | Claude 2.1's text-completion API needs the `Human:` / `Assistant:` format the handler uses. |

Claude 2.1 is an old model. Moving to a current Claude model means switching the handler to Bedrock's Messages API.

## Clean up

```bash
cd terraform
terraform destroy \
  -var "opensearch_master_user_arn=<your IAM user or role ARN>" \
  -var "opensearch_endpoint=$ENDPOINT"
```

## License

MIT
