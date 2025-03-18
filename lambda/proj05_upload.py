import json
import boto3
import os
import uuid
import base64
import pathlib
import datatier
from configparser import ConfigParser

def lambda_handler(event, context):
    try:
        print("**STARTING**")
        print("**lambda: resume_upload**")

        # Setup AWS based on config file
        config_file = 'resumeapp-config.ini'
        os.environ['AWS_SHARED_CREDENTIALS_FILE'] = config_file
        
        configur = ConfigParser()
        configur.read(config_file)
        
        # Configure for S3 access
        s3_profile = 's3readwrite'
        boto3.setup_default_session(profile_name=s3_profile)
        
        bucketname = configur.get('s3', 'bucket_name')
        
        s3 = boto3.resource('s3')
        bucket = s3.Bucket(bucketname)
        
        # Configure for RDS access
        rds_endpoint = configur.get('rds', 'endpoint')
        rds_portnum = int(configur.get('rds', 'port_number'))
        rds_username = configur.get('rds', 'user_name')
        rds_pwd = configur.get('rds', 'user_pwd')
        rds_dbname = configur.get('rds', 'db_name')

        # Extract userid from event
        print("**Accessing event/pathParameters**")
        
        # if "userid" in event:
        #     userid = event["userid"]
        # elif "pathParameters" in event:
        #     if "userid" in event["pathParameters"]:
        #         userid = event["pathParameters"]["userid"]
        #     else:
        #         raise Exception("requires userid parameter in pathParameters")
        # else:
        #     raise Exception("requires userid parameter in event")

        # print("userid:", userid)
        
        # Extract file data from request body
        print("**Accessing request body**")
        
        if "body" not in event:
            raise Exception("event has no body")
        
        body = json.loads(event["body"])
        
        if "filename" not in body:
            raise Exception("event has a body but no filename")
        if "data" not in body:
            raise Exception("event has a body but no data")
        
        filename = body["filename"]
        datastr = body["data"]
        
        print("filename:", filename)
        print("datastr (first 10 chars):", datastr[0:10])

        # Open database connection
        # print("**Opening connection**")
        
        # dbConn = datatier.get_dbConn(rds_endpoint, rds_portnum, rds_username, rds_pwd, rds_dbname)
        
        # # Fetch user details
        # print("**Fetching user details from DB**")
        # sql = "SELECT firstname, lastname FROM users WHERE userid = %s;"
        # row = datatier.retrieve_one_row(dbConn, sql, [userid])
        
        # if row == ():
        #     print("**No such user, returning...**")
        #     return {
        #         'statusCode': 400,
        #         'body': json.dumps("no such user...")
        #     }
        
        # firstname, lastname = row
        
        # Prepare the file for upload
        base64_bytes = datastr.encode()
        file_bytes = base64.b64decode(base64_bytes)
        
        local_filename = "/tmp/resume.pdf"
        
        bucketkey = str(uuid.uuid4()) + ".pdf"        
        # bucketkey = "resume-nu-cs310/" + str(uuid.uuid4()) + ".pdf"        
        with open(local_filename, "wb") as f:
            f.write(file_bytes)
        
        print("**Uploading to S3**")
        
        bucket.upload_file(
        local_filename, 
        bucketkey, 
        ExtraArgs={
            'ACL': 'public-read',
            'ContentType': 'application/pdf'
        }
    )
        
        # Update the database
        # print("**Updating user resume file in DB**")
        # sql = "UPDATE users SET resume_file = %s WHERE userid = %s;"
        # datatier.perform_action(dbConn, sql, [bucketkey, userid])
        
        print("**DONE, returning success**")
        
        return {
            'statusCode': 200,
            'body': json.dumps("Resume uploaded successfully")
        }
    
    except Exception as err:
        print("**ERROR**")
        print(str(err))
        
        return {
            'statusCode': 500,
            'body': json.dumps(str(err))
        }
