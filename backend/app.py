from flask import Flask, request, jsonify
from datetime import datetime
import os
import time
import logging
from flask_cors import CORS
from sqlalchemy import func
from extensions import db
from models import (
    User,
    Module,
    Quiz,
    Question,
    UserProgress,
    ForumPost,
    Badge,
    UserBadge,
)

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'db.sqlite')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
CORS(app)
print("Using database file:", os.path.abspath("db.sqlite"))
db.init_app(app)

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

POINTS_PER_CORRECT = 20

QUESTION_POOL_SEED = [
    {
        'title': 'Cloud Computing',
        'description': 'Assess core cloud-computing concepts.',
        'topic': 'Cloud Computing',
        'questions': [
            {
                'question': 'Which of the following is NOT an IaaS provider?',
                'options': ['AWS EC2', 'Azure VM', 'Google Docs', 'DigitalOcean'],
                'answer': 'Google Docs',
                'time_limit': 45,
            },
            {
                'question': 'What does PaaS stand for?',
                'options': [
                    'Product as a Service',
                    'Platform as a Service',
                    'Protocol as a Service',
                    'Power as a Service',
                ],
                'answer': 'Platform as a Service',
                'time_limit': 45,
            },
            {
                'question': 'Which AWS service is considered serverless compute?',
                'options': ['EC2', 'S3', 'AWS Lambda', 'RDS'],
                'answer': 'AWS Lambda',
                'time_limit': 45,
            },
            {
                'question': 'What does VPC stand for?',
                'options': [
                    'Virtual Public Cloud',
                    'Virtual Private Cloud',
                    'Very Private Container',
                    'Visual Processing Center',
                ],
                'answer': 'Virtual Private Cloud',
                'time_limit': 45,
            },
            {
                'question': 'Which AWS storage option is object storage?',
                'options': ['EBS', 'EFS', 'S3', 'RDS'],
                'answer': 'S3',
                'time_limit': 45,
            },
        ],
    },
    {
        'title': 'Web Design with JavaScript',
        'description': 'JavaScript and front-end fundamentals.',
        'topic': 'Web Design with JavaScript',
        'questions': [
            {
                'question': 'What does DOM stand for?',
                'options': [
                    'Data Object Model',
                    'Document Object Model',
                    'Dynamic Object Method',
                    'Display Object Manager',
                ],
                'answer': 'Document Object Model',
                'time_limit': 45,
            },
            {
                'question': 'Which of the following is NOT a JavaScript framework?',
                'options': ['React', 'Vue', 'Angular', 'Photoshop'],
                'answer': 'Photoshop',
                'time_limit': 45,
            },
            {
                'question': 'What does the === operator do in JavaScript?',
                'options': [
                    'Assignment',
                    'Loose equality',
                    'Strict equality',
                    'Type conversion',
                ],
                'answer': 'Strict equality',
                'time_limit': 45,
            },
            {
                'question': 'In an object method, what does this refer to?',
                'options': ['Global object', 'The function', 'The object', 'undefined'],
                'answer': 'The object',
                'time_limit': 45,
            },
            {
                'question': 'What is event bubbling?',
                'options': [
                    'Events travel down the DOM tree',
                    'Events propagate up the DOM tree',
                    'Events stop immediately',
                    'Events loop forever',
                ],
                'answer': 'Events propagate up the DOM tree',
                'time_limit': 45,
            },
        ],
    },
    {
        'title': 'Data Structures',
        'description': 'Core data structure knowledge check.',
        'topic': 'Data Structures',
        'questions': [
            {
                'question': 'Which data structure uses the LIFO principle?',
                'options': ['Queue', 'Array', 'Stack', 'Tree'],
                'answer': 'Stack',
                'time_limit': 45,
            },
            {
                'question': 'Which data structure uses the FIFO principle?',
                'options': ['Stack', 'Queue', 'List', 'Graph'],
                'answer': 'Queue',
                'time_limit': 45,
            },
            {
                'question': 'Which structure typically offers O(1) average lookup time?',
                'options': ['Array', 'Linked List', 'Hash Table', 'Binary Tree'],
                'answer': 'Hash Table',
                'time_limit': 45,
            },
            {
                'question': 'Which structure is best suited for contiguous sorting?',
                'options': ['Linked List', 'Array', 'Stack', 'Queue'],
                'answer': 'Array',
                'time_limit': 45,
            },
            {
                'question': 'Which approach is used for graph traversal?',
                'options': ['LIFO', 'FIFO', 'BFS/DFS', 'Hashing'],
                'answer': 'BFS/DFS',
                'time_limit': 45,
            },
        ],
    },
    {
        'title': 'Deep Learning',
        'description': 'Deep learning fundamentals and terminology.',
        'topic': 'Deep Learning',
        'questions': [
            {
                'question': 'What is a neuron in a neural network?',
                'options': ['Layer', 'Basic unit', 'Dataset', 'GPU'],
                'answer': 'Basic unit',
                'time_limit': 45,
            },
            {
                'question': 'What does backpropagation do?',
                'options': [
                    'Data collection',
                    'Model saving',
                    'Optimizes weights via gradient descent',
                    'Visualization',
                ],
                'answer': 'Optimizes weights via gradient descent',
                'time_limit': 45,
            },
            {
                'question': 'What is overfitting?',
                'options': [
                    'Too good on training data',
                    'Too bad on test data',
                    'No training occurred',
                    'No data provided',
                ],
                'answer': 'Too good on training data',
                'time_limit': 45,
            },
            {
                'question': 'What are CNNs primarily used for?',
                'options': ['Text', 'Audio', 'Images', 'Time series'],
                'answer': 'Images',
                'time_limit': 45,
            },
            {
                'question': 'What is ReLU?',
                'options': ['Optimizer', 'Loss function', 'Activation function', 'Layer'],
                'answer': 'Activation function',
                'time_limit': 45,
            },
        ],
    },
]


def seed_question_pool(force=False):
    """Seed the quiz question pool so every topic has questions available."""
    with app.app_context():
        if Question.query.first() and not force:
            return

        if force:
            Question.query.delete()
            db.session.commit()

        for quiz_data in QUESTION_POOL_SEED:
            quiz = Quiz.query.filter_by(title=quiz_data['title']).first()
            if not quiz:
                quiz = Quiz(
                    title=quiz_data['title'],
                    description=quiz_data.get('description'),
                )
                db.session.add(quiz)
                db.session.flush()

            existing_questions = {q.question_text for q in quiz.questions}
            for question_data in quiz_data['questions']:
                if question_data['question'] in existing_questions and not force:
                    continue
                question_record = Question(
                    quiz_id=quiz.id,
                    topic=quiz_data['topic'],
                    question_text=question_data['question'],
                    options=question_data['options'],
                    correct_answer=question_data['answer'],
                    time_limit_seconds=question_data.get('time_limit', 45),
                )
                db.session.add(question_record)

        db.session.commit()
        logger.debug('Question pool seeded with %d quizzes', len(QUESTION_POOL_SEED))


def quiz_target_score(quiz):
    if not quiz:
        return 100
    total_questions = len(quiz.questions)
    target = total_questions * POINTS_PER_CORRECT
    return target if target > 0 else 100

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
    seed_question_pool()
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
                
                user2 = User(username='Sumayah', email='sumayahkh@hotmail.com')
                user2.set_password('123456')
                db.session.add(user2)
                db.session.commit()
                
                user2.set_password('123456')
                db.session.add(user2)
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


@app.route('/dashboard/<int:user_id>', methods=['GET'])
def get_user_dashboard(user_id):
    user = User.query.get_or_404(user_id)

    progress_records = UserProgress.query.filter_by(user_id=user.id).all()
    progress_payload = []
    for record in progress_records:
        label = None
        if record.module:
            label = record.module.title
        elif record.quiz:
            label = record.quiz.title
        else:
            label = 'Learning Progress'

        target_score = quiz_target_score(record.quiz)
        percent_complete = 0
        if target_score:
            percent_complete = min(100, int(((record.score or 0) / target_score) * 100))

        progress_payload.append({
            'id': record.id,
            'module_id': record.module_id,
            'quiz_id': record.quiz_id,
            'module_name': label,
            'status': record.status,
            'score': record.score or 0,
            'streak': record.streak_count or 0,
            'percent_complete': percent_complete,
        })

    if not progress_payload:
        modules = Module.query.order_by(Module.order).all()
        for module in modules:
            progress_payload.append({
                'id': f"module-{module.id}",
                'module_id': module.id,
                'quiz_id': None,
                'module_name': module.title,
                'status': 'Not Started',
                'score': 0,
                'streak': 0,
                'percent_complete': 0,
            })

    badges = UserBadge.query.filter_by(user_id=user.id).all()
    badges_payload = []
    for badge in badges:
        badges_payload.append({
            'id': badge.id,
            'name': badge.badge.name if badge.badge else 'Badge',
            'description': badge.badge.description if badge.badge else '',
            'level': badge.level,
            'awarded_date': badge.awarded_date.isoformat(),
        })

    return jsonify({
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
        },
        'progress': progress_payload,
        'badges': badges_payload,
    })


@app.route('/quizzes', methods=['GET'])
def list_quizzes():
    quizzes = Quiz.query.all()
    response = []
    for quiz in quizzes:
        response.append({
            'id': quiz.id,
            'title': quiz.title,
            'description': quiz.description,
            'question_count': len(quiz.questions),
            'topic': quiz.questions[0].topic if quiz.questions else None,
        })
    return jsonify({'quizzes': response})


@app.route('/quiz/<int:quiz_id>/questions', methods=['GET'])
def get_quiz_questions(quiz_id):
    limit = request.args.get('limit', default=5, type=int)
    topic = request.args.get('topic')
    quiz = Quiz.query.get_or_404(quiz_id)

    limit = 5 if not limit or limit <= 0 else min(limit, 20)
    query = Question.query.filter_by(quiz_id=quiz.id)
    if topic:
        query = query.filter(Question.topic == topic)

    questions = query.order_by(func.random()).limit(limit).all()
    if not questions:
        return jsonify({'message': 'No questions available for this quiz'}), 404

    question_payload = []
    for question in questions:
        question_payload.append({
            'id': question.id,
            'topic': question.topic,
            'question': question.question_text,
            'options': question.options,
            'time_limit_seconds': question.time_limit_seconds,
        })

    return jsonify({
        'quiz': {
            'id': quiz.id,
            'title': quiz.title,
            'description': quiz.description,
            'question_count': len(quiz.questions),
        },
        'questions': question_payload,
    })


@app.route('/quiz/<int:quiz_id>/answer', methods=['POST'])
def submit_quiz_answer(quiz_id):
    data = request.get_json() or {}
    question_id = data.get('question_id')
    answer = data.get('answer')
    time_taken = data.get('time_taken')
    time_expired = data.get('time_expired', False)
    user_id = data.get('user_id')

    if not question_id:
        return jsonify({'message': 'question_id is required'}), 400
    if not user_id:
        return jsonify({'message': 'user_id is required'}), 400

    quiz = Quiz.query.get_or_404(quiz_id)
    question = Question.query.filter_by(id=question_id, quiz_id=quiz.id).first()
    if not question:
        return jsonify({'message': 'Question not found for this quiz'}), 404

    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    allowed_time = question.time_limit_seconds or 0
    if not time_expired and time_taken is not None and allowed_time and time_taken > allowed_time:
        time_expired = True

    progress = UserProgress.query.filter_by(user_id=user.id, quiz_id=quiz.id).first()
    if not progress:
        progress = UserProgress(
            user_id=user.id,
            quiz_id=quiz.id,
            module_id=None,
            status='Not Started',
            score=0,
            streak_count=0,
        )
        db.session.add(progress)
        db.session.commit()

    target_score = quiz_target_score(quiz)
    answered_correctly = False
    message = ''

    if time_expired:
        message = 'Time expired for this question.'
    elif not answer:
        return jsonify({'message': 'Answer is required'}), 400
    else:
        answered_correctly = answer.strip().lower() == question.correct_answer.strip().lower()
        message = 'Correct answer!' if answered_correctly else 'Incorrect answer.'

    if answered_correctly:
        progress.score = (progress.score or 0) + POINTS_PER_CORRECT
        progress.streak_count = (progress.streak_count or 0) + 1
        progress.status = 'Completed' if (progress.score or 0) >= target_score else 'In Progress'
    else:
        progress.streak_count = max(0, (progress.streak_count or 0) - 1)
        if progress.status == 'Not Started':
            progress.status = 'In Progress'

    db.session.commit()

    return jsonify({
        'correct': answered_correctly,
        'message': message,
        'correct_answer': question.correct_answer,
        'score_delta': POINTS_PER_CORRECT if answered_correctly else 0,
        'total_score': progress.score or 0,
        'streak': progress.streak_count,
        'time_limit_seconds': question.time_limit_seconds,
        'timed_out': time_expired,
        'status': progress.status,
        'target_score': target_score,
    })
# Quiz endpoint
@app.route('/quiz/<int:quiz_id>', methods=['GET', 'POST'])
def quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    request_data = request.get_json() if request.method == 'POST' else None
    user_id = request.args.get('user_id', type=int) or (request_data or {}).get('user_id')
    if not user_id:
        return jsonify({'message': 'user_id is required'}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    # Get or create progress record for this user and quiz
    progress = UserProgress.query.filter_by(user_id=user.id, quiz_id=quiz.id).first()
    if not progress:
        progress = UserProgress(user_id=user.id, quiz_id=quiz.id, module_id=None, status='Not Started', score=0, streak_count=0)
        db.session.add(progress)
        db.session.commit()

    if request.method == 'POST':
        data = request_data or {}
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
        'score': progress.score or 0,
        'streak': progress.streak_count,
        'question_pool_size': len(quiz.questions),
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
