from flask import Flask, render_template, request, redirect
from datetime import datetime
import csv
import os

app = Flask(__name__)

sales = []

@app.route('/')
def index():
    total_income = sum(s['total'] for s in sales)
    total_cost = sum(s['cost'] for s in sales)
    total_profit = total_income - total_cost
    return render_template('index.html', sales=sales, total_income=round(total_income, 2), total_cost=round(total_cost, 2), total_profit=round(total_profit, 2))

@app.route('/add', methods=['POST'])
def add():
    venta_total = float(request.form['product'])  # Precio que cobraste al cliente por unidad
    flash = float(request.form['flash'])
    install = float(request.form['install'])
    cantidad = int(request.form.get('cantidad', 1))
    tag = request.form['tag']
    sub_included = request.form.get('sub')
    sub = '✅' if sub_included else '—'

    # Costos internos
    product_cost = 191.94
    shipping_cost = 35.14  # incluido en el producto entregado
    sub_cost = 20.0 if sub_included else 0.0
    cost_unitario = product_cost + shipping_cost + sub_cost
    total_cost = cost_unitario * cantidad

    total = (venta_total + flash + install + (29.0 if sub_included else 0.0)) * cantidad
    fee = round(total * 0.054 + 0.3, 2)
    profit = round(total - total_cost - fee, 2)

    sales.append({
        'install': install,
        'sub': sub,
        'tag': tag,
        'cantidad': cantidad,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'total': round(total, 2),
        'cost': round(total_cost, 2),
        'fee': fee,
        'profit': profit,
        'flash': flash,
        'venta': venta_total,
        'sub_price': 29.0 if sub_included else 0.0
    })
    return redirect('/')

@app.route('/delete/<int:index>', methods=['POST'])
def delete(index):
    if 0 <= index < len(sales):
        sales.pop(index)
    return redirect('/')

@app.route('/export')
def export():
    filename = 'sales_export.csv'
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['install', 'sub', 'tag', 'timestamp', 'cantidad', 'total', 'cost', 'fee', 'profit', 'flash', 'venta', 'sub_price']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for s in sales:
            writer.writerow(s)
    return redirect(f'/{filename}')

if __name__ == '__main__':
    app.run(debug=True)
