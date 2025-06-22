# app.py
from flask import Flask, render_template, request, redirect, send_file
from datetime import datetime
import csv
import io

app = Flask(__name__)

sales = []

@app.route("/")
def index():
    total_profit = sum(s['profit'] for s in sales)
    total_income = sum(s['total'] for s in sales)
    total_cost = sum(s['cost'] for s in sales)
    return render_template("index.html", sales=sales, total_profit=round(total_profit, 2), total_income=round(total_income, 2), total_cost=round(total_cost, 2))

@app.route("/add", methods=["POST"])
def add():
    product = float(request.form['product'])
    flash = float(request.form['flash'])
    install = float(request.form['install'])
    cantidad = int(request.form['cantidad'])
    sub = 1 if 'sub' in request.form else 0
    tag = request.form['tag']

    # Costo del producto (solo el producto base)
    costo_producto = 191.94
    cost = costo_producto * cantidad
    venta = 468 * cantidad
    fee = 0
    sub_income = sub * 29
    sub_cost = sub * 20
    ganancia_sub = sub_income - sub_cost

    # El total que se cobra incluye todo lo que se le cobra al cliente
    total = venta + flash + install + sub_income

    # La ganancia real solo se le resta el costo del producto y de la sub (flash e install ya son 100% tuyos)
    profit = (venta - cost) + flash + install + ganancia_sub

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
        'cost': round(cost + sub_cost, 2),
        'fee': fee,
        'profit': round(profit, 2),
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
    writer.writerow(["Product", "Flash", "Install", "Cantidad", "Sub", "Tag", "Date", "Venta", "Total", "Cost", "Fee", "Profit"])
    for s in sales:
        writer.writerow([s['product'], s['flash'], s['install'], s['cantidad'], s['sub'], s['tag'], s['timestamp'], s['venta'], s['total'], s['cost'], s['fee'], s['profit']])
    output.seek(0)
    return send_file(io.BytesIO(output.getvalue().encode()), mimetype='text/csv', as_attachment=True, download_name='ventas.csv')

if __name__ == "__main__":
    app.run(debug=True)
