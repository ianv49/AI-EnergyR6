const apiSources = [
    'collect1.txt', 'collect2.txt', 'collect3.txt', 
    'collect4.txt', 'collect5.txt', 'collect6.txt', 'collect7.txt'
];

async function fetchApiRegistry() {
    const grid = document.getElementById('api-grid');
    const status = document.getElementById('sync-status');
    grid.innerHTML = ''; 

    for (const fileName of apiSources) {
        try {
            const response = await fetch(`${fileName}?v=${Date.now()}`);
            if (!response.ok) continue;

            const text = await response.text();
            const rows = text.trim().split('\n');
            
            // Logic to find the 'source' field in the CSV structure
            // Sample Row: id,timestamp,temp,humi,irra,wind,SOURCE,wind_power,solar
            // 'source' is at index 6 (the 7th item)
            let detectedSource = "UNKNOWN API";

            // We check the first row of data (index 0 or 1 if there's a header)
            const dataRow = rows.length > 1 ? rows[1] : rows[0]; 
            
            if (dataRow && dataRow.includes(',')) {
                const columns = dataRow.split(',');
                if (columns.length >= 7) {
                    detectedSource = columns[6].trim().replace(/_/g, ' ').toUpperCase();
                }
            }

            createCard(detectedSource, rows.length);
        } catch (err) {
            console.warn(`Error reading ${fileName}`);
        }
    }
    status.innerText = `LAST SYNC: ${new Date().toLocaleTimeString()}`;
}

function createCard(name, count) {
    const grid = document.getElementById('api-grid');
    const card = document.createElement('div');
    card.className = 'api-card';
    card.innerHTML = `
        <span class="api-title">${name}</span>
        <span class="data-count">${count} DATA ROWS</span>
    `;
    grid.appendChild(card);
}

// Auto-run on load
document.addEventListener('DOMContentLoaded', fetchApiRegistry);
