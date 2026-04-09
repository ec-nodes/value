import requests
import os

API_KEY = os.environ.get('API_KEY')
TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

SPORTS = ['soccer_epl', 'soccer_spain_la_liga', 'soccer_italy_serie_a', 'soccer_germany_bundesliga']

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={message}"
    requests.get(url)

def check_bets():
    for sport in SPORTS:
        url = f"https://api.the-odds-api.com/v4/sports/{sport}/odds/?apiKey={API_KEY}&regions=eu&markets=h2h"
        response = requests.get(url)
        
        # Verificăm dacă cererea a reușit
        if response.status_code != 200:
            print(f"Eroare API pentru {sport}: {response.text}")
            continue
            
        data = response.json()
        
        # Verificăm dacă data este într-adevăr o listă
        if not isinstance(data, list):
            print(f"Date invalide primite pentru {sport}")
            continue
        
        for match in data:
            # Verificăm dacă 'bookmakers' există în obiectul match
            if 'bookmakers' not in match:
                continue
                
            pinnacle = next((b for b in match['bookmakers'] if b['key'] == 'pinnacle'), None)
            if not pinnacle: continue
            
            for bookie in match['bookmakers']:
                if bookie['key'] == 'pinnacle': continue
                
                # Verificăm dacă există cote
                try:
                    for i in range(3):
                        cota_reala = pinnacle['markets'][0]['outcomes'][i]['price']
                        cota_gasita = bookie['markets'][0]['outcomes'][i]['price']
                        
                        if cota_gasita > (cota_reala * 1.06):
                            msg = f"🔥 VALUE BET: {match['home_team']} vs {match['away_team']}\nCasa: {bookie['title']}\nPariu: {['1', 'X', '2'][i]}\nCota: {cota_gasita} (Real: {cota_reala})"
                            send_telegram(msg)
                except (IndexError, KeyError):
                    continue

if __name__ == "__main__":
    check_bets()
