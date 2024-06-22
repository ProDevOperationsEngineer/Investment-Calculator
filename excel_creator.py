"""This is the first attempt at creating something useful out of my studies,
we shall see how it goes...
"""
from typing import Union
import json
import os
import string
import subprocess
import xlsxwriter
from modules.invester import Invester


# Grundläggande skapandet av excel dokument och sida
excel_document = xlsxwriter.Workbook("InvestmentCalc.xlsx")
excel_sheet = excel_document.add_worksheet("Project 1")

if os.getenv('GITHUB_ACTIONS') == 'true':
    # GitHub Actions environment
    file_path: str = (
        "https://github.com/ProDevOperationsEngineer/"
        "Investmentcalculator/blob/main/shared_data.json"
    )
else:
    # Local environment
    file_path = "shared_data.json"

if os.path.getsize(file_path) > 0:
    with open(file_path, 'r', encoding='utf-8') as f:
        invester_dict = json.load(f)
else:
    print(f"Error: File '{file_path}' is empty.")

# Convert the dictionary back to an Invester instance
invester = Invester.from_dict(invester_dict)

# Check the number of existing projects
existing_projects = invester.list_projects()
num_projects = len(existing_projects)

# If there are existing projects, assign project to be the next one
if num_projects > 0:
    project = invester.get_project(num_projects - 1)
else:
    project = invester.get_project(num_projects)


# Dynamiska variablar
projekt_tid = project.År
skattesats = project.Skattesats
kalkylrantan = project.Kalkylräntan
inbet = project.Inbetalningar
utbet = project.Utbetalningar * -1
utbet_ar_noll = project.Utbetalningar_0 * -1
rest = project.Rest
grundinvestering = project.Grundinvestering * -1
avskrivningar = ((-grundinvestering) / projekt_tid) * skattesats
project.Avskrivningar = avskrivningar
rorelsebindandekapital = project.Rörelsebindandekapital * -1


# Skattepålägg funktion
def skatte_funktion(
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
    """Modifierar värderna på belopp som ska tas hänsyn till skatt och
    returerar de nya värderna som sedan manuellts blir
    tilldelade de gamla variablarna
    """
    inb *= (1-skatt)
    utb *= (1-skatt)
    utb_ar_noll *= (1-skatt)
    kalk *= (1-skatt)
    re *= (1-skatt)
    return inb, utb, utb_ar_noll, re, kalk


inbet, utbet, rest, utbet_ar_noll, kalkylrantan = skatte_funktion(
    inbet,
    utbet,
    rest,
    utbet_ar_noll,
    kalkylrantan,
    skattesats
)

# Icke-dynamiska variablar
alfabet: str = string.ascii_uppercase
count: int = 1
ar_noll_netto: int | float = (
    grundinvestering +
    utbet_ar_noll +
    rorelsebindandekapital
)
ack_mellan_nuvarde: int | float = ar_noll_netto

# Formatering
bold_format = excel_document.add_format({"bold": True})
italic_format = excel_document.add_format({"italic": True})
bold_centered__colored_format = excel_document.add_format({
    "bold": True,
    "align": "center"
    # "font_color": "white",
    # "bg_color": "azeal"
})
center_economic_format = excel_document.add_format({
    "align": "center",
    "num_format": "#,##0.000"
})
bold_centered_economic_format = excel_document.add_format({
    "bold": True,
    "align": "center",
    "num_format": "#,##0.00"
})
excel_sheet.set_column("A:A", 25)
excel_sheet.set_column("B:T", 15, center_economic_format)

# Grundläggande rubriker/kostnadsställen
excel_sheet.write("A1", "År", bold_format)
excel_sheet.write("A2", "Grundinvestering")
excel_sheet.write("A3", "Avskrivningar")
excel_sheet.write("A4", "Inbetalningar")
excel_sheet.write("A5", "Utbetalningar")
excel_sheet.write("A6", "Rest")
excel_sheet.write("A7", "Rörelsebindandekapital")
excel_sheet.write("A8", "Årligt netto")
excel_sheet.write("A9", "Nuvärde")
excel_sheet.write("A10", "Ackumelerat nuvärde")
excel_sheet.write("A11", "Nettonuvärde", bold_format)
excel_sheet.write("A13", "Nominell Kalkylräntan", italic_format)
excel_sheet.write("A14", "Kalkylräntan efter skatt", italic_format)
excel_sheet.write("A15", "Skattesats", italic_format)

# Skapar lika många kolummer som projektets estimerade livstid
for letter in alfabet[1:projekt_tid + 2]:
    ar_row_string: str = letter + "1"
    excel_sheet.write(ar_row_string, count - 1, bold_centered__colored_format)
    count += 1


# Grundinvestering utplacering
excel_sheet.write("B2", grundinvestering)

# Placerar ut värdet för avskrivningarna
for letter in alfabet[2:projekt_tid + 2]:
    avskriv_row_string: str = letter + "3"
    excel_sheet.write(avskriv_row_string, avskrivningar)

# Placerar ut värdet för inbetalningar
for letter in alfabet[2:projekt_tid + 2]:
    inbetal_row_string: str = letter + "4"
    excel_sheet.write(inbetal_row_string, inbet)

# Placerar ut värdet för utbetalningar
excel_sheet.write("B5", utbet_ar_noll)

for letter in alfabet[2:projekt_tid + 2]:
    utbetal_row_string: str = letter + "5"
    excel_sheet.write(utbetal_row_string, utbet)

# Placerar ut värdet för rest
rest_row: str = str(alfabet[projekt_tid + 1]) + "6"
excel_sheet.write(rest_row, rest)


# Placerar ut värdet för rörelsebindandekapital
rorelse_row: str = str(alfabet[projekt_tid + 1]) + "7"
excel_sheet.write("B7", rorelsebindandekapital)
excel_sheet.write(rorelse_row, -rorelsebindandekapital)

# Placerar ut värdet för årligt netto
excel_sheet.write("B8", ar_noll_netto, bold_centered_economic_format)

ar_mellan_netto: int | float = inbet + utbet + avskrivningar
for letter in alfabet[2:projekt_tid + 1]:
    mellan_netto_row: str = letter + "8"
    excel_sheet.write(
        mellan_netto_row, ar_mellan_netto, bold_centered_economic_format
    )

ar_sista_netto: int | float = (
    inbet +
    utbet +
    avskrivningar -
    rorelsebindandekapital +
    rest
)
ar_sista_netto_row: str = str(alfabet[projekt_tid + 1]) + "8"
excel_sheet.write(
    ar_sista_netto_row, ar_sista_netto, bold_centered_economic_format
)


# Placerar ut värdet för nuvärde
excel_sheet.write("B9", ar_noll_netto)

counter: int = 1
for letter in alfabet[2:projekt_tid + 1]:
    ar_mellan_nuvarde: int | float = (
        ar_mellan_netto / ((1 + kalkylrantan) ** counter)
    )
    counter += 1
    mellan_nuvarde_row: str = letter + "9"
    excel_sheet.write(
        mellan_nuvarde_row, ar_mellan_nuvarde)

ar_sista_nuvarde_row: str = str(alfabet[projekt_tid + 1]) + "9"
ar_sista_nuvarde: int | float = (
    ar_sista_netto / ((1 + kalkylrantan) ** (projekt_tid))
)
excel_sheet.write(ar_sista_nuvarde_row, ar_sista_nuvarde)

# Placerar ut värdet för ackumelerat nuvärde
excel_sheet.write("B10", ar_noll_netto)

counter_ett: int = 1
for letter in alfabet[2:projekt_tid + 1]:
    mellan_ack_nuvarde_row: str = letter + "10"
    ar_mellan_nuvarde = (
        ar_mellan_netto / ((1 + kalkylrantan) ** counter_ett)
    )
    counter_ett += 1
    ack_mellan_nuvarde += ar_mellan_nuvarde
    excel_sheet.write(mellan_ack_nuvarde_row, ack_mellan_nuvarde)

ar_sista_ack_nuvarde: int | float = ack_mellan_nuvarde + ar_sista_nuvarde
ar_sista_ack_nuvarde_row: str = str(alfabet[projekt_tid + 1]) + "10"
excel_sheet.write(ar_sista_ack_nuvarde_row, ar_sista_ack_nuvarde)

# Placerar ut värdet för nettonuvärde
excel_sheet.write("B11", ar_sista_ack_nuvarde, bold_centered_economic_format)

# Sparar datan till en JSON fil
project.ar_sista_ack_nuvarde = ar_sista_ack_nuvarde
project.Avskrivningar = avskrivningar

with open('shared_data.json', 'w', encoding='utf-8') as f:
    json.dump(invester.to_dict(), f, ensure_ascii=False, indent=4)

print("Data successfully saved to shared_data.json")

# Placerar ut värdet för nominella kalkylräntan
excel_sheet.write("B13", kalkylrantan / (1-skattesats))

# Placerar ut värdet för reala kalkylräntan
excel_sheet.write("B14", kalkylrantan)

# Placerar ut värdet för skattesats
excel_sheet.write("B15", skattesats)

# Korrigerar bakgrunden för positiva och negativa värden

excel_document.close()


def run_colorizer_script():
    """Function to run the correct path to the script for colorizing"""
    # Check if running in a GitHub environment
    if os.getenv('GITHUB_ACTIONS') == 'true':
        # GitHub Actions environment
        local_path = (
            "https://github.com/ProDevOperationsEngineer/"
            "Investmentcalculator/blob/main/excel_colorizer.py"
        )
    else:
        # Local environment
        local_path = "excel_colorizer.py"

    try:
        subprocess.run(
            ['python', local_path], capture_output=True, text=True, check=True
        )
    except subprocess.CalledProcessError as e:
        print("Error executing excel_colorizer.py:", e)


run_colorizer_script()
