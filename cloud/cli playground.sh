aws bedrock  create-inference-profile --profile nisarga --inference-profile-name CliIProfile --model-source us.anthropic.claude-3-haiku-20240307-v1:0

aws bedrock create-inference-profile --profile nisarga --inference-profile-name CliIProfile --model-source=us.anthropic.claude-3-haiku-20240307-v1:0

aws bedrock create-inference-profile --profile=nisarga --inference-profile-name=CliIProfile --model-source=us.anthropic.claude-3-5-haiku-20241022-v1:0



aws bedrock-runtime invoke-model --profile nisarga --model-id "us.anthropic.claude-3-5-haiku-20241022-v1:0" --body '{"prompt": "what can you do?"}' --accept application/json --content-type application/json --region us-east-2 --debug outfile

aws bedrock-runtime invoke-model --profile nisarga --model-id "us.anthropic.claude-3-5-haiku-20241022-v1:0" --body eyJwcm9tcHQiOiAid2hhdCBjYW4geW91IGRvPyIsICJtYXhfdG9rZW5zX3RvX3NhbXBsZSI6IDUwfQ== --accept application/json --content-type application/json --region us-east-2 --debug outfile

aws bedrock-runtime invoke-model --cli-binary-format raw-in-base64-out --profile nisarga --model-id "us.anthropic.claude-3-5-haiku-20241022-v1:0" --body '{"prompt": "what can you do?", "max_tokens_to_sample": 50}' --accept application/json --content-type application/json --region us-east-2 outfile


echo -n '{"prompt": "what can you do?", "max_tokens_to_sample": 50}' | base64

aws bedrock-runtime invoke-model --cli-binary-format raw-in-base64-out --profile nisarga --model-id "us.anthropic.claude-3-5-haiku-20241022-v1:0" --body '{"prompt": "Human: what can you do?", "max_tokens_to_sample": 50}' --accept application/json --content-type application/json --region us-east-2 outfile

aws bedrock-runtime invoke-model --cli-binary-format raw-in-base64-out --profile nisarga --model-id "us.anthropic.claude-3-5-haiku-20241022-v1:0" --body '{"prompt": "Human: what can you do?\n\nAssistant:", "max_tokens_to_sample": 50}' --accept application/json --content-type application/json --region us-east-2 outfile



aws bedrock-runtime converse \
--profile nisarga \
--model-id "anthropic.claude-3-5-haiku-20241022-v1:0" \
--region us-east-2 \
--messages '[{"role": "user", "content": [{"text": "what can you do?"}]}]' \
--query "output.content[0].text" \
--output text



aws bedrock-runtime converse \
--profile nisarga \
--model-id "anthropic.claude-3-5-haiku-20241022-v1:0" \
--region us-east-1 \
--messages '[{"role": "user", "content": [{"text": "what can you do?"}]}]' \
--query "output.content[0].text" \
--output text

aws bedrock-runtime converse \
--profile nisarga \
--model-id "us.anthropic.claude-3-5-haiku-20241022-v1:0" \
--region us-east-1 \
--messages '[{"role": "user", "content": [{"text": "what can you do?"}]}]' \
--query "output.content[0].text" \
--output text

aws bedrock-runtime converse \
--profile nisarga \
--model-id "us.anthropic.claude-3-7-sonnet-20250219-v1:0" \
--region us-east-2 \
--messages '[{"role": "user", "content": [{"text": "how is the weather today?"}]}]' \
--query "output.content[0].text" \
--output text

## works finally
aws bedrock-runtime converse \
--profile nisarga \
--model-id "us.anthropic.claude-3-7-sonnet-20250219-v1:0" \
--region us-east-2 \
--messages '[{"role": "user", "content": [{"text":"how is the weather today?"}]}]' \
--query "output.message.content[0].text" \
--output text

aws bedrock-runtime converse \
--profile nisarga \
--model-id "us.anthropic.claude-3-5-sonnet-20240620-v1:0" \
--region us-east-2 \
--messages '[{"role": "user", "content": [{"text": "what can you do?"}]}]' \
--query "output.message.content[0].text" \
--output text
{
  "modelId": "anthropic.claude-3-7-sonnet-20250219-v1:0",
  "contentType": "application/json",
  "accept": "application/json",
  "body": {
    "anthropic_version": "bedrock-2023-05-31",
    "max_tokens": 200,
    "top_k": 250,
    "stop_sequences": [],
    "temperature": 1,
    "top_p": 0.999,
    "messages": [
      {
        "role": "user",
        "content": [
          {
            "type": "text",
            "text": "hello world"
          }
        ]
      }
    ]
  }
}