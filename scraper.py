def get_data():
    # Folosim 'eu' pentru a include casele din Germania
    response = requests.get(URL) # URL-ul are deja regions=eu din variabila globală
    if response.status_code != 200: 
        print(f"Eroare API: {response.status_code}")
        return []
    
    data = response.json()
    lista = []
    
    for match in data:
        # Debug: Afișează ce case de pariuri sunt disponibile pentru acest meci
        bookmakers = [b['key'] for b in match['bookmakers']]
        print(f"Meci: {match['home_team']} vs {match['away_team']} | Case: {bookmakers}")

        # Căutăm Pinnacle (ca referință) și Betano (ca sursă de pariu)
        pinnacle = next((b for b in match['bookmakers'] if b['key'] == 'pinnacle'), None)
        betano = next((b for b in match['bookmakers'] if b['key'] == 'betano'), None)
        
        # Dacă nu găsim Pinnacle, sărim peste meci (nu avem referință)
        if not pinnacle: continue
        
        # Luăm cota de la Pinnacle
        cota_reala = pinnacle['markets'][0]['outcomes'][0]['price']
        
        # Dacă avem Betano, comparăm, dacă nu, luăm Tipico
        casa_pariu = betano if betano else next((b for b in match['bookmakers'] if b['key'] == 'tipico'), None)
        
        if not casa_pariu: continue
        
        cota_gasita = casa_pariu['markets'][0]['outcomes'][0]['price']
        
        # Calculăm valoarea
        value_procent = round(((cota_gasita / cota_reala) - 1) * 100, 2)
        
        # Definim ce înseamnă Value pentru tine (ex: > 2%)
        is_value = value_procent > 2.0 
        
        meci = {
            "echipa_gazda": match['home_team'],
            "echipa_oaspete": match['away_team'],
            "cota_1": cota_gasita,
            "cota_reala": cota_reala,
            "value_procent": value_procent,
            "is_value": is_value
        }
        
        # Trimitem notificare doar dacă este un Value Bet real
        if is_value:
            send_telegram_message(meci)
            
        lista.append(meci)
            
    return lista
