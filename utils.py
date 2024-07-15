"""main functions to be utilized throughout
the project can be found here"""
import csv
import os
import json
import random
import string
import subprocess
from typing import Union


def generate_random_id(length=8):
    """Generate a random string of fixed length."""
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(random.choice(letters_and_digits) for i in range(length))


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
        print("Error: File is empty.")

    return invester_dict


def load_last_shared_data() -> dict:
    """Loads the last dictionary from shared data"""
    if os.path.getsize("shared_data.json") > 0:
        with open("shared_data.json", 'r', encoding='utf-8') as f:
            shared_data_list = json.load(f)
            print(shared_data_list)
    else:
        print("Error: File is empty.")
    return shared_data_list[-1]


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


def save_to_csv_user(data, filename, mode='a'):
    """Saves a dictionary to a CSV file, optionally in append mode"""

    fieldnames = ["username", "password"]

    file_exists = os.path.isfile(filename)

    with open(filename, mode, newline='', encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        # Only write the header if the file is new (write mode)
        if not file_exists:
            writer.writeheader()
        writer.writerow(data)


def save_to_csv_project(data, filename, mode='a'):
    """Saves a dictionary to a CSV file, optionally in append mode"""

    fieldnames = [
        "project_name", "lifetime", "initial_investment", "incoming_payments",
        "outgoing_payments", "outgoing_payments_0", "restricted_equity",
        "residual", "discount_rate", "tax_rate", "net_present_value",
        "depreciation",
    ]

    file_exists = os.path.isfile(filename)

    with open(filename, mode, newline='', encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        # Only write the header if the file is new (write mode)
        if not file_exists:
            writer.writeheader()
        writer.writerow(data)


def save_to_csv_image(data, csv_filename, mode="a"):
    """Saves image in byte64data to a CSV file"""
    file_exists = os.path.isfile(csv_filename)
    with open(csv_filename, mode, newline='', encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        if not file_exists:
            writer.writerow(['ImageName', 'Base64Data'])
        for image_name, base64_data in data.items():
            writer.writerow([image_name, base64_data])


def load_from_csv(filename) -> list:
    """Loads data from a CSV file and returns a list of dictionaries."""
    data_list = []
    with open(filename, mode="r", newline='', encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            data_list.append(row)
    return data_list


def load_from_csv_image(filename) -> list:
    """Loads byte64data image from a CSV file and returns a list."""
    data_list = []
    with open(filename, mode="r", newline="", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            data_list.append(row)
    return data_list


def json_file_amender(filename, investor_data) -> list:
    """Loads json file if it exist and amends it with new data"""
    # Check if the file exists
    if os.path.exists(filename):
        # Read existing data
        with open(filename, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                print(data)
            except json.JSONDecodeError:
                data = []  # If file is empty, initialize as an empty list
    else:
        data = []  # If file does not exist, initialize as an empty list

    # Add new data
    data.append(investor_data)

    # Write the updated data back to the JSON file
    with open("shared_data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    return data
