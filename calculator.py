"""Main functionality of the calculator. Outputs the data to excel files"""
import string
import xlsxwriter
from modules.investor import Investor
from utils import (
    colorizer,
    load_last_shared_data,
    taxes,
    json_file_amender
)


# Creation of excel document and sheet
excel_document = xlsxwriter.Workbook("investment_portfolio.xlsx")
excel_sheet = excel_document.add_worksheet("Project 1")


# Loads the dictionary from shared data
investor_dict = load_last_shared_data()

# Convert the dictionary back to an Invester instance
investor = Investor.from_dict(investor_dict)

# Check the number of existing projects
existing_projects = investor.list_projects()
num_projects = len(existing_projects)


# If there are existing projects, assign project to be the next one
if num_projects > 0:
    project = investor.get_project(num_projects - 1)
else:
    project = investor.get_project(num_projects)


# Dynamic variables
projekt_tid = project.lifetime
skattesats = project.tax_rate
kalkylrantan = project.discount_rate
inbet = project.incoming_payments
utbet = project.outgoing_payments * -1
utbet_ar_noll = project.outgoing_payments_0 * -1
rest = project.residual
grundinvestering = project.initial_investment * -1
avskrivningar = ((-grundinvestering) / projekt_tid) * skattesats
rorelsebindandekapital = project.restricted_equity * -1
acc_list = project.accumulated_net_value_list


# Applies taxes to correct variables
inbet, utbet, rest, utbet_ar_noll, kalkylrantan = taxes(
    inbet,
    utbet,
    rest,
    utbet_ar_noll,
    kalkylrantan,
    skattesats
)

# Static variables (after taxes)
alfabet: str = string.ascii_uppercase
count: int = 1
ar_noll_netto: int | float = (
    grundinvestering +
    utbet_ar_noll +
    rorelsebindandekapital
)
ack_mellan_nuvarde: int | float = ar_noll_netto

# Designing excel document
bold_format = excel_document.add_format({"bold": True})
italic_format = excel_document.add_format({"italic": True})
bold_centered__colored_format = excel_document.add_format({
    "bold": True,
    "align": "center"
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

# Headlines for all relevant data
excel_sheet.write("A1", "Project lifetime", bold_format)
excel_sheet.write("A2", "Initial Investment")
excel_sheet.write("A3", "Depreciation")
excel_sheet.write("A4", "Incoming Payments")
excel_sheet.write("A5", "Outgoing Payments")
excel_sheet.write("A6", "Residual")
excel_sheet.write("A7", "Restricted Equity")
excel_sheet.write("A8", "Yearly Net")
excel_sheet.write("A9", "Present Value")
excel_sheet.write("A10", "Accumulated Present Value")
excel_sheet.write("A11", "Net Present Value", bold_format)
excel_sheet.write("A13", "Nominal Discount Rate", italic_format)
excel_sheet.write("A14", "Discount Rate After TaX", italic_format)
excel_sheet.write("A15", "Tax Rate", italic_format)

# Creates as many columns as the estimated lifetime of the project
for letter in alfabet[1:projekt_tid + 2]:
    ar_row_string: str = letter + "1"
    excel_sheet.write(ar_row_string, count - 1, bold_centered__colored_format)
    count += 1


# Initial investment deployment
excel_sheet.write("B2", grundinvestering)

# Places the value of the depreciation
for letter in alfabet[2:projekt_tid + 2]:
    avskriv_row_string: str = letter + "3"
    excel_sheet.write(avskriv_row_string, avskrivningar)

# Places the value for incoming payments
for letter in alfabet[2:projekt_tid + 2]:
    inbetal_row_string: str = letter + "4"
    excel_sheet.write(inbetal_row_string, inbet)

# Places the value for outgoing payments
excel_sheet.write("B5", utbet_ar_noll)

for letter in alfabet[2:projekt_tid + 2]:
    utbetal_row_string: str = letter + "5"
    excel_sheet.write(utbetal_row_string, utbet)

# Places the value for residual
rest_row: str = str(alfabet[projekt_tid + 1]) + "6"
excel_sheet.write(rest_row, rest)


# Places the value for restricted equity
rorelse_row: str = str(alfabet[projekt_tid + 1]) + "7"
excel_sheet.write("B7", rorelsebindandekapital)
excel_sheet.write(rorelse_row, -rorelsebindandekapital)

# Places the value for yearly net
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


# Places the value for present value
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

# Places the value for accumulated present value
excel_sheet.write("B10", ar_noll_netto)
acc_list.append(ar_noll_netto)

counter_ett: int = 1
for letter in alfabet[2:projekt_tid + 1]:
    mellan_ack_nuvarde_row: str = letter + "10"
    ar_mellan_nuvarde = (
        ar_mellan_netto / ((1 + kalkylrantan) ** counter_ett)
    )
    counter_ett += 1
    ack_mellan_nuvarde += ar_mellan_nuvarde
    acc_list.append(ack_mellan_nuvarde)
    excel_sheet.write(mellan_ack_nuvarde_row, ack_mellan_nuvarde)

ar_sista_ack_nuvarde: int | float = ack_mellan_nuvarde + ar_sista_nuvarde
acc_list.append(ar_sista_ack_nuvarde)
ar_sista_ack_nuvarde_row: str = str(alfabet[projekt_tid + 1]) + "10"
excel_sheet.write(ar_sista_ack_nuvarde_row, ar_sista_ack_nuvarde)

# Places the value for net present value
excel_sheet.write("B11", ar_sista_ack_nuvarde, bold_centered_economic_format)

# Saves data to json file
project.net_present_value = ar_sista_ack_nuvarde
project.depreciation = avskrivningar
project.accumulated_net_value_list = acc_list

json_file_amender("shared_data.json", investor.to_dict())

# Places the value for nominell discount rate
excel_sheet.write("B13", kalkylrantan / (1-skattesats))

# Places the value for real discount rate
excel_sheet.write("B14", kalkylrantan)

# Places the value for tax rate
excel_sheet.write("B15", skattesats)

# Corrects the background for positive and negative values
excel_document.close()
colorizer()
