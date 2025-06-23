import os
from app import app, db

def init_db():
    # Ensure instance directory exists
    instance_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance')
    os.makedirs(instance_path, exist_ok=True)
    
    with app.app_context():
        # Create all database tables
        db.create_all()
        print("Database initialized!")

if __name__ == '__main__':
    init_db() 