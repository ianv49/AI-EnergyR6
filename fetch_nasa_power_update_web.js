// This script is meant to be called from the browser (GUI.html) via fetchData()
// It will check if today's data exists in nasa-api.txt, and if not, trigger the Python fetch script via a backend endpoint.

async function fetchNasaPowerUpdate() {
    // 1. Check if today's data exists in nasa-api.txt (via backend endpoint)
    const today = new Date().toISOString().slice(0, 10);
    let hasToday = false;
    try {
        const resp = await fetch('http://127.0.0.1:5001/nasa-api-latest-date'); // Use full backend URL
        const data = await resp.json();
        if (data && data.latest_date && data.latest_date.startsWith(today)) {
            hasToday = true;
        }
    } catch (e) {
        alert('Could not check NASA API data: ' + e);
        return;
    }
    if (hasToday) {
        alert('NASA POWER API data for today already exists. No fetch needed.');
        return;
    }
    // 2. Trigger the backend to run fetch_nasa_power_update.py
    try {
        const resp = await fetch('http://127.0.0.1:5001/run-fetch-nasa-power', { method: 'POST' }); // Use full backend URL
        const result = await resp.json();
        alert(result.message || 'NASA POWER API fetch complete.');
    } catch (e) {
        alert('Failed to fetch new NASA POWER data: ' + e);
    }
}
