"""
Email Service — Numista.AI Passport Protocol & Notification Service
Handles non-blocking email dispatches with PDF attachments via SendGrid API or SMTP.
"""

import os
import logging
import base64
from typing import Dict, Any, Optional
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import smtplib

from config import (
    APP_PUBLIC_DOMAIN,
    APP_BASE_URL,
    SENDER_EMAIL,
    SENDGRID_API_KEY,
    SMTP_HOST,
    SMTP_PORT,
    SMTP_USER,
    SMTP_PASSWORD
)

logger = logging.getLogger("numista_backend.email_service")


def send_passport_transfer_email(
    recipient_email: str,
    transfer_data: Dict[str, Any],
    pdf_bytes: Optional[bytes] = None
) -> Dict[str, Any]:
    """
    Sends Passport Certificate of Lateral Transfer notification to recipient_email with PDF attached.
    """
    if not recipient_email or "@" not in recipient_email:
        return {"status": "error", "message": "Invalid recipient email address"}

    transfer_id = transfer_data.get("transfer_id", "N/A")
    claim_pin = transfer_data.get("claim_pin", "******")
    sender_id = transfer_data.get("sender_id", "Numista.AI Collector")
    expires_at = transfer_data.get("expires_at", "")[:10]
    items = transfer_data.get("items", [])
    item_count = len(items)

    claim_url = f"{APP_BASE_URL}/#/claim?transfer_id={transfer_id}&pin={claim_pin}"

    subject = f"Official Passport Certificate of Lateral Transfer — Claim PIN: {claim_pin}"

    items_html = ""
    for itm in items[:10]:
        title = itm.get("title") or f"{itm.get('year', '')} {itm.get('programSeries', '')} {itm.get('denomination', '')}".strip()
        cond = itm.get("condition", "Ungraded")
        items_html += f"<li style='margin-bottom: 4px;'><b>{title}</b> ({cond})</li>"

    if item_count > 10:
        items_html += f"<li><i>...and {item_count - 10} more items</i></li>"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="utf-8"></head>
    <body style="font-family: Arial, sans-serif; background-color: #0F172A; color: #F8FAFC; padding: 24px;">
      <div style="max-width: 600px; margin: 0 auto; background-color: #1E293B; border-radius: 12px; padding: 32px; border: 1px solid #334155;">
        <h2 style="color: #0284C7; margin-top: 0;">NUMISTA.AI • PASSPORT PROTOCOL</h2>
        <h3 style="color: #FFFFFF; margin-bottom: 8px;">Passport Certificate of Lateral Transfer</h3>
        <p style="color: #CBD5E1; font-size: 14px;">
          You have received a lateral property transfer of <b>{item_count} item(s)</b> from <b>{sender_id}</b>.
        </p>

        <div style="background-color: #0F172A; padding: 20px; border-radius: 8px; margin: 20px 0; border: 1px solid #334155;">
          <p style="margin: 0 0 6px 0; font-size: 12px; color: #94A3B8; font-weight: bold;">TRANSFER DETAILS</p>
          <p style="margin: 4px 0; color: #FFFFFF; font-size: 13px;"><b>Transfer ID:</b> <code style="color: #38BDF8;">{transfer_id}</code></p>
          <p style="margin: 4px 0; color: #FFFFFF; font-size: 13px;"><b>6-Digit Claim PIN:</b> <span style="color: #38BDF8; font-size: 20px; font-weight: bold; letter-spacing: 2px;">{claim_pin}</span></p>
          <p style="margin: 4px 0; color: #FFFFFF; font-size: 13px;"><b>Expiration Date:</b> {expires_at} (60-Day Limit)</p>
        </div>

        <p style="color: #94A3B8; font-size: 12px; font-style: italic;">
          🔒 Security Notice: This transfer is locked exclusively to <b>{recipient_email}</b>. Only an account signed in with this email address can adopt these items into their vault.
        </p>

        <h4 style="color: #FFFFFF; margin-top: 20px; margin-bottom: 8px;">Transferred Items Preview:</h4>
        <ul style="color: #CBD5E1; font-size: 13px; padding-left: 20px;">
          {items_html}
        </ul>

        <div style="text-align: center; margin-top: 28px;">
          <a href="{claim_url}" style="background-color: #0284C7; color: #FFFFFF; text-decoration: none; padding: 14px 28px; border-radius: 8px; font-weight: bold; display: inline-block; font-size: 15px;">
            Claim &amp; Adopt Items into Vault
          </a>
        </div>

        <p style="color: #64748B; font-size: 12px; text-align: center; margin-top: 24px;">
          If you do not have a Numista.AI account yet, clicking the button above will allow you to create a free account with {recipient_email} to claim your items.
        </p>
      </div>
    </body>
    </html>
    """

    # 1. Try SendGrid API if SENDGRID_API_KEY available
    if SENDGRID_API_KEY:
        try:
            import urllib.request
            import json

            payload = {
                "personalizations": [{"to": [{"email": recipient_email}]}],
                "from": {"email": SENDER_EMAIL, "name": "Numista.AI Transfers"},
                "subject": subject,
                "content": [{"type": "text/html", "value": html_content}]
            }

            if pdf_bytes:
                b64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
                payload["attachments"] = [{
                    "content": b64_pdf,
                    "filename": f"Passport_Certificate_{transfer_id[:8]}.pdf",
                    "type": "application/pdf",
                    "disposition": "attachment"
                }]

            req_data = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(
                "https://api.sendgrid.com/v3/mail/send",
                data=req_data,
                headers={
                    "Authorization": f"Bearer {SENDGRID_API_KEY}",
                    "Content-Type": "application/json"
                },
                method="POST"
            )
            with urllib.request.urlopen(req) as resp:
                if resp.status in (200, 202):
                    msg_id = resp.headers.get("X-Message-Id", f"sg_{transfer_id[:8]}")
                    logger.info(f"Successfully sent SendGrid transfer email to {recipient_email}")
                    return {"status": "sent", "provider": "sendgrid", "message_id": msg_id}
        except Exception as sge:
            logger.warning(f"SendGrid API dispatch failed: {sge}")

    # 2. Try SMTP if SMTP_HOST available
    if SMTP_HOST:
        try:
            msg = MIMEMultipart()
            msg["From"] = SENDER_EMAIL
            msg["To"] = recipient_email
            msg["Subject"] = subject

            msg.attach(MIMEText(html_content, "html"))

            if pdf_bytes:
                att = MIMEApplication(pdf_bytes, _subtype="pdf")
                att.add_header("Content-Disposition", "attachment", filename=f"Passport_Certificate_{transfer_id[:8]}.pdf")
                msg.attach(att)

            with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
                server.starttls()
                if SMTP_USER and SMTP_PASSWORD:
                    server.login(SMTP_USER, SMTP_PASSWORD)
                server.send_message(msg)

            msg_id = f"smtp_{transfer_id[:8]}"
            logger.info(f"Successfully sent SMTP transfer email to {recipient_email}")
            return {"status": "sent", "provider": "smtp", "message_id": msg_id}
        except Exception as smtpe:
            logger.warning(f"SMTP dispatch failed: {smtpe}")

    # Fallback when credentials are unconfigured or fail
    logger.info(f"Email credentials offline/unconfigured. Skipping automated email to {recipient_email}")
    return {
        "status": "unconfigured",
        "message": "Email delivery credentials not configured. Manual PDF download required."
    }
