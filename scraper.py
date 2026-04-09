from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import json
from datetime import datetime

def get_value_bets():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_extra_http_headers({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"})
        
        page.goto("https://www.flashscore.ro/fotbal/")
        page.wait_for_timeout(5000)
        
        soup = BeautifulSoup(page.content(), 'html.parser')
        meciuri_gasite = []
        
        # Selectăm rândurile meciurilor
        for event in soup.select('.event__match'):
            try:
                gazda = event.select_one('.event__participant--home').text.strip()
                oaspete = event.select_one('.event__participant--away').text.strip()
                cote = event.select('.event__odds')
                
                if len(cote) >= 3:
                    cota_1 = float(cote[0].text.strip())
                    # Aici simulăm o "cotă reală" (în realitate, ai nevoie de un API pentru asta)
                    # Pentru test, considerăm că orice cotă peste 2.00 este "Value"
                    cota_reala = 1.90 
                    
                    if cota_1 > cota_reala:
                        value_procent = round(((cota_1 / cota_reala) - 1) * 100, 2)
                        meciuri_gasite.append({
                            "echipa_gazda": gazda,
                            "echipa_oaspete": oaspete,
                            "data_ora": "Azi",
                            "tip_pariu": "[1] - Victorie Gazde",
                            "cota_reala": cota_reala,
                            "cota_gasita": cota_1,
                            "casa_pariuri": "Flashscore",
                            "value_procent": value_procent
                        })
            except:
                continue
        browser.close()
        return meciuri_gasite

# Salvarea rezultatelor
data = get_value_bets()
output = {
    "ultima_actualizare": datetime.now().strftime("%d %B %Y, %H:%M"),
    "meciuri": data
}

with open('date_meciuri.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=4, ensure_ascii=False)
