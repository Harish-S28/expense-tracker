# 💰 SpendLog — Personal Expense Tracker

A full-stack personal finance web application to track, manage, and analyze daily expenses.

🔗 **Live Demo:** https://expense-tracker-476k.onrender.com

📂 **GitHub:** https://github.com/Harish-S28/expense-tracker

---

## 📸 Features

- ➕ **Add Expense** — Log daily expenses with date, amount, category, and notes
- 📊 **Dashboard** — Visual analytics with charts and spending insights
- 📋 **History** — View, search, filter, and delete expense records
- 🔍 **Filter** — Filter by category, month, or keyword
- 📈 **Charts** — Category-wise doughnut chart and monthly bar chart
- 🏆 **Top Spending Days** — See which days you spent the most

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Frontend | HTML5, CSS3, JavaScript |
| Charts | Chart.js |
| Backend | Python, Flask (REST API) |
| Database | SQLite |
| Deployment | Railway |
| Version Control | Git & GitHub |

---

## 📁 Project Structure

```
expense-tracker/
├── app.py                  ← Flask backend & REST API
├── requirements.txt        ← Python dependencies
├── Procfile                ← Railway deployment config
├── README.md
├── templates/
│   └── index.html          ← Frontend UI (single page)
└── static/
    ├── css/
    │   └── style.css       ← Styling
    └── js/
        └── app.js          ← Frontend logic & API calls
```

---

## ⚙️ API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Serve the web app |
| POST | `/api/expenses` | Add a new expense |
| GET | `/api/expenses` | Get all expenses (supports filters) |
| DELETE | `/api/expenses/<id>` | Delete an expense |
| GET | `/api/analytics` | Get dashboard statistics |
| GET | `/api/categories` | Get all used categories |

### Query Parameters for GET /api/expenses
- `category` — filter by category name
- `month` — filter by month (format: YYYY-MM)
- `search` — search in notes or category

---

## 🗄️ Database Schema

```sql
CREATE TABLE expenses (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    date       TEXT NOT NULL,
    amount     REAL NOT NULL,
    category   TEXT NOT NULL,
    note       TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);
```

---

## 🚀 Run Locally

**1. Clone the repository**
```bash
git clone https://github.com/Harish-S28/expense-tracker.git
cd expense-tracker
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Run the app**
```bash
python app.py
```

**4. Open in browser**
```
http://127.0.0.1:5000
```

The SQLite database (`expenses.db`) is created automatically on first run.

---

## 📊 Dashboard Preview

- **Total Spent** — sum of all expenses
- **Transaction Count** — number of entries
- **Average per Entry** — total ÷ count
- **By Category** — doughnut chart breakdown
- **Monthly Trend** — bar chart for last 6 months
- **Top Spending Days** — highest spend dates with visual bar

---

## 🔮 Future Improvements

- [ ] User authentication (login & register)
- [ ] PostgreSQL for multi-user cloud support
- [ ] Budget limits per category with alerts
- [ ] Export data to CSV / Excel
- [ ] Weekly and yearly analytics view
- [ ] Mobile app version

---

## 👨‍💻 Author

**Harish S**  
GitHub: [@Harish-S28](https://github.com/Harish-S28)

---

## 📄 License

This project is for personal and educational use.
