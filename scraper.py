import requests
from bs4 import BeautifulSoup
import time
import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

COUNTRIES = ["Spain", "France", "Germany", "United Kingdom", "Italy", "Turkey"]
SEARCH_TEMPLATE = "tennis academy in {} site:.com"

def search_google(query):
    url = "https://www.startpage.com/sp/search"
    params = {"query": query}
    response = requests.get(url, headers=HEADERS, params=params)
    soup = BeautifulSoup(response.text, "html.parser")
    return [a['href'] for a in soup.select('a.result-link') if 'href' in a.attrs]

def scrape_academy_page(url):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")
        title = soup.title.string.strip() if soup.title else "No title"
        text = soup.get_text(" ", strip=True)
        return {
            "academy": title,
            "address": "Not found",
            "website": url,
            "details": text[:500]
        }
    except Exception as e:
        return {"academy": "ERROR", "address": "", "website": url, "details": str(e)}

def send_to_google_sheet(rows):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_dict = json.loads(os.getenv("GOOGLE_CREDENTIALS_JSON"))
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)

    sheet = client.open_by_key(os.getenv("GOOGLE_SHEET_ID")).sheet1

    # Header
    if sheet.row_count < 1 or sheet.cell(1, 1).value != "Country":
        sheet.append_row(["Country", "Academy", "Address", "Website", "Details"])

    for row in rows:
        sheet.append_row([row["country"], row["academy"], row["address"], row["website"], row["details"]])
        time.sleep(1)

def run():
    all_data = []
    for country in COUNTRIES:
        query = SEARCH_TEMPLATE.format(country)
        print(f"Searching academies in {country}...")
        links = search_google(query)
        for link in links[:5]:
            print(f"Scraping: {link}")
            data = scrape_academy_page(link)
            data["country"] = country
            all_data.append(data)
            time.sleep(2)
        time.sleep(5)

    send_to_google_sheet(all_data)

if __name__ == "__main__":
    run()
