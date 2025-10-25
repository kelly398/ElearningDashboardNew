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

# Configure logging
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
                user = User(username='JohnDoe22', email='john@email.com')
                user.set_password('password123')
                db.session.add(user)
                db.session.commit()

                module = Module(title='SQL JOINs', category='SQL', description='Master INNER/LEFT JOINs...', duration=45, order=3)
                db.session.add(module)
                db.session.commit()

                quiz = Quiz(title='SQL JOINs Quiz', description='What JOIN combines all records?')
                db.session.add(quiz)
                db.session.commit()

                progress = UserProgress(user_id=user.id, module_id=module.id, status='InProgress', streak_count=5, score=0)
                post = ForumPost(user_id=user.id, thread_id=None, content='Need JOIN syntax help!')
                badge = Badge(name='SQL Explorer', description='Complete 3 SQL modules', icon='sql_icon.png', criteria={'mods': 3})
                db.session.add_all([progress, post, badge])
                db.session.commit()

                user_badge = UserBadge(user_id=user.id, badge_id=badge.id)
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

# Basic forum endpoint
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
# Quiz endpoint
@app.route('/quiz/<int:quiz_id>', methods=['GET', 'POST'])
def quiz(quiz_id):
    user_id = 1  # Replace with actual authenticated user ID in production
    quiz = Quiz.query.get_or_404(quiz_id)

    # Get or create progress record for this user and quiz
    progress = UserProgress.query.filter_by(user_id=user_id, quiz_id=quiz.id).first()
    if not progress:
        progress = UserProgress(user_id=user_id, quiz_id=quiz.id, module_id=None, status='Not Started', score=0, streak_count=0)
        db.session.add(progress)
        db.session.commit()

    if request.method == 'POST':
        data = request.get_json()
        answer = data.get('answer')
        if not answer:
            return jsonify({'message': 'Answer is required'}), 400

        # Example logic: correct answer is stored in quiz.description (or extend model)
        correct_answer = getattr(quiz, 'correct_answer', None)
        if correct_answer and answer.strip().lower() == correct_answer.strip().lower():
            progress.score = (progress.score or 0) + 10  # increment score
            progress.streak_count += 1
            progress.status = 'Completed'
            db.session.commit()
            return jsonify({
                'message': 'Correct answer!',
                'score': progress.score,
                'streak': progress.streak_count
            })
        else:
            progress.streak_count = max(0, progress.streak_count - 1)
            progress.status = 'In Progress'
            db.session.commit()
            return jsonify({
                'message': 'Incorrect answer',
                'score': progress.score,
                'streak': progress.streak_count
            })

    # GET request returns quiz info
    return jsonify({
        'quiz_id': quiz.id,
        'title': quiz.title,
        'description': quiz.description,
        'status': progress.status,
        'score': progress.score,
        'streak': progress.streak_count
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
