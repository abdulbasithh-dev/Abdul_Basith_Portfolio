import os
import smtplib
import ssl
import logging
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from flask import Flask, render_template, request, flash, redirect, url_for

# Load local environment variables from .env file if available
load_dotenv()

app = Flask(__name__)
# Secret key for session management and flash messages
app.secret_key = os.environ.get("SECRET_KEY", "dev_secret_key_change_in_production")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Recipient email for contact inquiries
RECIPIENT_EMAIL = os.environ.get("RECIPIENT_EMAIL", "abdulbasithh.dev@gmail.com")


def send_contact_email(name, sender_email, message_content):
    """
    Sends contact email via Gmail SMTP with timeout limits suitable for serverless execution.
    Tries Port 465 (SSL) first, and falls back to Port 587 (TLS).
    """
    mail_username = os.environ.get("MAIL_USERNAME")
    mail_password = os.environ.get("MAIL_PASSWORD")
    recipient = os.environ.get("RECIPIENT_EMAIL", RECIPIENT_EMAIL)

    if not mail_username or not mail_password:
        logger.error(
            "Email credentials not configured! "
            "Please configure MAIL_USERNAME and MAIL_PASSWORD in your environment variables."
        )
        return False, "Email service is temporarily unconfigured on the server."

    # Construct the message
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Portfolio Contact: Message from {name}"
    msg["From"] = f"{name} via Portfolio <{mail_username}>"
    msg["To"] = recipient
    msg["Reply-To"] = sender_email

    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    text_content = f"""New Message from Portfolio Contact Form:

Name: {name}
Email: {sender_email}
Received At: {timestamp}

Message:
{message_content}

---
Reply directly to this email to respond to {name}.
"""

    html_content = f"""
    <html>
      <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #0f172a; color: #f1f5f9; padding: 24px; margin: 0;">
        <div style="max-width: 600px; margin: 0 auto; background-color: #1e293b; border-radius: 12px; overflow: hidden; border: 1px solid #334155;">
          <div style="background: linear-gradient(135deg, #2563eb, #7c3aed); padding: 20px 24px;">
            <h2 style="color: #ffffff; margin: 0; font-size: 20px;">New Portfolio Contact Message</h2>
          </div>
          <div style="padding: 24px;">
            <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
              <tr>
                <td style="padding: 8px 0; color: #94a3b8; width: 80px; font-weight: 600;">From:</td>
                <td style="padding: 8px 0; color: #f1f5f9; font-weight: 500;">{name}</td>
              </tr>
              <tr>
                <td style="padding: 8px 0; color: #94a3b8; font-weight: 600;">Email:</td>
                <td style="padding: 8px 0;"><a href="mailto:{sender_email}" style="color: #60a5fa; text-decoration: none;">{sender_email}</a></td>
              </tr>
              <tr>
                <td style="padding: 8px 0; color: #94a3b8; font-weight: 600;">Date:</td>
                <td style="padding: 8px 0; color: #94a3b8; font-size: 13px;">{timestamp}</td>
              </tr>
            </table>
            <div style="margin-top: 16px;">
              <p style="color: #94a3b8; font-weight: 600; margin: 0 0 8px 0;">Message:</p>
              <div style="background-color: #0f172a; border-radius: 8px; padding: 16px; color: #e2e8f0; white-space: pre-wrap; font-size: 15px; line-height: 1.5; border: 1px solid #334155;">{message_content}</div>
            </div>
            <div style="margin-top: 24px; text-align: center;">
              <a href="mailto:{sender_email}" style="display: inline-block; background-color: #2563eb; color: #ffffff; padding: 10px 20px; border-radius: 6px; text-decoration: none; font-weight: 600; font-size: 14px;">Reply to {name}</a>
            </div>
          </div>
          <div style="background-color: #0f172a; padding: 12px 24px; text-align: center; border-top: 1px solid #1e293b;">
            <p style="color: #64748b; font-size: 12px; margin: 0;">Sent automatically from Abdul Basith's Portfolio Website</p>
          </div>
        </div>
      </body>
    </html>
    """

    msg.attach(MIMEText(text_content, "plain"))
    msg.attach(MIMEText(html_content, "html"))

    # Attempt 1: Port 465 (SSL) with strict 6s timeout to avoid Vercel 10s serverless cutoff
    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context, timeout=6) as server:
            server.login(mail_username, mail_password.strip())
            server.send_message(msg)
            logger.info("Contact email sent successfully via SSL (Port 465).")
            return True, None
    except smtplib.SMTPAuthenticationError as auth_err:
        logger.error(
            f"SMTP Authentication Error: {auth_err}. "
            "Please verify that MAIL_PASSWORD is a valid 16-character Google App Password."
        )
        return False, "Authentication failed with email provider."
    except Exception as e:
        logger.warning(f"Port 465 (SSL) attempt failed ({e}), attempting fallback to Port 587 (TLS)...")

    # Attempt 2: Port 587 (STARTTLS)
    try:
        context = ssl.create_default_context()
        with smtplib.SMTP("smtp.gmail.com", 587, timeout=6) as server:
            server.starttls(context=context)
            server.login(mail_username, mail_password.strip())
            server.send_message(msg)
            logger.info("Contact email sent successfully via TLS (Port 587).")
            return True, None
    except smtplib.SMTPAuthenticationError as auth_err:
        logger.error(f"SMTP Authentication Error: {auth_err}.")
        return False, "Authentication failed with email provider."
    except Exception as e:
        logger.error(f"SMTP connection error: {str(e)}")
        return False, str(e)


@app.route("/")
def home():
    projects = [
        {
            "title": "ResQ — Emergency Ambulance Booking & Dispatch System",
            "description": "A production-grade Emergency Medical Dispatch (EMD) and live tracking platform featuring real-time WebSockets, autonomous GPS simulation, multi-factor ambulance matching (Haversine & ETA), and role-based access for Citizens, Ambulance Drivers, Hospital ER, and Dispatchers.",
            "technologies": ["FastAPI", "Python", "WebSockets", "Leaflet GIS", "React", "SQLAlchemy"],
            "github_link": "https://github.com/abdulbasithh-dev/emergency-ambulance-booking-system",
            "image": "/static/img/ambulance.jpg",
        }
    ]

    certifications = [
        {
            "name": "Oracle Cloud Infrastructure Foundations Associate",
            "issuer": "Oracle",
            "link": "#",
        },
        {
            "name": "Getting Started with Artificial Intelligence",
            "issuer": "IBM",
            "link": "#",
        },
    ]

    return render_template(
        "index.html",
        title="Abdul Basith | Python Full Stack Developer",
        projects=projects,
        certifications=certifications,
    )


@app.route("/contact", methods=["POST"])
def contact():
    name = (request.form.get("name") or "").strip()
    email = (request.form.get("email") or "").strip()
    message = (request.form.get("message") or "").strip()

    if not name or not email or not message:
        flash("Please fill in all fields before sending your message.", "danger")
        return redirect(url_for("home", _anchor="contact"))

    success, error = send_contact_email(name, email, message)

    if success:
        flash("Message sent successfully! I'll get back to you soon.", "success")
    else:
        logger.error(f"Contact form dispatch error: {error}")
        flash(
            f"Could not send email automatically right now. Please email me directly at {RECIPIENT_EMAIL}",
            "danger",
        )

    return redirect(url_for("home", _anchor="contact"))


if __name__ == "__main__":
    app.run(debug=True)
