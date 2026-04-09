async function incarcaDate() {
    const tableBody = document.getElementById('table-body');
    const lastUpdate = document.getElementById('last-update');
    
    tableBody.innerHTML = '<tr><td colspan="6" style="text-align:center;">Se caută value bets...</td></tr>';

    try {
        // Adăugăm un timestamp pentru a evita cache-ul browserului
        const response = await fetch(`date_meciuri.json?t=${new Date().getTime()}`);
        const data = await response.json();

        tableBody.innerHTML = ''; // Curățăm tabelul
        lastUpdate.innerText = data.ultima_actualizare;

        if (data.meciuri.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="6" style="text-align:center;">Nu s-au găsit value bets momentan.</td></tr>';
            return;
        }

        data.meciuri.forEach(meci => {
            // Colorăm procentul în funcție de valoare
            let valueClass = meci.value_procent > 5 ? 'value-high' : 'value-medium';

            const row = `
                <tr>
                    <td><strong>${meci.echipa_gazda} - ${meci.echipa_oaspete}</strong><br><small>${meci.data_ora}</small></td>
                    <td>${meci.tip_pariu}</td>
                    <td>${meci.cota_reala}</td>
                    <td><strong>${meci.cota_gasita}</strong></td>
                    <td>${meci.casa_pariuri}</td>
                    <td class="${valueClass}">+${meci.value_procent}%</td>
                </tr>
            `;
            tableBody.innerHTML += row;
        });

    } catch (error) {
        tableBody.innerHTML = '<tr><td colspan="6" style="text-align:center; color:red;">Eroare la încărcarea datelor. Verifică dacă fișierul JSON există.</td></tr>';
        console.error("Eroare:", error);
    }
}

// Încarcă datele automat când deschizi pagina
window.onload = incarcaDate;
