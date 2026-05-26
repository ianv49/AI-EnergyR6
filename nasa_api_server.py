from flask import Flask, jsonify, request
import subprocess
import os

app = Flask(__name__)

NASA_API_TXT = os.path.join('data', 'nasa-api.txt')
FETCH_SCRIPT = 'fetch_nasa_power_update.py'

@app.route('/nasa-api-latest-date', methods=['GET'])
def nasa_api_latest_date():
    latest_date = None
    try:
        with open(NASA_API_TXT, 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#') and not line.startswith('['):
                    parts = line.strip().split(',')
                    if len(parts) > 1:
                        latest_date = parts[1]
                        break
        # The file is in reverse order (latest at top), so we need the first data row
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    return jsonify({'latest_date': latest_date})

@app.route('/run-fetch-nasa-power', methods=['POST'])
def run_fetch_nasa_power():
    try:
        result = subprocess.run(['python', FETCH_SCRIPT], capture_output=True, text=True, timeout=120)
        if result.returncode == 0:
            return jsonify({'message': result.stdout.strip()})
        else:
            return jsonify({'error': result.stderr.strip()}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=5001, debug=True)
