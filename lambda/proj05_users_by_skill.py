#
# Retrieves and returns all the users in the 
# BenfordApp database.
#

import json
import boto3
import os
import datatier

from configparser import ConfigParser

def lambda_handler(event, context):
  try:
    print("**STARTING**")
    print("**lambda: proj05_users_by_skill**")

    #
    # setup AWS based on config file:
    #
    config_file = 'resumeapp-config.ini'
    os.environ['AWS_SHARED_CREDENTIALS_FILE'] = config_file
    
    configur = ConfigParser()
    configur.read(config_file)
    
    #
    # configure for RDS access
    #
    rds_endpoint = configur.get('rds', 'endpoint')
    rds_portnum = int(configur.get('rds', 'port_number'))
    rds_username = configur.get('rds', 'user_name')
    rds_pwd = configur.get('rds', 'user_pwd')
    rds_dbname = configur.get('rds', 'db_name')
    
    
    if "skill_name" in event:
      skill_name = event["skill_name"]
    elif "pathParameters" in event:
      if "skill_name" in event["pathParameters"]:
        skill_name = event["pathParameters"]["skill_name"]
      else:
        raise Exception("requires skill_name parameter in pathParameters")
    else:
        raise Exception("requires skill_name parameter in event")
        
    print("**Opening connection**")
    
    dbConn = datatier.get_dbConn(rds_endpoint, rds_portnum, rds_username, rds_pwd, rds_dbname)
    
    print("**Retrieving data**")

    #
    sql = "select distinct userid, firstname, lastname, email, skills from users where lower(skills) like lower(%s)  order by userid asc;"
    
    rows = datatier.retrieve_all_rows(dbConn, sql, parameters=[f"%{skill_name}%"])
    
    for row in rows:
      print(row)

    print("**DONE, returning rows**")
    
    return {
      'statusCode': 200,
      'body': json.dumps(rows)
    }
    
  except Exception as err:
    print("**ERROR**")
    print(str(err))
    
    return {
      'statusCode': 500,
      'body': json.dumps(str(err))
    }
