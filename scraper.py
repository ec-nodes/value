import requests
import json
import os
from datetime import datetime

# Luăm cheia API din setările GitHub
API_KEY = os.environ.get('f0a8de6ec6e351947e0872946ecfa11d')
SPORT = 'soccer_epl' # Premier League (poți schimba cu alte sporturi)
REGIONS = 'eu' # Case de pariuri din Europa
MARKETS = 'h2h' # 1X2 (Rezultat final)

def get_odds():
    url = f'https://api.the-odds-api.com/v4/sports/{SPORT}/odds/?apiKey={API_KEY}&regions={REGIONS}&markets={MARKETS}'
    response = requests.get(url)
    if response.status_code != 200:
        print("Eroare la API:", response.text)
        return []
    return response.json()

def calculate_value_bets(data):
    value_bets = []
    
    for match in data:
        pinnacle_odds = None
        other_bookies = []
        
        # Căutăm cotele
        for bookmaker in match['bookmakers']:
            if bookmaker['key'] == 'pinnacle':
                pinnacle_odds = bookmaker['markets'][0]['outcomes']
            else:
                other_bookies.append(bookmaker)
                
        # Dacă nu avem Pinnacle ca referință, sărim peste meci
        if not pinnacle_odds:
            continue
            
        # Comparăm cotele
        for bookie in other_bookies:
            for i in range(3): # 1, X, 2
                try:
                    echipa = pinnacle_odds[i]['name']
                    cota_reala = pinnacle_odds[i]['price']
                    cota_gasita = bookie['markets'][0]['outcomes'][i]['price']
                    
                    # Formula Value Bet: (1 / Cota_Reala) * Cota_Gasita > 1
                    probabilitate_reala = 1 / cota_reala
                    value = probabilitate_reala * cota_gasita
                    
                    # Dacă valoarea e mai mare de 1.03 (3% profit pe termen lung)
                    if value > 1.03:
                        value_bets.append({
                            "echipa_gazda": match['home_team'],
                            "echipa_oaspete": match['away_team'],
                            "data_ora": match['commence_time'][:10] + " " + match['commence_time'][11:16],
                            "tip_pariu": f"Victorie {echipa}",
                            "cota_reala": cota_reala,
                            "cota_gasita": cota_gasita,
                            "casa_pariuri": bookie['title'],
                            "value_procent": round((value - 1) * 100, 2)
                        })
                except:
                    continue
                    
    return value_bets

# Rulăm scriptul
print("Se scanează cotele...")
raw_data = get_odds()
bune = calculate_value_bets(raw_data)

# Salvăm în formatul cerut de site-ul tău HTML
rezultat_final = {
    "ultima_actualizare": datetime.now().strftime("%d %B %Y, %H:%M"),
    "meciuri": bune
}

with open('date_meciuri.json', 'w', encoding='utf-8') as f:
    json.dump(rezultat_final, f, indent=4, ensure_ascii=False)

print(f"S-au găsit {len(bune)} value bets. Fișierul a fost actualizat.")
