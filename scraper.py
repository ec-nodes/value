import requests
import json
import os
from datetime import datetime

# Configurare
API_KEY = os.environ.get('API_KEY')
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')
URL = f"https://api.the-odds-api.com/v4/sports/soccer_epl/odds/?apiKey={API_KEY}&regions=eu&markets=h2h"

def send_telegram_message(meci):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID: 
        return
    
    text = (f"🔥 *Value Bet Găsit!*\n\n"
            f"⚽ {meci['echipa_gazda']} - {meci['echipa_oaspete']}\n"
            f"Cota Unibet: {meci['cota_1']}\n"
            f"Cota Pinnacle: {meci['cota_reala']}\n"
            f"Value: {meci['value_procent']}%\n")
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "Markdown"})
    except Exception as e:
        print(f"Eroare trimitere Telegram: {e}")

def get_data():
    response = requests.get(URL)
    if response.status_code != 200: 
        return []
    
    data = response.json()
    lista = []
    
    for match in data:
        pinnacle = next((b for b in match['bookmakers'] if b['key'] == 'pinnacle'), None)
        unibet = next((b for b in match['bookmakers'] if b['key'] == 'unibet'), None)
        
        if not pinnacle or not unibet: 
            continue
        
        cota_reala = pinnacle['markets'][0]['outcomes'][0]['price']
        cota_gasita = unibet['markets'][0]['outcomes'][0]['price']
        
        is_value = cota_gasita > (cota_reala * 1.03)
        
        meci = {
            "echipa_gazda": match['home_team'],
            "echipa_oaspete": match['away_team'],
            "cota_1": cota_gasita,
            "cota_reala": cota_reala,
            "value_procent": round(((cota_gasita/cota_reala)-1)*100, 2),
            "is_value": is_value
        }
        
        # Trimitere notificare doar dacă este value bet
        if is_value:
            send_telegram_message(meci)
            
        lista.append(meci)
    return lista

# Execuție
if __name__ == "__main__":
    meciuri = get_data()
    output = {
        "ultima_actualizare": datetime.now().strftime("%d %B %Y, %H:%M"), 
        "meciuri": meciuri
    }
    with open('date_meciuri.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=4, ensure_ascii=False)
