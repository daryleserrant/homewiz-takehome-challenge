import smtplib
from email.mime.text import MIMEText
#import configparser
import os

#config = configparser.ConfigParser()
#config.read('backend/config.ini')

# Set up configuration from environment variables for deployment in Render or similar platforms.
# You can set these environment variables in your deployment platform.
# If you have a config.ini file, you can read it instead.
config = {
    "SETTINGS": {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "DATABASE_FILE": os.getenv("DATABASE_FILE", "backend/lead_to_lease.db"),
        "MODEL": "gpt-4o",
        "SMTP_SERVER": os.getenv("SMTP_SERVER"),
        "SMTP_PORT": int(os.getenv("SMTP_PORT", "587")),
        "SMTP_USERNAME": os.getenv("SMTP_USERNAME"),
        "SMTP_PASSWORD": os.getenv("SMTP_PASSWORD"),
        "FROM_EMAIL": os.getenv("FROM_EMAIL")
    }
}

def send_confirmation_email(name: str, email: str, property: dict, start_time: str):
    msg = MIMEText(f"""
Hi {name},

Your tour is confirmed!

Property: {property['address']}
Unit: {property['id']}
Time: {start_time}

– Leasing Bot
""")
    msg["Subject"] = "Tour Confirmation"
    msg["From"] = config['SETTINGS']['FROM_EMAIL']
    msg["To"] = email

    with smtplib.SMTP(config['SETTINGS']['SMTP_SERVER'], config['SETTINGS']['SMTP_PORT']) as server:
        server.starttls()
        server.login(config['SETTINGS']['SMTP_USERNAME'], config['SETTINGS']['SMTP_PASSWORD'])
        server.sendmail(msg["From"], [msg["To"]], msg.as_string())
