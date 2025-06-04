# RAG on a Budget 🚀

A lightweight Retrieval-Augmented Generation (RAG) system built using:
- **Amazon Bedrock** for text embedding and LLM inference
- **OpenSearch** for semantic search
- **AWS Lambda** for serverless execution
- **API Gateway** for exposing a simple HTTP interface
- **Terraform** for fully automated IaC deployment

## 🧠 What It Does

This project takes in a natural language question via an API endpoint, embeds it using **Amazon Titan Text Embeddings V2**, performs a similarity search using **OpenSearch**, and uses **Anthropic Claude v2** via Bedrock to answer based on the top-k retrieved documents.

## 📁 Project Structure

```
.
├── lambda/
│   └── handler.py               # Lambda entrypoint
├── scripts/
│   ├── create_index.py         # Creates OpenSearch index with knn_vector mapping
│   └── embed_documents.py      # Embeds and indexes a few seed documents
├── terraform/
│   └── main.tf                 # All infrastructure defined here
└── README.md
```

## 🛠️ Setup & Deployment

### 1. Clone and Set Up

```bash
git clone https://github.com/your-username/rag-on-a-budget.git
cd rag-on-a-budget
```

### 2. Create `.env` (optional for local testing)

```dotenv
REGION=us-east-1
OPENSEARCH=https://your-opensearch-endpoint
AWS_PROFILE=your-profile-name
```

### 3. Deploy Infra with Terraform

```bash
cd terraform
terraform init
terraform apply
```

This sets up:
- OpenSearch domain with KNN index
- Lambda function packaged with dependencies
- API Gateway endpoint

### 4. Create and Populate Index

```bash
python scripts/create_index.py
python scripts/embed_documents.py
```

### 5. Test the Endpoint

```bash
curl -X POST https://<api-id>.execute-api.<region>.amazonaws.com/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is OpenSearch?"}'
```

## 🧩 Models Used

- **Embedding**: `amazon.titan-embed-text-v2:0` — 1024-dim vector
- **LLM**: `anthropic.claude-v2:1` — used for natural language answer generation

## 🔐 IAM & Permissions

Ensure the Lambda execution role has permission to:
- `bedrock:InvokeModel` for both Titan and Claude
- `es:*` for the OpenSearch domain (use fine-grained if needed)

## 📌 Notes

- This is optimized for low-cost experimentation: serverless compute + small OpenSearch node
- Embedding vector size must match the OpenSearch index dimension
- Document and query vectors are normalized for similarity comparison

## 🧼 Cleanup

To tear everything down:

```bash
cd terraform
terraform destroy
```

---

## 👨‍💻 Author

Built by [Your Name](https://github.com/your-username)  
Inspired by AWS Bedrock, OpenSearch, and the RAG architecture pattern.
