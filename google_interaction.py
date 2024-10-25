from datetime import datetime, timedelta
import os.path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Scopes define what part of the user's account the application can access
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
CALENDAR_ID = os.getenv('CALENDAR_ID')

def get_calendar_events():

    # init return
    event_details = ''

    # Check if token.json exists to store the user's access and refresh tokens
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If no valid credentials, initiate login flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for future use
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    # Build the Google Calendar API service
    service = build('calendar', 'v3', credentials=creds)

    # Get the current time in UTC
    now = datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time

    # Calculate timeMax (one week from now)
    one_week_later = (datetime.utcnow() + timedelta(days=7)).isoformat() + 'Z'


    # Call the Calendar API
    # Retrieve events for the next week
    events_result = service.events().list(
        calendarId=CALENDAR_ID,
        timeMin=now,
        timeMax=one_week_later,  # Time range up to one week from now
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    events = events_result.get('items', [])

    if not events:
        print('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        end = event['end'].get('dateTime', event['end'].get('date'))
        location = event.get('location', 'No location provided')
        description = event.get('description', 'No description provided')
        attendees = ', '.join([attendee['email'] for attendee in event.get('attendees', [])]) or 'None'
        creator = event.get('creator', {}).get('email', 'No creator provided')
        organizer = event.get('organizer', {}).get('email', 'No organizer provided')
        status = event.get('status', 'No status provided')
        html_link = event.get('htmlLink', 'No link provided')

        # Create a single formatted string for the event
        event_details += (
            f"Event: {event['summary']}, "
            f"Start: {start}, "
            f"End: {end}, "
            f"Location: {location}, "
            f"Description: {description}, "
            f"Attendees: {attendees}, "
            f"Creator: {creator}, "
            f"Organizer: {organizer}, "
            f"Status: {status}, "
            f"Event Link: {html_link}, "
            "\n\n"
        )

    # return events
    return event_details
        


