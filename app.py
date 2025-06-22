# app.py
from flask import Flask, render_template, request, redirect, send_file
from datetime import datetime
import csv
import io
from collections import defaultdict

app = Flask(__name__)

sales = []

def calcular_totales():
    totales = defaultdict(float)
    for s in sales:
        totales['profit'] += s['profit']
        totales['income'] += s['total']
        totales['cost'] += s['cost']
        totales['flash'] += s['flash']
        totales['install'] += s['install']
        totales['sub_profit'] += s['ganancia_sub']
    return {k: round(v, 2) for k, v in totales.items()}

@app.route("/")
def index():
    totales = calcular_totales()
    return render_template("index.html", sales=sales, **totales)

@app.route("/add", methods=["POST"])
def add():
    product = float(request.form['product'])
    flash = float(request.form['flash'])
    install = float(request.form['install'])
    cantidad = int(request.form['cantidad'])
    sub = 1 if 'sub' in request.form else 0
    tag = request.form['tag']

    # Valores fijos del negocio
    costo_producto = 191.94
    costo_sub = 20
    precio_sub = 29
    venta_unidad = 468

    cost = (costo_producto * cantidad) + (sub * costo_sub)
    venta = venta_unidad * cantidad
    sub_income = sub * precio_sub
    ganancia_sub = sub_income - (sub * costo_sub)
    fee = 0  # Aquí puedes agregar lógica para fee si es necesario

    total = venta + flash + install + sub_income
    profit = (venta - (costo_producto * cantidad)) + flash + install + ganancia_sub

    sales.append({
        'product': product,
        'flash': flash,
        'install': install,
        'cantidad': cantidad,
        'sub': '✔' if sub else '✘',
        'tag': tag,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'venta': venta,
        'total': round(total, 2),
        'cost': round(cost, 2),
        'fee': fee,
        'profit': round(profit, 2),
        'ganancia_sub': round(ganancia_sub, 2)
    })
    return redirect("/")

@app.route("/delete/<int:index>", methods=["POST"])
def delete(index):
    if 0 <= index < len(sales):
        sales.pop(index)
    return redirect("/")

@app.route("/export")
def export():
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Product", "Flash", "Install", "Cantidad", "Sub", "Tag", "Date", "Venta", "Total", "Cost", "Fee", "Profit", "Sub Profit"])
    for s in sales:
        writer.writerow([s['product'], s['flash'], s['install'], s['cantidad'], s['sub'], s['tag'], s['timestamp'], s['venta'], s['total'], s['cost'], s['fee'], s['profit'], s['ganancia_sub']])
    output.seek(0)
    return send_file(io.BytesIO(output.getvalue().encode()), mimetype='text/csv', as_attachment=True, download_name='ventas.csv')

if __name__ == "__main__":
    app.run(debug=True)
