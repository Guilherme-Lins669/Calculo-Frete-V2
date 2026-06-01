from flask import Flask, render_template, request, redirect, session
from datetime import datetime
import json
import os

app = Flask(__name__)
app.secret_key = "fretefacil"

HISTORY_FILE = "history.json"


def get_region(cep):
    prefix = int(cep.replace("-", "")[:5])

    # Sudeste
    if 1000 <= prefix <= 19999:   # SP
        return "Sudeste"
    if 20000 <= prefix <= 29999:  # RJ + ES
        return "Sudeste"
    if 30000 <= prefix <= 39999:  # MG
        return "Sudeste"

    # Nordeste
    if 40000 <= prefix <= 48999:  # BA
        return "Nordeste"
    if 49000 <= prefix <= 49999:  # SE
        return "Nordeste"
    if 50000 <= prefix <= 56999:  # PE
        return "Nordeste"
    if 57000 <= prefix <= 57999:  # AL
        return "Nordeste"
    if 58000 <= prefix <= 58999:  # PB
        return "Nordeste"
    if 59000 <= prefix <= 59999:  # RN
        return "Nordeste"
    if 60000 <= prefix <= 63999:  # CE
        return "Nordeste"
    if 64000 <= prefix <= 64999:  # PI
        return "Nordeste"
    if 65000 <= prefix <= 65999:  # MA
        return "Nordeste"

    # Norte
    if 66000 <= prefix <= 69999:  # PA, AP, AM, RR, AC
        return "Norte"

    # Centro-Oeste
    if 70000 <= prefix <= 79999:  # DF, GO, RO, TO, MT, MS
        return "Centro-Oeste"

    # Sul
    if 80000 <= prefix <= 99999:  # PR, SC, RS
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

        origin_cep = request.form.get("origin_cep", "").replace("-", "").strip()
        destination_cep = request.form.get("destination_cep", "").replace("-", "").strip()

        error = None
        if not origin_cep.isdigit() or len(origin_cep) != 8:
            error = "CEP de origem inválido. Digite apenas 8 números."
        elif not destination_cep.isdigit() or len(destination_cep) != 8:
            error = "CEP de destino inválido. Digite apenas 8 números."

        if error:
            history = load_history()
            return render_template("index.html", error=error, history=history, show_history=len(history) > 0)

        data = {
            "origin_cep": origin_cep,
            "destination_cep": destination_cep,
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
