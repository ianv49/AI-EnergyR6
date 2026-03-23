// Matches the files seen in your repository screenshot
const collectFiles = [
    'collect1.txt', 'collect2.txt', 'collect3.txt', 
    'collect4.txt', 'collect5.txt', 'collect6.txt', 'collect7.txt'
];

async function refreshDashboard() {
    const grid = document.getElementById('summary-grid');
    const status = document.getElementById('status-bar');

    for (const fileName of collectFiles) {
        try {
            // Fetch with a timestamp to prevent browser caching
            const response = await fetch(`${fileName}?t=${Date.now()}`);
            if (!response.ok) throw new Error("Missing");

            const text = await response.text();
            const lines = text.trim().split('\n');
            
            // Extract the very last value (last line, last item if CSV)
            const lastEntry = lines[lines.length - 1];
            const displayValue = lastEntry.includes(',') ? lastEntry.split(',').pop() : lastEntry;

            renderCard(fileName, displayValue, lines.length);
        } catch (err) {
            renderCard(fileName, "OFFLINE", 0);
        }
    }
    status.innerText = `Last Updated: ${new Date().toLocaleTimeString()}`;
}

function renderCard(name, value, total) {
    const grid = document.getElementById('summary-grid');
    const id = `card-${name.replace('.', '-')}`;
    let card = document.getElementById(id);

    if (!card) {
        card = document.createElement('div');
        card.id = id;
        card.className = 'card';
        grid.appendChild(card);
    }

    // Clean up file name for display (e.g., collect2.txt -> SENSOR 2)
    const displayName = name === 'collect.txt' ? 'PRIMARY SENSOR' : `SENSOR ${name.match(/\d+/)}`;

    card.innerHTML = `
        <div class="card-label">${displayName}</div>
        <div class="card-value">${value}</div>
        <div class="card-meta">DATA POINTS: ${total}</div>
    `;
}

// Start immediately and auto-refresh every minute
document.addEventListener('DOMContentLoaded', refreshDashboard);
setInterval(refreshDashboard, 60000);
