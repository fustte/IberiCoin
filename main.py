import os
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, jsonify
from dotenv import load_dotenv
from llamada_api import get_coin_prices


# Cargar las variables de entorno
load_dotenv()

DATABASE_URI_WALLET = os.getenv('DATABASE_URI_WALLET')
if DATABASE_URI_WALLET is None:
    raise ValueError("DATABASE_URI_WALLET no está definida en el archivo .env")

app = Flask(__name__)

def log_error(error_message):
    """Registra un mensaje de error en la consola."""
    print(f"Error: {error_message}")

def validate_amount(amount):
    """Valida que la cantidad sea un número positivo."""
    try:
        amount = float(amount)
        if amount <= 0:
            raise ValueError("La cantidad debe ser un número positivo.")
        return amount
    except ValueError as ve:
        log_error(f"Error de validación: {ve}")
        return None

def get_wallet_balance(currency=None):
    """Obtiene y muestra el balance actual de todas las monedas en la cartera."""
    conn = sqlite3.connect(DATABASE_URI_WALLET)
    cursor = conn.cursor()

    if currency:
        query = '''
        SELECT
            COALESCE(SUM(CASE WHEN to_currency = ? THEN to_quantity ELSE 0 END), 0) -
            COALESCE(SUM(CASE WHEN from_currency = ? THEN from_quantity ELSE 0 END), 0) AS balance
        FROM WALLET
        '''
        cursor.execute(query, (currency, currency))
        balance = cursor.fetchone()[0]
        conn.close()
        return balance or 0

    query = '''
    SELECT currency, SUM(quantity) AS balance
    FROM (
        SELECT from_currency AS currency, -SUM(from_quantity) AS quantity
        FROM WALLET
        GROUP BY from_currency
        UNION ALL
        SELECT to_currency AS currency, SUM(to_quantity) AS quantity
        FROM WALLET
        GROUP BY to_currency
    ) AS balances
    GROUP BY currency
    '''
    cursor.execute(query)
    balances = cursor.fetchall()

    conn.close()

    return balances

def add_funds(amount):
    """Añade fondos en EUR a la cartera."""
    amount = validate_amount(amount)
    if amount is None or amount <= 0:
        return "La cantidad debe ser un número positivo."

    current_date = datetime.now().strftime("%Y-%m-%d")
    current_time = datetime.now().strftime("%H:%M:%S")
    conn = sqlite3.connect(DATABASE_URI_WALLET)
    cursor = conn.cursor()

    try:
        cursor.execute('''
        INSERT INTO WALLET (date, time, from_currency, from_quantity, to_currency, to_quantity)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (current_date, current_time, 'EUR', 0, 'EUR', amount))
        conn.commit()
    except sqlite3.Error as e:
        log_error(f"Error de base de datos: {e}")
        return "Error: No se pudo añadir fondos."
    finally:
        conn.close()
    return f"Fondos añadidos: {amount} EUR"

def trade_currency(from_currency, to_currency, amount):
    """Realiza el intercambio de monedas (compra/venta)."""
    amount = validate_amount(amount)
    if amount is None or amount <= 0:
        return "La cantidad debe ser un número positivo."

    current_date = datetime.now().strftime("%Y-%m-%d")
    current_time = datetime.now().strftime("%H:%M:%S")
    conn = sqlite3.connect(DATABASE_URI_WALLET)
    cursor = conn.cursor()

    balance = get_wallet_balance(from_currency)
    if balance < amount:
        return "No tienes fondos suficientes para realizar esta transacción."

    prices = get_coin_prices('EUR', [from_currency, to_currency])

    if from_currency == 'EUR':
        to_quantity = amount / prices[to_currency]
    elif to_currency == 'EUR':
        to_quantity = amount * prices[from_currency]
    else:
        to_eur = amount * prices[from_currency]
        to_quantity = to_eur / prices[to_currency]

    try:
        cursor.execute('''
        INSERT INTO WALLET (date, time, from_currency, from_quantity, to_currency, to_quantity)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (current_date, current_time, from_currency, amount, to_currency, to_quantity))
        conn.commit()
    except sqlite3.Error as e:
        log_error(f"Error de base de datos: {e}")
        return "Error: No se pudo realizar la transacción."
    finally:
        conn.close()
    return f"Transacción exitosa: {amount} {from_currency} convertidos a {to_quantity:.8f} {to_currency}"




def check_movements():
    """Consulta todos los movimientos en la base de datos."""
    conn = sqlite3.connect(DATABASE_URI_WALLET)
    cursor = conn.cursor()

    query = '''
    SELECT date, time, from_currency, from_quantity, to_currency, to_quantity
    FROM WALLET
    ORDER BY current_date DESC
    '''
    cursor.execute(query)
    rows = cursor.fetchall()
    
    conn.close()

    return rows

def init_wallet_db():
    """Inicializa la base de datos y crea las tablas necesarias si no existen."""
    if not os.path.isfile(DATABASE_URI_WALLET):
        conn = sqlite3.connect(DATABASE_URI_WALLET)
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS WALLET (
            id INTEGER PRIMARY KEY,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            from_currency TEXT NOT NULL,
            from_quantity REAL NOT NULL,
            to_currency TEXT NOT NULL,
            to_quantity REAL NOT NULL
        )
        ''')
        conn.commit()
        conn.close()

@app.route('/')
def index():
    movements = check_movements()
    return render_template('index.html', movements=movements)

@app.route('/add_funds', methods=['POST'])
def add_funds_route():
    amount = validate_amount(request.form['amount'])
    if amount is None or amount <= 0:
        return render_template('index.html', error_message="La cantidad debe ser un número positivo.", movements=check_movements())
    result = add_funds(amount)
    if "Error" in result:
        return render_template('index.html', error_message=result, movements=check_movements())
    return redirect(url_for('index'))

@app.route('/purchase', methods=['GET', 'POST'])
def purchase():
    balances = get_wallet_balance()
    available_currencies = [currency for currency, balance in balances if balance > 0]
    target_cryptocurrencies = ['EUR', 'BTC', 'ETH', 'USDT', 'ADA', 'SOL', 'XRP', 'DOT', 'DOGE', 'SHIB']
    balance_dict = {currency: balance for currency, balance in balances}

    if request.method == 'POST':
        from_currency = request.form['from_currency']
        to_currency = request.form['to_currency']
        amount = validate_amount(request.form['amount'])
        if amount is None or amount <= 0:
            return render_template('purchase.html', error_message="La cantidad debe ser un número positivo.", available_currencies=available_currencies, target_cryptocurrencies=target_cryptocurrencies, balance_dict=balance_dict)
        result = trade_currency(from_currency, to_currency, amount)
        if "Error" in result or "No tienes fondos suficientes" in result:
            return render_template('purchase.html', error_message=result, available_currencies=available_currencies, target_cryptocurrencies=target_cryptocurrencies, balance_dict=balance_dict)
        return redirect(url_for('index'))

    return render_template('purchase.html', available_currencies=available_currencies, target_cryptocurrencies=target_cryptocurrencies, balance_dict=balance_dict)


@app.route('/status')
def status():
    balances = get_wallet_balance()
    euros_gastados_query = '''
    SELECT SUM(from_quantity)
    FROM WALLET
    WHERE from_currency = 'EUR'
    '''
    conn = sqlite3.connect(DATABASE_URI_WALLET)
    cursor = conn.cursor()
    cursor.execute(euros_gastados_query)
    euros_gastados = cursor.fetchone()[0] or 0

    valor_actual = 0
    for currency, balance in balances:
        if currency != 'EUR' and balance > 0:
            prices = get_coin_prices('EUR', [currency])
            valor_actual += balance * prices[currency]

    conn.close()
    return render_template('status.html', euros_gastados=euros_gastados, valor_actual=valor_actual, balances=balances)

@app.route('/calculate')
def calculate():
    from_currency = request.args.get('from_currency')
    to_currency = request.args.get('to_currency')
    amount = float(request.args.get('amount'))

    prices = get_coin_prices('EUR', [from_currency, to_currency])

    if from_currency == 'EUR':
        result = amount / prices[to_currency]
    elif to_currency == 'EUR':
        result = amount * prices[from_currency]
    else:
        to_eur = amount * prices[from_currency]
        result = to_eur / prices[to_currency]

    
    formatted_result = f"{result:.8f}" if result < 1 else f"{result:.6f}"

    return jsonify({'result': formatted_result})

if __name__ == '__main__':
    init_wallet_db()
    app.run(debug=True)

