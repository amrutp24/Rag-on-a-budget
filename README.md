# RAG on a Budget

A minimal Retrieval-Augmented Generation (RAG) system using **AWS Lambda**, **Amazon Bedrock**, and **OpenSearch** — optimized for low cost and simplicity.

---

## 🧠 What It Does

- **Embeds documents** using `amazon.titan-embed-text-v2` (1024-d).
- **Stores** those embeddings in an OpenSearch index with KNN enabled.
- **Handles queries** by embedding the input, retrieving top-k similar docs, and generating a response using `anthropic.claude-v2`.

---

## ⚖️ Stack

- **Compute**: AWS Lambda (Python 3.12)
- **Embedding**: Amazon Titan Embedding V2 (1024-d)
- **Vector DB**: OpenSearch with `knn_vector`
- **LLM Completion**: Claude v2 via Bedrock
- **Infra-as-Code**: Terraform

---

## ⚙️ Setup

### Prerequisites

- Python 3.10+
- AWS CLI configured (`aws configure`)
- Terraform v1.5+
- Bedrock access to Titan and Claude
- IAM user or role with permission for:
  - `bedrock:InvokeModel`
  - `es:*` (for OpenSearch)
  - `lambda:*`, `iam:*`, `s3:*`

---

## 🚀 Deployment Steps

### 1. Deploy Infrastructure

```bash
terraform init
terraform apply
