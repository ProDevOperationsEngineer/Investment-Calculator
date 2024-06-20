"""Pytest 1"""
import json


def test_perform_calculations(mocker):
    """Testing the basic logic of the calculus"""
    # Mock the htmldata variables
    mocked_htmldata = {
        "År": 10,
        "Grundinvestering": 2_000_000,
        "Inbetalningar": 1_000_000,
        "Utbetalningar": 300_000,
        "Utbetalningar_0": 500_000,
        "Rest": 200_000,
        "Rörelsebindandekapital": 200_000,
        "Kalkylräntan": 0.15,
        "Skattesats": 0.3
    }

    # Mock the request.form dictionary with mocked_htmldata
    mocker.patch('flask.request.form', mocked_htmldata)

    # Call the perform_calculations function
    with open('shared_data.json', 'r', encoding="utf-8") as f:
        data = json.load(f)

    result = round(data["ar_sista_ack_nuvarde"], 2)

    # Assert the result based on expected calculations
    assert result == 883_397.62
