"""
Endpoint Assist - Authentication Module
Simple authentication system with role-based access control
"""

import hashlib
import secrets
import functools
from datetime import datetime, timedelta
from flask import request, jsonify, session
from database import get_db_connection, init_db
import sqlite3

# ==================== DATABASE SETUP ====================

def init_auth_db():
    """Initialize authentication tables"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                email TEXT,
                full_name TEXT,
                role TEXT DEFAULT 'technician',
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                failed_attempts INTEGER DEFAULT 0,
                locked_until TIMESTAMP
            )
        ''')
        
        # Sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                token TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                ip_address TEXT,
                user_agent TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # Create default admin user if not exists
        cursor.execute('SELECT COUNT(*) FROM users WHERE username = ?', ('admin',))
        if cursor.fetchone()[0] == 0:
            admin_hash = hash_password('admin123')  # Default password - CHANGE IN PRODUCTION
            cursor.execute('''
                INSERT INTO users (username, password_hash, email, full_name, role)
                VALUES (?, ?, ?, ?, ?)
            ''', ('admin', admin_hash, 'admin@localhost', 'Administrator', 'admin'))
            print("✅ Default admin user created (username: admin, password: admin123)")
        
        conn.commit()

# ==================== PASSWORD UTILITIES ====================

def hash_password(password):
    """Hash a password using SHA-256 with salt"""
    salt = secrets.token_hex(16)
    hash_obj = hashlib.sha256((password + salt).encode())
    return f"{salt}${hash_obj.hexdigest()}"

def verify_password(password, password_hash):
    """Verify a password against its hash"""
    try:
        salt, hash_value = password_hash.split('$')
        hash_obj = hashlib.sha256((password + salt).encode())
        return hash_obj.hexdigest() == hash_value
    except:
        return False

def generate_token():
    """Generate a secure session token"""
    return secrets.token_urlsafe(32)

# ==================== USER OPERATIONS ====================

def create_user(username, password, email=None, full_name=None, role='technician'):
    """Create a new user"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            password_hash = hash_password(password)
            cursor.execute('''
                INSERT INTO users (username, password_hash, email, full_name, role)
                VALUES (?, ?, ?, ?, ?)
            ''', (username, password_hash, email, full_name, role))
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            return None  # Username already exists

def get_user_by_username(username):
    """Get user by username"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        row = cursor.fetchone()
        return dict(row) if row else None

def get_user_by_id(user_id):
    """Get user by ID"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id, username, email, full_name, role, is_active, created_at, last_login FROM users WHERE id = ?', (user_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

def get_all_users():
    """Get all users (without password hashes)"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id, username, email, full_name, role, is_active, created_at, last_login FROM users ORDER BY created_at DESC')
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

def update_user(user_id, **kwargs):
    """Update user fields"""
    allowed_fields = ['email', 'full_name', 'role', 'is_active']
    updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
    
    if not updates:
        return False
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        fields = ', '.join(f'{k} = ?' for k in updates.keys())
        values = list(updates.values()) + [user_id]
        cursor.execute(f'UPDATE users SET {fields} WHERE id = ?', values)
        conn.commit()
        return cursor.rowcount > 0

def change_password(user_id, new_password):
    """Change user password"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        password_hash = hash_password(new_password)
        cursor.execute('UPDATE users SET password_hash = ? WHERE id = ?', (password_hash, user_id))
        conn.commit()
        return cursor.rowcount > 0

def delete_user(user_id):
    """Delete a user"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM user_sessions WHERE user_id = ?', (user_id,))
        cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
        conn.commit()
        return cursor.rowcount > 0

# ==================== SESSION MANAGEMENT ====================

def create_session(user_id, ip_address=None, user_agent=None, expires_hours=24):
    """Create a new session for a user"""
    token = generate_token()
    expires_at = datetime.now() + timedelta(hours=expires_hours)
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO user_sessions (user_id, token, expires_at, ip_address, user_agent)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, token, expires_at.isoformat(), ip_address, user_agent))
        
        # Update last login
        cursor.execute('UPDATE users SET last_login = ? WHERE id = ?', (datetime.now().isoformat(), user_id))
        conn.commit()
    
    return token

def validate_session(token):
    """Validate a session token and return user info"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT u.id, u.username, u.email, u.full_name, u.role, u.is_active, s.expires_at
            FROM user_sessions s
            JOIN users u ON s.user_id = u.id
            WHERE s.token = ?
        ''', (token,))
        row = cursor.fetchone()
        
        if not row:
            return None
        
        user = dict(row)
        
        # Check if session expired
        expires_at = datetime.fromisoformat(user['expires_at'])
        if datetime.now() > expires_at:
            invalidate_session(token)
            return None
        
        # Check if user is active
        if not user['is_active']:
            return None
        
        return user

def invalidate_session(token):
    """Invalidate a session"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM user_sessions WHERE token = ?', (token,))
        conn.commit()

def invalidate_all_sessions(user_id):
    """Invalidate all sessions for a user"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM user_sessions WHERE user_id = ?', (user_id,))
        conn.commit()

def cleanup_expired_sessions():
    """Remove expired sessions"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM user_sessions WHERE expires_at < ?', (datetime.now().isoformat(),))
        conn.commit()
        return cursor.rowcount

# ==================== AUTHENTICATION ====================

def authenticate(username, password):
    """Authenticate a user and return session token"""
    user = get_user_by_username(username)
    
    if not user:
        return None, "Invalid username or password"
    
    if not user['is_active']:
        return None, "Account is disabled"
    
    # Check if account is locked
    if user['locked_until']:
        locked_until = datetime.fromisoformat(user['locked_until'])
        if datetime.now() < locked_until:
            return None, f"Account is locked. Try again later."
    
    if not verify_password(password, user['password_hash']):
        # Increment failed attempts
        with get_db_connection() as conn:
            cursor = conn.cursor()
            new_attempts = user['failed_attempts'] + 1
            
            # Lock account after 5 failed attempts
            if new_attempts >= 5:
                locked_until = datetime.now() + timedelta(minutes=15)
                cursor.execute('UPDATE users SET failed_attempts = ?, locked_until = ? WHERE id = ?', 
                             (new_attempts, locked_until.isoformat(), user['id']))
            else:
                cursor.execute('UPDATE users SET failed_attempts = ? WHERE id = ?', (new_attempts, user['id']))
            conn.commit()
        
        return None, "Invalid username or password"
    
    # Reset failed attempts on successful login
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET failed_attempts = 0, locked_until = NULL WHERE id = ?', (user['id'],))
        conn.commit()
    
    return user, None

# ==================== DECORATORS ====================

def get_current_user():
    """Get the current authenticated user from request"""
    # Check Authorization header
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header[7:]
        return validate_session(token)
    
    # Check session cookie
    token = session.get('auth_token')
    if token:
        return validate_session(token)
    
    return None

def login_required(f):
    """Decorator to require authentication"""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            return jsonify({"status": "error", "message": "Authentication required"}), 401
        request.current_user = user
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to require admin role"""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            return jsonify({"status": "error", "message": "Authentication required"}), 401
        if user['role'] != 'admin':
            return jsonify({"status": "error", "message": "Admin access required"}), 403
        request.current_user = user
        return f(*args, **kwargs)
    return decorated_function

def role_required(*roles):
    """Decorator to require specific roles"""
    def decorator(f):
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            user = get_current_user()
            if not user:
                return jsonify({"status": "error", "message": "Authentication required"}), 401
            if user['role'] not in roles:
                return jsonify({"status": "error", "message": f"Access denied. Required roles: {', '.join(roles)}"}), 403
            request.current_user = user
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# ==================== ROLE DEFINITIONS ====================

ROLES = {
    'admin': {
        'name': 'Administrator',
        'description': 'Full system access',
        'permissions': ['all']
    },
    'technician': {
        'name': 'IT Technician',
        'description': 'Can run diagnostics, manage tickets, view reports',
        'permissions': ['diagnostics', 'tickets', 'reports', 'tools']
    },
    'viewer': {
        'name': 'Viewer',
        'description': 'Read-only access to dashboards and reports',
        'permissions': ['view_dashboard', 'view_reports']
    }
}

def get_user_permissions(role):
    """Get permissions for a role"""
    return ROLES.get(role, {}).get('permissions', [])

def has_permission(user, permission):
    """Check if user has a specific permission"""
    if not user:
        return False
    permissions = get_user_permissions(user['role'])
    return 'all' in permissions or permission in permissions
