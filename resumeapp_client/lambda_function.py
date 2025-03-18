#
# Python program to open and process a PDF file, extracting
# all numeric values from the document. The goal is to tally
# the first significant (non-zero) digit of each numeric
# value, and save the results to a text file. This will
# allow checking to see if the results follow Benford's Law,
# a common method for detecting fraud in numeric data.
#
# https://en.wikipedia.org/wiki/Benford%27s_law
# https://chance.amstat.org/2021/04/benfords-law/
#

import json
import boto3
import os
import uuid
import base64
import pathlib
import datatier
import urllib.parse
import string

from configparser import ConfigParser
from pypdf import PdfReader

def lambda_handler(event, context):
  try:
    print("**STARTING**")
    print("**lambda: proj03_compute**")
    
    # 
    # in case we get an exception, initial this filename
    # so we can write an error message if need be:
    #
    bucketkey_results_file = ""
    
    #
    # setup AWS based on config file:
    #
    config_file = 'benfordapp-config.ini'
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
    # this function is event-driven by a PDF being
    # dropped into S3. The bucket key is sent to 
    # us and obtain as follows:
    #
    bucketkey = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    
    print("bucketkey:", bucketkey)
      
    extension = pathlib.Path(bucketkey).suffix
    
    if extension != ".pdf" : 
      raise Exception("expecting S3 document to have .pdf extension")
    
    bucketkey_results_file = bucketkey[0:-4] + ".txt"
    
    print("bucketkey results file:", bucketkey_results_file)
      
    #
    # download PDF from S3 to LOCAL file system:
    #
    print("**DOWNLOADING '", bucketkey, "'**")

    #
    # TODO #1 of 8: where do we write local files? Replace
    # the ??? with the local directory where we have access.
    #
    local_pdf = "/tmp/data.pdf"

    bucket.download_file(bucketkey, local_pdf)

    #
    # open LOCAL pdf file:
    #
    print("**PROCESSING local PDF**")
    
    reader = PdfReader(local_pdf)
    number_of_pages = len(reader.pages)

    #
    # TODO #2 of 8: update status column in DB for this job,
    # change the value to "processing - starting". Use the
    # bucketkey --- stored as datafilekey in the table ---
    # to identify the row to update. Use the datatier.
    #
    # open connection to the database:
    #
    print("**Opening DB connection**")
    
    dbConn = datatier.get_dbConn(rds_endpoint, rds_portnum, rds_username, rds_pwd, rds_dbname)
    query = "UPDATE jobs SET status = 'processing - starting' WHERE datafilekey = %s"
    datatier.perform_action(dbConn, query, (bucketkey,))
    # Dictionary to count first significant digits
    digit_counts = {str(i): 0 for i in range(0, 10)}


    # Process each page
    for i in range(number_of_pages):
        page = reader.pages[i]
        text = page.extract_text()
        words = text.split()
        print(f"** Page {i+1}, text length {len(text)}, num words {len(words)}")

        for word in words:
            word = word.translate(str.maketrans('', '', string.punctuation))
            if word.isnumeric():
              word = word.strip()
              stripped_word = word.lstrip('0')
              # Ensure we still have a valid number after stripping
              if stripped_word and stripped_word != "" and stripped_word[0] != '0' and stripped_word[0] in digit_counts:
                  digit_counts[stripped_word[0]] += 1
        # TODO #4: Update status column in DB for this job to "processing - page x of y completed"
        query = "UPDATE jobs SET status = %s WHERE datafilekey = %s"
        status_msg = f"processing - page {i+1} of {number_of_pages} completed"
        datatier.perform_action(dbConn, query, (status_msg, bucketkey))
    
    #
    # analysis complete, write the results to local results file:
    #
    # TODO #5 of 8: where do we write local files? Replace
    # the ??? with the local directory where we have access.
    #
    local_results_file = "/tmp/results.txt"

    print("local results file:", local_results_file)

    outfile = open(local_results_file, "w")
    outfile.write("**RESULTS**\n")
    outfile.write(str(number_of_pages))
    outfile.write(" pages\n")

    #
    # TODO #6 of 8: Write the 10 counts to the file:
    #
    # ???
    #
    for digit, count in digit_counts.items():
        outfile.write(f"{digit} {count}\n")
    
    outfile.close()
    
    #
    # upload the results file to S3:
    #
    print("**UPLOADING to S3 file", bucketkey_results_file, "**")

    bucket.upload_file(local_results_file,
                       bucketkey_results_file,
                       ExtraArgs={
                         'ACL': 'public-read',
                         'ContentType': 'text/plain'
                       })
    
    # 
    # The last step is to update the database to change
    # the status of this job, and store the results
    # bucketkey for download:
    #
    # TODO #7 of 8: update both the status column and the 
    # resultsfilekey for this job in the DB. The job is 
    # identified by the bucketkey --- datafilekey in the 
    # table. Change the status to "completed", and set
    # resultsfilekey to the contents of your variable
    # bucketkey_results_file.
    #
    # ???
    #
    query = "UPDATE jobs SET status = 'completed', resultsfilekey = %s WHERE datafilekey = %s"
    datatier.perform_action(dbConn, query, (bucketkey_results_file, bucketkey))
    #
    # done!
    #
    # respond in an HTTP-like way, i.e. with a status
    # code and body in JSON format:
    #
    print("**DONE, returning success**")
    
    return {
      'statusCode': 200,
      'body': json.dumps("success")
    }
    
  #
  # on an error, try to upload error message to S3:
  #
  except Exception as err:
    print("**ERROR**")
    print(str(err))
    
    local_results_file = "/tmp/results.txt"
    outfile = open(local_results_file, "w")

    outfile.write(str(err))
    outfile.write("\n")
    outfile.close()
    
    if bucketkey_results_file == "": 
      #
      # we can't upload the error file:
      #
      pass
    else:
      # 
      # upload the error file to S3
      #
      print("**UPLOADING**")
      #
      bucket.upload_file(local_results_file,
                         bucketkey_results_file,
                         ExtraArgs={
                           'ACL': 'public-read',
                           'ContentType': 'text/plain'
                         })

    #
    # update jobs row in database:
    #
    # TODO #8 of 8: open connection, update job in database
    # to reflect that an error has occurred. The job is 
    # identified by the bucketkey --- datafilekey in the 
    # table. Set the status column to 'error' and set the
    # resultsfilekey column to the contents of the variable
    # bucketkey_results_file.
    #
    dbConn = datatier.get_dbConn(rds_endpoint, rds_portnum, rds_username, rds_pwd, rds_dbname)
    query = "UPDATE jobs SET status = 'error', resultsfilekey = %s WHERE datafilekey = %s"
    datatier.perform_action(dbConn, query, (bucketkey_results_file, bucketkey))
    #
    # done, return:
    #    
    return {
      'statusCode': 500,
      'body': json.dumps(str(err))
    }
