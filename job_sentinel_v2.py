#!/usr/bin/env python3
"""Freelance Job Sentinel v2"""
import os, re, time, json, requests, sqlite3
from datetime import datetime

BOT_TOKEN = "8866563797:AAHDbk_LaD4gtwzIc8i1K0Ud1o3HMdmhCvY"
CHAT_ID = "1012757518"
KEYWORDS = ["telegram bot","whatsapp bot","python bot","web scraper","n8n automation",
    "automation workflow","instagram bot","discord bot","chatbot","python automation",
    "selenium","api integration","telegram automation","whatsapp api","bot development",
    "data scraping","python script","automation script","workflow automation"]
EXCLUDE = ["unpaid","intern","volunteer","revshare","equity only","no pay","for free","fiverr","upwork","cheap","budget","<£"]
RSS_FEEDS = [
    ("forAH", "https://www.reddit.com/r/forhire.rss"),
    ("remotAJ", "https://www.reddit.com/r/remoteorjob.rss"),
    ("authenticjobs", "https://www.authenticjobs.com/rss.xml"),
    ("remotive", "https://remotive.com/remote-jobs/feed/technical"),
    ("django gigs", "https://djangogigs.com/feeds/jobs.xml"),
]
DB_FILE = "/home/ubuntu/hermes_scripts/job_sentinel/jobs.db"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; PythonBot/1.0; +http://example.com/bot)"}

def init_db():
    os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
    sqlite3.connect(DB_FILE).execute("""
        CREATE TABLE IF NOT EXISTS seen_jobs (
            id TEXT PRIMARY KEY, title TEXT, url TEXT, source TEXT,
            salary TEXT, posted_at TEXT, matched_at TEXT)
    """)

def is_relevant(title, body=""):
    text = (title + " " + body).lower()
    for e in EXCLUDE:
        if e.lower() in text: return False
    for kw in KEYWORDS:
        if kw.lower() in text: return True
    return False

def extract_salary(text):
    for p in [r"\$[\d,]+-?[\d,]*\/?hr?", r"₹[\d,]+-?[\d,]*\/?mo?", r"(?:budget|pay)[:\s]*[\$₹][\d,]+"]:
        m = re.search(p, text, re.I)
        if m: return m.group()
    return ""

def send_tg(msg):
    try:
        r = requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"}, timeout=10)
        return r.status_code == 200
    except: return False

def parse_rss(xml, src):
    jobs = []
    for item in re.findall(r"<item>(.*?)</item>", xml, re.DOTALL):
        try:
            t = re.search(r"<title>(.*?)</title>", item, re.DOTALL)
            l = re.search(r"<link>(.*?)</link>", item, re.DOTALL)
            d = re.search(r"<pubDate>(.*?)</pubDate>", item, re.DOTALL)
            desc = re.search(r"<description>(.*?)</description>", item, re.DOTALL)
            tt = re.sub(r"<[^>]+>","",(t.group(1) if t else "")).strip()
            body = re.sub(r"<[^>]+>","",(desc.group(1)[:2000] if desc else "")).strip()
            if is_relevant(tt, body):
                salary = extract_salary(body)
                job_id = (l.group(1).split("/")[-1][:50] if l else tt[:50])
                posted = (d.group(1)[:16] if d else "")
                jobs.append({"id": job_id, "title": tt, "url": (l.group(1).strip() if l else ""),
                    "source": src, "salary": salary, "posted_at": posted, "body": body})
        except: pass
    return jobs

def load_seen():
    init_db()
    return {r[0] for r in sqlite3.connect(DB_FILE).execute("SELECT id FROM seen_jobs")}

def save_job(j):
    init_db()
    sqlite3.connect(DB_FILE).execute("""
        INSERT OR REPLACE INTO seen_jobs VALUES (?,?,?,?,?,?,?)
    """, (j["id"], j["title"], j["url"], j["source"], j.get("salary",""),
          j.get("posted_at",""), datetime.now().strftime("%Y-%m-%d %H:%M")))

def check():
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    print("="*50)
    print(f"JOB SENTINEL v2 — {ts}")
    print("="*50)
    seen = load_seen()
    new = []
    for name, url in RSS_FEEDS:
        print(f"  Checking {name}...", end=" ", flush=True)
        try:
            r = requests.get(url, headers=HEADERS, timeout=15)
            if r.status_code == 200:
                jobs = parse_rss(r.text, name)
                fresh = [j for j in jobs if j["id"] not in seen]
                print(f"{len(fresh)} new (of {len(jobs)} matched)")
                new.extend(fresh)
            else:
                print(f"HTTP {r.status_code}")
        except Exception as e:
            print(f"Error: {e}")
        time.sleep(2)
    print(f"\nTotal new: {len(new)}")
    for j in new:
        msg = f"🔥 <b>New Freelance Lead!</b>\n\n<b>{j['title']}</b>\n\n📍 Source: {j['source']}"
        if j.get("salary"): msg += f"\n💰 {j['salary']}"
        msg += f"\n🔗 <a href=\"{j['url']}\">View Job</a>"
        if send_tg(msg):
            save_job(j)
            print(f"  ✅ Alert sent: {j['title'][:50]}")
    if not new:
        print("  No new jobs this cycle.")
    return len(new)

if __name__ == "__main__":
    check()
