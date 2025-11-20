from flask import Flask, request, jsonify
from datetime import datetime
import os
import time
import logging
from flask_cors import CORS
from sqlalchemy import func, text
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
    UserModule,
)
from question_seed_data import QUESTION_POOL_SEED

basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.environ.get('DATABASE_URL')
if db_path:
    database_uri = db_path
else:
    persistent_path = os.environ.get('PERSISTENT_DB_PATH', os.path.join(basedir, 'db.sqlite'))
    if persistent_path.startswith('/app'):
        os.makedirs(os.path.dirname(persistent_path), exist_ok=True)
        database_uri = f"sqlite:////{persistent_path.lstrip('/')}"
    else:
        database_uri = f"sqlite:///{persistent_path}"

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = database_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
CORS(app)
print("Using database file:", os.path.abspath("db.sqlite"))
db.init_app(app)

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

POINTS_PER_CORRECT = 20
SESSION_QUESTION_LIMIT = 5
AVAILABLE_DIFFICULTIES = ['easy', 'medium', 'hard']
def ensure_schema_upgrades():
    with app.app_context():
        inspector = db.inspect(db.engine)
        quiz_columns = {col['name'] for col in inspector.get_columns('quizzes')}
        if 'module_id' not in quiz_columns:
            logger.info('Adding module_id column to quizzes table')
            with db.engine.connect() as connection:
                connection.execute(text('ALTER TABLE quizzes ADD COLUMN module_id INTEGER'))
        # ensure user_modules table exists
        db.create_all()

MODULE_CATALOG = [
    {'title': 'Python Foundations', 'category': 'Programming', 'description': 'Variables, control flow, and functions.', 'duration': 60, 'order': 1},
    {'title': 'SQL Basics', 'category': 'Data', 'description': 'SELECT/WHERE, filtering, aggregation.', 'duration': 50, 'order': 2},
    {'title': 'Data Visualization', 'category': 'Data', 'description': 'Charting with Matplotlib/Seaborn.', 'duration': 45, 'order': 3},
    {'title': 'Cloud Computing', 'category': 'Cloud', 'description': 'IaaS/PaaS/SaaS fundamentals and AWS/Azure basics.', 'duration': 60, 'order': 4},
    {'title': 'Web Design with JavaScript', 'category': 'Frontend', 'description': 'DOM manipulation, events, and UI patterns.', 'duration': 55, 'order': 5},
    {'title': 'Data Structures', 'category': 'CS', 'description': 'Arrays, stacks, queues, trees.', 'duration': 60, 'order': 6},
    {'title': 'Deep Learning Basics', 'category': 'AI', 'description': 'Neural networks, CNNs, RNNs.', 'duration': 75, 'order': 7},
    {'title': 'DevOps Fundamentals', 'category': 'DevOps', 'description': 'CI/CD, containers, and monitoring essentials.', 'duration': 70, 'order': 8},
    {'title': 'Machine Learning Intro', 'category': 'AI', 'description': 'Regression, classification, and model evaluation.', 'duration': 65, 'order': 9},
    {'title': 'React Essentials', 'category': 'Frontend', 'description': 'Components, props, hooks, and state management.', 'duration': 65, 'order': 10},
]

FORUM_TOPICS = ['General'] + [module['title'] for module in MODULE_CATALOG]


def seed_question_pool():
    """Seed quizzes and questions to align with module catalog."""
    with app.app_context():
        modules = {m.title: m for m in Module.query.all()}
        quiz_titles = set(quiz_data['title'] for quiz_data in QUESTION_POOL_SEED)

        # Remove quizzes that are no longer defined
        for quiz in Quiz.query.all():
            if quiz.title not in quiz_titles:
                Question.query.filter_by(quiz_id=quiz.id).delete()
                db.session.delete(quiz)

        for quiz_data in QUESTION_POOL_SEED:
            module = modules.get(quiz_data['module_title'])
            if not module:
                logger.warning('Module "%s" not found for quiz "%s"', quiz_data['module_title'], quiz_data['title'])
                continue

            quiz = Quiz.query.filter_by(title=quiz_data['title']).first()
            if not quiz:
                quiz = Quiz(
                    title=quiz_data['title'],
                    description=quiz_data.get('description'),
                    module_id=module.id,
                )
                db.session.add(quiz)
                db.session.flush()
            else:
                quiz.description = quiz_data.get('description')
                quiz.module_id = module.id

            Question.query.filter_by(quiz_id=quiz.id).delete()

            for difficulty, questions in quiz_data['difficulty_pools'].items():
                for question_data in questions:
                    question_record = Question(
                        quiz_id=quiz.id,
                        topic=quiz_data.get('topic', module.category),
                        question_text=question_data['question'],
                        options=question_data['options'],
                        correct_answer=question_data['answer'],
                        time_limit_seconds=question_data.get('time_limit', 45),
                        difficulty=difficulty,
                    )
                    db.session.add(question_record)

        db.session.commit()
        logger.debug('Question pool synchronized for %d quizzes', len(QUESTION_POOL_SEED))


def seed_module_catalog():
    with app.app_context():
        desired = {m['title']: m for m in MODULE_CATALOG}
        existing = Module.query.all()
        current_titles = set()

        for module in existing:
            data = desired.get(module.title)
            if data:
                module.category = data['category']
                module.description = data.get('description')
                module.duration = data.get('duration')
                module.order = data.get('order')
                current_titles.add(module.title)
            else:
                db.session.delete(module)

        for title, data in desired.items():
            if title in current_titles:
                continue
            module = Module(
                title=title,
                category=data['category'],
                description=data.get('description'),
                duration=data.get('duration'),
                order=data.get('order'),
            )
            db.session.add(module)

        db.session.commit()
        logger.debug('Module catalog synchronized with %d entries', len(desired))


def select_question_for_user(quiz, difficulty=None, exclude_ids=None):
    query = Question.query.filter_by(quiz_id=quiz.id)
    if difficulty:
        query = query.filter(Question.difficulty == difficulty)
    if exclude_ids:
# remove duplicates by converting to set of ints
        cleaned_ids = [int(qid) for qid in exclude_ids if qid is not None]
        if cleaned_ids:
            query = query.filter(~Question.id.in_(cleaned_ids))
    return query.order_by(func.random()).first()


def quiz_target_score(quiz):
    if not quiz:
        return 100
    total_questions = len(quiz.questions)
    target = total_questions * POINTS_PER_CORRECT
    return target if target > 0 else 100


def normalize_difficulty(value):
    if value in AVAILABLE_DIFFICULTIES:
        return value
    return 'medium'


def adjust_difficulty(current, answered_correctly):
    current = normalize_difficulty(current)
    idx = AVAILABLE_DIFFICULTIES.index(current)
    if answered_correctly and idx < len(AVAILABLE_DIFFICULTIES) - 1:
        return AVAILABLE_DIFFICULTIES[idx + 1]
    if not answered_correctly and idx > 0:
        return AVAILABLE_DIFFICULTIES[idx - 1]
    return current


def ordered_difficulty_sequence(current):
    current = normalize_difficulty(current)
    idx = AVAILABLE_DIFFICULTIES.index(current)
    sequence = AVAILABLE_DIFFICULTIES[idx:] + AVAILABLE_DIFFICULTIES[:idx]
    # Ensure current difficulty first, then harder levels, then wrap to easier ones
    return sequence

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
    ensure_schema_upgrades()
    seed_module_catalog()
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

                progress = UserProgress(
                    user_id=user.id,
                    module_id=module.id,
                    status='InProgress',
                    streak_count=5,
                    score=0,
                    current_difficulty='medium',
                    question_history=[],
                    active_session_answers=0,
                )
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


@app.route('/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'message': 'No input data provided'}), 400

        username = (data.get('username') or '').strip()
        email = (data.get('email') or '').strip().lower()
        password = data.get('password')

        if not username or not email or not password:
            return jsonify({'message': 'Username, email, and password are required'}), 400

        if User.query.filter((User.email == email) | (User.username == username)).first():
            return jsonify({'message': 'User already exists'}), 409

        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        return jsonify({
            'message': 'Signup successful',
            'user': {'id': user.id, 'username': user.username, 'email': user.email}
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Server error', 'error': str(e)}), 500

# Basic forum endpoint
@app.route('/forum', methods=['GET', 'POST'])
def forum():
    if request.method == 'POST':
        data = request.json or {}
        user_id = data.get('user_id')
        if not user_id:
            return jsonify({'message': 'user_id is required'}), 400
        user = User.query.get(user_id)
        if not user:
            return jsonify({'message': 'User not found'}), 404
        topic = (data.get('topic') or 'General').strip() or 'General'
        if topic not in FORUM_TOPICS:
            topic = 'General'
        thread_id = data.get('thread_id')
        if thread_id:
            parent_post = ForumPost.query.get(thread_id)
            if not parent_post:
                return jsonify({'message': 'Parent post not found'}), 404
            topic = parent_post.topic
        post = ForumPost(
            user_id=user.id,
            thread_id=thread_id,
            content=data.get('content'),
            topic=topic
        )
        db.session.add(post)
        db.session.commit()
        return jsonify({'message': 'Post added', 'post_id': post.id})
    posts = ForumPost.query.order_by(ForumPost.post_date.asc()).all()
    post_map = {}
    threads = []
    for post in posts:
        payload = {
            'id': post.id,
            'content': post.content,
            'date': post.post_date.isoformat(),
            'topic': post.topic,
            'author': post.author.username if post.author else 'User',
            'replies': []
        }
        post_map[post.id] = payload
        if post.thread_id is None:
            threads.append(payload)

    for post in posts:
        if post.thread_id:
            parent_payload = post_map.get(post.thread_id)
            if parent_payload:
                parent_payload['replies'].append(post_map[post.id])

    return jsonify({
        'posts': threads,
        'topics': FORUM_TOPICS
    })

# Badges endpoint
@app.route('/badges', methods=['GET'])
def get_badges():
    badges = Badge.query.all()
    return jsonify({'badges': [{'id': b.id, 'name': b.name, 'description': b.description} for b in badges]})


@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok'}), 200


@app.route('/modules', methods=['GET'])
def get_modules():
    modules = Module.query.order_by(Module.order.asc()).all()
    return jsonify({
        'modules': [
            {
                'id': module.id,
                'title': module.title,
                'category': module.category,
                'description': module.description,
                'duration': module.duration,
                'order': module.order,
            }
            for module in modules
        ]
    })


@app.route('/users/<int:user_id>/modules', methods=['GET', 'POST'])
def manage_user_modules(user_id):
    user = User.query.get_or_404(user_id)
    if request.method == 'GET':
        assignments = (
            db.session.query(UserModule, Module)
            .join(Module, UserModule.module_id == Module.id)
            .filter(UserModule.user_id == user.id)
            .order_by(Module.order.asc())
            .all()
        )
        return jsonify({
            'modules': [
                {
                    'module_id': module.id,
                    'title': module.title,
                    'category': module.category,
                    'description': module.description,
                    'duration': module.duration,
                    'assigned_at': assignment.assigned_at.isoformat(),
                }
                for assignment, module in assignments
            ]
        })

    data = request.get_json() or {}
    module_ids = data.get('module_ids')
    if not isinstance(module_ids, list):
        return jsonify({'message': 'module_ids must be provided as a list'}), 400

    valid_ids = {m.id for m in Module.query.filter(Module.id.in_(module_ids)).all()}
    invalid_ids = set(module_ids) - valid_ids
    if invalid_ids:
        return jsonify({'message': f'Invalid module IDs: {sorted(invalid_ids)}'}), 400

    # Remove assignments not in new list
    UserModule.query.filter(
        UserModule.user_id == user.id,
        ~UserModule.module_id.in_(valid_ids)
    ).delete(synchronize_session=False)

    existing_assignments = {
        assignment.module_id
        for assignment in UserModule.query.filter_by(user_id=user.id).all()
    }

    for module_id in valid_ids:
        if module_id in existing_assignments:
            continue
        db.session.add(UserModule(user_id=user.id, module_id=module_id))

    db.session.commit()
    return jsonify({'message': 'Modules updated successfully'})


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
            'current_difficulty': record.current_difficulty,
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
    user_id = request.args.get('user_id', type=int)
    quizzes_query = Quiz.query
    assigned_module_ids = []
    if user_id:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'message': 'User not found'}), 404
        assigned_module_ids = [
            assignment.module_id
            for assignment in UserModule.query.filter_by(user_id=user.id).all()
        ]
        if not assigned_module_ids:
            return jsonify({'quizzes': [], 'message': 'No modules selected. Choose modules to unlock quizzes.'})
        quizzes_query = quizzes_query.filter(Quiz.module_id.in_(assigned_module_ids))

    quizzes = quizzes_query.all()
    response = []
    for quiz in quizzes:
        response.append({
            'id': quiz.id,
            'title': quiz.title,
            'description': quiz.description,
            'question_count': len(quiz.questions),
            'topic': quiz.questions[0].topic if quiz.questions else None,
            'module_id': quiz.module_id,
            'module_title': quiz.module.title if quiz.module else None,
        })
    return jsonify({'quizzes': response})


@app.route('/quiz/<int:quiz_id>/questions', methods=['GET'])
def get_quiz_questions(quiz_id):
    user_id = request.args.get('user_id', type=int)
    if not user_id:
        return jsonify({'message': 'user_id is required'}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    quiz = Quiz.query.get_or_404(quiz_id)
    user_modules = {
        assignment.module_id
        for assignment in UserModule.query.filter_by(user_id=user.id).all()
    }
    if quiz.module_id and quiz.module_id not in user_modules:
        return jsonify({'message': 'Module not selected for this quiz'}), 403

    query = Question.query.filter_by(quiz_id=quiz.id)
    questions = query.order_by(func.random()).limit(SESSION_QUESTION_LIMIT).all()
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
            'difficulty': question.difficulty,
        })

    return jsonify({
        'quiz': {
            'id': quiz.id,
            'title': quiz.title,
            'description': quiz.description,
            'question_count': len(quiz.questions),
            'module_id': quiz.module_id,
        },
        'questions': question_payload,
    })


@app.route('/quiz/<int:quiz_id>/next-question', methods=['GET'])
def get_next_question(quiz_id):
    user_id = request.args.get('user_id', type=int)
    reset_session = (request.args.get('reset_session', 'false').lower() in ('1', 'true', 'yes'))

    if not user_id:
        return jsonify({'message': 'user_id is required'}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    quiz = Quiz.query.get_or_404(quiz_id)
    progress = UserProgress.query.filter_by(user_id=user.id, quiz_id=quiz.id).first()
    if not progress:
        progress = UserProgress(
            user_id=user.id,
            quiz_id=quiz.id,
            module_id=None,
            status='Not Started',
            score=0,
            streak_count=0,
            current_difficulty='medium',
            question_history=[],
            active_session_answers=0,
        )
        db.session.add(progress)
        db.session.commit()

    limit = SESSION_QUESTION_LIMIT

    if reset_session:
        progress.question_history = []
        progress.active_session_answers = 0
        progress.current_difficulty = 'medium'
        db.session.commit()

    if progress.question_history is None:
        progress.question_history = []

    answered_ids = progress.question_history
    if len(answered_ids) >= limit:
        progress.active_session_answers = len(answered_ids)
        db.session.commit()
        return jsonify({
            'quiz_complete': True,
            'session_answers': progress.active_session_answers,
            'max_questions': limit,
            'message': 'Session complete. No more questions available within limit.',
            'current_difficulty': progress.current_difficulty,
        })

    difficulty_sequence = ordered_difficulty_sequence(progress.current_difficulty or 'medium')
    question = None
    for difficulty in difficulty_sequence:
        question = select_question_for_user(quiz, difficulty, answered_ids)
        if question:
            break

    if not question:
        question = select_question_for_user(quiz, None, answered_ids)

    if not question:
        progress.active_session_answers = len(answered_ids)
        db.session.commit()
        return jsonify({
            'quiz_complete': True,
            'session_answers': progress.active_session_answers,
            'max_questions': limit,
            'message': 'No more unique questions available for this session.',
            'current_difficulty': progress.current_difficulty,
        })

    return jsonify({
        'quiz_id': quiz.id,
        'question': {
            'id': question.id,
            'topic': question.topic,
            'question': question.question_text,
            'options': question.options,
            'time_limit_seconds': question.time_limit_seconds,
            'difficulty': question.difficulty,
        },
        'current_difficulty': progress.current_difficulty,
        'session_answers': progress.active_session_answers,
        'max_questions': limit,
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

    user_module_ids = {
        assignment.module_id
        for assignment in UserModule.query.filter_by(user_id=user.id).all()
    }
    if quiz.module_id and quiz.module_id not in user_module_ids:
        return jsonify({'message': 'Module not selected for this quiz'}), 403

    allowed_time = question.time_limit_seconds or 0
    if not time_expired and time_taken is not None and allowed_time and time_taken > allowed_time:
        time_expired = True

    progress = UserProgress.query.filter_by(user_id=user.id, quiz_id=quiz.id).first()
    if not progress:
        progress = UserProgress(
            user_id=user.id,
            quiz_id=quiz.id,
            module_id=quiz.module_id,
            status='Not Started',
            score=0,
            streak_count=0,
            current_difficulty='medium',
            question_history=[],
            active_session_answers=0,
        )
        db.session.add(progress)
        db.session.commit()
    elif progress.module_id != quiz.module_id:
        progress.module_id = quiz.module_id

    if progress.question_history is None:
        progress.question_history = []

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

    if question.id not in progress.question_history:
        progress.question_history.append(question.id)

    limit = SESSION_QUESTION_LIMIT
    progress.active_session_answers = len(progress.question_history)

    progress.current_difficulty = adjust_difficulty(progress.current_difficulty, answered_correctly)
    session_complete = progress.active_session_answers >= limit

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
        'current_difficulty': progress.current_difficulty,
        'session_answers': progress.active_session_answers,
        'session_complete': session_complete,
        'max_questions': limit,
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
        progress = UserProgress(
            user_id=user.id,
            quiz_id=quiz.id,
            module_id=None,
            status='Not Started',
            score=0,
            streak_count=0,
            current_difficulty='medium',
            question_history=[],
            active_session_answers=0,
        )
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
        'current_difficulty': progress.current_difficulty,
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
