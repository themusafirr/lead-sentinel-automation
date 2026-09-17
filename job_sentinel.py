#!/usr/bin/env python3
"""
Freelance Job Sentinel — Monitors Reddit & job feeds
Alerts via Telegram when relevant jobs appear
"""
import os
import re
import time
import json
import requests
import sqlite3
from datetime import datetime, timedelta

# Telegram config
BOT_TOKEN = os.environ.get('TG_BOT_TOKEN', 'YOUR_TELEGRAM_BOT_TOKEN')
CHAT_ID = os.environ.get('TG_CHAT_ID', '1012757518')

# Keywords to watch for
KEYWORDS = [
    'telegram bot', 'whatsapp bot', 'python bot', 'web scraper', 'scraper',
    'n8n automation', 'automation workflow', 'instagram bot', 'discord bot',
    'chatbot development', 'python automation', 'selenium scraper', 'api integration',
    'telegram automation', 'whatsapp api', 'bot development', 'web automation',
    'data scraping', 'python script', 'automation script', 'workflow automation'
]

# Exclude keywords (noise)
EXCLUDE = [
    ' unpaid', 'intern', 'volunteer', 'revshare', 'rev share',
    'equity only', 'no pay', 'for free', 'fiverr', 'upwork', 'cheap', 'budget'
]

RSS_FEEDS = [
    ('r/forhire', 'https://www.reddit.com/r/forhire.rss'),
    ('r/freelance', 'https://www.reddit.com/r/freelance.rss'),
    ('r/remoteorjob', 'https://www.reddit.com/r/remoteorjob.rss'),
    ('weworkremotely', 'https://weworkremotely.com/categories/remote-python-developer-jobs.rss'),
    ('remoteok', 'https://remoteok.com/remote-python-jobs.rss'),
]

BASE_DIR = os.path.dirname(__file__)
DB_FILE = os.environ.get('JOBS_DB', '/home/ubuntu/hermes_scripts/job_sentinel/jobs.db' if os.path.exists('/home/ubuntu/hermes_scripts/job_sentinel') else os.path.join(BASE_DIR, 'jobs.db'))
STATE_FILE = os.environ.get('JOBS_STATE', '/home/ubuntu/hermes_scripts/job_sentinel/last_check.json' if os.path.exists('/home/ubuntu/hermes_scripts/job_sentinel') else os.path.join(BASE_DIR, 'last_check.json'))
LOG_FILE = os.environ.get('JOBS_LOG', '/home/ubuntu/hermes_scripts/job_sentinel/sentinel.log' if os.path.exists('/home/ubuntu/hermes_scripts/job_sentinel') else os.path.join(BASE_DIR, 'sentinel.log'))

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AutomationBot/1.0'
}

def init_db():
    os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
    conn = sqlite3.connect(DB_FILE)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS seen_jobs (
            id TEXT PRIMARY KEY,
            title TEXT,
            url TEXT,
            source TEXT,
            salary TEXT,
            posted_at TEXT,
            matched_at TEXT
        )
    ''')
    conn.commit()
    conn.close()

def is_relevant(title, body=''):
    """Check if job matches our keywords"""
    text = (title + ' ' + body).lower()
    
    # Check exclude
    for exc in EXCLUDE:
        if exc.lower() in text:
            return False
    
    # Check keywords
    for kw in KEYWORDS:
        if kw.lower() in text:
            return True
    
    return False

def extract_salary(text):
    """Extract salary from job text"""
    patterns = [
        r'\$[\d,]+-?[\d,]*\/?hr?',
        r'₹[\d,]+-?[\d,]*\/?mo?',
        r'[\d]+[\d,]*\s*(?:INR|USD)\s*(?:per|/)\s*(?:hour|month|hr|mo)',
        r'(?:budget|pay|range)[:\s]*[\$₹][\d,]+',
        r'[\d,]+[\s](?:dollars?|rupees?)\s*(?:per|/)\s*(?:hour|hr|month|mo)',
    ]
    for p in patterns:
        m = re.search(p, text, re.I)
        if m:
            return m.group()
    return ''

def send_telegram(message):
    """Send Telegram alert"""
    try:
        url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
        data = {
            'chat_id': CHAT_ID,
            'text': message,
            'parse_mode': 'HTML',
            'disable_web_page_preview': False
        }
        resp = requests.post(url, data=data, timeout=10)
        return resp.status_code == 200
    except Exception as e:
        print(f"Telegram error: {e}")
        return False

def parse_reddit_rss(xml_text, source_name):
    """Parse Reddit RSS feed"""
    jobs = []
    
    # Simple regex-based parsing (faster than full XML parsing)
    entries = re.findall(r'<entry>(.*?)</entry>', xml_text, re.DOTALL)
    
    for entry in entries:
        try:
            title = re.search(r'<title>(.*?)</title>', entry, re.DOTALL)
            link = re.search(r'<link[^>]*href=["\'](.*?)["\']', entry, re.DOTALL)
            updated = re.search(r'<updated>(.*?)</updated>', entry, re.DOTALL)
            content = re.search(r'<content[^>]*>(.*?)</content>', entry, re.DOTALL)
            
            title_text = title.group(1).replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&#39;', "'").strip() if title else ''
            link_text = link.group(1) if link else ''
            updated_text = updated.group(1)[:10] if updated else ''  # Just date
            
            if is_relevant(title_text, content.group(1)[:500] if content else ''):
                salary = extract_salary(content.group(1)[:1000] if content else '')
                jobs.append({
                    'id': link_text.split('/')[-2] if link_text else title_text[:50],
                    'title': title_text,
                    'url': link_text,
                    'source': source_name,
                    'salary': salary,
                    'posted_at': updated_text,
                    'body': content.group(1)[:2000] if content else ''
                })
        except Exception as e:
            continue
    
    return jobs

def parse_rss_generic(xml_text, source_name):
    """Parse generic RSS feed"""
    jobs = []
    
    items = re.findall(r'<item>(.*?)</item>', xml_text, re.DOTALL)
    
    for item in items:
        try:
            title = re.search(r'<title>(.*?)</title>', item, re.DOTALL)
            link = re.search(r'<link>(.*?)</link>', item, re.DOTALL)
            pubdate = re.search(r'<pubDate>(.*?)</pubDate>', item, re.DOTALL)
            desc = re.search(r'<description>(.*?)</description>', item, re.DOTALL)
            
            title_text = title.group(1).replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&#39;', "'").replace('<[^>]+>', '').strip() if title else ''
            link_text = link.group(1).strip() if link else ''
            pubdate_text = pubdate.group(1).strip()[:16] if pubdate else ''
            
            desc_text = desc.group(1).replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&#39;', "'").replace('<[^>]+>', '').strip() if desc else ''
            
            if is_relevant(title_text, desc_text):
                salary = extract_salary(desc_text)
                jobs.append({
                    'id': link_text.split('/')[-1][:50] if link_text else title_text[:50],
                    'title': title_text,
                    'url': link_text,
                    'source': source_name,
                    'salary': salary,
                    'posted_at': pubdate_text,
                    'body': desc_text[:2000]
                })
        except Exception as e:
            continue
    
    return jobs

def load_seen_ids():
    """Load already-seen job IDs from DB"""
    init_db()
    conn = sqlite3.connect(DB_FILE)
    cur = conn.execute('SELECT id FROM seen_jobs')
    seen = {row[0] for row in cur.fetchall()}
    conn.close()
    return seen

def save_job(job):
    """Save job to DB"""
    init_db()
    conn = sqlite3.connect(DB_FILE)
    conn.execute('''
        INSERT OR REPLACE INTO seen_jobs (id, title, url, source, salary, posted_at, matched_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        job['id'], job['title'], job['url'], job['source'],
        job.get('salary', ''), job.get('posted_at', ''),
        datetime.now().strftime('%Y-%m-%d %H:%M')
    ))
    conn.commit()
    conn.close()

def build_alert_message(job):
    """Build Telegram alert message"""
    salary = f" 💰 {job['salary']}" if job.get('salary') else ""
    
    message = f"""🔥 <b>New Freelance Lead!</b>

<b>{job['title']}</b>

📍 Source: <code>{job['source']}</code>{salary}
📅 Posted: {job['posted_at']}

🔗 <a href="{job['url']}">Apply / View Job</a>

🏷️ Keywords matched: <code>telegram bot</code>"""

    return message

def check_feeds():
    """Main check loop"""
    print("=" * 60)
    print("JOB SENTINEL — Checking feeds...")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    seen_ids = load_seen_ids()
    new_jobs = []
    
    for source_name, feed_url in RSS_FEEDS:
        print(f"\n📡 Checking {source_name}...")
        try:
            resp = requests.get(feed_url, headers=HEADERS, timeout=15)
            resp.raise_for_status()
            
            if 'reddit' in source_name:
                jobs = parse_reddit_rss(resp.text, source_name)
            else:
                jobs = parse_rss_generic(resp.text, source_name)
            
            print(f"  Found {len(jobs)} relevant jobs")
            
            for job in jobs:
                if job['id'] not in seen_ids:
                    new_jobs.append(job)
                    print(f"  🆕 NEW: {job['title'][:60]}")
        
        except Exception as e:
            print(f"  ❌ Error fetching {source_name}: {e}")
        
        time.sleep(2)
    
    print(f"\n📊 Total new jobs: {len(new_jobs)}")
    
    # Send Telegram alerts
    sent = 0
    for job in new_jobs:
        msg = build_alert_message(job)
        if send_telegram(msg):
            save_job(job)
            sent += 1
            print(f"  ✅ Alert sent: {job['title'][:50]}")
        else:
            print(f"  ❌ Alert failed: {job['title'][:50]}")
    
    print(f"\n✅ Sent {sent} Telegram alerts")
    
    # Save state
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, 'w') as f:
        json.dump({
            'last_check': datetime.now().isoformat(),
            'new_jobs': len(new_jobs),
            'sent': sent
        }, f)
    
    return len(new_jobs)

def run_once():
    check_feeds()

def run_loop(interval_minutes=30):
    """Run continuously"""
    print(f"\n🔄 SENTINEL LOOP — Running every {interval_minutes} minutes")
    print("Press Ctrl+C to stop\n")
    
    while True:
        try:
            check_feeds()
            print(f"\n💤 Sleeping {interval_minutes} minutes...")
            time.sleep(interval_minutes * 60)
        except KeyboardInterrupt:
            print("\n\n⏹️ Sentinel stopped.")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(60)

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--loop':
        run_loop(30)
    else:
        run_once()
