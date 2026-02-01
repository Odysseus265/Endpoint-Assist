"""
Endpoint Assist - Database Module
SQLite database for persistent storage of tickets, audit logs, and settings
"""

import sqlite3
import os
from datetime import datetime
from contextlib import contextmanager
import json

# Database file path
DATABASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'endpoint_assist.db')

def ensure_data_directory():
    """Ensure the data directory exists"""
    data_dir = os.path.dirname(DATABASE_PATH)
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    ensure_data_directory()
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    """Initialize the database with required tables"""
    ensure_data_directory()
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Create tickets table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tickets (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                status TEXT DEFAULT 'open',
                priority TEXT DEFAULT 'medium',
                category TEXT,
                assigned_to TEXT,
                created_by TEXT DEFAULT 'System',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                resolved_at TIMESTAMP,
                resolution TEXT
            )
        ''')
        
        # Create audit_logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_logs (
                id TEXT PRIMARY KEY,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                action TEXT NOT NULL,
                details TEXT,
                user TEXT DEFAULT 'System',
                ip_address TEXT,
                user_agent TEXT
            )
        ''')
        
        # Create settings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create device_inventory table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS device_inventory (
                id TEXT PRIMARY KEY,
                hostname TEXT,
                ip_address TEXT,
                mac_address TEXT,
                os_info TEXT,
                last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notes TEXT
            )
        ''')
        
        conn.commit()
        print("✅ Database initialized successfully")

# ==================== TICKET OPERATIONS ====================

def create_ticket(ticket_data):
    """Create a new ticket"""
    import uuid
    ticket_id = str(uuid.uuid4())
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO tickets (id, title, description, status, priority, category, assigned_to, created_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            ticket_id,
            ticket_data.get('title', 'Untitled'),
            ticket_data.get('description', ''),
            ticket_data.get('status', 'open'),
            ticket_data.get('priority', 'medium'),
            ticket_data.get('category', 'General'),
            ticket_data.get('assigned_to', ''),
            ticket_data.get('created_by', 'System')
        ))
        conn.commit()
    
    return ticket_id

def get_all_tickets(status_filter=None, limit=100):
    """Get all tickets, optionally filtered by status"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        if status_filter:
            cursor.execute('''
                SELECT * FROM tickets WHERE status = ? ORDER BY created_at DESC LIMIT ?
            ''', (status_filter, limit))
        else:
            cursor.execute('''
                SELECT * FROM tickets ORDER BY created_at DESC LIMIT ?
            ''', (limit,))
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

def get_ticket_by_id(ticket_id):
    """Get a single ticket by ID"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM tickets WHERE id = ?', (ticket_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

def update_ticket(ticket_id, ticket_data):
    """Update an existing ticket"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Build dynamic update query
        fields = []
        values = []
        
        for key in ['title', 'description', 'status', 'priority', 'category', 'assigned_to', 'resolution']:
            if key in ticket_data:
                fields.append(f'{key} = ?')
                values.append(ticket_data[key])
        
        if ticket_data.get('status') == 'resolved':
            fields.append('resolved_at = ?')
            values.append(datetime.now().isoformat())
        
        fields.append('updated_at = ?')
        values.append(datetime.now().isoformat())
        values.append(ticket_id)
        
        query = f"UPDATE tickets SET {', '.join(fields)} WHERE id = ?"
        cursor.execute(query, values)
        conn.commit()
        
        return cursor.rowcount > 0

def delete_ticket(ticket_id):
    """Delete a ticket"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM tickets WHERE id = ?', (ticket_id,))
        conn.commit()
        return cursor.rowcount > 0

def get_ticket_stats():
    """Get ticket statistics"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status = 'open' THEN 1 ELSE 0 END) as open,
                SUM(CASE WHEN status = 'in-progress' THEN 1 ELSE 0 END) as in_progress,
                SUM(CASE WHEN status = 'resolved' THEN 1 ELSE 0 END) as resolved,
                SUM(CASE WHEN status = 'closed' THEN 1 ELSE 0 END) as closed
            FROM tickets
        ''')
        
        row = cursor.fetchone()
        return dict(row) if row else {}

# ==================== AUDIT LOG OPERATIONS ====================

def add_audit_log(action, details, user="System", ip_address=None, user_agent=None):
    """Add an entry to the audit log"""
    import uuid
    log_id = str(uuid.uuid4())
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO audit_logs (id, action, details, user, ip_address, user_agent)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (log_id, action, details, user, ip_address, user_agent))
        conn.commit()
    
    return log_id

def get_audit_logs(limit=100, action_filter=None):
    """Get audit logs, optionally filtered by action"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        if action_filter:
            cursor.execute('''
                SELECT * FROM audit_logs WHERE action LIKE ? ORDER BY timestamp DESC LIMIT ?
            ''', (f'%{action_filter}%', limit))
        else:
            cursor.execute('''
                SELECT * FROM audit_logs ORDER BY timestamp DESC LIMIT ?
            ''', (limit,))
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

def clear_old_audit_logs(days=30):
    """Clear audit logs older than specified days"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            DELETE FROM audit_logs WHERE timestamp < datetime('now', ?)
        ''', (f'-{days} days',))
        conn.commit()
        return cursor.rowcount

# ==================== SETTINGS OPERATIONS ====================

def get_setting(key, default=None):
    """Get a setting value"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT value FROM settings WHERE key = ?', (key,))
        row = cursor.fetchone()
        return row['value'] if row else default

def set_setting(key, value):
    """Set a setting value"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO settings (key, value, updated_at)
            VALUES (?, ?, ?)
        ''', (key, value, datetime.now().isoformat()))
        conn.commit()

def get_all_settings():
    """Get all settings"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT key, value FROM settings')
        rows = cursor.fetchall()
        return {row['key']: row['value'] for row in rows}

# ==================== DEVICE INVENTORY OPERATIONS ====================

def add_device(device_data):
    """Add or update a device in inventory"""
    import uuid
    device_id = device_data.get('id', str(uuid.uuid4()))
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO device_inventory (id, hostname, ip_address, mac_address, os_info, notes, last_seen)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            device_id,
            device_data.get('hostname', ''),
            device_data.get('ip_address', ''),
            device_data.get('mac_address', ''),
            device_data.get('os_info', ''),
            device_data.get('notes', ''),
            datetime.now().isoformat()
        ))
        conn.commit()
    
    return device_id

def get_all_devices():
    """Get all devices from inventory"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM device_inventory ORDER BY last_seen DESC')
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

# Initialize database on module import
if __name__ == '__main__':
    init_db()
