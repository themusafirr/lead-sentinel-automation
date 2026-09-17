# 🎯 LeadSentinel: B2B Lead Generation & Automated Outreach Suite

[![Python](https://img.shields.io/badge/Python-3.9+-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![Web Scraping](https://img.shields.io/badge/Scraping-BeautifulSoup_|_Requests-green?style=for-the-badge)](https://pypi.org/project/beautifulsoup4/)
[![Automation](https://img.shields.io/badge/Outreach-SMTP_Cold_Email-orange?style=for-the-badge)](https://docs.python.org/3/library/smtplib.html)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

> **An automated sales intelligence and business development pipeline.** Scrapes local business leads across 18+ major metro & tier-2 cities, extracts validated emails and contact numbers, triggers personalized cold email outreach sequences with built-in rate-limiting, and monitors freelance job boards in real time.

---

## 🌟 Capabilities & Features

- 🔍 **Multi-City & Multi-Category Lead Scraper**: Scrapes verified small-and-medium business leads across 18+ cities (Mumbai, Delhi, Bangalore, Jaipur, Kota, Indore, etc.) across 10+ industries (clinics, salons, restaurants, coaching, gyms, etc.).
- ✉️ **Automated Cold Email Sequencing**:
  - Category-specific high-converting email copy templates (e.g. appointment automation for clinics, table booking for restaurants).
  - Built-in anti-spam safety: strict batch limits (max 20/run) and cooldown delays.
- 📡 **JobSentinel Freelance Radar**: Automatically tracks high-paying remote developer and automation contracts from RemoteOK, RSS feeds, and job aggregators.
- 🛒 **Shop Bot**: Automated product price tracking and inventory notification assistant.

---

## 🚀 Quick Start

### 1. Installation
```bash
git clone https://github.com/pixelssudio/lead-sentinel-automation.git
cd lead-sentinel-automation
pip install -r requirements.txt
```

### 2. Configure Credentials
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Fill in your Gmail SMTP App Password:
```env
OUTREACH_EMAIL=your_email@gmail.com
OUTREACH_PASS=your_16_char_gmail_app_password
STORE_URL=https://github.com/pixelssudio
```

### 3. Run Tools

**Scrape Leads:**
```bash
python lead_scraper.py
```
*(Saves extracted leads into `leads.csv` with fields: Business Name, City, Category, Email, Phone)*

**Send Automated Outreach:**
```bash
python email_outreach.py
```

**Run Freelance Job Sentinel:**
```bash
python job_sentinel.py
```

---

## 📁 Repository Structure

```text
├── lead_scraper.py       # High-speed web scraper for local businesses & contacts
├── email_outreach.py     # Automated SMTP cold outreach engine with template router
├── job_sentinel.py       # Remote freelance job monitoring & SQLite storage
├── job_sentinel_v2.py    # Lightweight job feed monitor
├── shop_bot.py           # E-commerce store crawler & price tracker
├── requirements.txt      # Dependencies
├── .env.example          # Environment configuration template
└── .gitignore            # Excludes sensitive leads.csv and logs
```

---

## 💼 B2B Lead Generation & Scraping Services

Need custom scrapers, targeted B2B lead lists, or automated outreach funnels for your agency or SaaS?

- 🕷️ **Custom Web Scrapers** (E-commerce, Real Estate, Google Maps, LinkedIn)
- 📧 **Cold Email Automation & Inbox Deliverability Setup**
- ⚡ **Real-Time Data Pipelines & Webhook Alert Bots**

**Hire me for freelance projects:**
- 📧 **Email**: Contact via GitHub profile
- 💬 **Telegram**: [@the_musafir](https://t.me/the_musafir)
- 💼 **Upwork / Fiverr**: Available for hire

---

## 📄 License
MIT License. Developed by Pankaj (@the.musafir).
