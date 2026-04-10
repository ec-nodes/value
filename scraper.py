import requests
import json
import os
from datetime import datetime

API_KEY = os.environ.get('API_KEY')
# Folosim Bundesliga pentru Germania
URL = f"https://api.the-odds-api.com/v4/sports/soccer_germany_bundesliga/odds/?apiKey={API_KEY}&regions=eu&markets=h2h"

def get_data():
    response = requests.get(URL)
    if response.status_code != 200: return []
    
    data = response.json()
    lista = []
    
    for match in data:
        # Extragem toate cotele disponibile pentru "1" (gazda)
        cote = []
        for bookmaker in match['bookmakers']:
            for market in bookmaker['markets']:
                if market['key'] == 'h2h':
                    cote.append(market['outcomes'][0]['price'])
        
        if not cote: continue
        
        # Calculăm media pieței (cota "corectă" teoretică)
        cota_medie = sum(cote) / len(cote)
        
        # Căutăm Betano sau Tipico
        casa = next((b for b in match['bookmakers'] if b['key'] in ['betano', 'tipico']), None)
        if not casa: continue
        
        cota_noastra = casa['markets'][0]['outcomes'][0]['price']
        
        # Value Bet: Cota noastră e mai mare decât media pieței
        value_procent = round(((cota_noastra / cota_medie) - 1) * 100, 2)
        
        lista.append({
            "echipa_gazda": match['home_team'],
            "echipa_oaspete": match['away_team'],
            "cota_pariu": cota_noastra,
            "cota_medie": round(cota_medie, 2),
            "value_procent": value_procent,
            "casa": casa['key'],
            "is_value": value_procent > 1.5 # Prag de 1.5%
        })
    return lista

output = {"ultima_actualizare": datetime.now().strftime("%d %B %Y, %H:%M"), "meciuri": get_data()}
with open('date_meciuri.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=4, ensure_ascii=False)
