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
        # Flashscore are nevoie de un User-Agent real
        page.set_extra_http_headers({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"})
        
        page.goto("https://www.flashscore.ro/fotbal/")
        page.wait_for_timeout(7000) # Așteptăm mai mult pentru încărcarea cotelor
        
        soup = BeautifulSoup(page.content(), 'html.parser')
        
        for event in soup.select('.event__match'):
            try:
                gazda = event.select_one('.event__participant--home').text.strip()
                oaspete = event.select_one('.event__participant--away').text.strip()
                
                # Flashscore afișează cotele într-un format specific
                # Vom încerca să extragem cotele 1, X, 2
                cote_elemente = event.select('.event__odds')
                if len(cote_elemente) < 3: continue
                
                cota_1 = float(cote_elemente[0].text.strip())
                cota_x = float(cote_elemente[1].text.strip())
                cota_2 = float(cote_elemente[2].text.strip())
                
                # Calculăm media pieței (simplificat)
                media_cotei_1 = (cota_1 + cota_x + cota_2) / 3 # Aceasta este o aproximare
                
                # Dacă cota 1 este cu 15% mai mare decât media (Value Bet)
                if cota_1 > (media_cotei_1 * 1.15):
                    msg = (f"🔥 VALUE BET DETECTAT!\n"
                           f"⚽ {gazda} vs {oaspete}\n"
                           f"✅ Pariu: 1 (Victorie Gazde)\n"
                           f"💰 Cota: {cota_1}\n"
                           f"📊 Media pieței: {round(media_cotei_1, 2)}")
                    send_telegram(msg)
                    
            except Exception as e:
                continue
        browser.close()

if __name__ == "__main__":
    check_bets()
