from flask import Flask, render_template, request, redirect, session
from datetime import datetime
import json
import os

app = Flask(__name__)
app.secret_key = "fretefacil"

HISTORY_FILE = "history.json"


def get_region(cep):
    prefix = int(cep.replace("-", "")[:5])

    if 1000  <= prefix <= 39999: return "Sudeste"   # SP, RJ, ES, MG
    if 40000 <= prefix <= 65999: return "Nordeste"  # BA, SE, PE, AL, PB, RN, CE, PI, MA
    if 66000 <= prefix <= 69999: return "Norte"     # PA, AP, AM, RR, AC
    if 70000 <= prefix <= 79999: return "Centro-Oeste"  # DF, GO, RO, TO, MT, MS
    if 80000 <= prefix <= 99999: return "Sul"       # PR, SC, RS

    return "Desconhecida"


# Tabela de prazo em dias por par de regiões (origem -> destino)
DELIVERY_DAYS = {
    ("Sudeste",      "Sudeste"):      2,
    ("Sudeste",      "Sul"):          3,
    ("Sudeste",      "Centro-Oeste"): 3,
    ("Sudeste",      "Nordeste"):     5,
    ("Sudeste",      "Norte"):        7,
    ("Sul",          "Sul"):          2,
    ("Sul",          "Sudeste"):      3,
    ("Sul",          "Centro-Oeste"): 4,
    ("Sul",          "Nordeste"):     6,
    ("Sul",          "Norte"):        8,
    ("Centro-Oeste", "Centro-Oeste"): 2,
    ("Centro-Oeste", "Sudeste"):      3,
    ("Centro-Oeste", "Sul"):          4,
    ("Centro-Oeste", "Nordeste"):     5,
    ("Centro-Oeste", "Norte"):        6,
    ("Nordeste",     "Nordeste"):     2,
    ("Nordeste",     "Sudeste"):      5,
    ("Nordeste",     "Sul"):          6,
    ("Nordeste",     "Centro-Oeste"): 5,
    ("Nordeste",     "Norte"):        7,
    ("Norte",        "Norte"):        3,
    ("Norte",        "Sudeste"):      7,
    ("Norte",        "Sul"):          8,
    ("Norte",        "Centro-Oeste"): 6,
    ("Norte",        "Nordeste"):     7,
}


def get_weight_rate(final_weight):
    """Tarifa por faixa de peso (R$/kg), parecido com tabela real de transportadora."""
    if final_weight <= 1:
        return 6.0
    elif final_weight <= 5:
        return 5.0
    elif final_weight <= 10:
        return 4.5
    elif final_weight <= 20:
        return 4.0
    elif final_weight <= 50:
        return 3.5
    else:
        return 3.0


def calculate_shipping(data):
    weight = float(data["weight"])
    height = float(data["height"])
    width  = float(data["width"])
    length = float(data["length"])

    # Peso cubado
    cubed_weight = (height * width * length) / 6000
    final_weight = max(weight, cubed_weight)

    origin_region      = get_region(data["origin_cep"])
    destination_region = get_region(data["destination_cep"])

    # --- Base: frete peso por faixa ---
    rate       = get_weight_rate(final_weight)
    frete_peso = final_weight * rate

    # --- Adicional de região ---
    regional_fee = 0
    if origin_region != destination_region:
        regional_fee = 15  # regiões diferentes

    # --- GRIS: 0,4% sobre valor declarado da mercadoria ---
    declared_value = float(data.get("declared_value") or 0)
    gris = round(declared_value * 0.004, 2)

    # --- Taxas fixas ---
    taxa_ademe = 4.50   # taxa ambiental
    taxa_tda   = 6.00   # taxa de despacho

    # --- Subtotal antes do expresso ---
    subtotal = frete_peso + regional_fee + gris + taxa_ademe + taxa_tda

    # --- Frete mínimo ---
    FRETE_MINIMO = 30.00
    subtotal = max(subtotal, FRETE_MINIMO)

    # --- Expresso ---
    express = data.get("express", False)
    if express:
        subtotal *= 1.4

    # --- Prazo ---
    base_days = DELIVERY_DAYS.get(
        (origin_region, destination_region),
        7  # fallback
    )
    delivery_days = max(1, base_days - 2) if express else base_days

    return {
        "price":              round(subtotal, 2),
        "delivery_days":      delivery_days,
        "cubed_weight":       round(cubed_weight, 2),
        "final_weight":       round(final_weight, 2),
        "origin_region":      origin_region,
        "destination_region": destination_region,
        "frete_peso":         round(frete_peso, 2),
        "regional_fee":       round(regional_fee, 2),
        "gris":               round(gris, 2),
        "taxa_ademe":         taxa_ademe,
        "taxa_tda":           taxa_tda,
        "express":            express,
    }


def load_history():
    if not os.path.exists(HISTORY_FILE):
        return []
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_history(item):
    history = load_history()
    history.insert(0, item)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history[:10], f, ensure_ascii=False, indent=2)


@app.route("/", methods=["GET", "POST"])
def index():
    result = session.pop("result", None)

    if request.method == "POST":
        origin_cep      = request.form.get("origin_cep", "").replace("-", "").strip()
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
            "origin_cep":      origin_cep,
            "destination_cep": destination_cep,
            "weight":          request.form.get("weight"),
            "height":          request.form.get("height"),
            "width":           request.form.get("width"),
            "length":          request.form.get("length"),
            "declared_value":  request.form.get("declared_value") or 0,
            "express":         request.form.get("express") == "on",
        }

        result = calculate_shipping(data)

        save_history({
            "date":        datetime.now().strftime("%d/%m/%Y %H:%M"),
            "origin":      data["origin_cep"],
            "destination": data["destination_cep"],
            "price":       result["price"],
        })

        session["result"] = result
        return redirect("/")

    history     = load_history()
    show_history = len(history) > 0

    return render_template(
        "index.html",
        result=result,
        history=history,
        show_history=show_history,
    )


@app.route("/clear-history", methods=["POST"])
def clear_history():
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump([], f)
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
