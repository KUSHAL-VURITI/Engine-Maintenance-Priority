import os
import pandas as pd
from flask import Flask, render_template, jsonify

app = Flask(__name__)
DATA_FILE = 'fleet.csv'

def load_fleet():
    """
    Load engine predictions from fleet.csv.
    Returns a DataFrame if the file exists and is not empty, otherwise None.
    """
    if not os.path.exists(DATA_FILE) or os.path.getsize(DATA_FILE) == 0:
        return None
    try:
        df = pd.read_csv(DATA_FILE)
        if df.empty:
            return None
        return df
    except Exception:
        return None

# Route: Dashboard web page displaying the engine priority table and summary cards
@app.route('/')
def home():
    fleet = load_fleet()
    if fleet is None:
        return render_template(
            'index.html',
            rows=[],
            critical=0,
            warning=0,
            healthy=0,
            error="Fleet data file ('fleet.csv') is missing or empty."
        ), 500

    counts = fleet['risk'].value_counts().to_dict()
    return render_template(
        'index.html',
        rows=fleet.to_dict('records'),
        critical=counts.get('Critical', 0),
        warning=counts.get('Warning', 0),
        healthy=counts.get('Healthy', 0),
        error=None
    )

# Route: REST API endpoint returning all engine predictions as JSON
@app.route('/api/fleet')
def api_fleet():
    fleet = load_fleet()
    if fleet is None:
        return jsonify({'error': "Fleet data file ('fleet.csv') is missing or empty."}), 500
    return jsonify(fleet.to_dict('records'))

if __name__ == '__main__':
    app.run(debug=True)