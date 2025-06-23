from app import app, db, User
from getpass import getpass
from zoneinfo import ZoneInfo

email = input("Enter the email of the user to promote to superuser: ").strip()

with app.app_context():
    user = User.query.filter_by(email=email).first()
    if user:
        user.is_superuser = True
        db.session.commit()
        print(f"User {user.email} is now a superuser!")
    else:
        print("User not found.")

    if user:
        print(f'User with email {email} found. Updating to superuser...')
    else:
        name = input('Enter name for new superuser: ').strip()
        password = getpass('Enter password for new superuser: ')
        user = User(name=name, email=email)  # type: ignore
        user.set_password(password)
        db.session.add(user)
        db.session.flush()  # Ensure user gets an ID if needed

    user.is_admin = True
    user.is_superuser = True
    user.is_blocked = False
    db.session.commit()
    print(f'Success! {email} is now a superuser.') 