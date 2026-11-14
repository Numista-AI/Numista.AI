"""Wishlist email composition and fail-closed delivery helpers."""

import html
import logging
import os
import re
import smtplib
from email.message import EmailMessage
from typing import Any, Dict, List
from urllib.parse import parse_qs, quote_plus, urlparse

import httpx

logger = logging.getLogger("numista_backend.wishlist_email")

EPN_CAMPID = "5339148752"
EPN_MKRID = "711-53200-19255-0"
EMAIL_REGEX = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")


class EmailProviderNotConfiguredError(RuntimeError):
    """Raised when neither API key nor SMTP credentials are present."""


def ensure_epn_affiliate_url(item: Dict[str, Any], custom_id: str) -> str:
    """Return a valid EPN search URL stamped with the configured campid/mkrid."""
    raw_url = str(item.get("ebay_url") or "").strip()
    if raw_url.startswith("https://www.ebay.com/sch/i.html"):
        qs = parse_qs(urlparse(raw_url).query)
        if EPN_CAMPID in qs.get("campid", []) and EPN_MKRID in qs.get("mkrid", []):
            return raw_url
    query = str(item.get("ebay_query") or "").strip() or " ".join(
        part
        for part in [
            str(item.get("year") or "").strip(),
            str(item.get("mint_mark") or "").strip(),
            str(item.get("program_name") or "").strip(),
            str(item.get("coin_name") or item.get("title") or "").strip(),
            "coin",
        ]
        if part
    )
    encoded_q = quote_plus(query or "US coin")
    safe_custom = quote_plus(custom_id[:48])
    return (
        f"https://www.ebay.com/sch/i.html?_nkw={encoded_q}&_sacat=11116"
        f"&mkevt=1&mkcid=1&mkrid={EPN_MKRID}&campid={EPN_CAMPID}&toolid=10001&siteid=0"
        f"&customid={safe_custom}"
    )


def build_wishlist_email_html(
    *,
    owner_alias: str,
    personal_note: str,
    share_url: str,
    items: List[Dict[str, Any]],
) -> str:
    """Build accessible HTML email grouped by program with escaped user inputs."""
    safe_alias = html.escape(owner_alias or "Numista Collector")
    safe_note = html.escape(personal_note.strip()) if personal_note else ""
    safe_share_url = html.escape(share_url, quote=True)

    grouped: Dict[str, List[Dict[str, Any]]] = {}
    for item in items:
        group = str(item.get("program_name") or "Individual Wanted Coins").strip()
        grouped.setdefault(group, []).append(item)

    sections_html: List[str] = []
    for group_name, group_items in grouped.items():
        rows_html: List[str] = []
        for idx, item in enumerate(group_items):
            year = html.escape(str(item.get("year") or "").strip())
            coin_name = html.escape(
                str(item.get("coin_name") or item.get("title") or "Coin").strip()
            )
            variety = html.escape(
                str(item.get("variety_label") or item.get("mint_mark") or "Any Mint").strip()
            )
            ebay_href = html.escape(
                ensure_epn_affiliate_url(item, f"email_{idx}"), quote=True
            )
            rows_html.append(
                f"""
                <tr>
                  <td style="padding:12px;border-bottom:1px solid #D5DEEA;font-size:18px;color:#0B1A2E;">
                    <strong>{year} {coin_name}</strong><br>
                    <span style="display:inline-block;margin-top:4px;padding:3px 10px;background:#EEF3F8;
                      border:1px solid #C9A400;border-radius:6px;font-size:16px;font-weight:bold;color:#0B1A2E;">
                      {variety}
                    </span>
                  </td>
                  <td align="right" style="padding:12px;border-bottom:1px solid #D5DEEA;">
                    <a href="{ebay_href}" style="display:inline-block;padding:12px 18px;background:#1D4F91;
                      color:#FFFFFF;text-decoration:none;font-size:18px;font-weight:bold;border-radius:8px;">
                      Buy on eBay &rarr;
                    </a>
                  </td>
                </tr>
                """.strip()
            )
        sections_html.append(
            f"""
            <h2 style="margin:24px 0 8px 0;font-size:20px;color:#0B1A2E;">
              {html.escape(group_name)} ({len(group_items)})
            </h2>
            <table width="100%" cellpadding="0" cellspacing="0"
              style="border-collapse:collapse;background:#FFFFFF;border:1px solid #D5DEEA;border-radius:8px;">
              {"".join(rows_html)}
            </table>
            """.strip()
        )

    note_block = (
        f'<p style="font-size:18px;color:#0B1A2E;background:#FFFFFF;padding:14px;'
        f'border-left:5px solid #C9A400;margin:14px 0;">&ldquo;{safe_note}&rdquo;</p>'
        if safe_note
        else ""
    )

    return f"""<!DOCTYPE html>
<html><body style="margin:0;padding:24px;background:#EEF3F8;font-family:Arial,Helvetica,sans-serif;color:#0B1A2E;">
  <div style="max-width:680px;margin:0 auto;background:#FFFFFF;border:1px solid #D5DEEA;border-radius:12px;padding:24px;">
    <h1 style="margin:0 0 8px 0;font-size:24px;color:#0B1A2E;">{safe_alias} sent you their Coin Wish List</h1>
    <p style="font-size:18px;line-height:1.5;margin:0 0 16px 0;">
      Each coin shows the exact year and mint mark needed, with a direct <strong>Buy on eBay</strong> link.
    </p>
    {note_block}
    <p style="margin:20px 0;">
      <a href="{safe_share_url}" style="display:inline-block;padding:16px 24px;background:#0F766E;
        color:#FFFFFF;text-decoration:none;font-size:18px;font-weight:bold;border-radius:10px;">
        Open Interactive Gift List (Tap &ldquo;I Bought This&rdquo; to Reserve)
      </a>
    </p>
    {"".join(sections_html)}
    <p style="margin-top:24px;font-size:15px;color:#475569;">
      Tip: Prefer eBay sellers with 99%+ positive feedback, and mark purchased coins on the interactive Gift List link above so relatives do not buy duplicates.
    </p>
  </div>
</body></html>"""


def build_wishlist_email_text(
    *,
    owner_alias: str,
    personal_note: str,
    share_url: str,
    items: List[Dict[str, Any]],
) -> str:
    """Build plain-text fallback version of the Wish List email."""
    lines = [
        f"{owner_alias or 'Numista Collector'} sent you their Coin Wish List",
        f"Interactive Gift List (mark 'I Bought This'): {share_url}",
    ]
    if personal_note and personal_note.strip():
        lines.append(f"Note: {personal_note.strip()}")
    lines.append("")
    for idx, item in enumerate(items):
        group = str(item.get("program_name") or "Individual Wanted Coins").strip()
        year = str(item.get("year") or "").strip()
        coin_name = str(item.get("coin_name") or item.get("title") or "Coin").strip()
        variety = str(
            item.get("variety_label") or item.get("mint_mark") or "Any Mint"
        ).strip()
        ebay_url = ensure_epn_affiliate_url(item, f"txt_{idx}")
        lines.append(f"- [{group}] {year} {coin_name} ({variety})")
        lines.append(f"  Buy on eBay: {ebay_url}")
    return "\n".join(lines)


async def send_wishlist_email(
    *,
    recipient_email: str,
    subject: str,
    html_body: str,
    text_body: str,
) -> str:
    """Send Wish List email via Resend, SendGrid, or SMTP; fail closed if unconfigured."""
    resend_key = os.environ.get("RESEND_API_KEY", "").strip()
    sendgrid_key = os.environ.get("SENDGRID_API_KEY", "").strip()
    smtp_host = os.environ.get("SMTP_HOST", "").strip()
    smtp_user = os.environ.get("SMTP_USER", "").strip()
    smtp_pass = os.environ.get("SMTP_PASSWORD", "").strip()
    from_email = os.environ.get("WISHLIST_FROM_EMAIL", "wishlist@numista.ai").strip()

    if resend_key:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(
                "https://api.resend.com/emails",
                headers={"Authorization": f"Bearer {resend_key}"},
                json={
                    "from": from_email,
                    "to": [recipient_email],
                    "subject": subject,
                    "html": html_body,
                    "text": text_body,
                },
            )
            resp.raise_for_status()
        return "resend"

    if sendgrid_key:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(
                "https://api.sendgrid.com/v3/mail/send",
                headers={"Authorization": f"Bearer {sendgrid_key}"},
                json={
                    "personalizations": [{"to": [{"email": recipient_email}]}],
                    "from": {"email": from_email},
                    "subject": subject,
                    "content": [
                        {"type": "text/plain", "value": text_body},
                        {"type": "text/html", "value": html_body},
                    ],
                },
            )
            resp.raise_for_status()
        return "sendgrid"

    if smtp_host and smtp_user and smtp_pass:
        smtp_port = int(os.environ.get("SMTP_PORT", "587"))
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = from_email
        msg["To"] = recipient_email
        msg.set_content(text_body)
        msg.add_alternative(html_body, subtype="html")
        with smtplib.SMTP(smtp_host, smtp_port, timeout=15) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
        return "smtp"

    raise EmailProviderNotConfiguredError(
        "No email provider key or SMTP configuration is set."
    )
