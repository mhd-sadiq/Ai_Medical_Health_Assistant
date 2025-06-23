#!/usr/bin/env python3
"""
Script to make user "sadiq.k" an admin
"""

from app import app, db, User

def make_sadiq_admin():
    """Make user sadiq.k an admin"""
    
    print("👑 Making sadiq.k an Admin User")
    print("=" * 50)
    
    with app.app_context():
        try:
            # Find the user sadiq.k
            user = User.query.filter_by(name="sadiq.k").first()
            
            if user:
                print(f"✅ Found user: {user.name}")
                print(f"   Email: {user.email}")
                print(f"   Current Is Admin: {user.is_admin}")
                print(f"   Current Is Superuser: {user.is_superuser}")
                
                # Update admin permissions
                user.is_admin = True
                user.is_superuser = True
                user.is_blocked = False
                
                db.session.commit()
                
                print("\n✅ Successfully made sadiq.k an admin!")
                print(f"   Updated Is Admin: {user.is_admin}")
                print(f"   Updated Is Superuser: {user.is_superuser}")
                print(f"   Is Blocked: {user.is_blocked}")
                
            else:
                print("❌ User 'sadiq.k' not found!")
                print("\n📋 Available users:")
                all_users = User.query.all()
                for u in all_users:
                    print(f"   - {u.name} (Email: {u.email}, Admin: {u.is_admin})")
                
                # Check if there are similar names
                similar_users = User.query.filter(User.name.like('%sadiq%')).all()
                if similar_users:
                    print("\n🔍 Similar users found:")
                    for u in similar_users:
                        print(f"   - {u.name} (Email: {u.email})")
                
        except Exception as e:
            print(f"❌ Error updating user: {e}")
            db.session.rollback()
    
    print("\n" + "=" * 50)
    print("📋 Next Steps:")
    print("1. Start your Flask app: python app.py")
    print("2. Go to http://localhost:5000")
    print("3. Login with sadiq.k's credentials")
    print("4. Access admin dashboard from the user dropdown")
    print("5. Or go directly to http://localhost:5000/admin")

if __name__ == "__main__":
    make_sadiq_admin() 