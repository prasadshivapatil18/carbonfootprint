"""
Database Management Service for Carbon Footprint Application
------------------------------------------------------------
Provides a robust, local SQLite database layer with auto-initialization,
parameterized SQL queries, and safe history cleanup mechanisms.
"""

import os
import sqlite3
import json
from pathlib import Path
from datetime import datetime

# Path to the database file
BASE_DIR = Path(__file__).resolve().parent.parent
DB_DIR = os.path.join(BASE_DIR, 'database')
DB_PATH = os.path.join(DB_DIR, 'carbon_footprint.db')


def get_db_connection():
    """
    Creates and returns a connection to the local SQLite database.
    Row factory is set to sqlite3.Row for convenient dictionary-like access.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """
    Ensures the database directory and required tables exist.
    Called automatically on application startup.
    """
    # 1. Ensure directory exists
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR, exist_ok=True)
        
    # 2. Connect and create table if it does not exist
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS calculations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                transportation REAL NOT NULL,
                electricity REAL NOT NULL,
                lpg REAL NOT NULL,
                food REAL NOT NULL,
                waste REAL NOT NULL,
                water REAL NOT NULL,
                total_monthly REAL NOT NULL,
                total_yearly REAL NOT NULL,
                largest_category TEXT NOT NULL,
                inputs_json TEXT
            )
        ''')
        conn.commit()
    finally:
        conn.close()


def save_calculation(calc_data):
    """
    Saves a newly computed carbon footprint record into SQLite.
    
    Parameters:
        calc_data (dict): Dictionary produced by calculator.compute_carbon_footprint
        
    Returns:
        int: The inserted record ID.
    """
    init_db()  # Guarantees table exists even if DB was deleted mid-session
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO calculations (
                transportation,
                electricity,
                lpg,
                food,
                waste,
                water,
                total_monthly,
                total_yearly,
                largest_category,
                inputs_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            calc_data.get('transportation', 0.0),
            calc_data.get('electricity', 0.0),
            calc_data.get('lpg', 0.0),
            calc_data.get('food', 0.0),
            calc_data.get('waste', 0.0),
            calc_data.get('water', 0.0),
            calc_data.get('total_monthly', 0.0),
            calc_data.get('total_yearly', 0.0),
            calc_data.get('largest_category', 'General'),
            json.dumps(calc_data.get('user_inputs', {}))
        ))
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def get_calculation_by_id(calc_id):
    """
    Retrieves a single calculation record by ID.
    
    Returns:
        dict or None: Formatted dictionary containing calculated values and parsed input JSON.
    """
    init_db()
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM calculations WHERE id = ?', (calc_id,))
        row = cursor.fetchone()
        
        if not row:
            return None
            
        data = dict(row)
        
        # Parse inputs JSON safely
        try:
            data['user_inputs'] = json.loads(data.get('inputs_json') or '{}')
        except (ValueError, TypeError):
            data['user_inputs'] = {}
            
        # Re-derive percentages and yearly tonnes for template rendering
        total_monthly = data['total_monthly']
        categories = {
            'transportation': data['transportation'],
            'electricity': data['electricity'],
            'lpg': data['lpg'],
            'food': data['food'],
            'waste': data['waste'],
            'water': data['water']
        }
        
        percentages = {}
        if total_monthly > 0:
            for cat, val in categories.items():
                percentages[cat] = round((val / total_monthly) * 100.0, 1)
        else:
            for cat in categories:
                percentages[cat] = 0.0
                
        data['percentages'] = percentages
        data['total_yearly_tonnes'] = round(data['total_yearly'] / 1000.0, 2)
        
        # Format date for human readability
        try:
            created_dt = datetime.fromisoformat(str(data['created_at']).replace('Z', ''))
            data['formatted_date'] = created_dt.strftime('%d %b %Y, %I:%M %p')
        except Exception:
            data['formatted_date'] = str(data['created_at'])
            
        return data
    finally:
        conn.close()


def get_all_calculations():
    """
    Retrieves all calculation history records sorted by newest first.
    
    Returns:
        list of dict: List of calculation summaries.
    """
    init_db()
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM calculations ORDER BY id DESC')
        rows = cursor.fetchall()
        
        results = []
        for row in rows:
            item = dict(row)
            item['total_yearly_tonnes'] = round(item['total_yearly'] / 1000.0, 2)
            try:
                created_dt = datetime.fromisoformat(str(item['created_at']).replace('Z', ''))
                item['formatted_date'] = created_dt.strftime('%d %b %Y, %I:%M %p')
            except Exception:
                item['formatted_date'] = str(item['created_at'])
            results.append(item)
            
        return results
    finally:
        conn.close()


def delete_calculation(calc_id):
    """
    Deletes a single calculation record by ID.
    
    Returns:
        bool: True if deleted, False otherwise.
    """
    init_db()
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM calculations WHERE id = ?', (calc_id,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


def delete_all_calculations():
    """
    Deletes all records from the calculations table.
    Preserves table structure.
    
    Returns:
        int: Number of deleted rows.
    """
    init_db()
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM calculations')
        deleted_count = cursor.rowcount
        conn.commit()
        return deleted_count
    finally:
        conn.close()
