"""App konfiguration för att placera värden till variablar
"""
import json
import subprocess
from flask import Flask, request, render_template, redirect, url_for

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

        # Save the data to a JSON file
        with open('shared_data.json', 'w', encoding="utf-8") as f:
            json.dump(htmldata, f)

        # Run the other Python script using subprocess
        subprocess.run(
            ['python', 'excel_skapare_test.py'],
            capture_output=True,
            text=True,
            check=True
        )

    # Redirect to a success page or the same form with a success message
        return redirect(url_for('nettonuvarde'))
    except ValueError as e:
        # Handle invalid input
        return f"Invalid input: {e}"


@app.route("/nettonuvarde")
def nettonuvarde():
    """Nettonuvärde på investering"""
    with open('shared_data.json', 'r', encoding="utf-8") as f:
        data = json.load(f)
    return render_template("resultat.html", data=data)


if __name__ == '__main__':
    app.run(debug=True)
