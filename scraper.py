from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import json
from datetime import datetime

def get_odds_from_flashscore():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        # Flashscore are nevoie de un User-Agent real
        page.set_extra_http_headers({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"})
        
        print("Accesăm Flashscore...")
        page.goto("https://www.flashscore.ro/fotbal/")
        page.wait_for_timeout(5000) # Așteptăm încărcarea JS
        
        html = page.content()
        soup = BeautifulSoup(html, 'html.parser')
        
        meciuri = []
        # Căutăm containerele de meciuri (clasele pot varia, trebuie verificate periodic)
        for event in soup.select('.event__match'):
            try:
                gazda = event.select_one('.event__participant--home').text.strip()
                oaspete = event.select_one('.event__participant--away').text.strip()
                # Extragem cotele (exemplu simplificat)
                cote = event.select('.event__odds')
                if len(cote) >= 3:
                    meciuri.append({
                        "echipa_gazda": gazda,
                        "echipa_oaspete": oaspete,
                        "cota_1": cote[0].text.strip(),
                        "cota_x": cote[1].text.strip(),
                        "cota_2": cote[2].text.strip()
                    })
            except:
                continue
        
        browser.close()
        return meciuri

# Salvarea datelor
data = get_odds_from_flashscore()
output = {
    "ultima_actualizare": datetime.now().strftime("%d %B %Y, %H:%M"),
    "meciuri": data
}

with open('date_meciuri.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=4, ensure_ascii=False)
