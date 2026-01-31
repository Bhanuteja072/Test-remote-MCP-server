import os
from fastmcp import FastMCP
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), 'test_expensetracker.db')
CATEGORY_PATH = os.path.join(os.path.dirname(__file__), 'categories.json')


mcp = FastMCP(name="expensetracker")

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """ CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                subcategory TEXT DEFAULT '',
                note TEXT DEFAULT ''
            )
            """
        )

init_db()   

@mcp.tool
def add_expenses(date,amount,category,subcategory='',note=''):
    """Add a new expense to the database."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute(
            "INSERT INTO expenses (date, amount, category, subcategory, note) VALUES (?, ?, ?, ?, ?)",
            (date, amount, category, subcategory, note)
        )
        new_id = cursor.lastrowid
    return {"status": "success", "id": new_id}

@mcp.tool
def list_Expenses():
    """List all expenses from the database."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("SELECT id, date, amount, category, subcategory, note FROM expenses ORDER BY id ASC")
        cols = [description[0] for description in cursor.description]
        return [dict(zip(cols, row)) for row in cursor.fetchall()]



@mcp.tool
def list_expense_in_range(start_date, end_date):
    """List expenses within a specified date range."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute(
            "SELECT id, date, amount, category, subcategory, note FROM expenses WHERE date BETWEEN ? AND ? ORDER BY date ASC",
            (start_date, end_date)
        )
        cols = [description[0] for description in cursor.description]
        return [dict(zip(cols, row)) for row in cursor.fetchall()]
    
@mcp.tool
def edit_expense(expense_id, date, amount, category, subcategory='', note=''):
    """Edit an existing expense by its id."""
    if expense_id is None:
        return {"status": "error", "message": "expense_id is required"}

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute(
            "UPDATE expenses SET date = ?, amount = ?, category = ?, subcategory = ?, note = ? WHERE id = ?",
            (date, amount, category, subcategory, note, expense_id)
        )

    if cursor.rowcount == 0:
        return {"status": "not_found", "id": expense_id}
    return {"status": "success", "id": expense_id}

@mcp.tool
def delete_expense(expense_id):
    """Delete an expense by its id."""
    if expense_id is None:
        return {"status": "error", "message": "expense_id is required"}

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute(
            "DELETE FROM expenses WHERE id = ?",
            (expense_id,)
        )

    if cursor.rowcount == 0:
        return {"status": "not_found", "id": expense_id}
    return {"status": "success", "id": expense_id}



@mcp.tool
def summarize(start_date,end_date,category = None):
    """ Summarize exxpenses by category within date range"""
    with sqlite3.connect(DB_PATH) as conn:
        query=("""SELECT category, SUM(amount) as total_amount FROM expenses WHERE date BETWEEN ? AND ?""")
        params=[start_date,end_date]
        if category:
            query += " AND category = ?"
            params.append(category)
        
        query += " GROUP BY category ORDER BY category ASC"

        cursor = conn.execute(query,params)
        cols = [description[0] for description in cursor.description]
        return [dict(zip(cols, row)) for row in cursor.fetchall()]
    


@mcp.resource("expense://categories",mime_type="application/json")
def categories():
    #Read fresh each time so you can edit the file without restarting
    with open(CATEGORY_PATH, "r" , encoding="utf-8") as f:
        return f.read()

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0" , port=8080)