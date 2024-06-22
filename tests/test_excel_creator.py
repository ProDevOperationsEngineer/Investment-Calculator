"""Pytest 1"""
import json
import os
from flask import Flask
import pytest

# Load shared data
if os.getenv('GITHUB_ACTIONS') == 'true':
    # GitHub Actions environment
    file_path = (
        "https://github.com/ProDevOperationsEngineer/"
        "Investmentcalculator/blob/main/shared_data.json"
    )
else:
    # Local environment
    file_path = "shared_data.json"

with open(file_path, 'r', encoding='utf-8') as f:
    project_list_dict = json.load(f)
    project = project_list_dict["projects"][-1]

# Assuming app is already defined globally
app = Flask(__name__)


# Define the route and its logic
@app.route('/test', methods=['POST'])
def test_route():
    """Creating a test route to be able to mock the form data"""
    result = project["ar_sista_ack_nuvarde"]
    return json.dumps(result)


# Global klient fixture
@pytest.fixture
def client():
    """A test client for the Flask app."""
    with app.test_client() as client:
        yield client


# Test funktion
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

    # Print result for debugging
    print("Result:", result)

    # Assert the type of result
    assert isinstance(result, float), "Expected result to be a float"

    # Assert the result based on expected calculations
    expected_value = 883397.62
    actual_value = round(result, 2)
    assert actual_value == expected_value
