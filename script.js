const targetFiles = [
    'collect1.txt', 'collect2.txt', 'collect3.txt', 
    'collect4.txt', 'collect5.txt', 'collect6.txt', 'collect7.txt'
];

async function updateDashboard() {
    const grid = document.getElementById('source-grid');
    const status = document.getElementById('sync-status');
    grid.innerHTML = ''; // Clear for refresh

    for (const file of targetFiles) {
        try {
            const response = await fetch(`${file}?nocache=${Date.now()}`);
            if (!response.ok) continue;

            const text = await response.text();
            const lines = text.trim().split('\n');
            
            // Logic to find the Source Name (API Name)
            // It looks for "source: NAME" or "source=NAME"
            let apiName = "Unknown API";
            const firstLine = lines[0] || "";

            if (firstLine.toLowerCase().includes('source')) {
                // Split by colon or equals, then clean up the result
                const parts = firstLine.split(/[:=]/);
                if (parts.length > 1) {
                    apiName = parts[1].split(',')[0].trim();
                }
            }

            createSourceCard(apiName, lines.length);
        } catch (err) {
            console.error(`Error reading ${file}:`, err);
        }
    }
    status.innerText = `SYNCED AT: ${new Date().toLocaleTimeString()}`;
}

function createSourceCard(sourceName, count) {
    const grid = document.getElementById('source-grid');
    const card = document.createElement('div');
    card.className = 'card';
    card.innerHTML = `
        <span class="source-label">${sourceName}</span>
        <span class="count-label">${count} DATA POINTS</span>
    `;
    grid.appendChild(card);
}

// Initial initialization
document.addEventListener('DOMContentLoaded', updateDashboard);
