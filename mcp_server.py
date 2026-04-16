from fastmcp import FastMCP
import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), 'expenses.db')
CATEGORIES_PATH = os.path.join(os.path.dirname(__file__), "categories.json")

mcp = FastMCP("ExpenseTracker")


def init_db():
    """Initialize the SQLite database and create the expenses table if it doesn't exist."""
    with sqlite3.connect(DB_PATH) as c:
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                subcategory TEXT DEFAULT '',
                date TEXT NOT NULL,
                note TEXT DEFAULT ''
            )
            """
        )

init_db()

@mcp.tool()
def add_expense(amount: float, category: str, subcategory: str = '', date   : str = '', note: str = '') -> str:
    """Add a new expense to the database."""
    
    
    with sqlite3.connect(DB_PATH) as c:
        c.execute(
            """
            INSERT INTO expenses (amount, category, subcategory, date, note)
            VALUES (?, ?, ?, ?, ?)
            """,
            (amount, category, subcategory, date, note)
        )
    
    return "Expense added successfully!"

@mcp.tool()
def list_expenses(start_date, end_date) -> list[dict]:
    """List all expenses in the database."""
    with sqlite3.connect(DB_PATH) as c:
        cur = c.execute("SELECT * FROM expenses WHERE date BETWEEN ? AND ? ORDER BY id", (start_date, end_date))
        cols = [col[0] for col in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]
    

@mcp.tool()
def summarize(start_date, end_date, category=None):
    with sqlite3.connect(DB_PATH) as c:
        query = (
            """
            SELECT category, SUM(amount) as total
            FROM expenses
            WHERE date BETWEEN ? AND ?
            """
        )
        params = [start_date, end_date]
        if category:
            query += " AND category = ?"
            params.append(category)
        query += " GROUP BY category"
        cur = c.execute(query, params)
        cols = [col[0] for col in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]


@mcp.resource("expense://categories", mime_type="application/json")
def categories():
    # Read fresh each time so you can edit the file without restarting
    with open(CATEGORIES_PATH, "r", encoding="utf-8") as f:
        return f.read()
    
if __name__ == "__main__":
    mcp.serve()