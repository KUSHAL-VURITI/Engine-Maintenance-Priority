import os
import pytest
import pandas as pd
from app import app

DATA_FILE = 'fleet.csv'

@pytest.fixture
def client():
    """Create a Flask test client for making test requests."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_fleet_csv_structure():
    """Check that fleet.csv exists, has 100 rows, and correct columns."""
    assert os.path.exists(DATA_FILE), "fleet.csv file does not exist"
    df = pd.read_csv(DATA_FILE)
    assert len(df) == 100, f"Expected 100 engines, found {len(df)}"
    expected_columns = ['engine', 'predicted_rul', 'risk']
    assert list(df.columns) == expected_columns, f"Columns must be {expected_columns}"

def test_fleet_risk_labels():
    """Verify risk labels match the defined cut-off thresholds."""
    df = pd.read_csv(DATA_FILE)
    for _, row in df.iterrows():
        rul = row['predicted_rul']
        risk = row['risk']
        if rul <= 40:
            assert risk == 'Critical', f"Engine {row['engine']} RUL={rul} should be Critical, got {risk}"
        elif rul <= 80:
            assert risk == 'Warning', f"Engine {row['engine']} RUL={rul} should be Warning, got {risk}"
        else:
            assert risk == 'Healthy', f"Engine {row['engine']} RUL={rul} should be Healthy, got {risk}"

def test_no_duplicate_engines():
    """Ensure all engine IDs in fleet.csv are unique."""
    df = pd.read_csv(DATA_FILE)
    assert df['engine'].nunique() == len(df), "Engine IDs contain duplicates"

def test_home_route_status_200(client):
    """Test that the '/' route returns HTTP 200 status code."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"Engine Maintenance Priority List" in response.data

def test_api_fleet_returns_100_records(client):
    """Test that '/api/fleet' returns HTTP 200 and a list of 100 engine records."""
    response = client.get('/api/fleet')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list), "API response should be a JSON list"
    assert len(data) == 100, f"Expected 100 records in API response, got {len(data)}"
