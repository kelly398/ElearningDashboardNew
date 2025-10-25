from flask import Flask, request, jsonify
from datetime import datetime
import os
import time
import logging
from flask_cors import CORS
from extensions import db
from models import User, Module, Quiz, UserProgress, ForumPost, Badge, UserBadge

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'db.sqlite')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
CORS(app)
print("📁 Using database file:", os.path.abspath("db.sqlite"))
db.init_app(app)

# Logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Ensure DB file exists and is writable
if not os.path.exists('db.sqlite'):
    open('db.sqlite', 'a').close()
elif not os.access('db.sqlite', os.W_OK):
    raise Exception("db.sqlite is not writable. Check permissions.")

# Create tables on startup
def create_tables_on_startup():
    with app.app_context():
        db.create_all()
        db.session.commit()
        time.sleep(0.5)
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        if 'users' in tables:
            logger.debug('Tables created successfully')
        else:
            logger.error('Table creation failed')
            raise Exception("Table creation failed during startup")

try:
    create_tables_on_startup()
except Exception as e:
    logger.error(f"Startup failed: {str(e)}")
    raise

# Endpoint to recreate tables manually
@app.route('/create-tables', methods=['GET'])
def create_tables_route():
    with app.app_context():
        db.create_all()
        db.session.commit()
        time.sleep(0.5)
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        if 'users' in tables:
            return jsonify({'status': 'Tables created successfully'})
        return jsonify({'status': 'Table creation failed'}), 500

# Initialize sample data
@app.route('/init-data', methods=['GET'])
def init_data():
    with app.app_context():
        if not User.query.first():
            try:
                # Create user
                user = User(username='JohnDoe22', email='john@email.com')
                user.set_password('password123')
                db.session.add(user)
                db.session.commit()

                # Create module
                module = Module(title='SQL JOINs', category='SQL', description='Master INNER/LEFT JOINs...', duration=45, order=1)
                db.session.add(module)
                db.session.commit()

                # Create quiz
                quiz = Quiz(title='SQL JOINs Quiz', description='What JOIN combines all records?')
                db.session.add(quiz)
                db.session.commit()

                # Create user progress
                progress = UserProgress(user_id=user.id, module_id=module.id, status='InProgress', streak_count=5, score=45)
                db.session.add(progress)

                # Create forum post
                post = ForumPost(user_id=user.id, thread_id=None, content='Need JOIN syntax help!')
                db.session.add(post)

                # Create badge
                badge = Badge(name='SQL Explorer', description='Complete 3 SQL modules', icon='sql_icon.png', criteria={'mods': 3})
                db.session.add(badge)
                db.session.commit()

                # Assign badge to user
                user_badge = UserBadge(user_id=user.id, badge_id=badge.id, level=1)
                db.session.add(user_badge)
                db.session.commit()

                return jsonify({'status': 'Sample data added'})
            except Exception as e:
                db.session.rollback()
                return jsonify({'status': f'Error adding data: {str(e)}'}), 500
        return jsonify({'status': 'Data already exists'})

# Login endpoint
@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'message': 'No input data provided'}), 400

        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({'message': 'Email and password required'}), 400

        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({'message': 'User not found'}), 404

        if user.check_password(password):
            return jsonify({'message': 'Login successful', 'user': {'id': user.id, 'username': user.username, 'email': user.email}}), 200
        else:
            return jsonify({'message': 'Invalid password'}), 401

    except Exception as e:
        return jsonify({'message': 'Server error', 'error': str(e)}), 500

# Dashboard endpoint
@app.route('/dashboard-data/<int:user_id>', methods=['GET'])
def dashboard_data(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'message': 'User not found'}), 404

        # User progress
        progress_records = UserProgress.query.filter_by(user_id=user.id).all()
        progress_data = []
        for pr in progress_records:
            module_name = pr.module.title if pr.module else "Unknown Module"
            progress_data.append({
                'module': module_name,
                'status': pr.status,
                'score': pr.score or 0,
                'streak': pr.streak_count
            })

        # User badges
        user_badges = UserBadge.query.filter_by(user_id=user.id).all()
        badges_data = []
        for ub in user_badges:
            badge = Badge.query.get(ub.badge_id)
            if badge:
                badges_data.append({
                    'name': badge.name,
                    'description': badge.description,
                    'icon': badge.icon or 'default.png',
                    'level': ub.level
                })

        return jsonify({
            'user': {'id': user.id, 'username': user.username},
            'progress': progress_data,
            'badges': badges_data
        })

    except Exception as e:
        return jsonify({'message': 'Error fetching dashboard data', 'error': str(e)}), 500

# Forum endpoint
@app.route('/forum', methods=['GET', 'POST'])
def forum():
    if request.method == 'POST':
        data = request.json
        post = ForumPost(
            user_id=1,
            thread_id=data.get('thread_id'),
            content=data.get('content')
        )
        db.session.add(post)
        db.session.commit()
        return jsonify({'message': 'Post added', 'post_id': post.id})
    posts = ForumPost.query.all()
    return jsonify({'posts': [{'id': p.id, 'content': p.content, 'date': p.post_date.isoformat()} for p in posts]})

# Badges endpoint
@app.route('/badges', methods=['GET'])
def get_badges():
    badges = Badge.query.all()
    return jsonify({'badges': [{'id': b.id, 'name': b.name, 'description': b.description} for b in badges]})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
