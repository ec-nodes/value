async function incarcaDate() {
    const tableBody = document.getElementById('table-body');
    const lastUpdate = document.getElementById('last-update');
    
    // Folosim URL-ul complet pentru a evita problemele de path
    const url = 'https://ec-nodes.github.io/value/date_meciuri.json?t=' + new Date().getTime();
    
    try {
        const response = await fetch(url);
        if (!response.ok) throw new Error('Nu am putut accesa datele');
        
        const data = await response.json();

        if (lastUpdate) {
            lastUpdate.innerText = data.ultima_actualizare;
        }
        
        if (tableBody) {
            tableBody.innerHTML = '';
            data.meciuri.forEach(meci => {
                const row = document.createElement('tr');
                // Aplicăm clasa CSS dacă este Value Bet
                if (meci.is_value) {
                    row.className = 'value-row';
                }
                
                row.innerHTML = `
                    <td><strong>${meci.echipa_gazda} - ${meci.echipa_oaspete}</strong></td>
                    <td>${meci.casa.toUpperCase()}</td>
                    <td>${meci.cota_pariu}</td>
                    <td>${meci.cota_medie}</td>
                    <td>${meci.value_procent}%</td>
                `;
                tableBody.appendChild(row);
            });
        }
    } catch (error) {
        console.error("Eroare la încărcarea datelor:", error);
        if (tableBody) {
            tableBody.innerHTML = '<tr><td colspan="5">Eroare la încărcarea datelor. Verifică consola.</td></tr>';
        }
    }
}

document.addEventListener('DOMContentLoaded', incarcaDate);
