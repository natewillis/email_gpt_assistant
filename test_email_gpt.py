import unittest
import os
from dotenv import load_dotenv


from email_gpt import process_request
load_dotenv()

class TestEmailGPT(unittest.TestCase):
    def test_process_request_coding_question(self):

        # setup input
        email_address = os.getenv('VALID_SENDERS').split(",")[0]
        subject = "Coding Question"
        email_body = "What is the time complexity of a binary search?"

        process_request(email_address, subject, email_body)

if __name__ == "__main__":
    unittest.main()