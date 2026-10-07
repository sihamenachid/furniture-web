import os

import requests
from flask import Flask, render_template, request

app = Flask(__name__)

# Address of the FastAPI API that contains the model.
# Locally: http://127.0.0.1:8080  -  On Heroku: set the API_URL config var.
API_URL = os.environ.get("API_URL", "http://127.0.0.1:8080")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():
    # 1. Read the form and build the JSON expected by the API
    try:
        features = {
            "category": int(request.form["category"]),
            "sellable_online": int(request.form["sellable_online"]),
            "other_colors": int(request.form["other_colors"]),
            "depth": float(request.form["depth"]),
            "height": float(request.form["height"]),
            "width": float(request.form["width"]),
        }
    except ValueError:
        return render_template("index.html", prediction_text="Please enter numbers for the dimensions.")

    # 2. Call the FastAPI API
    try:
        response = requests.post(f"{API_URL}/make_predictions", json=features, timeout=60)
    except requests.exceptions.RequestException:
        return render_template("index.html", prediction_text="The prediction API is not reachable.")

    # 3. Show the API's answer
    if response.status_code == 200:
        price = response.json()["predicted_price"]
        text = f"Furniture prediction price is : $ {price}"
    elif response.status_code == 422:
        errors = response.json()["detail"]
        text = "Invalid input. " + ", ".join(f"{e['loc'][-1]}: {e['msg']}" for e in errors)
    else:
        text = f"API error ({response.status_code})"
    return render_template("index.html", prediction_text=text)


if __name__ == "__main__":
    app.run(debug=True)
