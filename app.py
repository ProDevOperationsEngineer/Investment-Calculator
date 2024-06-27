"""App configuration
"""
import json
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
    load_from_csv
)

app = Flask(__name__)


@app.route("/")
def home():
    """Route to an introduction in
    investment calculation and basic info"""
    if os.path.isfile("user_database.csv") is True:
        investor = load_from_csv("user_database.csv")
        print(f"investor type: {type(investor)}")
        return render_template(
            "info.html",
            investor=investor)
    else:
        return render_template("info.html")


@app.route("/calculus")
def kalkyl():
    """Route to investment calculation form"""
    return render_template("index.html")


@app.route("/saveproject")
def save_project():
    """save current project to list of projects"""
    investor = load_shared_data()
    investor_user = {
        "username": investor["username"], "password": investor["password"]
    }
    investor_project_dict = investor["projects"][-1]
    del investor["projects"][-1]["accumulated_net_value_list"]
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
    t = np.arange(project["year"] + 1)
    fig, ax = plt.subplots(figsize=(15, 10), layout='constrained')
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
    ax.set_title("Accumulated Net Value of Investment by Year")
    ax.set_xlabel("Year")
    ax.set_ylabel("Accumulated Net Value")

    # Convert the plot to a PNG image and encode it to base64
    img = io.BytesIO()
    fig.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()

    # Calculate key assessment data
    count = 0
    for i in project["accumulated_net_value_list"]:
        count += 1
        print(i)
        if i > 0:
            break
    break_even = count - 1
    return render_template(
        "diagram.html",
        plot_url=plot_url,
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
            "year": int(request.form["year"]),
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
        investor = Investor(data["username"], data["password"])
        investor.add_project(htmldata)

        # Converts class instance into a dict
        investor_dict = investor.to_dict()

        # Save the data to a JSON file
        with open('shared_data.json', 'w', encoding='utf-8') as f:
            json.dump(investor_dict, f, ensure_ascii=False, indent=4)

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

        # Save the data to a JSON file
        with open('shared_data.json', 'w', encoding='utf-8') as f:
            json.dump(investor_dict, f, ensure_ascii=False, indent=4)

    except ValueError as e:
        # Handle invalid input
        return f"Invalid input: {e}"
    return redirect(url_for("home"))


@app.route("/netpresentvalue")
def netpresentvalue():
    """Net present value of investment"""
    project = load_last_shared_data()
    return render_template("result.html", data=project)


if __name__ == '__main__':
    app.run(debug=True)
