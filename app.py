from flask import Flask, render_template, request, redirect, session
from datetime import datetime
import json
import os

app = Flask(__name__)
app.secret_key = "fretefacil"

HISTORY_FILE = "history.json"


def get_region(cep):
    prefix = int(cep[:2])

    if 1 <= prefix <= 28:
        return "Sudeste"
    elif 29 <= prefix <= 39:
        return "Nordeste"
    elif 40 <= prefix <= 49:
        return "Bahia"
    elif 50 <= prefix <= 65:
        return "Nordeste Interior"
    elif 66 <= prefix <= 68:
        return "Norte"
    elif 69 <= prefix <= 79:
        return "Centro-Oeste"
    elif 80 <= prefix <= 99:
        return "Sul"

    return "Desconhecida"


def calculate_shipping(data):

    weight = float(data["weight"])
    height = float(data["height"])
    width = float(data["width"])
    length = float(data["length"])

    cubed_weight = (height * width * length) / 6000
    final_weight = max(weight, cubed_weight)

    origin_region = get_region(data["origin_cep"])
    destination_region = get_region(data["destination_cep"])

    base_price = 18

    if origin_region != destination_region:
        base_price += 12

    shipping_price = base_price + (final_weight * 4.5)

    delivery_days = 3 if data.get("express") else 7

    if data.get("express"):
        shipping_price *= 1.4

    return {
        "price": round(shipping_price, 2),
        "delivery_days": delivery_days,
        "cubed_weight": round(cubed_weight, 2),
        "final_weight": round(final_weight, 2),
        "origin_region": origin_region,
        "destination_region": destination_region,
    }


def load_history():

    if not os.path.exists(HISTORY_FILE):
        return []

    with open(HISTORY_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def save_history(item):

    history = load_history()

    history.insert(0, item)

    with open(HISTORY_FILE, "w", encoding="utf-8") as file:
        json.dump(history[:10], file, ensure_ascii=False, indent=2)


@app.route("/", methods=["GET", "POST"])
def index():

    result = session.pop("result", None)

    if request.method == "POST":

        data = {
            "origin_cep": request.form.get("origin_cep"),
            "destination_cep": request.form.get("destination_cep"),
            "weight": request.form.get("weight"),
            "height": request.form.get("height"),
            "width": request.form.get("width"),
            "length": request.form.get("length"),
            "express": request.form.get("express") == "on"
        }

        result = calculate_shipping(data)

        save_history({
            "date": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "origin": data["origin_cep"],
            "destination": data["destination_cep"],
            "price": result["price"]
        })

        session["result"] = result

        return redirect("/")

    history = load_history()

    show_history = len(history) > 0

    return render_template(
        "index.html",
        result=result,
        history=history,
        show_history=show_history
    )


@app.route("/clear-history", methods=["POST"])
def clear_history():

    with open(HISTORY_FILE, "w", encoding="utf-8") as file:
        json.dump([], file)

    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)