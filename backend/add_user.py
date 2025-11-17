# backend/add_user.py
from app import app, db
from models import User
from werkzeug.security import generate_password_hash

def add_sumayah():
    with app.app_context():
        # Check if user exists
        if User.query.filter_by(email='sumayahkh@hotmail.com').first():
            print("User already exists!")
            return

        # Create new user
        user = User(
            username='Sumayah',
            email='sumayahkh@hotmail.com',
            password_hash=generate_password_hash('123456')
        )
        db.session.add(user)
        db.session.commit()
        print("Sumayah added successfully!")
        print("Login: sumayahkh@hotmail.com / 123456")

if __name__ == '__main__':
    add_sumayah()