# RAG on a Budget 🚀

This project demonstrates a lightweight and cost-effective Retrieval-Augmented Generation (RAG) system using:

- **Amazon Titan Text Embeddings V2** for embeddings
- **OpenSearch Serverless** for vector search
- **Anthropic Claude** for final answer generation
- **AWS Lambda** for inference logic
- **API Gateway** to expose the RAG system as a public API
- **Terraform** for infrastructure management

---

## Project Structure

```
.
├── lambda/
│   └── handler.py              # Main Lambda function for end-to-end RAG
├── scripts/
│   ├── create_index.py         # Creates index in OpenSearch with vector mapping
│   └── embed_documents.py      # Embeds and indexes sample documents
├── terraform/
│   └── main.tf                 # Infrastructure: Lambda, API Gateway, OpenSearch, S3
└── README.md                   # You are here
```

---

## 🧪 Setup Instructions

### 1. Clone and Configure
```bash
git clone https://github.com/<your-username>/rag-on-a-budget.git
cd rag-on-a-budget
```

### 2. Set Environment Variables

```bash
export REGION=us-east-1
export OPENSEARCH=<your-opensearch-endpoint>
export AWS_PROFILE=<your-aws-profile>
```

### 3. Create OpenSearch Index

```bash
python scripts/create_index.py
```

### 4. Embed Documents

```bash
python scripts/embed_documents.py
```

### 5. Deploy Lambda using Terraform

```bash
cd terraform
terraform init
terraform apply
```

This zips the handler, installs required Python packages (like `requests` and `requests_aws4auth`), uploads to S3, and deploys the Lambda function with correct IAM role and API Gateway setup.

---

## 📡 Example cURL Request

```bash
curl -X POST https://<api-id>.execute-api.us-east-1.amazonaws.com/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is OpenSearch?"}'
```

---

## 🧯 Known Issues and Troubleshooting

| Issue | Description | Fix |
|-------|-------------|------|
| `403 Forbidden` from OpenSearch | IAM role missing `es:*` permissions or role not mapped in OpenSearch | Update `access_policies` and map role in OpenSearch |
| `AccessDeniedException` from Bedrock | Lambda role missing access to model | Add inline policy with `bedrock:InvokeModel` |
| Vector dimension mismatch (`1024` vs `1536`) | Titan V2 supports multiple sizes; mismatch causes search error | Ensure consistent embedding size and index dimension |
| `No module named 'requests'` in Lambda | Python packages not bundled | Use Terraform to install dependencies and zip |
| `Claude prompt` error | Claude requires `Human:` in prompt | Format prompt accordingly |

---

## 🧠 Why both Titan and Claude?

- Titan V2 is used for generating embeddings.
- Claude is used for generating answers based on retrieved context.

---

## 🧼 Clean Up

```bash
terraform destroy
```

---

## 📜 License

MIT
