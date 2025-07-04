# 🏠 Onondaga County Property Scraper

A headless web scraper for extracting structured property data from the Onondaga County Image Mate system. Built with Python, Playwright, SQLAlchemy, and PostgreSQL.

---

## 🚀 Features

- Scrapes property report pages using Playwright
- Parses full property data into structured JSON
- Stores data in a Postgres database using SQLAlchemy
- Supports upserts (update existing records)
- Dockerized for repeatable, headless deployment
- Resumable scraping with checkpointing

---

## 📦 Tech Stack

- Python 3.11
- [Playwright](https://playwright.dev/python/) (headless browser automation)
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) (HTML parsing)
- [SQLAlchemy](https://www.sqlalchemy.org/) + Alembic (ORM + migrations)
- PostgreSQL (via Supabase or local)
- Docker (for production builds)

---

## 🛠️ Setup

### 1. Install Python deps

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Create `.env`

```dotenv
DATABASE_URL=postgresql+psycopg2://user:pass@host:port/dbname
HEADLESS=True
```

### 3. Run scraper

```bash
python3 main.py
```

---

## 🐳 Docker

```bash
docker build -t property-scraper .
docker run --env-file .env property-scraper
```

---

## 🧪 Developer Tools

- `debug_html/`: saved HTML pages for offline inspection
- `scraper_checkpoint.json`: progress checkpoint for resumability
- Logs output to stdout with rich `DEBUG`/`INFO` levels

---

## 🧬 Database Schema

Table: `property_reports`

| Column       | Type     | Description              |
|--------------|----------|--------------------------|
| id           | UUID     | Primary key              |
| swiscode     | String   | Location identifier      |
| printkey     | String   | Tax map ID               |
| report_json  | JSONB    | Parsed report data       |
| scraped_at   | DateTime | Timestamp of last update |

Uniqueness: `swiscode + printkey`

---

## 🧰 Scripts

| Script         | Description                         |
|----------------|-------------------------------------|
| `main.py`      | Full scraper start point            |
| `fetcher.py`   | Downloads and stores property data  |
| `parser.py`    | Converts raw HTML to structured JSON|

---

## ⚡ Speeding Up the Scraper

The scraper can be slow when polling 190,000+ properties one-by-one. To increase performance, you can:

- Use **asyncio + Playwright concurrency** (e.g., 10–50 pages in parallel)
- Minimize duplicate lookups with checkpoints or database checks
- Retry failed requests in a separate async queue

We recommend running batches of 10–20 concurrent page tabs for safe, high-speed scraping without IP throttling.

---

## 🧭 Resolving Full Property Addresses

The raw report often contains only a partial address (e.g., just street name). To generate a usable address:

- Extract full mailing address from the `owners` section when available
- Use `SWIS + printkey` to reference local GIS or tax maps
- (Optional) Use reverse geocoding on lat/lon from report to look up ZIP code and city
- Normalize results for use in mailing, mapping, or appraisal workflows

---

## ⚠️ Disclaimers

- This is not affiliated with Onondaga County or SDG
- Use responsibly and respect website terms of service

---

## 📄 License

MIT (or your choice)