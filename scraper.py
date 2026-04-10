import requests
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import os
import json
from datetime import datetime

TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

def send_telegram(message):
    if TOKEN and CHAT_ID:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={message}"
        try: requests.get(url)
        except: pass

def check_bets():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        # Accesăm Livescore.in
        page.goto("https://www.livescore.in/ro/fotbal/")
        page.wait_for_timeout(10000)
        
        soup = BeautifulSoup(page.content(), 'html.parser')
        # Pe Livescore, meciurile sunt în div-uri cu clasa 'event__match'
        meciuri = soup.select('.event__match')
        
        lista_meciuri = []
        for event in meciuri:
            try:
                gazda = event.select_one('.event__participant--home').text.strip()
                oaspete = event.select_one('.event__participant--away').text.strip()
                cote = event.select('.event__odds')
                
                if len(cote) >= 3:
                    cota_1 = float(cote[0].text.strip())
                    cota_x = float(cote[1].text.strip())
                    cota_2 = float(cote[2].text.strip())
                    
                    media = (cota_1 + cota_x + cota_2) / 3
                    is_value = cota_1 > (media * 1.05)
                    
                    lista_meciuri.append({
                        "echipa_gazda": gazda,
                        "echipa_oaspete": oaspete,
                        "cota_1": cota_1,
                        "cota_reala": round(media, 2),
                        "value_procent": round(((cota_1/media)-1)*100, 2),
                        "is_value": is_value
                    })
            except: continue
        
        # Salvare
        output = {"ultima_actualizare": datetime.now().strftime("%d %B %Y, %H:%M"), "meciuri": lista_meciuri}
        with open('date_meciuri.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=4, ensure_ascii=False)
        browser.close()

if __name__ == "__main__":
    check_bets()
