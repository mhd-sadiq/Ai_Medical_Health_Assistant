# Admin & Superuser Features

## Database Migration
After updating the User model, you need to migrate your database. If using SQLite and no migration tool, you may need to delete the old database and re-initialize:

```
rm instance/users.db  # or delete manually on Windows
python init_db.py
```

## Creating a Superuser
You can create a superuser by running a script or using the Flask shell. Example (Flask shell):

```
from app import db, User
user = User(name='admin', email='admin@example.com')
user.set_password('yourpassword')
user.is_admin = True
user.is_superuser = True
db.session.add(user)
db.session.commit()
```

## Accessing the Admin Dashboard
- Log in as a user with `is_admin` or `is_superuser` set to `True`.
- Go to `/admin` to access the dashboard.
