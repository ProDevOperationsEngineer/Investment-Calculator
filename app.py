"""App konfiguration för att placera värden till variablar
"""
import json
import os
import subprocess
from flask import Flask, request, render_template, redirect, url_for
from modules.invester import Invester

app = Flask(__name__)


@app.route('/')
def home():
    """Introduktion till investeringskalkylering och grundläggande info"""
    return render_template('info.html')


@app.route("/kalkyl")
def kalkyl():
    """Investeringskalkyl formulär"""
    return render_template("index.html")


@app.route('/submit', methods=['POST'])
def submit():
    """Submit formulär för att inhämta data från användaren"""
    try:
        # Retrieve data from the form
        htmldata = {
            "År": int(request.form['year']),
            "Grundinvestering": float(request.form['investment']),
            "Inbetalningar": float(request.form['inflows']),
            "Utbetalningar": float(request.form['outflows']),
            "Utbetalningar_0": float(request.form['outflow_0']),
            "Rest": float(request.form['residual']),
            "Rörelsebindandekapital": float(request.form['work_cap']),
            "Kalkylräntan": float(request.form['discount_rate']),
            "Skattesats": float(request.form['tax_rate'])
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
        return redirect(url_for('nettonuvarde'))
    except ValueError as e:
        # Handle invalid input
        return f"Invalid input: {e}"


@app.route("/nettonuvarde")
def nettonuvarde():
    """Nettonuvärde på investering"""
    if os.path.getsize("shared_data.json") > 0:
        with open("shared_data.json", 'r', encoding='utf-8') as f:
            project_list_dict = json.load(f)
            project = project_list_dict["projects"][-1]
    else:
        print("Error: File shared_data.json is empty.")

    with open("shared_data.json", 'r', encoding='utf-8') as f:
        data = json.load(f)
        print(json.dumps(data, indent=4, ensure_ascii=False))

    return render_template("resultat.html", data=project)


if __name__ == '__main__':
    app.run(debug=True)
