from flask import Flask, request, jsonify, render_template
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
DB_PATH = os.path.join(os.path.dirname(__file__), 'expenses.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                note TEXT,
                created_at TEXT DEFAULT (datetime('now'))
            )
        ''')
        conn.commit()

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
        cur = conn.execute(
            'INSERT INTO expenses (date, amount, category, note) VALUES (?, ?, ?, ?)',
            (data['date'], float(data['amount']), data['category'], data.get('note', ''))
        )
        conn.commit()
        expense_id = cur.lastrowid
    return jsonify({'id': expense_id, 'message': 'Expense added'}), 201

# ── API: Get all expenses (with optional filters) ───────
@app.route('/api/expenses', methods=['GET'])
def get_expenses():
    category = request.args.get('category')
    month    = request.args.get('month')   # YYYY-MM
    search   = request.args.get('search')

    query  = 'SELECT * FROM expenses WHERE 1=1'
    params = []

    if category:
        query += ' AND category = ?'
        params.append(category)
    if month:
        query += " AND strftime('%Y-%m', date) = ?"
        params.append(month)
    if search:
        query += ' AND (note LIKE ? OR category LIKE ?)'
        params += [f'%{search}%', f'%{search}%']

    query += ' ORDER BY date DESC, id DESC'

    with get_db() as conn:
        rows = conn.execute(query, params).fetchall()
    return jsonify([dict(r) for r in rows])

# ── API: Delete expense ─────────────────────────────────
@app.route('/api/expenses/<int:expense_id>', methods=['DELETE'])
def delete_expense(expense_id):
    with get_db() as conn:
        conn.execute('DELETE FROM expenses WHERE id = ?', (expense_id,))
        conn.commit()
    return jsonify({'message': 'Deleted'})

# ── API: Analytics ──────────────────────────────────────
@app.route('/api/analytics', methods=['GET'])
def analytics():
    month = request.args.get('month')  # YYYY-MM, optional

    filter_sql = ''
    params     = []
    if month:
        filter_sql = " WHERE strftime('%Y-%m', date) = ?"
        params.append(month)

    with get_db() as conn:
        # Total
        total = conn.execute(
            f'SELECT COALESCE(SUM(amount),0) as total FROM expenses{filter_sql}', params
        ).fetchone()['total']

        # By category
        by_cat = conn.execute(
            f'SELECT category, SUM(amount) as total FROM expenses{filter_sql} GROUP BY category ORDER BY total DESC',
            params
        ).fetchall()

        # By date (top spending days)
        by_date = conn.execute(
            f'SELECT date, SUM(amount) as total FROM expenses{filter_sql} GROUP BY date ORDER BY total DESC LIMIT 10',
            params
        ).fetchall()

        # Monthly trend (last 6 months)
        trend = conn.execute(
            "SELECT strftime('%Y-%m', date) as month, SUM(amount) as total "
            "FROM expenses GROUP BY month ORDER BY month DESC LIMIT 6"
        ).fetchall()

        # Count
        count = conn.execute(
            f'SELECT COUNT(*) as cnt FROM expenses{filter_sql}', params
        ).fetchone()['cnt']

    return jsonify({
        'total':      round(total, 2),
        'count':      count,
        'by_category': [dict(r) for r in by_cat],
        'by_date':     [dict(r) for r in by_date],
        'trend':       [dict(r) for r in reversed(trend)]
    })

# ── API: Categories list ────────────────────────────────
@app.route('/api/categories', methods=['GET'])
def categories():
    with get_db() as conn:
        rows = conn.execute('SELECT DISTINCT category FROM expenses ORDER BY category').fetchall()
    return jsonify([r['category'] for r in rows])

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    print('\n  Expense Tracker running → http://127.0.0.1:5000\n')
    app.run(host='0.0.0.0', port=port, debug=False)
