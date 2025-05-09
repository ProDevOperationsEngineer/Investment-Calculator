"""Main functionality of the calculator. Outputs the data to excel files"""
import os
import xlsxwriter
from modules.investor import Investor
from utils import (
    load_last_shared_data,
    taxes,
    json_file_amender,
    calculator,
    excel_merger,
    save_to_csv_excel
)


# Loads the dictionary from shared data
investor_dict = load_last_shared_data()
# investor_dict['projects'][-1].pop('break_even', None)
EXCEL_PORTFOLIO_NAME = f"{investor_dict['username']} Portfolio.xlsx"
EXCEL_PROJ = f"{investor_dict['projects'][-1]['project_name']}"

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


# Apply taxes
inbet, utbet, rest, utbet_ar_noll, kalkylrantan = taxes(
    inbet, utbet, rest, utbet_ar_noll, kalkylrantan, skattesats
)

if os.path.exists(EXCEL_PORTFOLIO_NAME):
    ar_sista_ack_nuvarde, acc_list, avskrivningar = excel_merger(
        EXCEL_PORTFOLIO_NAME,
        EXCEL_PROJ,
        lambda wb, ws: calculator(
            wb, ws,
            projekt_tid,
            kalkylrantan,
            skattesats,
            grundinvestering,
            utbet_ar_noll,
            rorelsebindandekapital,
            avskrivningar,
            inbet,
            utbet,
            rest,
            acc_list
        )
    )
else:
    excel_document = xlsxwriter.Workbook(EXCEL_PORTFOLIO_NAME)
    excel_sheet = excel_document.add_worksheet(EXCEL_PROJ)
    ar_sista_ack_nuvarde, acc_list, avskrivningar = calculator(
        excel_document,
        excel_sheet,
        projekt_tid,
        kalkylrantan,
        skattesats,
        grundinvestering,
        utbet_ar_noll,
        rorelsebindandekapital,
        avskrivningar,
        inbet,
        utbet,
        rest,
        acc_list
    )
    excel_document.close()
    save_to_csv_excel(
        EXCEL_PORTFOLIO_NAME,
        EXCEL_PROJ,
        "portfolio_database.csv",
        username=investor_dict["username"]
    )


# Update project with calculated results
project.net_present_value = ar_sista_ack_nuvarde
project.depreciation = avskrivningar
project.accumulated_net_value_list = acc_list


# Save updated investor data to JSON
investor_projects_dict = investor.to_dict()
investor_last_project = investor_projects_dict['projects'][-1]
investor.add_project(investor_last_project)

json_file_amender("shared_data.json", investor.to_dict())
