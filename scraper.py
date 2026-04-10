import requests
import json
import os
from datetime import datetime

# Folosește secretul din GitHub
API_KEY = os.environ.get('API_KEY') 
# Scanează Premier League
URL = f"https://api.the-odds-api.com/v4/sports/soccer_epl/odds/?apiKey={API_KEY}&regions=eu&markets=h2h"

def get_data():
    response = requests.get(URL)
    if response.status_code != 200: return []
    
    data = response.json()
    lista = []
    for match in data:
        # Căutăm Pinnacle (cota reală)
        pinnacle = next((b for b in match['bookmakers'] if b['key'] == 'pinnacle'), None)
        if not pinnacle: continue
        
        # Căutăm o altă casă (ex: Unibet)
        unibet = next((b for b in match['bookmakers'] if b['key'] == 'unibet'), None)
        if not unibet: continue
        
        cota_reala = pinnacle['markets'][0]['outcomes'][0]['price']
        cota_gasita = unibet['markets'][0]['outcomes'][0]['price']
        
        lista.append({
            "echipa_gazda": match['home_team'],
            "echipa_oaspete": match['away_team'],
            "cota_1": cota_gasita,
            "cota_reala": cota_reala,
            "value_procent": round(((cota_gasita/cota_reala)-1)*100, 2),
            "is_value": cota_gasita > (cota_reala * 1.03)
        })
    return lista

output = {"ultima_actualizare": datetime.now().strftime("%d %B %Y, %H:%M"), "meciuri": get_data()}
with open('date_meciuri.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=4, ensure_ascii=False)
