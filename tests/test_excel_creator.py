"""Pytest 1"""
import json
from flask import Flask
import pytest

# Load shared data
with open('shared_data.json', 'r', encoding="utf-8") as f:
    data = json.load(f)

# Assuming app is already defined globally
app = Flask(__name__)


# Define the route and its logic
@app.route('/test', methods=['POST'])
def test_route():
    # Perform calculations using request form data
    result = data["ar_sista_ack_nuvarde"]
    return json.dumps(result)


# Global client fixture
@pytest.fixture
def client():
    """A test client for the Flask app."""
    with app.test_client() as client:
        yield client


# Test function
def test_perform_calculations(client):
    """Testing the basic logic of the calculations"""
    # Mock the form data as it would be received in a request
    form_data = {
        "År": '10',
        "Grundinvestering": '2000000',
        "Inbetalningar": '1000000',
        "Utbetalningar": '300000',
        "Utbetalningar_0": '500000',
        "Rest": '200000',
        "Rörelsebindandekapital": '200000',
        "Kalkylräntan": '0.15',
        "Skattesats": '0.3'
    }

    # Simulate a POST request with form data
    response = client.post(
        '/test', data=form_data,
        content_type='application/x-www-form-urlencoded'
    )

    # Assert the response status code
    assert response.status_code == 200

    # Decode the JSON response
    result = json.loads(response.data.decode('utf-8'))

    # Assert the result based on expected calculations
    assert round(result["ar_sista_ack_nuvarde"], 2) == 883397.62
