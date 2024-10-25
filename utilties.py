from datetime import datetime

def log_message(message):
    """Print the message with the current time."""
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}")