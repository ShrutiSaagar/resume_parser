import json
import boto3
import os
import base64
import datatier
from configparser import ConfigParser

def lambda_handler(event, context):
    try:
        print("**STARTING**")
        print("**lambda: resume_download**")

        #
        # setup AWS based on config file:
        #
        config_file = 'resumeapp-config.ini'
        os.environ['AWS_SHARED_CREDENTIALS_FILE'] = config_file

        configur = ConfigParser()
        configur.read(config_file)

        #
        # configure for S3 access:
        #
        s3_profile = 's3readwrite'
        boto3.setup_default_session(profile_name=s3_profile)

        bucketname = configur.get('s3', 'bucket_name')

        s3 = boto3.resource('s3')
        bucket = s3.Bucket(bucketname)

        #
        # configure for RDS access
        #
        rds_endpoint = configur.get('rds', 'endpoint')
        rds_portnum = int(configur.get('rds', 'port_number'))
        rds_username = configur.get('rds', 'user_name')
        rds_pwd = configur.get('rds', 'user_pwd')
        rds_dbname = configur.get('rds', 'db_name')

        #
        # userid from event: could be a parameter or part of URL path
        #
        if "userid" in event:
            userid = event["userid"]
        elif "pathParameters" in event:
            if "userid" in event["pathParameters"]:
                userid = event["pathParameters"]["userid"]
            else:
                raise Exception("requires userid parameter in pathParameters")
        else:
            raise Exception("requires userid parameter in event")

        print("userid:", userid)

        #
        # open connection to the database:
        #
        print("**Opening connection**")

        dbConn = datatier.get_dbConn(rds_endpoint, rds_portnum, rds_username, rds_pwd, rds_dbname)

        #
        # Fetch the resume S3 key from the database:
        #
        print("**Fetching resume file key from DB**")

        sql = "SELECT resume_file FROM users WHERE userid = %s;"
        row = datatier.retrieve_one_row(dbConn, sql, [userid])

        if row == ():  # No resume found
            print("**No resume found, returning...**")
            return {
                'statusCode': 404,
                'body': json.dumps("No resume found for the given userid")
            }

        resume_key = row[0]
        print("Resume file key:", resume_key)

        #
        # Download the resume file from S3:
        #
        local_filename = "/tmp/resume.pdf"

        print("**Downloading resume from S3**")
        print(f"**file : {resume_key}**")

        bucket.download_file(resume_key, local_filename)

        #
        # Read the file and encode it as base64:
        #
        with open(local_filename, "rb") as infile:
            file_bytes = infile.read()
            file_base64 = base64.b64encode(file_bytes).decode('utf-8')

        print("**DONE, returning resume**")
        print(f"**resume : {file_base64[:200]}**")

        return {
            'statusCode': 200,
            'body': json.dumps({'resume_file': resume_key, 'file_content': file_base64}),
            'headers': {'Content-Type': 'application/json'}
        }

    except Exception as err:
        print("**ERROR**")
        print(str(err))

        return {
            'statusCode': 500,
            'body': json.dumps(str(err))
        }
