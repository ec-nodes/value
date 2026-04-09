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
        page.goto("https://www.flashscore.ro/fotbal/")
        page.wait_for_timeout(10000)
        
        soup = BeautifulSoup(page.content(), 'html.parser')
        meciuri = soup.select('.event__match')
        
        # TEST: Trimitem doar primul meci găsit, indiferent de valoare
        if len(meciuri) > 0:
            event = meciuri[0]
            gazda = event.select_one('.event__participant--home').text.strip()
            oaspete = event.select_one('.event__participant--away').text.strip()
            cote = event.select('.event__odds')
            cota_1 = cote[0].text.strip()
            
            msg = f"🤖 TEST ROBOT: {gazda} vs {oaspete} | Cota 1: {cota_1}"
            send_telegram(msg)
        
        browser.close()

if __name__ == "__main__":
    check_bets()
