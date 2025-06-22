from flask import Flask, render_template, request, redirect, url_for, jsonify
import csv
import datetime

app = Flask(__name__)

sales = []  # Each sale: {'product': ..., 'flash': ..., 'install': ..., 'sub': ..., 'total': ..., 'profit': ..., 'tag': ..., 'timestamp': ...}

# --- Constants ---
PRODUCT_COST = 191.99
KEY_COST = 20.00
PLATFORM_FEE_PERCENT = 10

# --- Functions ---
def calculate_profit(sale):
    income = sale['product'] + sale['flash'] + sale['install'] + (sale['sub'] * 29)
    cost = PRODUCT_COST + (KEY_COST if sale['sub'] else 0)
    platform_fee = income * (PLATFORM_FEE_PERCENT / 100)
    profit = income - cost - platform_fee
    return round(income, 2), round(cost, 2), round(platform_fee, 2), round(profit, 2)

# --- Routes ---
@app.route("/")
def index():
    total_income = total_cost = total_profit = 0
    for s in sales:
        total_income += s['total']
        total_cost += s['cost'] + s['fee']
        total_profit += s['profit']
    return render_template("index.html", sales=sales, total_income=total_income, total_cost=total_cost, total_profit=total_profit)

@app.route("/add", methods=["POST"])
def add_sale():
    try:
        product = float(request.form['product'])
        flash = float(request.form['flash'])
        install = float(request.form['install'])
        sub = True if request.form.get('sub') == 'on' else False
        tag = request.form.get('tag', '')

        income, cost, fee, profit = calculate_profit({
            'product': product,
            'flash': flash,
            'install': install,
            'sub': sub
        })

        sales.append({
            'product': product,
            'flash': flash,
            'install': install,
            'sub': sub,
            'tag': tag,
            'total': income,
            'cost': cost,
            'fee': fee,
            'profit': profit,
            'timestamp': datetime.datetime.now().strftime("%Y-%m-%d")
        })

        return redirect(url_for('index'))
    except Exception as e:
        return str(e)

@app.route("/delete/<int:index>", methods=["POST"])
def delete_sale(index):
    if 0 <= index < len(sales):
        sales.pop(index)
    return redirect(url_for('index'))

@app.route("/export")
def export_csv():
    with open("sales_export.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Product", "Flash", "Install", "Sub", "Tag", "Date", "Total", "Cost", "Fee", "Profit"])
        for s in sales:
            writer.writerow([s['product'], s['flash'], s['install'], s['sub'], s['tag'], s['timestamp'], s['total'], s['cost'], s['fee'], s['profit']])
    return "Exported to sales_export.csv"

@app.route("/data")
def get_data():
    return jsonify(sales)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
