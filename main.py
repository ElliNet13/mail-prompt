import smtplib
import imaplib
import email
import json
import os
from email import policy

def save_credentials(email, password):
    credentials = {
        "email": email,
        "password": password
    }
    with open("credentials.json", "w") as f:
        json.dump(credentials, f)
    print("Credentials saved successfully!")

def load_credentials():
    try:
        with open("credentials.json", "r") as f:
            credentials = json.load(f)
        return credentials["email"], credentials["password"]
    except FileNotFoundError:
        print("No saved credentials found.")
        return None, None
    except Exception as e:
        print("An error occurred while loading credentials:", e)
        return None, None

def remove_credentials_file():
    if os.path.exists("credentials.json"):
        os.remove("credentials.json")
        print("Credentials file removed.")
    else:
        print("No credentials file found.")

def send_email():
    sender_email, password = load_credentials()
    if not all((sender_email, password)):
        print("You have not logged in. Please use the login command.")
        return
    recipient_email = input("Enter recipient email address: ")
    subject = input("Enter email subject: ")
    body = input("Enter email body: ")

    message = f"From: {sender_email}\nTo: {recipient_email}\nSubject: {subject}\n\n{body}"

    try:
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(sender_email, password)
        server.sendmail(sender_email, recipient_email, message)
        print("Email sent successfully!")
        server.quit()
    except Exception as e:
        print("An error occurred:", e)

def view_emails(num_emails=1):
    user_email, password = load_credentials()
    if not all((user_email, password)):
        print("You have not logged in. Please use the login command.")
        return
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(user_email, password)
        mail.select('inbox')
        _, data = mail.search(None, 'ALL')
        mail_ids = data[0].split()
        latest_mail_ids = mail_ids[-num_emails:]

        for num in latest_mail_ids:
            _, data = mail.fetch(num, '(RFC822)')
            raw_email = data[0][1]
            email_message = email.message_from_bytes(raw_email)
            print('ID:', num.decode())
            print('From:', email_message['From'])
            print('Subject:', email_message['Subject'])
            print('Date:', email_message['Date'])
            print()
        mail.logout()
    except Exception as e:
        print("An error occurred:", e)

def read_email_file(email_id):
    try:
        with open(f"{email_id}", "rb") as f:
            email_message = email.message_from_binary_file(f, policy=policy.default)
            print("From:", email_message['From'])
            print("Subject:", email_message['Subject'])
            print("Date:", email_message['Date'])
            print("\nBody:")
            if email_message.is_multipart():
                for part in email_message.walk():
                    if part.get_content_type() == "text/plain":
                        print(part.get_payload(decode=True).decode())
            else:
                print(email_message.get_payload(decode=True).decode())
    except FileNotFoundError:
        print(f"No EML file found for email ID: {email_id}")
    except Exception as e:
        print("An error occurred:", e)

def read_email(email_id):
    user_email, password = load_credentials()
    if not all((user_email, password)):
        print("You have not logged in. Please use the login command.")
        return
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(user_email, password)
        mail.select('inbox')
        status, data = mail.fetch(email_id.encode(), '(RFC822)')
        raw_email = data[0][1]
        email_message = email.message_from_bytes(raw_email)
        print("From:", email_message['From'])
        print("Subject:", email_message['Subject'])
        print("Date:", email_message['Date'])
        print("\nBody:")
        if email_message.is_multipart():
            for part in email_message.walk():
                if part.get_content_type() == "text/plain":
                    print(part.get_payload(decode=True).decode())
        else:
            print(email_message.get_payload(decode=True).decode())
        mail.logout()
    except Exception as e:
        print("An error occurred:", e)

def save_email(email_id):
    user_email, password = load_credentials()
    if not all((user_email, password)):
        print("You have not logged in. Please use the login command.")
        return
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(user_email, password)
        mail.select('inbox')
        status, data = mail.fetch(email_id.encode(), '(RFC822)')
        raw_email = data[0][1]
        email_message = email.message_from_bytes(raw_email)

        # Save email as EML file
        with open(f"email_{email_id}.eml", "wb") as f:
            f.write(email_message.as_bytes(policy=policy.default))

        print(f"Email {email_id} saved as email_{email_id}.eml")

        mail.logout()
    except Exception as e:
        print("An error occurred:", e)

def search_email(keyword):
    user_email, password = load_credentials()
    if not all((user_email, password)):
        print("You have not logged in. Please use the login command.")
        return
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(user_email, password)
        mail.select('inbox')
        _, data = mail.search(None, 'ALL')
        mail_ids = data[0].split()

        for num in mail_ids:
            _, data = mail.fetch(num, '(RFC822)')
            raw_email = data[0][1]
            email_message = email.message_from_bytes(raw_email)
            if keyword.lower() in email_message['Subject'].lower():
                print('ID:', num.decode())
                print('From:', email_message['From'])
                print('Subject:', email_message['Subject'])
                print('Date:', email_message['Date'])
                print()
        mail.logout()
    except Exception as e:
        print("An error occurred:", e)

def login():
    remove_credentials_file()
    email = input("Enter your email address: ")
    password = input("Enter your email password: ")
    save_credentials(email, password)
    # Test connecting after saving credentials
    test_connection()

def test_connection():
    email, password = load_credentials()
    if not all((email, password)):
        print("You have not logged in. Please use the login command.")
        return
    try:
        # Test SMTP connection
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(email, password)
        server.quit()
        print("SMTP connection test successful.")
        # Test IMAP connection
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(email, password)
        mail.logout()
        print("IMAP connection test successful.")
    except Exception as e:
        print("Connection test failed:", e)

def help_menu():
    print("Available commands:")
    print("login - Log in with your Google email and password. If you have 2-step authentication enabled, you may need to create an app password.")
    print("send - Send an email")
    print("q [num_emails] - View emails. Optional argument [num_emails] specifies how many of the latest emails to view. Default is 1.")
    print("read [email_id] - Read the contents of an email with the given ID.")
    print("readf [file_name] - read an EML file.")
    print("save [email_id] - Save an email with the given ID as an EML file.")
    print("search [keyword] - Search for emails with the given keyword in the subject.")
    print("help - Display this help menu")
    print("quit - Exit the Mail prompt")

def mail_prompt():
    print("Welcome to Mail Prompt!")
    help_menu()
    while True:
        command = input(">> ").strip().lower()
        if command.startswith("q"):
            try:
                num_emails = int(command.split()[1])
            except IndexError:
                num_emails = 1
            except ValueError:
                print("Invalid number of emails.")
                continue
            view_emails(num_emails)
        elif command.startswith("readf"):
            try:
                email_id = command.split()[1]
            except IndexError:
                print("Please provide an EML file name.")
                continue
            read_email_file(email_id)
        elif command.startswith("save"):
            try:
                email_id = command.split()[1]
            except IndexError:
                print("Please provide an email ID.")
                continue
            save_email(email_id)
        elif command.startswith("read"):
            try:
                email_id = command.split()[1]
            except IndexError:
                print("Please provide an email ID.")
                continue
            read_email(email_id)
        elif command.startswith("search"):
            try:
                keyword = command.split(maxsplit=1)[1]
            except IndexError:
                print("Please provide a keyword to search for.")
                continue
            search_email(keyword)
        elif command == "login":
            login()
        elif command == "send":
            send_email()
        elif command == "help":
            help_menu()
        elif command == "quit":
            print("Goodbye!")
            break
        else:
            print("Invalid command. Type 'help' to see available commands.")

if __name__ == "__main__":
    mail_prompt()
