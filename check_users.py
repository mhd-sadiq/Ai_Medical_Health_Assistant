import sqlite3
import os

# Check database
db_path = 'instance/users.db'
if os.path.exists(db_path):
    print(f"Database found: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check user table
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user'")
    if cursor.fetchone():
        print("\n✅ user table exists!")
        
        # Get all users
        cursor.execute("SELECT id, name, email, is_admin, is_superuser, is_blocked FROM user")
        users = cursor.fetchall()
        print(f"\nTotal users: {len(users)}")
        print("\nUser details:")
        for user in users:
            user_id, name, email, is_admin, is_superuser, is_blocked = user
            admin_status = "Admin" if is_admin else "Regular User"
            super_status = " (Superuser)" if is_superuser else ""
            blocked_status = " (Blocked)" if is_blocked else ""
            print(f"  - ID: {user_id}, Name: {name}, Email: {email}, Status: {admin_status}{super_status}{blocked_status}")
            
            # Check if this user would show the promote button
            if not is_admin and not is_superuser:
                print(f"    ✅ Would show 'Promote' button for this user")
            elif is_admin and not is_superuser:
                print(f"    🔄 Would show 'Demote' button for this user")
            elif is_superuser:
                print(f"    ❌ No admin action buttons for superuser")
    else:
        print("\n❌ user table does NOT exist!")
    
    conn.close()
else:
    print(f"Database not found: {db_path}") 