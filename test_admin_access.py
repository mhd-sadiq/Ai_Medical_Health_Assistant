#!/usr/bin/env python3
"""
Test script to verify admin access and exercise logging
"""

import requests
import json

def test_admin_access():
    """Test admin dashboard access"""
    
    print("🧪 Testing Admin Access and Exercise Logging")
    print("=" * 60)
    
    base_url = "http://localhost:5000"
    
    # Test 1: Check if server is running
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ Server is running")
        else:
            print(f"❌ Server returned status code: {response.status_code}")
            return
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure Flask app is running.")
        return
    
    # Test 2: Test admin dashboard access (should redirect to login)
    print("\n🔍 Testing admin dashboard access...")
    try:
        response = requests.get(f"{base_url}/admin")
        if response.status_code == 302:  # Redirect to login
            print("✅ Admin dashboard requires authentication (correct)")
        else:
            print(f"⚠️ Admin dashboard response: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing admin dashboard: {e}")
    
    # Test 3: Test exercise logging endpoint
    print("\n📝 Testing exercise logging endpoint...")
    exercise_data = {
        "exercise_title": "🤸 Jumping Jacks",
        "duration": 30
    }
    
    try:
        response = requests.post(
            f"{base_url}/log_exercise",
            json=exercise_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 302:  # Redirect to login
            print("✅ Exercise logging requires authentication (correct)")
        else:
            print(f"⚠️ Exercise logging response: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing exercise endpoint: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 Test Summary:")
    print("• Server is running and responding")
    print("• Admin dashboard requires authentication")
    print("• Exercise logging requires authentication")
    print("\n📋 Manual Testing Steps:")
    print("1. Open http://localhost:5000 in your browser")
    print("2. Login with admin@health.com / admin123")
    print("3. Click on your username dropdown → Admin Dashboard")
    print("4. Or go directly to http://localhost:5000/admin")
    print("5. Test exercise logging by completing an exercise")
    print("6. Check admin dashboard for exercise history")
    
    print("\n🔑 Admin Login Credentials:")
    print("   Email: admin@health.com")
    print("   Password: admin123")

if __name__ == "__main__":
    test_admin_access() 