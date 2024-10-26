import time
from dotenv import load_dotenv
from email_interaction import check_zoho_email, send_response_email
from ai_interaction import ask_ai
from database_utilities import create_database
from utilties import log_message
from google_interaction import get_calendar_events
import os

# Load environment variables
script_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(script_dir, '.env')
load_dotenv(dotenv_path=env_path)

# Load environment variables
VALID_SENDERS = os.getenv('VALID_SENDERS').split(",")

def process_request(email_address, subject, email_body):
    
    # only process emails from nate
    if email_address not in VALID_SENDERS:
        log_message(f'not processing message from {email_address}')
        return

    if (subject == "calendar"):
        response = ask_ai(subject, f"Create a few paragraph digest of using the following events and make sure to include any actions that could be useful to complete prior to those events: \n {get_calendar_events()}", "You are an assistant with the humor style of robin williams in good morning vietnam.")
    else: 
        # ask gpt
        response = ask_ai(subject, email_body, "You are an assistant.")

    # send email back
    send_response_email(email_address, subject, response)

def main():

    # create database if necessary
    create_database()

    while True:

            # logging
            log_message('Checking Email...')

            # check email
            email_ai_requests = check_zoho_email()

            # go through requests if there are any
            for email_ai_request in email_ai_requests:
                process_request(email_ai_request['email_address'], email_ai_request['subject'], email_ai_request['body'])

            time.sleep(60)

if __name__ == "__main__":
    main()