#!/usr/bin/env python3
"""
Script to remove the admin user named 'Health Assistant Admin'
"""

from app import app, db, User

def remove_health_admin():
    print("🗑️ Removing admin user named 'Health Assistant Admin'")
    print("=" * 50)
    with app.app_context():
        try:
            user = User.query.filter_by(name="Health Assistant Admin").first()
            if user:
                print(f"✅ Found user: {user.name} ({user.email})")
                db.session.delete(user)
                db.session.commit()
                print("✅ Successfully removed 'Health Assistant Admin' from the database.")
            else:
                print("❌ No user named 'Health Assistant Admin' found.")
        except Exception as e:
            print(f"❌ Error removing user: {e}")
            db.session.rollback()
    print("\n" + "=" * 50)
    print("Done.")

if __name__ == "__main__":
    remove_health_admin() 