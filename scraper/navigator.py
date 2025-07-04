# scraper/navigator.py
import re

import asyncio
from playwright.async_api import async_playwright

from config import HEADLESS, logger
from utils.checkpoint import save_keys_checkpoint

async def _collect_keys_and_continue():
    keys = set()
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=HEADLESS)
    page = await browser.new_page()

    await page.goto("https://ocfintax.ongov.net/Imate/index.aspx")
    await page.click("#btnPublicAccess")
    await page.wait_for_url("**/disclaimer.aspx", timeout=10000)
    await page.check("#chkAgree")
    await page.wait_for_selector("#btnSubmit", timeout=10000)
    await page.click("#btnSubmit")
    await page.wait_for_url("**/search.aspx", timeout=10000)
    await page.click("input[value='Search']")
    await page.wait_for_url("**/viewlist.aspx**", timeout=10000)



    # Get total page count from body text
    body_text = await page.inner_text("body")
    match = re.search(r"Page \d+ of (\d+)", body_text)
    total_pages = int(match.group(1)) if match else 1

    logger.info(f"[NAV] Detected total_pages = {total_pages}")

    # for page_num in range(1, 2):
    for page_num in range(1, total_pages + 1):
        logger.info(f"[NAV] Processing page {page_num}")
        await page.goto(f"https://ocfintax.ongov.net/Imate/viewlist.aspx?sort=printkey&swis=all&page={page_num}")
        rows = await page.query_selector_all("table#tblList tbody tr")
        for row in rows:
            links = await row.query_selector_all("a")
            for link in links:
                href = await link.get_attribute("href")
                if href and "printkey" in href:
                    parts = href.split("?")[1].split("&")
                    swis = parts[0].split("=")[1]
                    printkey = parts[1].split("=")[1]
                    keys.add((swis, printkey))

    save_keys_checkpoint(keys)
    logger.info("[DONE] All keys collected")
    return list(keys), page, browser


def collect_keys_and_return_page():
    return asyncio.run(_collect_keys_and_continue())
