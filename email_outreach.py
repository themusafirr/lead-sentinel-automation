#!/usr/bin/env python3
"""
Email Outreach Engine — Automated Cold Email Sender
Sends pitch emails to leads from leads.csv
Uses Gmail SMTP with environment variable credentials
"""
import os
import sys
import csv
import time
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# Config
SMTP_HOST = os.environ.get('SMTP_HOST', 'smtp.gmail.com')
SMTP_PORT = int(os.environ.get('SMTP_PORT', '587'))
SMTP_USER = os.environ.get('OUTREACH_EMAIL', '')
SMTP_PASS = os.environ.get('OUTREACH_PASS', '')
FROM_NAME = 'Pankaj | Automation Expert'

# Rate limiting
MAX_EMAILS_PER_RUN = 20
COOLDOWN_SECONDS = 300  # 5 min between runs

LEADS_FILE = os.environ.get('LEADS_FILE', os.path.join(os.path.dirname(__file__), 'leads.csv'))
LOG_FILE = os.environ.get('LOG_FILE', os.path.join(os.path.dirname(__file__), 'outreach.log'))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s — %(levelname)s — %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

STORE_URL = os.environ.get('STORE_URL', 'https://github.com/pixelssudio')

def get_email_content(lead):
    """Generate personalized email based on lead category"""
    category = lead.get('category', '')
    business = lead.get('business', '')
    city = lead.get('city', '')
    
    # Email template variations by category
    templates = {
        'clinic': {
            'subject': f'⚕️ Automate Patient Reminders & Appointments — Free Tool Inside',
            'body': f"""Hi {business} Team,

I came across {business} in {city} and wanted to share something that could save your clinic hours every week.

Most clinics spend 2-3 hours daily on:
→ Reminding patients about appointments
→ Collecting feedback after visits
→ Following up on pending reports

What if all of this ran on autopilot?

We built a ready-to-use WhatsApp + Email automation kit specifically for clinics:
✅ Auto appointment reminders (1 day before, morning of)
✅ Patient feedback collection
✅ Report delivery notifications
✅ 24/7 auto-reply for common queries

Our client — a dental clinic in Kota — saved 15+ hours per week. No coding needed.

👉 See the full kit here: {STORE_URL}

Price: ₹799 (one-time, lifetime access)

Worth a 10-minute look?

Best,
Pankaj
"""
        },
        'coaching': {
            'subject': f'📚 Automate Student Enquiries & Fee Reminders — Free Demo Inside',
            'body': f"""Hi {business} Team,

I know {city}'s coaching industry is competitive. Institutes that respond fastest to enquiries usually win the student.

Most coaching institutes miss 30-40% of enquiries because:
→ No instant reply (parents move on)
→ Manual WhatsApp responses take too long
→ Fee reminders are embarrassing to send manually

We've built automation templates for coaching institutes that:
✅ Reply to enquiries within 30 seconds (auto)
✅ Send fee reminders on schedule
✅ Collect student feedback automatically
✅ Send daily/weekly performance updates to parents

Our Allen-style kit covers everything: {STORE_URL}

Price: ₹999 (includes n8n workflows + setup guide)

Would you like a free 15-minute demo call this week?

Best,
Pankaj
"""
        },
        'gym': {
            'subject': f'💪 Automate Gym Member Reminders & Renewals — Free Tool Inside',
            'body': f"""Hi {business} Team,

Gym owners in {city} are losing members because of poor follow-up.

Here's what happens:
→ Members forget to renew → revenue leak
→ No automated class reminders → drop in attendance
→ New enquiries get no instant response → they join elsewhere

We built a WhatsApp + Email automation kit for gyms:
✅ Auto renewal reminders (3 days, 1 day before expiry)
✅ Class/session reminders to members
✅ Instant reply to new enquiries
✅ Birthday/discount offer automation

All templates ready to use: {STORE_URL}

Price: ₹799

Worth a quick look?

Best,
Pankaj
"""
        },
        'cafe': {
            'subject': f'☕ Automate Cafe Orders & Table Reservations — Free Inside',
            'body': f"""Hi {business} Team,

Restaurants and cafes that use automation see 20-30% better repeat customer rates.

Here's what {city} cafes are missing:
→ No WhatsApp ordering system (customers want to order via chat)
→ No automated birthday/discount offers
→ No table reservation system — they rely on calls

Our restaurant automation kit includes:
✅ WhatsApp ordering bot (customers order via chat)
✅ Table reservation system
✅ Birthday offer automation
✅ Review request after visits

See the full kit: {STORE_URL}

Price: ₹799

Would love to show you how it works on a quick call.

Best,
Pankaj
"""
        },
        'hotel': {
            'subject': f'🏨 Automate Hotel Bookings & Guest Communication — Free Demo',
            'body': f"""Hi {business} Team,

Guest expectations have changed. The hotel that responds fastest wins the booking.

Hotels in {city} lose bookings because:
→ No instant reply to booking enquiries
→ Manual follow-up on pending bookings
→ No automated check-in/check-out reminders

Our hotel automation kit:
✅ Instant booking confirmation via WhatsApp
✅ Pre-arrival information (check-in time, amenities)
✅ Automated review request after checkout
✅ Late checkout / early check-in offers

All templates: {STORE_URL}

Price: ₹999

Can we do a 10-minute demo this week?

Best,
Pankaj
"""
        },
        'restaurant': {
            'subject': f'🍽️ Automate Restaurant Orders & Reservations — Free Inside',
            'body': f"""Hi {business} Team,

Every restaurant in {city} is on WhatsApp. Why not let customers order directly from it?

Our restaurant automation kit:
✅ WhatsApp food ordering system
✅ Table reservation bot
✅ Auto delivery status updates
✅ Birthday discount automation
✅ Review collection after orders

All ready: {STORE_URL}

Price: ₹799

Worth a quick look?

Best,
Pankaj
"""
        },
        'salon': {
            'subject': f'✂️ Automate Salon Appointments & Reminders — Free Inside',
            'body': f"""Hi {business} Team,

Salons lose 20-30% of appointments to no-shows. Most of these can be prevented with a simple reminder system.

Our salon automation kit:
✅ WhatsApp appointment booking (customers book via chat)
✅ Auto-reminders 1 day and 2 hours before appointment
✅ Auto birthday offers
✅ Review request after visits

Templates ready: {STORE_URL}

Price: ₹799

Best,
Pankaj
"""
        },
        'pathlab': {
            'subject': f'🔬 Automate PathLab Reports & Follow-ups — Free Demo',
            'body': f"""Hi {business} Team,

PathLabs deal with a lot of follow-up work — reports ready, collection schedules, repeat bookings.

Our automation kit:
✅ Auto report-ready notifications via WhatsApp
✅ Sample collection reminders
✅ Health package promotion automation
✅ Feedback collection

Templates ready: {STORE_URL}

Price: ₹799

Best,
Pankaj
"""
        },
        'tutor': {
            'subject': f'📖 Automate Student Enquiries & Batches — Free Inside',
            'body': f"""Hi {business} Team,

Tuition and coaching businesses run on follow-up. The faster you respond, the more students you convert.

Our automation kit:
✅ Instant reply to enquiries (within 30 seconds)
✅ Batch schedule sharing
✅ Fee reminder automation
✅ Parent progress update system

All templates: {STORE_URL}

Price: ₹599 (AI Content Bundle) or ₹999 (full n8n pack)

Best,
Pankaj
"""
        },
        'photographer': {
            'subject': f'📸 Automate Photographer Bookings & Deliveries — Free Inside',
            'body': f"""Hi {business} Team,

Photographers lose bookings because of slow responses. Most inquiries come in the evening — by morning, they've already booked someone else.

Our automation kit:
✅ WhatsApp enquiry auto-reply (instant)
✅ Photo delivery notification system
✅ Booking confirmation + pre-shoot checklist
✅ Review and referral automation

Templates: {STORE_URL}

Price: ₹799

Best,
Pankaj
"""
        },
    }
    
    # Default template for uncategorized
    default_template = {
        'subject': f'⚡ Automate Your Business — Ready-to-Use Templates Inside',
        'body': f"""Hi {business} Team,

I wanted to share something that could save your team hours every week.

We've built automation templates for businesses like yours that handle:
✅ Instant customer replies (no more missed enquiries)
✅ Automated reminders and follow-ups
✅ Daily workflow automation

All templates are ready-to-use, no coding needed:
👉 {STORE_URL}

Prices start at ₹599. Most customers set this up in under 30 minutes.

Interested? Happy to do a free 10-minute demo.

Best,
Pankaj
"""
    }
    
    return templates.get(category, default_template)

def send_email(to_email, subject, body, from_name=FROM_NAME):
    """Send email via SMTP"""
    if not SMTP_USER or not SMTP_PASS:
        logger.warning(f"No SMTP credentials — email not sent to {to_email}")
        return False
    
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = f'{from_name} <{SMTP_USER}>'
        msg['To'] = to_email
        
        # Plain text version
        part1 = MIMEText(body, 'plain', 'utf-8')
        msg.attach(part1)
        
        # HTML version
        body_for_html = body.replace('\n', '<br>')
        html_body = f"""
        <html><body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <div style="background: #f8f9fa; padding: 20px; border-radius: 8px;">
        <div style="background: white; padding: 24px; border-radius: 8px;">
        {body_for_html}
        <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
        <p style="color: #666; font-size: 12px;">
        Sent by Pankaj | Automation Expert<br>
        Store: <a href="{STORE_URL}">{STORE_URL}</a>
        </p>
        </div></div></body></html>
        """
        part2 = MIMEText(html_body, 'html', 'utf-8')
        msg.attach(part2)
        
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(SMTP_USER, [to_email], msg.as_string())
        
        return True
    
    except Exception as e:
        logger.error(f"Email failed to {to_email}: {e}")
        return False

def update_lead_status(lead_row, status, filepath=LEADS_FILE):
    """Update lead status in CSV"""
    try:
        rows = []
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            for row in reader:
                if row['business'] == lead_row['business'] and row['email'] == lead_row['email']:
                    row['status'] = status
                    row['outreach_sent'] = 'yes'
                    row['outreach_date'] = datetime.now().strftime('%Y-%m-%d %H:%M')
                rows.append(row)
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
    except Exception as e:
        logger.error(f"Failed to update lead: {e}")

def run_outreach():
    """Main outreach loop"""
    logger.info("=" * 60)
    logger.info("OUTREACH ENGINE — Starting...")
    logger.info(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)
    
    if not os.path.exists(LEADS_FILE):
        logger.error(f"Leads file not found: {LEADS_FILE}")
        return
    
    # Read leads
    with open(LEADS_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        leads = list(reader)
    
    pending = [l for l in leads if l.get('outreach_sent', 'no') != 'yes' and l.get('email')]
    
    logger.info(f"Total leads: {len(leads)}")
    logger.info(f"Pending outreach: {len(pending)}")
    
    if not pending:
        logger.info("No pending leads — all done!")
        return
    
    # Check SMTP
    if not SMTP_USER:
        logger.warning("⚠️ No SMTP credentials set. Emails will be logged but not sent.")
        logger.warning("Set OUTREACH_EMAIL and OUTREACH_PASS environment variables.")
        logger.info("Running in DRY RUN mode — showing emails that would be sent:")
        for lead in pending[:5]:
            email_content = get_email_content(lead)
            logger.info(f"\n  TO: {lead['email']}")
            logger.info(f"  SUBJECT: {email_content['subject']}")
            logger.info(f"  BODY: {email_content['body'][:200]}...")
        return
    
    # Send emails
    sent = 0
    failed = 0
    
    for lead in pending[:MAX_EMAILS_PER_RUN]:
        email = lead['email']
        if not email or '@' not in email:
            continue
        
        email_content = get_email_content(lead)
        subject = email_content['subject']
        body = email_content['body']
        
        logger.info(f"\n✉️  Sending to: {email}")
        logger.info(f"   Subject: {subject[:60]}...")
        
        success = send_email(email, subject, body)
        
        if success:
            update_lead_status(lead, 'emailed')
            sent += 1
            logger.info(f"   ✅ Sent successfully")
        else:
            update_lead_status(lead, 'failed')
            failed += 1
            logger.info(f"   ❌ Failed")
        
        time.sleep(3)  # Delay between emails
    
    logger.info(f"\n📊 Outreach Complete:")
    logger.info(f"   Sent: {sent}")
    logger.info(f"   Failed: {failed}")
    logger.info(f"   Remaining: {len(pending) - sent}")

if __name__ == '__main__':
    run_outreach()
