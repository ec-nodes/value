import requests
import json
import os
import time
from datetime import datetime

# Luăm cheia API din setările GitHub
API_KEY = os.environ.get('API_KEY')

# LISTA CU CAMPIONATELE PE CARE VREI SĂ LE SCANEZI
SPORTS = [
    'soccer_epl',               # Anglia Premier League
    'soccer_spain_la_liga',     # Spania La Liga
    'soccer_italy_serie_a',     # Italia Serie A
    'soccer_germany_bundesliga',# Germania Bundesliga
    'soccer_france_ligue_one',  # Franta Ligue 1
    'soccer_uefa_champs_league' # Champions League
    # Poți adăuga și 'soccer_romania_liga_1' când este disponibil în API
]

REGIONS = 'eu' 
MARKETS = 'h2h' # 1X2 (Rezultat final)

def get_odds(sport_key):
    url = f'https://api.the-odds-api.com/v4/sports/{sport_key}/odds/?apiKey={API_KEY}&regions={REGIONS}&markets={MARKETS}'
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Eroare la API pentru {sport_key}:", response.text)
        return []
    return response.json()

def calculate_value_bets(data, nume_campionat):
    value_bets = []
    
    for match in data:
        pinnacle_odds = None
        other_bookies = []
        
        for bookmaker in match['bookmakers']:
            if bookmaker['key'] == 'pinnacle':
                pinnacle_odds = bookmaker['markets'][0]['outcomes']
            else:
                other_bookies.append(bookmaker)
                
        if not pinnacle_odds:
            continue
            
        for bookie in other_bookies:
            for i in range(len(pinnacle_odds)):
                try:
                    nume_selectie = pinnacle_odds[i]['name']
                    cota_reala = pinnacle_odds[i]['price']
                    
                    cota_gasita = None
                    for outcome in bookie['markets'][0]['outcomes']:
                        if outcome['name'] == nume_selectie:
                            cota_gasita = outcome['price']
                            break
                            
                    if not cota_gasita:
                        continue
                    
                    probabilitate_reala = 1 / cota_reala
                    value = probabilitate_reala * cota_gasita
                    
                    if value > 1.03: # Profit mai mare de 3%
                        echipa_gazda = match['home_team']
                        echipa_oaspete = match['away_team']
                        
                        if nume_selectie == echipa_gazda:
                            semn_pariu = "1"
                            explicatie = f"Victorie {echipa_gazda}"
                        elif nume_selectie == echipa_oaspete:
                            semn_pariu = "2"
                            explicatie = f"Victorie {echipa_oaspete}"
                        elif nume_selectie == 'Draw':
                            semn_pariu = "X"
                            explicatie = "Egalitate"
                        else:
                            semn_pariu = "?"
                            explicatie = nume_selectie

                        value_bets.append({
                            "echipa_gazda": echipa_gazda,
                            "echipa_oaspete": echipa_oaspete,
                            "data_ora": match['commence_time'][:10] + " " + match['commence_time'][11:16],
                            "tip_pariu": f"[{semn_pariu}] - {explicatie}",
                            "cota_reala": cota_reala,
                            "cota_gasita": cota_gasita,
                            "casa_pariuri": bookie['title'],
                            "value_procent": round((value - 1) * 100, 2),
                            "campionat": nume_campionat # Am adăugat campionatul pentru a ști de unde e meciul
                        })
                except Exception as e:
                    continue
                    
    return value_bets

# --- MOTORUL PRINCIPAL ---
toate_value_bets = []

print("Începem scanarea campionatelor...")

for sport in SPORTS:
    print(f"Scanez: {sport}...")
    raw_data = get_odds(sport)
    
    if raw_data:
        bune = calculate_value_bets(raw_data, sport)
        toate_value_bets.extend(bune) # Adăugăm meciurile găsite în lista principală
        
    # Pauză de 1 secundă între campionate pentru a nu bloca API-ul
    time.sleep(1)

# Sortăm TOATE meciurile din TOATE campionatele descrescător după valoare
toate_value_bets.sort(key=lambda x: x['value_procent'], reverse=True)

rezultat_final = {
    "ultima_actualizare": datetime.now().strftime("%d %B %Y, %H:%M"),
    "meciuri": toate_value_bets
}

with open('date_meciuri.json', 'w', encoding='utf-8') as f:
    json.dump(rezultat_final, f, indent=4, ensure_ascii=False)

print(f"GATA! S-au găsit în total {len(toate_value_bets)} value bets.")
