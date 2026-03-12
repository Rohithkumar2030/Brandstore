"""
Quick script to test email configuration and sending.
Run: python test_email.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'greatkart.settings')
django.setup()

from django.conf import settings

print("=" * 50)
print("Django Email Settings")
print("=" * 50)
print(f"EMAIL_BACKEND:       {settings.EMAIL_BACKEND}")
print(f"EMAIL_HOST:          {settings.EMAIL_HOST}")
print(f"EMAIL_PORT:          {settings.EMAIL_PORT}")
print(f"EMAIL_USE_TLS:       {settings.EMAIL_USE_TLS}")
print(f"EMAIL_HOST_USER:     {settings.EMAIL_HOST_USER}")
pwd_display = "*" * len(settings.EMAIL_HOST_PASSWORD) if settings.EMAIL_HOST_PASSWORD else "(EMPTY!)"
print(f"EMAIL_HOST_PASSWORD: {pwd_display}")
print(f"DEFAULT_FROM_EMAIL:  {settings.DEFAULT_FROM_EMAIL}")
print()

# ─── Test 1: Django EmailMessage (used in accounts/views.py) ───
print("=" * 50)
print("Test 1: Django EmailMessage (accounts app style)")
print("  → No explicit from_email passed")
print("=" * 50)

from django.core.mail import EmailMessage

msg = EmailMessage(
    subject="[Brandstore Test] Account verification style",
    body="<h1>Test</h1><p>This mimics the register/forgotPassword email.</p>",
    to=[settings.EMAIL_HOST_USER],  # send to yourself for testing
)
print(f"  from_email resolved to: {msg.from_email}")
print(f"  to:                     {msg.to}")

try:
    result = msg.send()
    if result:
        print("  ✅ SENT successfully!")
    else:
        print("  ⚠️  send() returned 0 — email may not have been sent")
except Exception as e:
    print(f"  ❌ FAILED: {e}")

print()

# ─── Test 2: Raw smtplib (used in orders/views.py) ───
print("=" * 50)
print("Test 2: Raw smtplib send_email (orders app style)")
print("=" * 50)

import smtplib
from email.message import EmailMessage as RawEmailMessage

sender_email = settings.EMAIL_HOST_USER
sender_password = settings.EMAIL_HOST_PASSWORD
to_email = settings.EMAIL_HOST_USER  # send to yourself

raw_msg = RawEmailMessage()
raw_msg.set_content("This is the plain text fallback.")
raw_msg.add_alternative("<h1>Order Confirmation Test</h1><p>This mimics the order email.</p>", subtype="html")
raw_msg["Subject"] = "[Brandstore Test] Order confirmation style"
raw_msg["From"] = sender_email
raw_msg["To"] = to_email

print(f"  From: {sender_email}")
print(f"  To:   {to_email}")

try:
    with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(raw_msg)
    print("  ✅ SENT successfully!")
except Exception as e:
    print(f"  ❌ FAILED: {e}")

print()
print("Done. Check your inbox at:", settings.EMAIL_HOST_USER)
