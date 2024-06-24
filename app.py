"""App configuration
"""
import json
import os
import subprocess
import io
import base64
import math
import matplotlib.pyplot as plt
import numpy as np
from flask import Flask, request, render_template, redirect, url_for
from modules.invester import Invester

app = Flask(__name__)


@app.route("/")
def home():
    """Route to  an introduction in
    investment calculation and basic info"""
    return render_template("info.html")


@app.route("/calculus")
def kalkyl():
    """Route to investment calculation form"""
    return render_template("index.html")


@app.route("/diagram")
def diagram():
    """Creating a diagram with the y-axel as
    accumulated net value and x-axel as number of years"""
    if os.getenv("GITHUB_ACTIONS") == "true":
        # GitHub Actions environment
        file_path = (
            "https://github.com/ProDevOperationsEngineer/"
            "Investmentcalculator/blob/main/shared_data.json"
        )
    else:
        # Local environment
        file_path = "shared_data.json"

    if os.path.getsize(file_path) > 0:
        with open(file_path, 'r', encoding='utf-8') as f:
            project_list_dict = json.load(f)
            project = project_list_dict["projects"][-1]
    else:
        print("Error: File shared_data.json is empty.")

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

    return render_template("diagram.html", plot_url=plot_url)


@app.route("/submit", methods=["POST"])
def submit():
    """Submit form to collect data from the user"""
    try:
        # Retrieve data from the form
        htmldata = {
            "year": int(request.form['year']),
            "initial_investment": float(request.form['investment']),
            "incoming_payments": float(request.form['inflows']),
            "outgoing_payments": float(request.form['outflows']),
            "outgoing_payments_0": float(request.form['outflow_0']),
            "residual": float(request.form['residual']),
            "restricted_equity": float(request.form['work_cap']),
            "discount_rate": float(request.form['discount_rate']),
            "tax_rate": float(request.form['tax_rate'])
        }

        # Creates instance of invester class and saves submit values
        invester = Invester()
        invester.add_project(htmldata)

        # Converts class instance into a dict
        invester_dict = invester.to_dict()

        # Save the data to a JSON file
        with open('shared_data.json', 'w', encoding='utf-8') as f:
            json.dump(invester_dict, f, ensure_ascii=False, indent=4)

        # Run the other Python script using subprocess
        if os.getenv('GITHUB_ACTIONS') == 'true':
            # GitHub Actions environment
            local_path = (
                "https://github.com/ProDevOperationsEngineer/"
                "Investmentcalculator/blob/main/excel_creator.py"
            )
        else:
            # Local environment
            local_path = "excel_creator.py"

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


@app.route("/netpresentvalue")
def netpresentvalue():
    """Net present value of investment"""
    if os.getenv('GITHUB_ACTIONS') == 'true':
        # GitHub Actions environment
        file_path = (
            "https://github.com/ProDevOperationsEngineer/"
            "Investmentcalculator/blob/main/shared_data.json"
        )
    else:
        # Local environment
        file_path = "shared_data.json"

    if os.path.getsize(file_path) > 0:
        with open(file_path, 'r', encoding='utf-8') as f:
            project_list_dict = json.load(f)
            project = project_list_dict["projects"][-1]
    else:
        print("Error: File shared_data.json is empty.")

    with open("shared_data.json", 'r', encoding='utf-8') as f:
        data = json.load(f)
        print(json.dumps(data, indent=4, ensure_ascii=False))

    return render_template("result.html", data=project)


if __name__ == '__main__':
    app.run(debug=True)
