"""App configuration
"""
import subprocess
import io
import os
import base64
import math
import matplotlib.pyplot as plt
import numpy as np
from flask import Flask, request, render_template, redirect, url_for
from modules.investor import Investor
from utils import (
    file_path_creator,
    load_shared_data,
    load_last_shared_data,
    save_to_csv_user,
    save_to_csv_project,
    save_to_csv_image,
    load_from_csv,
    load_from_csv_image,
    json_file_amender
)

app = Flask(__name__)


@app.route("/")
def home():
    """Route to an introduction in
    investment calculation and basic info"""
    if os.path.isfile("user_database.csv"):
        current_investor = load_last_shared_data()
        if not current_investor:
            return render_template("info.html")

        print("Current investor:", current_investor)

        if os.path.isfile("project_database.csv"):
            project = load_from_csv("project_database.csv")
            project_diagrams = load_from_csv_image("image_database.csv")
            if not project:
                return render_template(
                    "info.html",
                    current_investor=current_investor)

            list_of_projects = []
            list_of_npv = []
            for item in project:
                project_name = item["project_name"]
                net_present_value = round(float(item["net_present_value"]))
                net_present_value_str = f"{net_present_value:,.0f}"

                # Replace commas with spaces
                net_present_value_formatted = net_present_value_str.replace(
                    ",", " "
                )
                list_of_npv.append(net_present_value_formatted)
                list_of_projects.append(project_name)

            return render_template(
                "info.html",
                current_investor=current_investor,
                project_diagrams=project_diagrams,
                list_of_projects=list_of_projects,
                list_of_npv=list_of_npv
            )
        else:
            print("Project database file not found.")
            return render_template(
                "info.html",
                current_investor=current_investor
            )
    else:
        print("User database file not found.")
        return render_template("info.html")


@app.route("/calculus")
def kalkyl():
    """Route to investment calculation form"""
    user_dict = load_from_csv("user_database.csv")
    return render_template("index.html", user_dict=user_dict)


@app.route("/saveproject")
def save_project():
    """save current project to list of projects"""
    investor = load_shared_data()
    investor_user = {
        "username": investor["username"], "password": investor["password"]
    }
    del investor["projects"][-1]["accumulated_net_value_list"]
    investor_project_dict = investor["projects"][-1]
    save_to_csv_user(investor_user, "user_database.csv")
    save_to_csv_project(investor_project_dict, "project_database.csv")
    return redirect(url_for("home"))


@app.route("/account")
def account():
    """Page to create or log into account"""
    return render_template("account.html")


@app.route("/diagram")
def diagram():
    """Creating a diagram with the y-axel as
    accumulated net value and x-axel as number of years"""
    project = load_last_shared_data()
    # Diagram construction
    y_axel_list = project["accumulated_net_value_list"]
    t = np.arange(project["lifetime"] + 1)
    fig, ax = plt.subplots(figsize=(12, 8), layout='constrained')
    colors = ['green' if value >= 0 else '#B22222' for value in y_axel_list]
    bars = ax.bar(t, y_axel_list, color=colors)

    # Add the values on top of the bars
    for b, value in zip(bars, y_axel_list):
        height = b.get_height()
        rounded_value = math.floor(value)
        ax.annotate(f'{rounded_value}',
                    xy=(b.get_x() + b.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom')

    # Set x-axis ticks and labels
    ax.set_xticks(t)
    ax.set_xticklabels(t)
    ax.yaxis.set_ticks([])
    ax.set_title("Net Value of Investment by Year")
    ax.set_xlabel("Year")
    ax.set_ylabel("Accumulated Net Value")

    # Convert the plot to a PNG image and encode it to base64
    img = io.BytesIO()
    fig.savefig(img, format='png')
    img.seek(0)
    bar_plot_url = base64.b64encode(img.getvalue()).decode()

    # Diagram construction for line plot
    fig_line, ax_line = plt.subplots(figsize=(12, 9))
    ax_line.plot(t, y_axel_list, marker='o', linestyle='-', color='purple')

    # Set x-axis and y-axis labels for line plot
    ax_line.set_title("Net Value of Investment by Year")
    ax_line.set_xlabel("Year")
    ax_line.set_ylabel("Accumulated Net Value")

    # Set y-axis ticks to display only minimum and maximum values
    min_value = min(y_axel_list)
    max_value = max(y_axel_list)
    ax_line.yaxis.set_ticks([min_value, max_value])

    # Convert the line plot to a PNG image and encode it to base64
    img_line = io.BytesIO()
    fig_line.savefig(img_line, format='png')
    img_line.seek(0)
    line_plot_url = base64.b64encode(img_line.getvalue()).decode()

    # Calculate break-even point
    count = 0
    for i in project["accumulated_net_value_list"]:
        count += 1
        print(i)
        if i > 0:
            break
    break_even = count - 1
    project_name = str(project["project_name"])

    # Save byte64data image to CVS file
    byte64_dict = {project_name: line_plot_url}
    save_to_csv_image(byte64_dict, "image_database.csv")

    return render_template(
        "diagram.html",
        bar_plot_url=bar_plot_url,
        line_plot_url=line_plot_url,
        break_even=break_even,
        project=project
    )


@app.route("/submit", methods=["POST"])
def submit():
    """Submit form to collect investment data from the user"""
    data = load_shared_data()

    try:
        # Retrieve data from the form
        htmldata = {
            "project_name": str(request.form["project_name"]),
            "lifetime": int(request.form["lifetime"]),
            "initial_investment": float(request.form["investment"]),
            "incoming_payments": float(request.form["inflows"]),
            "outgoing_payments": float(request.form["outflows"]),
            "outgoing_payments_0": float(request.form["outflow_0"]),
            "residual": float(request.form["residual"]),
            "restricted_equity": float(request.form["work_cap"]),
            "discount_rate": float(request.form["discount_rate"]),
            "tax_rate": float(request.form["tax_rate"])
        }

        # Creates instance of invester class and saves submit values
        investor = Investor(data[-1]["username"], data[-1]["password"])
        investor.add_project(htmldata)

        # Converts class instance into a dict
        investor_dict = investor.to_dict()

        # Save the data to a JSON file
        json_file_amender("shared_data.json", investor_dict)

        local_path = file_path_creator()

        try:
            result = subprocess.run(
                ['python', local_path],
                capture_output=True,
                text=True,
                check=True
            )
            print("Output:", result.stdout)
        except subprocess.CalledProcessError as e:
            print("Error:", e)
            print("Output:", e.stdout)
            print("Error Output:", e.stderr)

    # Redirect to a success page or the same form with a success message
        return redirect(url_for("netpresentvalue"))
    except ValueError as e:
        # Handle invalid input
        return f"Invalid input: {e}"


@app.route("/submit/account", methods=["POST"])
def submit_account():
    """Submit form to collect invester data"""
    try:
        # Retrieve data from the form
        userdata = {
            "username": str(request.form["username"]),
            "password": str(request.form["password"]),
        }
        investor = Investor(userdata["username"], userdata["password"])

        # Converts class instance into a dict
        investor_dict = investor.to_dict()
        investor_user = {
            "username": investor_dict["username"],
            "password": investor_dict["password"]
        }
        save_to_csv_user(investor_user, "user_database.csv")

        json_file_amender("shared_data.json", investor_dict)

    except ValueError as e:
        # Handle invalid input
        return f"Invalid input: {e}"

    return redirect(url_for("home"))


@app.route("/submit/login", methods=["POST"])
def submit_login():
    """Submit form to check login credentials"""
    try:
        userdata = {
            "temp_user": str(request.form["temp_user"]),
            "temp_pswd": str(request.form["temp_pswd"])
        }
        investor = Investor(userdata["temp_user"], userdata["temp_pswd"])

    except ValueError as e:
        # Handle invalid input
        return f"Invalid input: {e}"

    if os.path.isfile("user_database.csv"):
        accounts = load_from_csv("user_database.csv")

        if any(
            user["username"] == userdata["temp_user"] and
            user["password"] == userdata["temp_pswd"]
            for user in accounts
        ):
            investor_dict = investor.to_dict()
            json_file_amender("shared_data.json", investor_dict)
            return redirect(url_for("home"))
        else:
            print("No account with that username or password can be found")
            print(investor)
            print(userdata["temp_user"])
    else:
        print("No accounts found")

    return redirect(url_for("account"))


@app.route("/netpresentvalue")
def netpresentvalue():
    """Net present value of investment"""
    project = load_last_shared_data()
    current_project = project["projects"][-1]
    print("Current project: ", current_project)
    return render_template("result.html", current_project=current_project)


if __name__ == '__main__':
    app.run(debug=True)
