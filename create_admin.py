#!/usr/bin/env python3
"""
Script to create a proper admin user
"""

from app import app, db, User

def create_admin_user():
    """Create a proper admin user"""
    
    print("👑 Creating Admin User")
    print("=" * 50)
    
    with app.app_context():
        try:
            # Check if admin already exists
            admin = User.query.filter_by(email="admin@health.com").first()
            
            if admin:
                print("✅ Admin user already exists!")
                print(f"   Email: {admin.email}")
                print(f"   Name: {admin.name}")
                print(f"   Is Admin: {admin.is_admin}")
                print(f"   Is Superuser: {admin.is_superuser}")
                
                # Update admin permissions if needed
                if not admin.is_admin or not admin.is_superuser:
                    admin.is_admin = True
                    admin.is_superuser = True
                    db.session.commit()
                    print("✅ Updated admin permissions!")
            else:
                # Create new admin user
                admin = User(
                    name="Health Assistant Admin",
                    email="admin@health.com",
                    is_admin=True,
                    is_superuser=True,
                    is_blocked=False
                )
                admin.set_password("admin123")
                
                db.session.add(admin)
                db.session.commit()
                
                print("✅ Admin user created successfully!")
                print("   Email: admin@health.com")
                print("   Password: admin123")
                print("   Is Admin: True")
                print("   Is Superuser: True")
            
            # Verify admin user
            admin = User.query.filter_by(email="admin@health.com").first()
            if admin and admin.is_admin and admin.is_superuser:
                print("\n🎯 Admin user is ready!")
                print("   You can now log in and access the admin dashboard.")
            else:
                print("\n❌ Admin user creation failed!")
                
        except Exception as e:
            print(f"❌ Error creating admin user: {e}")
            db.session.rollback()
    
    print("\n" + "=" * 50)
    print("📋 Next Steps:")
    print("1. Start your Flask app: python app.py")
    print("2. Go to http://localhost:5000")
    print("3. Login with admin@health.com / admin123")
    print("4. Access admin dashboard at /admin")

if __name__ == "__main__":
    create_admin_user() 