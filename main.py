# main.py
import asyncio
from scraper.navigator import _collect_keys_and_continue
from scraper.report_fetcher import fetch_and_store_reports_async

async def main():
    print("[START] Scraping Onondaga property records...")
    keys, page, browser = await _collect_keys_and_continue()
    print(f"[INFO] {len(keys)} property keys loaded.")

    await fetch_and_store_reports_async(keys, page)
    await browser.close()
    print("[DONE] All reports fetched and saved.")

if __name__ == "__main__":
    asyncio.run(main())