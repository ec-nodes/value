from playwright.sync_api import sync_playwright
import time

def scaneaza_casa_pariuri():
    with sync_playwright() as p:
        # Deschidem un browser invizibil (headless=True)
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Setăm un "User-Agent" ca să părem un om pe Windows, nu un robot
        page.set_extra_http_headers({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"})

        print("Accesăm site-ul...")
        # Aici pui link-ul către categoria de fotbal a casei de pariuri
        page.goto("https://www.exemplu-casa-pariuri.ro/fotbal")
        
        # Așteptăm 5 secunde să se încarce cotele (JavaScript-ul)
        time.sleep(5)
        
        # Acum trebuie să căutăm elementele HTML care conțin cotele.
        # ATENȚIE: Aceste clase (".nume-echipa", ".cota") diferă de la site la site!
        # Trebuie să dai click dreapta pe site -> Inspect Element ca să afli clasele reale.
        
        meciuri = page.query_selector_all('.rand-meci') # Clasa fictivă pentru rândul meciului
        
        rezultate = []
        for meci in meciuri:
            try:
                gazda = meci.query_selector('.echipa-gazda').inner_text()
                oaspete = meci.query_selector('.echipa-oaspete').inner_text()
                cota_1 = meci.query_selector('.cota-1').inner_text()
                
                print(f"Găsit: {gazda} vs {oaspete} | Cota 1: {cota_1}")
                
                rezultate.append({
                    "meci": f"{gazda} - {oaspete}",
                    "cota_1": float(cota_1)
                })
            except:
                continue # Dacă un meci nu are cote, trecem mai departe
                
        browser.close()
        return rezultate

# Rulăm funcția
date_extrase = scaneaza_casa_pariuri()
print(date_extrase)
