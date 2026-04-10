import requests
import json
import os
from datetime import datetime

# Configurare din variabilele de mediu (GitHub Secrets)
API_KEY = os.environ.get('API_KEY')
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

# URL pentru Bundesliga (Germania)
URL = f"https://api.the-odds-api.com/v4/sports/soccer_germany_bundesliga/odds/?apiKey={API_KEY}&regions=eu&markets=h2h"

def send_telegram_message(meci):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return
    
    text = (f"🔥 *Value Bet Găsit!*\n\n"
            f"⚽ {meci['echipa_gazda']} - {meci['echipa_oaspete']}\n"
            f"Casa: {meci['casa'].upper()}\n"
            f"Cota Ta: {meci['cota_pariu']}\n"
            f"Media Pieței: {meci['cota_medie']}\n"
            f"Value: {meci['value_procent']}%\n")
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "Markdown"})
    except Exception as e:
        print(f"Eroare Telegram: {e}")

def get_data():
    response = requests.get(URL)
    if response.status_code != 200:
        print(f"Eroare API: {response.status_code}")
        return []
    
    data = response.json()
    lista = []
    
    for match in data:
        # 1. Calculăm media pieței pentru cota de "1" (gazda)
        cote = []
        for bookmaker in match['bookmakers']:
            for market in bookmaker['markets']:
                if market['key'] == 'h2h':
                    cote.append(market['outcomes'][0]['price'])
        
        if not cote: continue
        cota_medie = sum(cote) / len(cote)
        
        # 2. Căutăm Betano sau Tipico
        casa = next((b for b in match['bookmakers'] if b['key'] in ['betano', 'tipico']), None)
        if not casa: continue
        
        cota_pariu = casa['markets'][0]['outcomes'][0]['price']
        value_procent = round(((cota_pariu / cota_medie) - 1) * 100, 2)
        
        # 3. Definim Value Bet (ex: cota e cu 1.5% mai mare decât media)
        is_value = value_procent > 1.5
        
        meci = {
            "echipa_gazda": match['home_team'],
            "echipa_oaspete": match['away_team'],
            "cota_pariu": cota_pariu,
            "cota_medie": round(cota_medie, 2),
            "value_procent": value_procent,
            "casa": casa['key'],
            "is_value": is_value
        }
        
        if is_value:
            send_telegram_message(meci)
            
        lista.append(meci)

    # 4. Meci de test (dacă lista e goală, să vedem ceva pe site)
    if len(lista) == 0:
        lista.append({
            "echipa_gazda": "TEST ECHIPA",
            "echipa_oaspete": "TEST ECHIPA",
            "cota_pariu": 2.50,
            "cota_medie": 2.00,
            "value_procent": 25.0,
            "casa": "betano",
            "is_value": True
        })
        
    return lista

# Execuție
if __name__ == "__main__":
    print("Pornire scraper...")
    meciuri = get_data()
    output = {
        "ultima_actualizare": datetime.now().strftime("%d %B %Y, %H:%M"), 
        "meciuri": meciuri
    }
    
    # Salvare fișier
    with open('date_meciuri.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=4, ensure_ascii=False)
    print("Fișier salvat cu succes.")
