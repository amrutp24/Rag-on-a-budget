import os
import json
import boto3
import requests
from requests_aws4auth import AWS4Auth

BEDROCK_REGION = os.environ.get("REGION", "us-east-1")
OPENSEARCH_ENDPOINT = os.environ.get("OPENSEARCH")

# Setup AWS SigV4 signing
aws_session = boto3.Session(profile_name=os.environ.get("AWS_PROFILE", "dev"))
credentials = aws_session.get_credentials()
auth = AWS4Auth(
    credentials.access_key,
    credentials.secret_key,
    BEDROCK_REGION,
    "es",
    session_token=credentials.token,
)

def embed_text(text):
    bedrock = boto3.client("bedrock-runtime", region_name=BEDROCK_REGION)
    response = bedrock.invoke_model(
        modelId="amazon.titan-embed-text-v2:0",
        body=json.dumps({"inputText": text}),
        contentType="application/json",
        accept="application/json"
    )
    return json.loads(response["body"].read())["embedding"]

def index_document(doc_id, text):
    embedding = embed_text(text)
    print(f"Embedding length for {doc_id}: {len(embedding)}")
    document = {
        "text": text,
        "embedding": embedding
    }
    response = requests.put(
        f"{OPENSEARCH_ENDPOINT}/documents/_doc/{doc_id}",
        auth=auth,
        json=document,
        headers={"Content-Type": "application/json"}
    )
    print(f"Indexed {doc_id}: {response.status_code}")

def main():
    docs = [
        {"id": "doc1", "text": "Amazon Web Services provides on-demand cloud computing platforms."},
        {"id": "doc2", "text": "OpenSearch is a distributed search and analytics suite."},
        {"id": "doc3", "text": "Retrieval-Augmented Generation enhances language models by grounding outputs in external data."}
    ]

    for doc in docs:
        index_document(doc["id"], doc["text"])

if __name__ == "__main__":
    main()
