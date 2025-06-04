import boto3, json
client = boto3.client("bedrock-runtime", region_name="us-east-1")
session = boto3.Session(profile_name="dev")  
bedrock = session.client("bedrock-runtime", region_name="us-east-1")
resp = client.invoke_model(
    modelId="amazon.titan-embed-text-v2:0",
    body=json.dumps({"inputText": "test"}), 
    contentType="application/json",
    accept="application/json"
)

response = bedrock.invoke_model(
    modelId="amazon.titan-embed-text-v2:0",
    body=json.dumps({"inputText": "hello"}),
    contentType="application/json",
    accept="application/json"
)
vec = json.loads(resp['body'].read())['embedding']
print(len(vec))  # Should print 1536
print(json.loads(response["body"].read()))
