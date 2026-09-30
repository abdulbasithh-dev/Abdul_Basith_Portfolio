import os
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load .env file
load_dotenv()

def test_smtp_configuration():
    print("=" * 60)
    print("  Abdul Basith Portfolio - Email Configuration Diagnostic")
    print("=" * 60)

    username = os.environ.get("MAIL_USERNAME")
    password = os.environ.get("MAIL_PASSWORD")
    recipient = os.environ.get("RECIPIENT_EMAIL", "abasith8074@gmail.com")

    if not username:
        print("[!] ERROR: MAIL_USERNAME environment variable is NOT set.")
        print("    -> Add MAIL_USERNAME=your_email@gmail.com to your .env file")
        print("    -> Or set it in Vercel Project Settings > Environment Variables")
        return False

    if not password:
        print("[!] ERROR: MAIL_PASSWORD environment variable is NOT set.")
        print("    -> Add MAIL_PASSWORD=your_16_character_app_password to your .env file")
        print("    -> Or set it in Vercel Project Settings > Environment Variables")
        print("    -> Generate one at: https://myaccount.google.com/apppasswords")
        return False

    masked_pw = password[:2] + "*" * (len(password) - 4) + password[-2:] if len(password) > 4 else "****"
    print(f"[+] MAIL_USERNAME : {username}")
    print(f"[+] MAIL_PASSWORD : {masked_pw}")
    print(f"[+] RECIPIENT_EMAIL: {recipient}")
    print("-" * 60)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "🧪 Portfolio Email Test - Configuration Verified"
    msg["From"] = f"Portfolio Bot <{username}>"
    msg["To"] = recipient
    msg["Reply-To"] = username

    text_body = "This is a diagnostic test email from your Portfolio backend. If you received this, your SMTP configuration is working perfectly!"
    html_body = f"""
    <html>
      <body style="font-family: Arial, sans-serif; background-color: #0f172a; color: #f8fafc; padding: 20px; border-radius: 8px;">
        <h2 style="color: #3b82f6;">✅ SMTP Configuration Verified!</h2>
        <p>Your portfolio email backend is properly authenticated and able to send messages.</p>
        <div style="background-color: #1e293b; padding: 15px; border-radius: 6px; border-left: 4px solid #3b82f6;">
          <p style="margin: 0;"><strong>Sender:</strong> {username}</p>
          <p style="margin: 5px 0 0 0;"><strong>Recipient:</strong> {recipient}</p>
        </div>
        <p style="color: #94a3b8; font-size: 12px; margin-top: 20px;">Sent from Abdul Basith's Portfolio Diagnostic Tool</p>
      </body>
    </html>
    """
    msg.attach(MIMEText(text_body, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    # Attempt 1: Port 465 (SSL) - Best for serverless
    print("[*] Testing Port 465 (SSL direct)...")
    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context, timeout=8) as server:
            server.login(username, password.strip())
            server.send_message(msg)
            print(" -> [SUCCESS] Connected, authenticated, and email dispatched via Port 465 (SSL)!")
            print(f" -> Check inbox for {recipient}")
            return True
    except smtplib.SMTPAuthenticationError as auth_err:
        print(f" -> [FAILED] Authentication Error (535): {auth_err}")
        print("    -> IMPORTANT: If using Gmail, you MUST use an App Password, NOT your regular password.")
        print("    -> How to create an App Password:")
        print("       1. Go to https://myaccount.google.com/security")
        print("       2. Turn on 2-Step Verification if not enabled.")
        print("       3. Search for 'App passwords' (or go to https://myaccount.google.com/apppasswords)")
        print("       4. Create an app named 'Portfolio' and copy the 16-character code.")
        print("       5. Put that 16-character code in MAIL_PASSWORD.")
        return False
    except Exception as e:
        print(f" -> [WARNING] Port 465 connection failed: {e}")
        print("[*] Falling back to Port 587 (STARTTLS)...")

    # Attempt 2: Port 587 (STARTTLS)
    try:
        context = ssl.create_default_context()
        with smtplib.SMTP("smtp.gmail.com", 587, timeout=8) as server:
            server.starttls(context=context)
            server.login(username, password.strip())
            server.send_message(msg)
            print(" -> [SUCCESS] Connected, authenticated, and email dispatched via Port 587 (TLS)!")
            print(f" -> Check inbox for {recipient}")
            return True
    except smtplib.SMTPAuthenticationError as auth_err:
        print(f" -> [FAILED] Authentication Error: {auth_err}")
        print("    -> Ensure you are using a 16-character Google App Password.")
        return False
    except Exception as e:
        print(f" -> [FAILED] Port 587 also failed: {e}")
        return False

if __name__ == "__main__":
    test_smtp_configuration()
