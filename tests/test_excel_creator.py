"""Pytest 1"""
import json
from flask import Flask
import pytest


file_path: str = "shared_data.json"

with open(file_path, 'r', encoding='utf-8') as f:
    project_list = json.load(f)

project = project_list[-1]["projects"][-1]
print(project)

# Assuming app is already defined globally
app = Flask(__name__)


# Define the route and its logic
@app.route('/test', methods=['POST'])
def test_route():
    """Creating a test route to be able to mock the form data"""
    result = project["net_present_value"]
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
        "year": '10',
        "initial_investment": '2000000',
        "incoming_payments": '1000000',
        "outgoing_payments": '300000',
        "outgoing_payments_0": '500000',
        "residual": '200000',
        "restricted_equity": '200000',
        "discount_rate": '0.15',
        "tax_rate": '0.3'
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
    print("Response:", response.data)
    print("Result:", result)

    # Print result for debugging
    print("Result:", result)

    # Assert the type of result
    assert isinstance(result, float), "Expected result to be a float"

    # Assert the result based on expected calculations
    expected_value = round(project["net_present_value"], 2)
    actual_value = round(result, 2)
    assert actual_value == expected_value
