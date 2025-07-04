import re
from bs4 import BeautifulSoup
from config import logger

def normalize_key(text):
    return re.sub(r'\W+', '_', text.strip().lower()).strip('_')

def parse_yearly_values(raw: str) -> dict:
    year_values = {}
    for line in raw.splitlines():
        match = re.match(r'(\d{4})\s*-\s*(.+)', line.strip())
        if match:
            year, value = match.groups()
            year_values[year] = value
    return year_values if year_values else raw

def parse_title_and_address(soup):
    title_tag = soup.select_one("h1 > span#lblReportTitle")
    if title_tag:
        m = re.search(r"Report For: (.*?)(, Municipality|$)", title_tag.get_text(strip=True))
        return m.group(1).strip() if m else None
    return None

def parse_property_summary(soup):
    summary = {}
    table = soup.select_one("div#property_info table")
    if not table:
        return summary

    for row in table.find_all("tr"):
        headers = row.find_all("th")
        for th in headers:
            key = normalize_key(th.get_text(strip=True))
            next_td = th.find_next_sibling("td")
            if not next_td:
                continue
            raw_value = next_td.get_text("\n", strip=True)
            value = parse_yearly_values(raw_value) if re.search(r'(\d{4})\s*-', raw_value) else raw_value
            summary[key] = value

    return summary

def parse_owners_section(section):
    owners = []
    for div in section.select("div.owner_info"):
        lines = list(div.stripped_strings)
        if lines:
            owners.append(lines)
    return owners

def parse_flat_table_section(section):
    flat_data = {}
    for row in section.select("table tr"):
        cells = row.find_all(['td', 'th'])
        for i in range(0, len(cells) - 1, 2):
            k = normalize_key(cells[i].get_text(strip=True))
            v = cells[i + 1].get_text(strip=True)
            flat_data[k] = v
    return flat_data if flat_data else None

def parse_multirow_table_section(section):
    tables = section.select("table")
    for table in tables:
        rows = table.find_all("tr")
        if len(rows) < 2:
            return []
        headers = [
           normalize_key(th.get_text(strip=True))
            for th in rows[0].find_all("th")
            if th.get_text(strip=True).strip()
        ]
        if not headers or len(headers) < 2:
            return []
        data_rows = []
        for row in rows[1:]:
            cells = row.find_all("td")
            if len(cells) == 1 and 'colspan' in cells[0].attrs:
                continue

            # 🔍 Add this debug block
            logger.debug(f"[TABLE] headers ({len(headers)}): {headers}")
            logger.debug(f"[TABLE] cells ({len(cells)}): {[c.get_text(strip=True) for c in cells]}")

            row_data = {}
            for i in range(min(len(headers), len(cells))):
                row_data[headers[i]] = cells[i].get_text(strip=True)
            data_rows.append(row_data)
        return data_rows
    return []

def is_likely_multirow_table(section):
    table = section.find("table")
    if not table:
        return False
    first_row = table.find("tr")
    if not first_row:
        return False
    ths = first_row.find_all("th")
    tds = first_row.find_all("td")
    return len(ths) > 1 and len(tds) == 0

def parse_special_districts(soup):
    result = {}
    section = soup.select_one("#ucSpecialDistricts")
    if not section:
        return result

    current_year = None
    tables = section.select("table")
    headings = section.select("h2")

    for heading, table in zip(headings, tables):
        year_match = re.search(r'(\d{4})', heading.get_text())
        if not year_match:
            continue
        year = year_match.group(1)

        rows = table.find_all("tr")
        if len(rows) < 2:
            result[year] = []
            continue

        headers = [normalize_key(th.get_text(strip=True)) for th in rows[0].find_all("th")]
        year_rows = []
        for row in rows[1:]:
            cells = row.find_all("td")
            if len(cells) != len(headers):
                continue
            row_data = {headers[i]: cells[i].get_text(strip=True) for i in range(len(headers))}
            year_rows.append(row_data)
        result[year] = year_rows

    return result

def parse_report_html(html: str) -> dict:
    soup = BeautifulSoup(html, 'html.parser')
    result = {}

    address = parse_title_and_address(soup)
    summary = parse_property_summary(soup)
    if address:
        summary['address'] = address
    result['property_summary'] = summary

    for section in soup.select("div.report_section"):
        heading = section.find(["h2", "h1"])
        if not heading:
            logger.debug("Skipping unnamed section — no heading found.")
            continue

        raw_name = heading.get_text(strip=True)
        section_name = normalize_key(raw_name)
        logger.debug(f"Processing section: {section_name}")

        if "special_districts_for" in section_name:
            continue

        if "owner" in section_name:
            result[section_name] = parse_owners_section(section)
            logger.debug(f"Parsed owners: {len(result[section_name])} entries")
            continue

        if is_likely_multirow_table(section):
            parsed = parse_multirow_table_section(section)
            logger.debug(f"Parsed multirow section: {section_name} → {len(parsed)} rows")
        else:
            parsed = parse_flat_table_section(section)
            logger.debug(f"Parsed flat section: {section_name} → {len(parsed)} keys" if parsed else f"Parsed flat section: {section_name} → empty")

        if section.find("table"):
            result[section_name] = parsed if parsed is not None else []
            logger.debug(f"Final result[{section_name}] = {type(result[section_name])} with {len(result[section_name]) if result[section_name] else 0} items")

    special_districts = parse_special_districts(soup)
    if special_districts:
        result["special_districts"] = special_districts

    return result
