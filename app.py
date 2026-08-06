from flask import Flask, request, jsonify, render_template
import os
import psycopg2
import psycopg2.extras
from datetime import datetime

app = Flask(__name__)
DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db():
    # Neon/most Postgres hosts require sslmode=require
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    return conn

def init_db():
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute('''
                CREATE TABLE IF NOT EXISTS expenses (
                    id SERIAL PRIMARY KEY,
                    date TEXT NOT NULL,
                    amount REAL NOT NULL,
                    category TEXT NOT NULL,
                    note TEXT,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            ''')
        conn.commit()

# Initialize DB immediately when app starts
init_db()

# ── Pages ──────────────────────────────────────────────
@app.route('/')
def index():
    return render_template('index.html')

# ── API: Add expense ────────────────────────────────────
@app.route('/api/expenses', methods=['POST'])
def add_expense():
    data = request.json
    if not data or not data.get('amount') or not data.get('category') or not data.get('date'):
        return jsonify({'error': 'amount, category and date are required'}), 400
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                'INSERT INTO expenses (date, amount, category, note) VALUES (%s, %s, %s, %s) RETURNING id',
                (data['date'], float(data['amount']), data['category'], data.get('note', ''))
            )
            expense_id = cur.fetchone()[0]
        conn.commit()
    return jsonify({'id': expense_id, 'message': 'Expense added'}), 201

# ── API: Get all expenses (with optional filters) ───────
@app.route('/api/expenses', methods=['GET'])
def get_expenses():
    category = request.args.get('category')
    month    = request.args.get('month')
    search   = request.args.get('search')

    query  = 'SELECT * FROM expenses WHERE 1=1'
    params = []

    if category:
        query += ' AND category = %s'
        params.append(category)
    if month:
        query += " AND to_char(date::date, 'YYYY-MM') = %s"
        params.append(month)
    if search:
        query += ' AND (note ILIKE %s OR category ILIKE %s)'
        params += [f'%{search}%', f'%{search}%']

    query += ' ORDER BY date DESC, id DESC'

    with get_db() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(query, params)
            rows = cur.fetchall()
    return jsonify([dict(r) for r in rows])

# ── API: Delete expense ─────────────────────────────────
@app.route('/api/expenses/<int:expense_id>', methods=['DELETE'])
def delete_expense(expense_id):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute('DELETE FROM expenses WHERE id = %s', (expense_id,))
        conn.commit()
    return jsonify({'message': 'Deleted'})

# ── API: Clear all expenses ─────────────────────────────
@app.route('/api/expenses/clear', methods=['DELETE'])
def clear_all():
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute('DELETE FROM expenses')
        conn.commit()
    return jsonify({'message': 'All data cleared'})

# ── API: Analytics ──────────────────────────────────────
@app.route('/api/analytics', methods=['GET'])
def analytics():
    month = request.args.get('month')

    filter_sql = ''
    params     = []
    if month:
        filter_sql = " WHERE to_char(date::date, 'YYYY-MM') = %s"
        params.append(month)

    with get_db() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(f'SELECT COALESCE(SUM(amount),0) as total FROM expenses{filter_sql}', params)
            total = cur.fetchone()['total']

            cur.execute(
                f'SELECT category, SUM(amount) as total FROM expenses{filter_sql} GROUP BY category ORDER BY total DESC',
                params
            )
            by_cat = cur.fetchall()

            cur.execute(
                f'SELECT date, SUM(amount) as total FROM expenses{filter_sql} GROUP BY date ORDER BY total DESC LIMIT 10',
                params
            )
            by_date = cur.fetchall()

            cur.execute(
                "SELECT to_char(date::date, 'YYYY-MM') as month, SUM(amount) as total "
                "FROM expenses GROUP BY month ORDER BY month DESC LIMIT 6"
            )
            trend = cur.fetchall()

            cur.execute(f'SELECT COUNT(*) as cnt FROM expenses{filter_sql}', params)
            count = cur.fetchone()['cnt']

    return jsonify({
        'total':       round(float(total), 2),
        'count':       count,
        'by_category': [dict(r) for r in by_cat],
        'by_date':     [dict(r) for r in by_date],
        'trend':       [dict(r) for r in reversed(trend)]
    })

# ── API: Categories list ────────────────────────────────
@app.route('/api/categories', methods=['GET'])
def categories():
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT DISTINCT category FROM expenses ORDER BY category')
            rows = cur.fetchall()
    return jsonify([r[0] for r in rows])

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print('\n  Expense Tracker running → http://127.0.0.1:5000\n')
    app.run(host='0.0.0.0', port=port, debug=False)
