"""Main functions to be utilized throughout
the project can be found here."""
import csv
import os
import json
import random
import string
from typing import Union
import openpyxl
from openpyxl.styles import PatternFill


def colorizer():
    """Simple function to help distinguish negative values from
    positive in the excel document."""
    # Load the workbook and select the active worksheet
    wb = openpyxl.load_workbook("investment_portfolio.xlsx")
    ws = wb.active

    # Define the colors for positive and negative values
    green_fill = PatternFill(
        start_color='FF00FF00', end_color='FF00FF00', fill_type='solid'
    )
    red_fill = PatternFill(
        start_color='FFFF0000', end_color='FFFF0000', fill_type='solid'
        )

    # Iterate through each row and column in the worksheet
    for row in ws.iter_rows(
        min_row=2, max_row=ws.max_row, min_col=1, max_col=ws.max_column
    ):
        for cell in row:
            if isinstance(cell.value, (int, float)):
                if cell.value > 0:
                    cell.fill = green_fill
                elif cell.value < 0:
                    cell.fill = red_fill

    # Save the workbook with changes
    wb.save("investment_portfolio.xlsx")


def file_path_creator() -> str:
    """handles the conditions for githubs testing environment,
    filepath creator."""
    if os.getenv('GITHUB_ACTIONS') == 'true':
        # GitHub Actions environment
        local_path = (
            "https://github.com/ProDevOperationsEngineer/"
            "Investmentcalculator/blob/main/calculator.py"
        )
    else:
        # Local environment
        local_path = "calculator.py"
    return local_path


def generate_random_id(length=8):
    """Generate a random string of fixed length."""
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(random.choice(letters_and_digits) for i in range(length))


def get_last_user(data: list, username: str) -> dict | None:
    """Returns the last user entry in the list that matches the username."""
    for entry in reversed(data):  # go from the end backwards
        if entry.get("username") == username:
            return entry
    return None  # if no match found


def json_file_amender(filename, investor_data) -> list:
    """Amends JSON file by overwriting projects with the same name."""

    # Load or init
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
    else:
        data = []

    if data:
        latest_entry = data[-1]

        if latest_entry.get("username") == investor_data.get("username"):
            existing_projects = latest_entry["projects"]
            new_projects = investor_data["projects"]

            for new_project in new_projects:
                # Remove any existing project with the same name
                existing_projects[:] = [
                    p for p in existing_projects
                    if p.get("project_name") != new_project.get("project_name")
                ]
                # Add the new version
                existing_projects.append(new_project)
        else:
            data.append(investor_data)
    else:
        data.append(investor_data)

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    return data


def load_from_csv(filename) -> list:
    """Loads data from a CSV file and returns a list of dictionaries."""
    data_list = []
    with open(filename, mode="r", newline='', encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            data_list.append(row)
    return data_list


def load_from_csv_image(filename) -> list:
    """Loads image data from a CSV file and returns a list of dictionaries."""
    data_list = []
    with open(filename, mode="r", newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            data_list.append(row)
    return data_list


def load_last_shared_data() -> dict:
    """Loads the last dictionary from shared data,
    creating the file if it doesn't exist."""
    file_path = "shared_data.json"

    # Create the file if it doesn't exist
    if not os.path.exists(file_path):
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump({}, f)

    # Check if the file is non-empty
    if os.path.getsize(file_path) > 0:
        with open(file_path, 'r', encoding='utf-8') as f:
            shared_data_list = json.load(f)
            if shared_data_list:
                return shared_data_list[-1]
            else:
                print("Warning: File contains an empty list.")
    else:
        print("Warning: File is empty.")

    return {}  # Return an empty dict if no valid data is found


def load_shared_data() -> list:
    """Loads the dictionary from shared data,
    creating the file if it doesn't exist."""
    file_path = "shared_data.json"

    if not os.path.exists(file_path):
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump([], f)

    if os.path.getsize(file_path) == 0:
        return []

    with open(file_path, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
            if isinstance(data, list):
                return data
            else:
                print("Warning: shared_data.json is not a list.")
                return []
        except json.JSONDecodeError:
            print("Warning: shared_data.json is corrupted.")
            return []


def save_to_csv_image(data, csv_filename, mode="a"):
    """Saves image in byte64data to a CSV file"""
    file_exists = os.path.isfile(csv_filename)

    if file_exists:
        project_list = load_from_csv(csv_filename)
        project_exist = 0
        for projects in project_list:
            if projects["project_name"] == data["project_name"]:
                project_exist = 1
        if project_exist == 0:
            with open(
                csv_filename, mode, newline='', encoding="utf-8"
            ) as csv_file:
                writer = csv.writer(csv_file)
                if not file_exists:
                    writer.writerow(
                        ["username", "project_name", "Base64Data"]
                    )
                writer.writerow(data.values())
    else:
        with open(
            csv_filename, mode, newline='', encoding="utf-8"
        ) as csv_file:
            writer = csv.writer(csv_file)
            if not file_exists:
                writer.writerow(["username", "project_name", "Base64Data"])
            writer.writerow(data.values())


def save_to_csv_project(data, filename):
    """Saves or updates a project in a CSV file."""
    fieldnames = [
        "username", "project_name", "lifetime", "initial_investment",
        "incoming_payments", "outgoing_payments", "outgoing_payments_0",
        "restricted_equity", "residual", "discount_rate", "tax_rate",
        "net_present_value", "depreciation",
    ]

    data = {key: data.get(key, "") for key in fieldnames}

    project_list = []
    updated = False

    if os.path.isfile(filename):
        with open(filename, mode="r", newline='', encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row["project_name"] == data["project_name"]:
                    project_list.append(data)
                    updated = True
                else:
                    project_list.append(row)
    else:
        project_list = [data]
        updated = True

    if not updated:
        project_list.append(data)

    with open(filename, mode="w", newline='', encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(project_list)


def save_to_csv_user(data, filename, mode='a'):
    """Saves a dictionary to a CSV file, optionally in append mode"""

    fieldnames = ["username", "password"]

    file_exists = os.path.isfile(filename)

    if file_exists:
        project_list = load_from_csv(filename)
        user_exist = 0
        for projects in project_list:
            if projects["username"] == data["username"]:
                user_exist = 1
        if user_exist == 0:
            with open(
                filename, mode, newline='', encoding="utf-8"
            ) as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writerow(data)
    else:
        with open(
            filename, mode, newline='', encoding="utf-8"
        ) as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow(data)


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
