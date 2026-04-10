def get_data():
    # Folosim 'eu' pentru a include casele din Germania
    response = requests.get(URL.replace("regions=eu", "regions=eu")) 
    if response.status_code != 200: return []
    
    data = response.json()
    lista = []
    
    for match in data:
        # Căutăm Tipico și Betano
        tipico = next((b for b in match['bookmakers'] if b['key'] == 'tipico'), None)
        betano = next((b for b in match['bookmakers'] if b['key'] == 'betano'), None)
        
        # Dacă nu avem ambele case, sărim peste meci
        if not tipico or not betano: 
            continue
        
        # Alegem Tipico ca referință (cota "reală") și Betano ca sursă de pariu
        # Sau invers, depinde unde vrei să cauți valoarea
        cota_referinta = tipico['markets'][0]['outcomes'][0]['price']
        cota_betano = betano['markets'][0]['outcomes'][0]['price']
        
        # Calculăm valoarea
        # Dacă cota Betano este mai mare decât cea de la Tipico, avem "Value"
        value_procent = round(((cota_betano / cota_referinta) - 1) * 100, 2)
        is_value = value_procent > 3.0 # Prag de 3% pentru a filtra
        
        if is_value:
            meci = {
                "echipa_gazda": match['home_team'],
                "echipa_oaspete": match['away_team'],
                "cota_1": cota_betano,
                "cota_reala": cota_referinta,
                "value_procent": value_procent,
                "is_value": True
            }
            lista.append(meci)
            # Trimitem notificare doar dacă e value
            send_telegram_message(meci)
            
    return lista
