import sqlite3
import os
from werkzeug.security import generate_password_hash

# Check database
db_path = 'instance/users.db'
if os.path.exists(db_path):
    print(f"Database found: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if test user already exists
    cursor.execute("SELECT id FROM user WHERE email = 'test@example.com'")
    if cursor.fetchone():
        print("Test user already exists!")
    else:
        # Create test user
        name = "Test User"
        email = "test@example.com"
        password_hash = generate_password_hash("test123")
        
        cursor.execute("""
            INSERT INTO user (name, email, password_hash, is_admin, is_superuser, is_blocked)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, email, password_hash, False, False, False))
        
        conn.commit()
        print(f"Created test user: {name} ({email})")
        print("Password: test123")
        print("This user is NOT an admin and should show the 'Promote' button")
    
    # Show all users
    cursor.execute("SELECT id, name, email, is_admin, is_superuser, is_blocked FROM user")
    users = cursor.fetchall()
    print(f"\nTotal users: {len(users)}")
    for user in users:
        user_id, name, email, is_admin, is_superuser, is_blocked = user
        admin_status = "Admin" if is_admin else "Regular User"
        super_status = " (Superuser)" if is_superuser else ""
        blocked_status = " (Blocked)" if is_blocked else ""
        print(f"  - ID: {user_id}, Name: {name}, Email: {email}, Status: {admin_status}{super_status}{blocked_status}")
    
    conn.close()
else:
    print(f"Database not found: {db_path}") 