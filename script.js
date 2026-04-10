async function incarcaDate() {
    const tableBody = document.getElementById('table-body');
    const response = await fetch('date_meciuri.json?t=' + new Date().getTime());
    const data = await response.json();
    
    tableBody.innerHTML = '';
    data.meciuri.forEach(meci => {
        const row = document.createElement('tr');
        if (meci.is_value) row.className = 'value-row';
        
        row.innerHTML = `
            <td>${meci.echipa_gazda} - ${meci.echipa_oaspete}</td>
            <td>${meci.casa.toUpperCase()}</td>
            <td>${meci.cota_pariu}</td>
            <td>${meci.cota_medie}</td>
            <td>${meci.value_procent}%</td>
        `;
        tableBody.appendChild(row);
    });
}
window.onload = incarcaDate;
