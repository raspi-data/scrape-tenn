
import requests
from bs4 import BeautifulSoup
import time
import csv

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

COUNTRIES = ["Spain", "France", "Germany", "United Kingdom", "Italy", "Turkey"]
SEARCH_TEMPLATE = "tennis academy in {} site:.com"

def search_google(query):
    # Folosește StartPage ca proxy pentru Google Search (gratuit și legal)
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

def run():
    all_data = []
    for country in COUNTRIES:
        query = SEARCH_TEMPLATE.format(country)
        print(f"Searching academies in {country}...")
        links = search_google(query)
        for link in links[:5]:  # Limităm pentru testare
            print(f"Scraping: {link}")
            data = scrape_academy_page(link)
            data["country"] = country
            all_data.append(data)
            time.sleep(2)
        time.sleep(5)

    with open("academies.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["country", "academy", "address", "website", "details"])
        writer.writeheader()
        writer.writerows(all_data)

if __name__ == "__main__":
    run()
