# SpendLog — Personal Expense Tracker

A personal expense tracker with analytics, built with Python (Flask) + SQLite + HTML/JS.

## Setup

1. **Install Python** (3.8+) if not already installed.

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the app:**
   ```bash
   python app.py
   ```

4. **Open in browser:**
   ```
   http://127.0.0.1:5000
   ```

That's it! The SQLite database (`expenses.db`) is created automatically on first run.

---

## Features

- ➕ **Add Expense** — date, amount, category (with quick-pick pills), and a note
- 📋 **History** — view all expenses, filter by category / month / search keyword, delete entries
- 📊 **Dashboard** — total spent, transaction count, average per entry, category doughnut chart, monthly bar chart, top spending days

## File Structure

```
expense-tracker/
├── app.py              ← Flask backend + SQLite API
├── expenses.db         ← Auto-created database
├── requirements.txt
├── templates/
│   └── index.html      ← Single-page UI
└── static/
    ├── css/style.css
    └── js/app.js
```

## API Endpoints

| Method | URL | Description |
|--------|-----|-------------|
| POST | /api/expenses | Add new expense |
| GET  | /api/expenses | List expenses (filter: category, month, search) |
| DELETE | /api/expenses/:id | Delete an expense |
| GET | /api/analytics | Dashboard stats (filter: month) |
| GET | /api/categories | List all used categories |
