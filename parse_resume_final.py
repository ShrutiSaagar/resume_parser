import json
import uuid
import boto3
import pymysql
from urllib.parse import unquote, unquote_plus
from pypdf import PdfReader
from io import BytesIO
import os

from configparser import ConfigParser

config_file = 'resumeapp-config.ini'
os.environ['AWS_SHARED_CREDENTIALS_FILE'] = config_file

configur = ConfigParser()
configur.read(config_file)

rds_endpoint = configur.get('rds', 'endpoint')
rds_portnum = int(configur.get('rds', 'port_number'))
rds_username = configur.get('rds', 'user_name')
rds_pwd = configur.get('rds', 'user_pwd')
rds_dbname = configur.get('rds', 'db_name')


def get_s3_file(bucket_name, file_key):
    s3 = boto3.client('s3')
    response = s3.get_object(Bucket=bucket_name, Key=file_key)
    return response['Body'].read()

def extract_pdf_text(pdf_bytes):
    pdf_stream = BytesIO(pdf_bytes)
    reader = PdfReader(pdf_stream)
    
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text

def process_with_bedrock(resume_text):
    session = boto3.Session()
    bedrock_runtime = session.client('bedrock-runtime', region_name='us-east-2')

    prompt = f"""
    You are an expert recruiter. Extract the following details from this resume text:
    - Full Name
    - Email (if available)
    - List of skills (comma-separated)
    Resume Text:
    {resume_text}

    Provide the output in JSON format with keys: 'fullname', 'email', 'skills'.
    """
    model_id = "us.anthropic.claude-3-7-sonnet-20250219-v1:0"

    response = bedrock_runtime.invoke_model(
        modelId=model_id,
        contentType='application/json',
        accept='application/json',
        body=json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 4000,  # Required field for Claude 3.7
            "messages": [{
                "role": "user",
                "content": [{
                    "type": "text",
                    "text": prompt
                }]
            }]
        })
    )
    

    response_body = response['body'].read().decode('utf-8')
    print('Bedrock response:')
    print(response_body)
    parsed_response = json.loads(response_body)

    # Get the text content which contains the markdown-formatted JSON
    json_response = parsed_response['content'][0]['text']

    # Remove the markdown code block formatting (```json and ```)
    clean_json_str = json_response.strip('```json\n').strip('\n```')

    # Parse the cleaned JSON string
    resume_data = json.loads(clean_json_str)

    # Now you have the extracted resume data as a Python dict
    print('resume_data')
    print(resume_data)
    return resume_data

def save_to_mysql(user_id, fname, lname, email, skills, resume_text, resume_file):
    connection = pymysql.connect(
        host=rds_endpoint,
        user=rds_username,
        password=rds_pwd,
        database=rds_dbname
    )
    with connection.cursor() as cursor:
        sql = """
        INSERT INTO users (userid, firstname, lastname, email, skills, resume_text, resume_file)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE skills=%s, resume_text=%s;
        """
        cursor.execute(sql, (user_id, fname, lname, email, skills, resume_text, resume_file, skills, resume_text))
    connection.commit()
    connection.close()

def lambda_handler(event, context):

    sqs_message = json.loads(event['Records'][0]['body'])
    body = sqs_message['Records'][0]
    print('event received ', body)

    bucket_name = body['s3']['bucket']['name']
    resume_file_key = unquote(body['s3']['object']['key'])

    print(f'Fetching file from S3: {bucket_name}/{resume_file_key}')
    
    pdf_bytes = get_s3_file(bucket_name, resume_file_key)

    resume_text = extract_pdf_text(pdf_bytes)

    print('Extracted Resume Text Preview:')
    print(resume_text[:500])

    bedrock_response = process_with_bedrock(resume_text)

    fullname = bedrock_response.get('fullname', '')
    email = bedrock_response.get('email', 'unknown@example.com')

    skills_list = bedrock_response.get('skills', [])
    skills = ", ".join(skills_list) if isinstance(skills_list, list) else skills_list
    if fullname:
        name_parts = fullname.strip().split()
        firstname = name_parts[0]
        lastname = name_parts[-1] if len(name_parts) > 1 else ''
    else:
        firstname = ''
        lastname = ''

    user_id = ''  # Populate appropriately
    random_uuid = uuid.uuid4()
    user_id = str(random_uuid)
    print('user_id', user_id, ' firstname ', firstname, ' lastname ', lastname, ' email ', email, ' skills ', skills)
    save_to_mysql(user_id, firstname, lastname, email, skills, resume_text, resume_file_key)

    return {
        'statusCode': 200,
        'body': json.dumps('Resume processed successfully!')
    }