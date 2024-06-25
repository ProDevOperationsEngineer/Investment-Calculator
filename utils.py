"""main functions to be utilized throughout
the project can be found here"""
import csv
import os
import json
import subprocess
from typing import Union


def file_path_colorizer() -> str:
    """handles the conditions for githubs testing environment,
    filepath colorizer"""
    if os.getenv("GITHUB_ACTIONS") == "true":
        # GitHub Actions environment
        local_path = (
            "https://github.com/ProDevOperationsEngineer/"
            "Investmentcalculator/blob/main/excel_colorizer.py"
        )
    else:
        # Local environment
        local_path = "excel_colorizer.py"
    return local_path


def file_path_creator() -> str:
    """handles the conditions for githubs testing environment,
    filepath creator"""
    if os.getenv('GITHUB_ACTIONS') == 'true':
        # GitHub Actions environment
        local_path = (
            "https://github.com/ProDevOperationsEngineer/"
            "Investmentcalculator/blob/main/excel_creator.py"
        )
    else:
        # Local environment
        local_path = "excel_creator.py"
    return local_path


def run_colorizer_script():
    """Function to run the script for colorizing the excel sheet"""

    local_path = file_path_colorizer()

    try:
        subprocess.run(
            ['python', local_path], capture_output=True, text=True, check=True
        )
    except subprocess.CalledProcessError as e:
        print("Error executing excel_colorizer.py:", e)


def load_shared_data() -> dict:
    """Loads the dictionary from shared data"""

    if os.path.getsize("shared_data.json") > 0:
        with open("shared_data.json", 'r', encoding='utf-8') as f:
            invester_dict = json.load(f)
    else:
        print(f"Error: File '{"shared_data.json"}' is empty.")

    return invester_dict


def load_last_shared_data() -> dict:
    """Loads the last dictionary from shared data"""
    if os.path.getsize("shared_data.json") > 0:
        with open("shared_data.json", 'r', encoding='utf-8') as f:
            project_list_dict = json.load(f)
    else:
        print("Error: File shared_data.json is empty.")
    return project_list_dict["projects"][-1]


def taxes(
    inb: Union[int, float],
    utb: Union[int, float],
    utb_ar_noll: Union[int, float],
    re: Union[int, float],
    kalk: Union[int, float],
    skatt: Union[int, float]
) -> tuple[
    Union[int, float],
    Union[int, float],
    Union[int, float],
    Union[int, float],
    Union[int, float],
]:
    """Modifying the values to be accounting for taxes and
    returns the new values to be assigned to the old variables
    """
    inb *= (1-skatt)
    utb *= (1-skatt)
    utb_ar_noll *= (1-skatt)
    kalk *= (1-skatt)
    re *= (1-skatt)
    return inb, utb, utb_ar_noll, re, kalk


def save_to_csv(data, filename, mode='a'):
    """Saves a dictionary to a CSV file, optionally in append mode"""
    # Ensure data is a dictionary
    if not isinstance(data, dict):
        raise ValueError("data must be a dictionary")
    print("Data to be written to CSV:", data)
    # Extract and serialize projects list
    projects = data.pop('projects', None)
    if projects is not None:
        data['projects'] = json.dumps(projects)

    fieldnames = [
        "username", "password", "projects", "name", "description",
        "restricted_equity", "residual", "discount_rate",
        "net_present_value", "incoming_payments", "outgoing_payments_0",
        "initial_investment", "outgoing_payments", "tax_rate",
        "depreciation", "accumulated_net_value_list", "year"
    ]
    print("Data to be written to CSV:", data)

    with open(filename, mode, newline='', encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        # Only write the header if the file is new (write mode)
        if mode == 'w':
            writer.writeheader()
        writer.writerow(data)
