# Resume Management System

## Overview
This Resume Management System is a serverless application built on AWS that helps recruiters filter and manage candidate resumes efficiently. The system allows for uploading resumes, extracting information using AWS Bedrock, storing the data in a database, and providing search functionality for recruiters.

## Architecture
The system uses the following AWS services:
- Amazon API Gateway
- AWS Lambda
- Amazon S3
- Amazon SQS
- Amazon RDS (MySQL)
- Amazon Bedrock (Claude 3.7 Sonnet model)

## Functionalities
1. **Upload Resume** - Upload PDF resumes directly to S3 storage
2. **Parse and Store** - Asynchronously process uploaded PDFs, extract details using AWS Bedrock, and store in database
3. **List Users/Skills** - Lambda functions to list all users or find specific user's skills
4. **Search by Skills** - Search through the database for specific skills to list all matching candidates
5. **Download Resume** - Download a candidate's resume from S3

## Files and Components

### Lambda Functions
- **proj05_upload.py** - Handles resume uploads to S3
- **proj05_parse_resume.py** - Processes PDFs, extracts text, and interacts with AWS Bedrock
- **proj05_users.py** - Retrieves the complete directory of all registered users
- **proj05_users_by_skill.py** - Filters and returns users possessing a specific skill
- **proj05_skills.py** - Retrieves the comprehensive skill profile for a specific user
- **proj05_download.py** - Retrieves and serves a stored resume for a specified user

### Supporting Files
- **datatier.py** - Database interaction layer for MySQL operations
- **skills-client-config.ini** - Configuration file for the Python client and 
- **resumeapp.ini** - Configuration for lambda functions

## Setup Instructions

### Prerequisites
1. AWS Account with access to Lambda, API Gateway, S3, SQS, RDS, and Bedrock
2. Python 3.8+ installed locally
3. AWS CLI configured with appropriate permissions

### Step 1: Database Setup
1. Create a MySQL database instance in Amazon RDS
2. Create tables for users, skills, and resume metadata
3. Update the connection details in the configs

### Step 2: AWS Service Configuration
1. Create an S3 bucket for storing resumes
2. Set up an SQS queue for processing notifications
3. Configure S3 event notifications to send messages to SQS when new files are uploaded

### Step 3: Lambda Function Deployment
1. Create the following Lambda functions in AWS:
   - proj05_upload
   - proj05_parse_resume
   - proj05_users
   - proj05_users_by_skill
   - proj05_skills
   - proj05_download

2. Upload the corresponding Python files to each Lambda function
3. Configure appropriate IAM roles with permissions for S3, SQS, RDS, and Bedrock
4. Configure environment variables with database connection details and bucket names

### Step 4: API Gateway Setup
1. Create a new REST API in API Gateway
2. Set up the following endpoints and connect them to the respective Lambda functions:
   - POST /resume/{userid} → proj05_upload
   - GET /users → proj05_users
   - GET /skill/{skill_name}/users → proj05_users_by_skill
   - GET /skills/{userid} → proj05_skills
   - GET /resume/{userid} → proj05_download

3. Deploy the API to a stage and note the API endpoint URL

### Step 5: SQS Trigger Configuration
1. Configure the SQS queue as a trigger for the proj05_parse_resume Lambda function
2. Set appropriate batch size and concurrency settings

### Step 6: Client Configuration
1. Update `skills-client-config.ini` with:
   - API Gateway endpoint URL
   - Database connection details
   - S3 bucket name
   - Other necessary configuration parameters

## Usage
After setting up the system, you can:

1. **Upload a Resume**:
   - Use the API endpoint `POST /resume/{userid}` with a PDF file

2. **List All Candidates**:
   - Call `GET /users` to retrieve all candidates

3. **View Candidate Skills**:
   - Call `GET /skills/{userid}` to see a specific candidate's skills

4. **Search by Skills**:
   - Call `GET /skill/{skill_name}/users` to find candidates with specific skills

5. **Download a Resume**:
   - Call `GET /resume/{userid}` to download a candidate's resume

## Error Handling
- The system includes proper error handling for file upload failures, parsing issues, and database errors
- Check CloudWatch logs for detailed error information when troubleshooting

## Contributors
- Nisarga
- Saloni
- Shruti

## Course Information
This project was developed for CS 310.
