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
        page.wait_for_timeout(5000)
        
        soup = BeautifulSoup(page.content(), 'html.parser')
        # Selectăm meciurile
        for event in soup.select('.event__match'):
            try:
                gazda = event.select_one('.event__participant--home').text.strip()
                oaspete = event.select_one('.event__participant--away').text.strip()
                cote = event.select('.event__odds')
                
                if len(cote) >= 3:
                    cota_1 = float(cote[0].text.strip())
                    cota_x = float(cote[1].text.strip())
                    cota_2 = float(cote[2].text.strip())
                    
                    # Logica de Value Bet: Dacă cota 1 este peste 2.20 (exemplu de prag)
                    # În lipsa unui API, folosim un prag fix sau o medie
                    if cota_1 > 2.20: 
                        msg = f"🔥 VALUE BET POSIBIL:\n{gazda} vs {oaspete}\nCota 1: {cota_1}"
                        send_telegram(msg)
            except:
                continue
        browser.close()

if __name__ == "__main__":
    check_bets()
