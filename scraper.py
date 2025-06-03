import requests
from bs4 import BeautifulSoup
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time

# --- Google Sheets Setup ---
SHEET_ID = "1Rp7ZZk-u9XEqfQmpGeB1Tf6Vv8KyzxQ-dDnePQt2omI"

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open_by_key(SHEET_ID).sheet1

# --- Scraper Setup ---
URL = "https://www.tenniseurope.org/page/12116/European-Junior-Tennis-Tour"  # example placeholder
headers = {
    "User-Agent": "Mozilla/5.0 (compatible; ScraperBot/1.0)"
}

response = requests.get(URL, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")

# Replace this selector with correct one from actual site
academy_cards = soup.select(".academy-card")  # update this to match real HTML structure

for card in academy_cards:
    try:
        name = card.select_one(".academy-name").text.strip()
        location = card.select_one(".academy-country").text.strip()
        website = card.select_one("a")["href"]
        
        print(f"Found: {name}, {location}, {website}")
        sheet.append_row([name, location, website])
        time.sleep(1)  # avoid hitting Google API rate limit
    except Exception as e:
        print(f"Error parsing academy: {e}")
