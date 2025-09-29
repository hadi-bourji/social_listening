import smtplib
from email.mime.text import MIMEText
import ssl


 
sender_gmail = "rssemail12@gmail.com"
sender_gmail_password = "dara fxoq wicw qefw"
sender_outlook = "vs2u@et.eurofinsus.com"
sender_outlook_password = "Finchita9712@@@@####"

def load_email():
    try:
        with open("email.txt", "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return None

def send_from_gmail(to, subject, body):
    msg = MIMEText(body, "html")
    msg["Subject"] = subject
    msg["From"] = sender_gmail
    msg["To"] = to

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_gmail, sender_gmail_password)
        server.sendmail(sender_gmail, to, msg.as_string())

def send_from_outlook(to, subject, body):
    msg = MIMEText(body, "html")
    msg["Subject"] = subject
    msg["From"] = sender_outlook
    msg["To"] = to

    context = ssl.create_default_context()
    with smtplib.SMTP("smtp.office365.com", 587) as server:
        server.starttls(context=context)
        server.login(sender_outlook, sender_outlook_password)
        server.sendmail(sender_outlook, to, msg.as_string())


def get_rss():
    return "hello"

if __name__ == "__main__":
    user_email = load_email()
    if user_email:
        try:
            print("Attempting Gmail...")
            send_from_gmail(user_email, "RSS Feed", get_rss())
        except Exception as e:
            print(f"Gmail failed: {e}")
            print("Falling back to Outlook...")
            try:
                send_from_outlook(user_email, "RSS Feed", get_rss())
            except Exception as e2:
                print(f"Outlook also failed: {e2}")
    else:
        print("No recipient email found in email.txt")