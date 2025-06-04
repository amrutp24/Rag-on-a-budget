import boto3
from requests_aws4auth import AWS4Auth
import requests

region = "us-east-1"  # your region
service = "es"

session = boto3.Session(profile_name="dev")  # or leave empty for default
credentials = session.get_credentials()
auth = AWS4Auth(
    credentials.access_key,
    credentials.secret_key,
    region,
    service,
    session_token=credentials.token
)

# DELETE request to remove index
endpoint = #"https://your-opensearch-endpoint"
index = "documents"
response = requests.delete(f"{endpoint}/{index}", auth=auth)
print(response.status_code, response.text)
