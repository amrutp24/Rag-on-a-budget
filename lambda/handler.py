
from requests_aws4auth import AWS4Auth
import os
import json
import boto3
import requests

BEDROCK_MODEL_ID = "anthropic.claude-v2"  # Replace with your preferred model
BEDROCK_REGION = os.environ.get("REGION")
OPENSEARCH_ENDPOINT = os.environ.get("OPENSEARCH")

def lambda_handler(event, context):
    query = event.get("query") or event.get("body")
    if not query:
        return {"statusCode": 400, "body": "Query is required"}

    # Set up AWS auth
    session = boto3.Session()
    credentials = session.get_credentials()
    auth = AWS4Auth(
        credentials.access_key,
        credentials.secret_key,
        BEDROCK_REGION,
        "es",
        session_token=credentials.token,
    )

    # Embed query
    bedrock = session.client("bedrock-runtime", region_name=BEDROCK_REGION)
    embedding_input = {"inputText": query}
    embedding_response = bedrock.invoke_model(
        modelId="amazon.titan-embed-text-v2:0",
        body=json.dumps(embedding_input),
        contentType="application/json",
        accept="application/json"
    )
    embedding = json.loads(embedding_response["body"].read())["embedding"]

    # Query OpenSearch
    search_payload = {
        "size": 3,
        "query": {
            "knn": {
                "embedding": {
                    "vector": embedding,
                    "k": 3
                }
            }
        }
    }
    response = requests.post(
        f"{OPENSEARCH_ENDPOINT}/documents/_search",
        json=search_payload,
        auth=auth,
        headers={"Content-Type": "application/json"}
    )
    if response.status_code != 200:
        return {"statusCode": response.status_code, "body": response.text}

    results = response.json()
    context_chunks = "".join([hit["_source"]["text"] for hit in results["hits"]["hits"]])

    # Generate answer with context
    prompt = f"Human: Answer the question using the context below:\n{context_chunks}\n\nQuestion: {query}\n\nAssistant:"
    completion_response = bedrock.invoke_model(
        modelId="anthropic.claude-v2:1",
        body=json.dumps({"prompt": prompt, "max_tokens_to_sample": 200}),
        contentType="application/json",
        accept="application/json"
    )
    result_text = json.loads(completion_response["body"].read())["completion"]

    #return {"statusCode": 400, "body": "Query is required"}
    return {
        "statusCode": 200,
        "body": json.dumps({"answer": result_text})
    }