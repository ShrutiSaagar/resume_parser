import boto3
from botocore.exceptions import ClientError

# Create Bedrock client with your profile/region
session = boto3.Session(profile_name='nisarga')
# bedrock = session.client('bedrock-runtime', region_name='us-east-2')
bedrock = session.client('bedrock-runtime', region_name='us-east-2')

model_id = "us.anthropic.claude-3-7-sonnet-20250219-v1:0"
prompt = "how is the weather today?"

try:
    response = bedrock.converse(
        modelId=model_id,
        messages=[
            {
                "role": "user",
                "content": [{"text": prompt}]
            }
        ],
        inferenceConfig={
            "maxTokens": 512,
            "temperature": 0.5,
            "topP": 0.9
        }
    )
    
    # Extract response text
    response_text = response['output']['message']['content'][0]['text']
    print(response_text)

except ClientError as e:
    print(f"API Error: {e.response['Error']['Message']}")
except Exception as e:
    print(f"Unexpected error: {str(e)}")
