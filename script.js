async function incarcaDate() {
    const tableBody = document.getElementById('table-body');
    const lastUpdate = document.getElementById('last-update');
    
    try {
        const response = await fetch(`date_meciuri.json?t=${new Date().getTime()}`);
        const data = await response.json();

        tableBody.innerHTML = '';
        lastUpdate.innerText = data.ultima_actualizare;

        data.meciuri.forEach(meci => {
            let rowClass = meci.is_value ? 'value-row' : '';
            const row = `
                <tr class="${rowClass}">
                    <td><strong>${meci.echipa_gazda} - ${meci.echipa_oaspete}</strong></td>
                    <td>1</td>
                    <td>${meci.cota_reala}</td>
                    <td><strong>${meci.cota_1}</strong></td>
                    <td>Flashscore</td>
                    <td>${meci.value_procent}%</td>
                </tr>
            `;
            tableBody.innerHTML += row;
        });
    } catch (error) {
        console.error("Eroare:", error);
    }
}
window.onload = incarcaDate;
