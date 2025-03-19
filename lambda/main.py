#
# Client-side python app for a skills management system, which calls
# a set of REST APIs on a server. The client allows managing users,
# their skills, and uploading/downloading resumes.
#
#  Author: Nisarga Madhav Murthy
#

import requests
import json
import base64
import pathlib
import logging
import sys
import os
import time
from configparser import ConfigParser

############################################################
#
# classes
#
class User:
    def __init__(self, user_data):
        self.userid = user_data.get('userid')
        self.username = user_data.get('firstname')
        self.email = user_data.get('email')
        self.phone = user_data.get('lastname')

###################################################################
#
# web_service_call
#
# Handles HTTP requests with retries for network failures.
#
def web_service_call(url, method="GET", data=None, json_data=None, files=None):
    """
    Submits a request to a web service at most 3 times, since 
    web services can fail to respond due to network issues.
    
    Parameters
    ----------
    url: url for calling the web service
    method: HTTP method (GET, POST, etc.)
    data: form data for POST requests
    json_data: JSON data for POST requests
    files: files for multipart/form-data requests
    
    Returns
    -------
    response received from web service
    """

    try:
        retries = 0
        
        while True:
            if method.upper() == "GET":
                response = requests.get(url)
            elif method.upper() == "POST":
                response = requests.post(url, data=data, json=json_data, files=files)
            elif method.upper() == "DELETE":
                response = requests.delete(url)
            else:
                print(f"Unsupported method: {method}")
                return None
                
            if response.status_code in [200, 400, 404, 500]:
                # we consider this a successful call and response
                break

            # failed, try again?
            retries = retries + 1
            if retries < 3:
                # try at most 3 times
                time.sleep(retries)
                continue
                
            # if get here, we tried 3 times, we give up:
            break

        return response

    except Exception as e:
        print("**ERROR**")
        logging.error(f"web_service_call() failed with {method} request:")
        logging.error(e)
        return None

############################################################
#
# prompt
#
def prompt():
    """
    Prompts the user and returns the command number

    Parameters
    ----------
    None

    Returns
    -------
    Command number entered by user (0, 1, 2, ...)
    """
    try:
        print()
        print(">> Enter a command:")
        print("   0 => end")
        print("   1 => list all users")
        print("   2 => find users by skill")
        print("   3 => list skills of a user")
        print("   4 => upload resume")
        print("   5 => download resume")

        cmd = input()

        if cmd == "":
            cmd = -1
        elif not cmd.isnumeric():
            cmd = -1
        else:
            cmd = int(cmd)

        return cmd

    except Exception as e:
        print("**ERROR")
        print("**ERROR: invalid input")
        print("**ERROR")
        return -1

############################################################
#
# list_all_users
#
def list_all_users(baseurl):
    """
    Prints out all the users in the database with their details

    Parameters
    ----------
    baseurl: baseurl for web service

    Returns
    -------
    nothing
    """

    try:
        # call the web service:
        api = '/users'
        url = baseurl + api

        res = web_service_call(url)

        # let's look at what we got back:
        if res.status_code == 200: # success
            pass
        else:
            # failed:
            print("Failed with status code:", res.status_code)
            print("url: " + url)
            if res.status_code == 500:
                # we'll have an error message
                body = res.json()
                print("Error message:", body)
            return

        # deserialize and extract users:
        body = res.json()

        users = json.loads(body.get('body', []))

        print("\n--- USER LIST ---")
        for user in users:
            print(f"  ID: {user[0]}")
            print(f"  Full name: {user[3]} {user[2]}")
            print(f"  Email: {user[1]}")
            print(f"  Skills: {user[5]}")
            print("-" * 20)

    except Exception as e:
        logging.error("**ERROR: list_all_users() failed:")
        logging.error(e)
        return

############################################################
#
# find_users_by_skill
#
def find_users_by_skill(baseurl):
    """
    Finds users with a specified skill

    Parameters
    ----------
    baseurl: baseurl for web service

    Returns
    -------
    nothing
    """

    try:
        print("Enter the skill>")
        skill_name = input()

        if not skill_name:
            print("Skill name cannot be empty")
            return

        # call the web service:
        api = f'/skill/{skill_name}/users'
        url = baseurl + api

        res = web_service_call(url)

        # let's look at what we got back:
        if res.status_code == 200: # success
            pass
        elif res.status_code == 404:
            print(f"No users found with skill '{skill_name}'")
            return
        else:
            # failed:
            print("Failed with status code:", res.status_code)
            print("url: " + url)
            if res.status_code == 500:
                # we'll have an error message
                body = res.json()
                print("Error message:", body)
            return

        # deserialize and extract users:
        body = res.json()
        users = body
        print(users)
        print("\n--- MATCHING USER LIST ---")
        for user in users:
            print(f"  ID: {user[0]}")
            print(f"  Full name: {user[2]} {user[1]}")
            print(f"  Email: {user[3]}")
            print(f"  Skills: {user[4]}")
            print("-" * 20)

    except Exception as e:
        logging.error("**ERROR: find_users_by_skill() failed:")
        logging.error(e)
        return

############################################################
#
# list_user_skills
#
def list_user_skills(baseurl):
    """
    Lists all skills of a specified user

    Parameters
    ----------
    baseurl: baseurl for web service

    Returns
    -------
    nothing
    """

    try:
        print("Enter user ID>")
        userid = input()

        if not userid:
            print("User ID cannot be empty")
            return

        # call the web service:
        api = f'/skills/{userid}'
        url = baseurl + api

        res = web_service_call(url)

        # let's look at what we got back:
        if res.status_code == 200: # success
            pass
        elif res.status_code == 404:
            print(f"User with ID '{userid}' not found or has no skills")
            return
        else:
            # failed:
            print("Failed with status code:", res.status_code)
            print("url: " + url)
            if res.status_code == 500:
                # we'll have an error message
                body = res.json()
                print("Error message:", body)
            return

        # deserialize and extract skills:
        body = res.json()
        # let's map each row into a Skill object:
        skills = []
        for skill_data in body:
            # skill = Skill(skill_data)
            for skill in skill_data:
                skills.append(skill)
        # Now we can display the skills:
        if len(skills) == 0:
            print(f"User with ID '{userid}' has no skills")
            return

        print(f"\n--- SKILLS FOR USER ID: {userid} ---")
        print(skills)
    except Exception as e:
        logging.error("**ERROR: list_user_skills() failed:")
        logging.error(e)
        return

############################################################
#
# upload_resume
#
def upload_resume(baseurl):
    """
    Uploads a resume file for a user

    Parameters
    ----------
    baseurl: baseurl for web service

    Returns
    -------
    nothing
    """

    try:
        print("Enter resume filename>")
        local_filename = input()

        if not pathlib.Path(local_filename).is_file():
            print("Resume file '", local_filename, "' does not exist...")
            return

        # print("Enter user ID>")
        # userid = input()

        # if not userid:
        #     print("User ID cannot be empty")
        #     return

        # read the file as binary data:
        with open(local_filename, "rb") as infile:
            file_bytes = infile.read()

        # encode as base64 for transmission
        datastr = base64.b64encode(file_bytes).decode('utf-8')
        
        # prepare the data packet
        data = {
            "filename": os.path.basename(local_filename),
            "data": datastr
        }

        # call the web service:
        api = f'/resume/upload'
        # api = f'/resume/{userid}'
        url = baseurl + api

        res = web_service_call(url, method="POST", json_data=data)

        # let's look at what we got back:
        if res.status_code == 200: # success
            pass
        elif res.status_code == 404:
            print('Status 404')
            # print(f"User with ID '{userid}' not found")
            return
        else:
            # failed:
            print("Failed with status code:", res.status_code)
            print("url: " + url)
            if res.status_code == 500:
                # we'll have an error message
                body = res.json()
                print("Error message:", body)
            return

        # success message
        response_data = res.json()
        print(f"Resume '{local_filename}' successfully uploaded!")
        print(f"Response: {response_data}")

    except Exception as e:
        logging.error("**ERROR: upload_resume() failed:")
        logging.error(e)
        return

############################################################
#
# download_resume
#
def download_resume(baseurl):
    """
    Downloads a resume file for a user

    Parameters
    ----------
    baseurl: baseurl for web service

    Returns
    -------
    nothing
    """

    try:
        print("Enter user ID>")
        userid = input()

        if not userid:
            print("User ID cannot be empty")
            return

        # call the web service:
        api = f'/resume/{userid}'
        url = baseurl + api

        res = web_service_call(url)
        # print('res file')
        # print(res.json())
        # res = res.json()
        # print(res['resume_file'])
        # print(res['file_content'])

        # if we get here, success! deserialize response:
        response_data = res.json()
        filename = response_data.get("filename", f"resume_user_{userid}.pdf")
        datastr = response_data.get("file_content")
        
        if not datastr:
            print("Error: No resume data in response")
            return
            
        # decode base64 data
        try:
            base64_bytes = datastr.encode('utf-8')
            decoded_bytes = base64.b64decode(base64_bytes)
            
            # Save to file
            output_filename = f"downloaded_{filename}"
            with open(output_filename, "wb") as outfile:
                outfile.write(decoded_bytes)
                
            print(f"Resume successfully downloaded and saved as '{output_filename}'")
            
        except Exception as e:
            print(f"Error decoding or saving resume data: {e}")

    except Exception as e:
        logging.error("**ERROR: download_resume() failed:")
        logging.error(e)
        return


############################################################
# main
#
try:
    print('** Welcome to Resume Management Client **')
    print()

    # eliminate traceback so we just get error message:
    sys.tracebacklimit = 0

    # what config file should we use for this session?
    config_file = 'skills-client-config.ini'

    # print("Config file to use for this session?")
    # print("Press ENTER to use default, or")
    # print("enter config file name>")
    # s = input()

    # if s == "":  # use default
    #     pass  # already set
    # else:
    #     config_file = s

    # does config file exist?
    if not pathlib.Path(config_file).is_file():
        print("**ERROR: config file '", config_file, "' does not exist, exiting")
        sys.exit(0)

    # setup base URL to web service:
    configur = ConfigParser()
    configur.read(config_file)
    baseurl = configur.get('client', 'webservice')

    # make sure baseurl does not end with /, if so remove:
    if len(baseurl) < 16:
        print("**ERROR: baseurl '", baseurl, "' is not nearly long enough...")
        sys.exit(0)

    if baseurl == "https://YOUR_API_ENDPOINT.com":
        print("**ERROR: update config file with your API endpoint")
        sys.exit(0)

    if baseurl.startswith("http:"):
        print("**WARNING: your URL starts with 'http', it should start with 'https' for security")

    lastchar = baseurl[len(baseurl) - 1]
    if lastchar == "/":
        baseurl = baseurl[:-1]

    # main processing loop:
    cmd = prompt()

    while cmd != 0:
        #
        if cmd == 1:
            list_all_users(baseurl)
        elif cmd == 2:
            find_users_by_skill(baseurl)
        elif cmd == 3:
            list_user_skills(baseurl)
        elif cmd == 4:
            upload_resume(baseurl)
        elif cmd == 5:
            download_resume(baseurl)
        else:
            print("** Unknown command, try again...")
        #
        cmd = prompt()

    #
    # done
    #
    print()
    print('** done **')
    sys.exit(0)

except Exception as e:
    logging.error("**ERROR: main() failed:")
    logging.error(e)
    sys.exit(0)