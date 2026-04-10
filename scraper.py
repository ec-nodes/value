import requests
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import os
import json  # <--- Adăugat
from datetime import datetime  # <--- Adăugat

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
        
        meciuri_gasite_pentru_json = [] 
        
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
                    
                    if cota_1 > (media * 1.05):
                        meciuri_gasite_pentru_json.append({
                            "echipa_gazda": gazda,
                            "echipa_oaspete": oaspete,
                            "data_ora": "Azi",
                            "tip_pariu": "1",
                            "cota_reala": round(media, 2),
                            "cota_gasita": cota_1,
                            "casa_pariuri": "Flashscore",
                            "value_procent": round(((cota_1/media)-1)*100, 2)
                        })
                        
                        msg = f"🔥 VALUE BET: {gazda} vs {oaspete} | Cota: {cota_1}"
                        send_telegram(msg)
            except:
                continue
        
        # SALVARE ÎN JSON
        output = {
            "ultima_actualizare": datetime.now().strftime("%d %B %Y, %H:%M"),
            "meciuri": meciuri_gasite_pentru_json
        }
        with open('date_meciuri.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=4, ensure_ascii=False)
            
        browser.close()

if __name__ == "__main__":
    check_bets()
