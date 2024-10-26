import imaplib
import smtplib
import ssl
from email.message import EmailMessage
from email.parser import BytesParser
from email.utils import parseaddr
from email import policy
from utilties import log_message
import os
from dotenv import load_dotenv

# Load environment variables
script_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(script_dir, '.env')
load_dotenv(dotenv_path=env_path)
EMAIL_ACCOUNT = os.getenv('EMAIL_ACCOUNT')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
IMAP_SERVER = 'imap.zoho.com'
IMAP_PORT = 993
SMTP_SERVER = 'smtp.zoho.com'
SMTP_PORT = 465

def get_email_address(sender):
    """Extract just the email address from the sender string."""
    name, email_address = parseaddr(sender)
    return email_address

def extract_text_from_email(parsed_email):
    """Extract plain text from a parsed email object."""
    if parsed_email.is_multipart():
        for part in parsed_email.iter_parts():
            if part.get_content_type() == 'text/plain':
                return part.get_payload(decode=True).decode(part.get_content_charset() or 'utf-8')
    else:
        return parsed_email.get_payload(decode=True).decode(parsed_email.get_content_charset() or 'utf-8')
    return ""

def send_response_email(to_email, subject, body):
    """Send a response email using Zoho SMTP."""
    msg = EmailMessage()
    msg['From'] = EMAIL_ACCOUNT
    msg['To'] = to_email
    msg['Subject'] = f"Re: {subject}"
    msg.set_content(body)
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as smtp:
        smtp.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
        smtp.send_message(msg)

def check_zoho_email():
    """Check Zoho IMAP for emails and process them."""

    # init return
    email_ai_requests=[]

    # open email account
    context = ssl.create_default_context()
    with imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT, ssl_context=context) as mail:
        mail.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
        mail.select('inbox')
        status, messages = mail.search(None, 'ALL')
        email_ids = messages[0].split()
        
        for email_id in email_ids:

            # fetch email
            status, msg_data = mail.fetch(email_id, '(RFC822)')

            # process email
            for response_part in msg_data:
                if isinstance(response_part, tuple):

                    # parse email parts
                    raw_email = response_part[1]
                    parsed_email = BytesParser(policy=policy.default).parsebytes(raw_email)
                    sender = parsed_email['From']
                    email_address = get_email_address(sender)
                    subject = parsed_email['Subject']
                    email_body = extract_text_from_email(parsed_email)

                    # logging
                    log_message(f'email from {email_address} with subject {subject}')

                    # create request
                    email_ai_requests.append({
                        'email_address': email_address,
                        'body': email_body,
                        'subject': subject
                    })
            
            # delete the email
            mail.store(email_id, '+FLAGS', '\\Deleted')

        # final delete
        mail.expunge()

    # return requests
    return email_ai_requests

