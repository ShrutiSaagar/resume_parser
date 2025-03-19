# Resume Management System - Detailed Setup Guide

This document provides step-by-step instructions for setting up and configuring the Resume Management System on AWS.

## Prerequisites

- AWS Account with access to:
  - Lambda
  - API Gateway
  - S3
  - SQS
  - RDS (MySQL)
  - Bedrock
- Python 3.8 or higher
- AWS CLI installed and configured
- Basic understanding of AWS services

## Step 1: Database Setup

### Create MySQL Database in RDS

1. Navigate to the Amazon RDS console
2. Click "Create database"
3. Select "Standard create" and "MySQL"
4. Choose an appropriate instance size (db.t3.micro is sufficient for testing)
5. Set up credentials (remember these for the config file)
6. Under "Additional configuration", specify a database name (e.g., `resume_db`)
7. Click "Create database"

### Create Database Schema

Connect to your database using a MySQL client and execute:

```sql
DROP TABLE IF EXISTS users;

CREATE TABLE users
(
    userid       int not null AUTO_INCREMENT,
    email        VARCHAR(128) not null,
    lastname     VARCHAR(64) not null,
    firstname    VARCHAR(64) not null,
    bucketfolder TEXT,
    resume_text  TEXT, 
    resume_file  TEXT, 
    PRIMARY KEY  (userid),
    UNIQUE       (email) 
);

```

## Step 2: S3 Bucket Configuration

### Create S3 Bucket

1. Navigate to the S3 console
2. Click "Create bucket"
3. Enter a globally unique name (e.g., `resume-management-pdfs-yourname`)
4. Choose your region
5. Leave default settings and click "Create bucket"

## Step 3: SQS Queue Setup

1. Navigate to the SQS console
2. Click "Create queue"
3. Select "Standard Queue"
4. Name it (e.g., `resume-processing-queue`)
5. Leave default settings and click "Create queue"
6. Note the queue ARN for later use

## Step 4: Lambda Function Deployment

For each Lambda function:

1. Navigate to Lambda console and click "Create function"
2. Choose "Author from scratch"
3. Enter function name (e.g., `proj05_upload`)
4. Select Python 3.9 as runtime
5. Create a new execution role with basic Lambda permissions
6. Click "Create function"
7. In the "Code" tab, upload the corresponding Python file

### Lambda Function-Specific Configurations

#### proj05_upload.py
- Add S3 write permissions to the execution role
- Set environment variables:
  - `BUCKET_NAME`: Your S3 bucket name
  - `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`: Your RDS details

#### proj05_parse_resume.py
- Add S3 read, SQS receive, Bedrock invoke, and RDS write permissions
- Set environment variables:
  - `BUCKET_NAME`: Your S3 bucket name
  - `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`: Your RDS details
  - `BEDROCK_MODEL_ID`: `anthropic.claude-3-sonnet-20240229-v1:0` or the Claude model ID you're using

#### Other Lambda Functions
- Add appropriate permissions (RDS read/write, S3 read)
- Set database connection environment variables

### Configure SQS Trigger for proj05_parse_resume

1. In the proj05_parse_resume Lambda function, go to "Configuration" tab
2. Click "Triggers" and "Add trigger"
3. Select "SQS" as source
4. Select your queue from the dropdown
5. Set batch size to 1 to start (can be increased later)
6. Click "Add"

### Configure S3 Event Notification

1. Go to your S3 bucket, click "Properties"
2. Find "Event notifications" and click "Create event notification"
3. Enter a name (e.g., `NewResumeUpload`)
4. For Event types, select "All object create events"
5. For Destination, choose "SQS Queue" and select your queue
6. Click "Save changes"

## Step 5: API Gateway Setup

1. Navigate to API Gateway console
2. Click "Create API" and select "REST API"
3. Name your API (e.g., `ResumeManagementAPI`)
4. Click "Create API"

### Create Resources and Methods

Create the following endpoints:

#### Upload Resume
- Create resource `/resume` and with `{userid}` path parameter
- Create POST method
- Integration type: Lambda Function
- Lambda Function: proj05_upload
- Enable CORS if needed

#### List All Users
- Create resource `/users`
- Create GET method
- Integration type: Lambda Function
- Lambda Function: proj05_users
- Enable CORS if needed

#### Find Users by Skill
- Create resource `/skill` with `{skill_name}` path parameter and then `/users` subresource
- Create GET method
- Integration type: Lambda Function
- Lambda Function: proj05_users_by_skill
- Enable CORS if needed

#### List Skills of a User
- Create resource `/skills` with `{userid}` path parameter
- Create GET method
- Integration type: Lambda Function
- Lambda Function: proj05_skills
- Enable CORS if needed

#### Download Resume
- For the existing resource `/resume/{userid}`
- Create GET method
- Integration type: Lambda Function
- Lambda Function: proj05_download
- Enable CORS if needed

### Deploy API

1. Click "Deploy API"
2. Create a new stage (e.g., `prod`)
3. Click "Deploy"
4. Note the "Invoke URL" for your client configuration

## Step 6: Update Configuration File

Edit `skills-client-config.ini` & `resumeapp-config.ini` with your specific settings:

skills-client-config.ini
```skills-client-config.ini
[client]
webservice=https://aba.execute-api.us-east-2.amazonaws.com/stage1

[s3]
bucket_name = resume-nu-cs310
region_name = us-east-2
```
resumeapp-config.ini
```resumeapp-config.ini
[s3]
bucket_name = resume-nu-cs310
region_name = us-east-2

[rds]
endpoint = mysql.us-east-2.rds.amazonaws.com
port_number = 3306
region_name = us-east-2
user_name = user
user_pwd = pwd
db_name = benfordapp

[s3readonly]
region_name = us-east-2
aws_access_key_id = xxx
aws_secret_access_key = xxx

[s3readwrite]
region_name = us-east-2
aws_access_key_id = xxx
aws_secret_access_key = xxx
```

## Step 7: Testing

### Client main.py
The aforementioned functionalities are available to be tested by providing appropriate input.

## Troubleshooting

- Check CloudWatch logs for each Lambda function
- Verify IAM permissions for Lambda roles
- Test database connectivity separately
- Ensure S3 event notifications are properly configured
- Verify API Gateway endpoints and methods
