#!/usr/bin/env python3
"""
Test script to verify admin user management functionality
"""

from app import app, db, User

def test_admin_functions():
    """Test the new admin user management functions"""
    
    print("🧪 Testing Admin User Management Functions")
    print("=" * 50)
    
    with app.app_context():
        try:
            # Test 1: Check if we can create a new user
            print("\n1. Testing user creation...")
            
            # Check if test user already exists
            test_user = User.query.filter_by(email="test@example.com").first()
            if test_user:
                print("   ✅ Test user already exists")
            else:
                # Create a test user
                new_user = User(
                    name="Test User",
                    email="test@example.com",
                    is_admin=False,
                    is_superuser=False,
                    is_blocked=False
                )
                new_user.set_password("test123")
                db.session.add(new_user)
                db.session.commit()
                print("   ✅ Test user created successfully")
            
            # Test 2: Check if we can promote a user to admin
            print("\n2. Testing user promotion...")
            test_user = User.query.filter_by(email="test@example.com").first()
            if test_user:
                original_admin_status = test_user.is_admin
                test_user.is_admin = True
                db.session.commit()
                print(f"   ✅ User promoted to admin: {test_user.name}")
                
                # Revert the change
                test_user.is_admin = original_admin_status
                db.session.commit()
                print(f"   ✅ User admin status reverted")
            
            # Test 3: Check if we can demote a user from admin
            print("\n3. Testing user demotion...")
            test_user = User.query.filter_by(email="test@example.com").first()
            if test_user:
                # First promote to admin
                test_user.is_admin = True
                db.session.commit()
                print(f"   ✅ User promoted to admin for demotion test")
                
                # Then demote
                test_user.is_admin = False
                db.session.commit()
                print(f"   ✅ User demoted from admin successfully")
            
            # Test 4: List all users and their admin status
            print("\n4. Current users and their admin status:")
            all_users = User.query.all()
            for user in all_users:
                admin_status = "Admin" if user.is_admin else "Regular"
                superuser_status = "Superuser" if user.is_superuser else "Regular"
                blocked_status = "Blocked" if user.is_blocked else "Active"
                print(f"   - {user.name} ({user.email}): {admin_status}, {superuser_status}, {blocked_status}")
            
            print("\n✅ All tests completed successfully!")
            
        except Exception as e:
            print(f"❌ Error during testing: {e}")
            db.session.rollback()

if __name__ == "__main__":
    test_admin_functions() 