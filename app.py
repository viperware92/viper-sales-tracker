from flask import Flask, render_template, request, redirect, send_file
from datetime import datetime
import csv
import os
import json

app = Flask(__name__)

DATA_FILE = 'sales.json'

# Load or initialize data
def load_sales():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return []

def save_sales(sales):
    with open(DATA_FILE, 'w') as f:
        json.dump(sales, f, indent=4)

sales = load_sales()

@app.route('/')
def index():
    total_income = sum(s['total'] for s in sales)
    total_profit = sum(s['profit'] for s in sales)
    return render_template('index.html', sales=sales, total_income=round(total_income, 2), total_profit=round(total_profit, 2))

@app.route('/add', methods=['POST'])
def add():
    product = float(request.form['product'])
    flash = float(request.form['flash'])
    cantidad = int(request.form['cantidad'])
    install = float(request.form['install'])
    sub = '✔' if 'sub' in request.form else '✘'
    tag = request.form['tag']

    # Sub price logic
    sub_price = 29 if sub == '✔' else 0
    sub_cost = 20 if sub == '✔' else 0
    sub_profit = sub_price - sub_cost

    # Total ingresado por venta (producto * cantidad + servicios)
    total = (product * cantidad) + flash + install + sub_price

    # Ganancia total es igual a total ingresado - costo base (solo el costo de sub si se incluye)
    profit = total - (sub_cost)

    sales.append({
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M'),
        'venta': product,
        'flash': flash,
        'install': install,
        'sub': sub,
        'tag': tag,
        'cantidad': cantidad,
        'total': round(total, 2),
        'profit': round(profit, 2)
    })

    save_sales(sales)
    return redirect('/')

@app.route('/delete/<int:index>', methods=['POST'])
def delete(index):
    if 0 <= index < len(sales):
        sales.pop(index)
        save_sales(sales)
    return redirect('/')

@app.route('/export')
def export():
    filepath = 'sales_export.csv'
    with open(filepath, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=sales[0].keys())
        writer.writeheader()
        writer.writerows(sales)
    return send_file(filepath, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
