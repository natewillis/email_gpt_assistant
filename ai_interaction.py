from openai import OpenAI
import anthropic
import os
from database_utilities import get_chat_history, update_chat_history

# Load environment variables
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')

# initialize the OpenAI client
openai_client = OpenAI(
    api_key=OPENAI_API_KEY
)

# initialize the anthropic client
anthropic_client = anthropic.Anthropic(
    api_key=ANTHROPIC_API_KEY
)

def ask_ai(subject, email_body, context):
    """Send email body to ChatGPT and get a response, using subject as chat thread."""

    # decide which models to use
    if subject[0] == "!":
        open_ai_model = "gpt-4o"
        anthropic_model = 'claude-3-5-sonnet-20240620'
        subject = subject[1:]
    else:
        open_ai_model = "gpt-4o-mini"
        anthropic_model = 'claude-3-haiku-20240307'

    # retrieve chat history
    chat_history = get_chat_history(subject)

    

    # open ai interaction
    try:

        # create messages object for openai
        messages = [{"role": "system", "content": f"{context}"}]
        messages.extend(chat_history)
        messages.append({"role": "user", "content": email_body})

        # ask openai
        response = openai_client.chat.completions.create(
            model=open_ai_model,
            messages=messages
        )

        # strip reply
        openai_reply = response.choices[0].message.content.strip()

        # add to database
        update_chat_history(subject, "openai", email_body, openai_reply)
    
    except Exception as e:
        print(f"An error occurred while communicating with OpenAI: {e}")
        return "I'm sorry, but I couldn't process your request."
    
    # anthropic interaction

    try:
        # create messages object for anthropic
        messages = chat_history
        messages.append({"role": "user", "content": email_body})

        # ask anthropic
        response = anthropic_client.messages.create(
            system=context,
            messages=messages,
            model=anthropic_model,  # or whichever Anthropic model you're using
            max_tokens=1024,
        )

        # strip reply
        print(response.content)
        anthropic_reply = response.content[0].text.strip()

        # add to database
        update_chat_history(subject, "anthropic", email_body, anthropic_reply)

    except Exception as e:
        print(f"An error occurred while communicating with Anthropic: {e}")
        return "I'm sorry, but I couldn't process your request."

    # return the reply to be sent back
    return f'{open_ai_model}:\n{openai_reply}\n\n{anthropic_model}:\n{anthropic_reply}'