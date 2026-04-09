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
        page.wait_for_timeout(10000)
        
        soup = BeautifulSoup(page.content(), 'html.parser')
        meciuri = soup.select('.event__match')
        
        gasite = 0
        for event in meciuri:
            try:
                gazda = event.select_one('.event__participant--home').text.strip()
                oaspete = event.select_one('.event__participant--away').text.strip()
                cote = event.select('.event__odds')
                
                if len(cote) >= 3:
                    cota_1 = float(cote[0].text.strip())
                    cota_x = float(cote[1].text.strip())
                    cota_2 = float(cote[2].text.strip())
                    
                    # Calculăm media pieței
                    media = (cota_1 + cota_x + cota_2) / 3
                    
                    # FILTRU: Dacă cota 1 este mai mare decât media pieței cu 5% (1.05)
                    # Am scăzut pragul de la 1.15 la 1.05 ca să găsească mai multe oportunități
                    if cota_1 > (media * 1.05):
                        msg = (f"🔥 VALUE BET DETECTAT!\n"
                               f"⚽ {gazda} vs {oaspete}\n"
                               f"✅ Pariu: 1 (Cota {cota_1})\n"
                               f"📊 Media pieței: {round(media, 2)}")
                        send_telegram(msg)
                        gasite += 1
                        if gasite >= 3: break # Trimitem maxim 3 mesaje pe rulare ca să nu facem spam
            except:
                continue
        browser.close()

if __name__ == "__main__":
    check_bets()
