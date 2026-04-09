import requests
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import os

TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={message}"
    requests.get(url)

def check_bets():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_extra_http_headers({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"})
        
        page.goto("https://www.flashscore.ro/fotbal/")
        page.wait_for_timeout(10000) # Am mărit timpul de așteptare
        
        soup = BeautifulSoup(page.content(), 'html.parser')
        
        # TEST: Câte meciuri găsește?
        meciuri = soup.select('.event__match')
        print(f"Am găsit {len(meciuri)} meciuri pe pagină.")
        
        if len(meciuri) == 0:
            send_telegram("Robotul a rulat, dar nu a găsit niciun meci pe Flashscore. Verifică clasele CSS!")
            return

        # Trimitem un mesaj de test că robotul e viu
        send_telegram(f"Robotul a scanat cu succes și a găsit {len(meciuri)} meciuri.")

        for event in meciuri[:3]: # Verificăm doar primele 3 pentru test
            try:
                gazda = event.select_one('.event__participant--home').text.strip()
                cote = event.select('.event__odds')
                if len(cote) >= 3:
                    cota_1 = cote[0].text.strip()
                    send_telegram(f"Test: {gazda} are cota 1: {cota_1}")
            except Exception as e:
                print(f"Eroare la citire: {e}")
        
        browser.close()

if __name__ == "__main__":
    check_bets()
