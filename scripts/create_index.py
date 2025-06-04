import os
import json
import requests
from requests_aws4auth import AWS4Auth
import boto3

# Setup: use AWS_PROFILE if provided
region = os.environ.get("REGION", "us-east-1")
service = "es"
session = boto3.Session(profile_name=os.environ.get("AWS_PROFILE", "default"))
credentials = session.get_credentials()
auth = AWS4Auth(
    credentials.access_key,
    credentials.secret_key,
    region,
    service,
    session_token=credentials.token,
)

# Env vars required:
OPENSEARCH_ENDPOINT = os.environ["OPENSEARCH"]
INDEX_NAME = "documents"
VECTOR_DIM = 1024  # Titan embeddings

index_config = {
    "settings": {
        "index": {
            "knn": True
        }
    },
    "mappings": {
        "properties": {
            "text": {"type": "text"},
            "embedding": {
                "type": "knn_vector",
                "dimension": VECTOR_DIM
            }
        }
    }
}

# Send signed request to create index
url = f"{OPENSEARCH_ENDPOINT}/{INDEX_NAME}"
response = requests.put(
    url,
    auth=auth,
    json=index_config,
    headers={"Content-Type": "application/json"}
)

print(f"Create index response: {response.status_code}")
print(response.text)

print(json.dumps({
    "status_code": response.status_code,
    "reason": response.reason,
    "url": url,
    "response_text": response.text
}, indent=2))