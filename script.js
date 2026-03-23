// Updated list to use collect1.txt instead of collect.txt
const apiFiles = [
    'collect1.txt', 'collect2.txt', 'collect3.txt', 
    'collect4.txt', 'collect5.txt', 'collect6.txt', 'collect7.txt'
];

async function runRegistryScan() {
    const grid = document.getElementById('source-grid');
    const status = document.getElementById('status-text');
    grid.innerHTML = ''; // Clear existing cards

    for (const fileName of apiFiles) {
        try {
            const response = await fetch(`${fileName}?v=${Date.now()}`);
            if (!response.ok) continue;

            const content = await response.text();
            const lines = content.trim().split('\n');
            
            // Look for 'source' in the first 3 lines
            let apiName = "UNKNOWN API";
            for (let i = 0; i < Math.min(3, lines.length); i++) {
                const currentLine = lines[i].toLowerCase();
                if (currentLine.includes('source')) {
                    // Extract value after : or =
                    const segments = lines[i].split(/[:=]/);
                    if (segments.length > 1) {
                        apiName = segments[1].split(',')[0].trim().toUpperCase();
                        break;
                    }
                }
            }

            createApiCard(apiName, lines.length);
        } catch (err) {
            console.error(`Could not read ${fileName}`);
        }
    }
    status.innerText = `SYNCED: ${new Date().toLocaleTimeString()}`;
}

function createApiCard(name, count) {
    const grid = document.getElementById('source-grid');
    const card = document.createElement('div');
    card.className = 'api-card';
    card.innerHTML = `
        <span class="api-title">${name}</span>
        <span class="row-count">${count} TOTAL RECORDS</span>
    `;
    grid.appendChild(card);
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', runRegistryScan);
