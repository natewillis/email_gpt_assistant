import sqlite3
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# read environment variables
DB_FILE = os.getenv('DATABASE_FILE')
print(f'dbfile is {DB_FILE}')

def create_database():
    """Create SQLite database to store chat threads if it doesn't exist."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS threads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT,
            user_message TEXT,
            ai_response TEXT,
            ai_type TEXT,
            datetime DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def get_chat_history(subject):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT user_message, ai_response FROM threads WHERE subject = ? ORDER BY datetime", (subject,))
    history = cursor.fetchall()
    conn.close()

    messages = []
    for user_message, ai_response in history:
        messages.append({"role": "user", "content": user_message})
        messages.append({"role": "assistant", "content": ai_response})
    return messages


def update_chat_history(subject, ai_type, human_prompt, ai_response):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    try:
        # If the subject already exists, this will update the existing row
        # If it doesn't exist, it will insert a new row
        cursor.execute("""
            INSERT INTO threads 
            (subject, user_message, ai_response, ai_type)
            VALUES (?, ?, ?, ?)
        """, (subject, human_prompt, ai_response, ai_type))

        conn.commit()
        print(f"Chat history updated for subject: {subject}")

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")

    finally:
        conn.close()