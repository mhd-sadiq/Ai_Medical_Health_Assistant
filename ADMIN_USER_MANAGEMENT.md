# Admin User Management Features

This document describes the new user management features added to the admin dashboard.

## Overview

The admin dashboard now includes comprehensive user management capabilities that allow administrators to:

1. **Add new users** - Create new user accounts directly from the admin dashboard
2. **Promote users to admin** - Grant admin privileges to existing users
3. **Demote admins** - Remove admin privileges from users
4. **Block/unblock users** - Control user access to the system
5. **Delete users** - Remove users from the system

## Access Requirements

- Only users with `is_admin=True` or `is_superuser=True` can access these features
- Superusers have additional privileges and cannot be demoted through the web interface

## Features

### 1. Add New User

**Location**: Admin Dashboard → "Add New User" button

**Form Fields**:
- **Full Name**: User's display name
- **Email Address**: Unique email for login
- **Password**: Minimum 6 characters
- **Confirm Password**: Must match password
- **Make this user an admin**: Checkbox to grant admin privileges

**Validation**:
- All fields are required
- Email must be unique
- Password must be at least 6 characters
- Passwords must match

### 2. Promote User to Admin

**Two Methods**:

#### Method 1: From User List
- Click "Promote" button next to any regular user in the user table
- Confirmation dialog will appear
- User will be promoted to admin immediately

#### Method 2: From Promotion Form
- Click "Promote to Admin" button in the User Management section
- Select user from dropdown (only shows non-admin users)
- Click "Promote to Admin" button

### 3. Demote Admin

**Location**: Admin Dashboard → User table → "Demote" button

**Restrictions**:
- Cannot demote superusers
- Cannot demote yourself
- Only admins can be demoted

### 4. Block/Unblock Users

**Location**: Admin Dashboard → User table → "Block"/"Unblock" buttons

**Features**:
- Blocked users cannot log in
- Admins can unblock users
- Cannot block yourself

### 5. Delete Users

**Location**: Admin Dashboard → User table → "Delete" button

**Restrictions**:
- Cannot delete yourself
- Confirmation dialog required
- All user data will be permanently removed

## User Roles

### Regular User
- `is_admin=False`
- `is_superuser=False`
- Can access all health features
- Cannot access admin dashboard

### Admin User
- `is_admin=True`
- `is_superuser=False`
- Can access admin dashboard
- Can manage users (add, promote, demote, block, delete)
- Cannot create superusers

### Superuser
- `is_admin=True`
- `is_superuser=True`
- Full system access
- Can create other superusers
- Cannot be demoted through web interface

## Security Features

1. **Access Control**: All admin routes require admin/superuser privileges
2. **Self-Protection**: Admins cannot delete or block themselves
3. **Superuser Protection**: Superusers cannot be demoted through web interface
4. **Confirmation Dialogs**: Destructive actions require confirmation
5. **Input Validation**: All form inputs are validated server-side
6. **Error Handling**: Comprehensive error handling with user-friendly messages

## Database Changes

No new database tables were added. The existing `User` model already supports:
- `is_admin` (Boolean)
- `is_superuser` (Boolean)
- `is_blocked` (Boolean)

## API Endpoints

### New Routes Added:

1. `POST /admin/add_user` - Create new user
2. `POST /admin/promote_user` - Promote user via email selection
3. `POST /admin/promote_user_admin/<user_id>` - Promote user via user ID
4. `POST /admin/demote_user/<user_id>` - Demote admin user

### Existing Routes Enhanced:

- All admin routes now include proper access control
- Enhanced error handling and user feedback

## Usage Examples

### Creating a New Admin User
1. Go to Admin Dashboard
2. Click "Add New User"
3. Fill in the form:
   - Name: "John Doe"
   - Email: "john@example.com"
   - Password: "secure123"
   - Confirm Password: "secure123"
   - Check "Make this user an admin"
4. Click "Create User"

### Promoting an Existing User
1. Go to Admin Dashboard
2. Find the user in the table
3. Click "Promote" button
4. Confirm the action

### Demoting an Admin
1. Go to Admin Dashboard
2. Find the admin user in the table
3. Click "Demote" button
4. Confirm the action

## Troubleshooting

### Common Issues:

1. **"Access denied" error**
   - Ensure you have admin privileges
   - Check if your account is blocked

2. **"User not found" error**
   - Verify the user email exists
   - Check for typos in email addresses

3. **"Cannot demote superuser" error**
   - Superusers must be demoted manually in the database
   - Use the provided scripts for superuser management

4. **"Email already exists" error**
   - Choose a different email address
   - Check if user was previously deleted

## Testing

Run the test script to verify functionality:
```bash
python test_admin_functions.py
```

This will test:
- User creation
- User promotion
- User demotion
- Database operations 