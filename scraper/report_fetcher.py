# scraper/report_fetcher.py
from datetime import datetime
import os

from db.session import SessionLocal
from db.models import PropertyReport
from config import logger
from scraper.parser import parse_report_html


async def fetch_and_store_reports_async(keys, page):
    session = SessionLocal()
    os.makedirs("debug_html", exist_ok=True)

    for swis, printkey in keys:
        url = f"https://ocfintax.ongov.net/Imate/report.aspx?file=&swiscode={swis}&printkey={printkey}&sitetype=res&siteNum=1"
        try:
            await page.goto(url)
            html = await page.content()
            data = parse_report_html(html)

            logger.debug(f"[REPORT DEBUG] Parsed data for {printkey}: {data}")
            with open(f"debug_html/{swis}_{printkey}.html", "w") as f:
                f.write(html)

            report = PropertyReport(
                swiscode=swis,
                printkey=printkey,
                report_json=data,
                scraped_at=datetime.utcnow()
            )
            session.merge(report)
            session.commit()
            logger.info(f"[REPORT] Inserted report for {printkey}")
        except Exception as e:
            logger.error(f"[ERROR] Failed to fetch or insert {printkey}: {e}")
            session.rollback()
    session.close()