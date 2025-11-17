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
FORUM_TOPICS = ['General', 'Cloud Computing', 'Web Design with JavaScript', 'Data Structures', 'Deep Learning']

QUESTION_POOL_SEED = [
    {
        'title': 'Cloud Computing',
        'description': 'Assess core cloud-computing concepts.',
        'topic': 'Cloud Computing',
        'difficulty_pools': {
            'easy': [
                {
                    'question': 'What does SaaS stand for?',
                    'options': ['Software as a Service', 'Storage as a Service', 'Security as a Service', 'Server as a Service'],
                    'answer': 'Software as a Service',
                },
                {
                    'question': 'Which model lets you rent virtual machines?',
                    'options': ['IaaS', 'SaaS', 'PaaS', 'FaaS'],
                    'answer': 'IaaS',
                },
                {
                    'question': 'AWS EC2 is an example of which service type?',
                    'options': ['SaaS', 'IaaS', 'PaaS', 'On-prem'],
                    'answer': 'IaaS',
                },
                {
                    'question': 'Which storage option is fully managed object storage?',
                    'options': ['Amazon S3', 'Amazon EC2', 'AWS Lambda', 'Amazon RDS'],
                    'answer': 'Amazon S3',
                },
                {
                    'question': 'Which provider offers Azure?',
                    'options': ['Google', 'Microsoft', 'Amazon', 'IBM'],
                    'answer': 'Microsoft',
                },
            ],
            'medium': [
                {
                    'question': 'What does PaaS primarily provide?',
                    'options': ['Full applications', 'Hardware only', 'Managed runtime and tools', 'Networking gear'],
                    'answer': 'Managed runtime and tools',
                },
                {
                    'question': 'Which AWS service lets you run code without managing servers?',
                    'options': ['EC2', 'Lambda', 'EBS', 'Route53'],
                    'answer': 'Lambda',
                },
                {
                    'question': 'A Virtual Private Cloud (VPC) provides what?',
                    'options': ['Physical servers', 'Isolated network within AWS', 'Database backups', 'User identities'],
                    'answer': 'Isolated network within AWS',
                },
                {
                    'question': 'Which service is best for delivering cached content globally?',
                    'options': ['CloudFront', 'RDS', 'SQS', 'Glue'],
                    'answer': 'CloudFront',
                },
                {
                    'question': 'What is auto scaling used for?',
                    'options': ['Scaling storage only', 'Automatically adjusting compute capacity', 'Encrypting data at rest', 'Monitoring logs'],
                    'answer': 'Automatically adjusting compute capacity',
                },
            ],
            'hard': [
                {
                    'question': 'Cloud bursting is primarily used to:',
                    'options': ['Move data to cold storage', 'Handle peak loads by extending to public cloud', 'Encrypt traffic', 'Turn off idle VMs'],
                    'answer': 'Handle peak loads by extending to public cloud',
                },
                {
                    'question': 'Which AWS service provides managed Kubernetes?',
                    'options': ['ECS', 'EKS', 'Fargate', 'Lightsail'],
                    'answer': 'EKS',
                },
                {
                    'question': 'What does multi-tenancy mean in cloud architecture?',
                    'options': ['Single user per resource', 'Multiple customers share resources securely', 'Dedicated hardware per customer', 'Multiple clouds linked together'],
                    'answer': 'Multiple customers share resources securely',
                },
                {
                    'question': 'Which service provides petabyte-scale data transfer using physical devices?',
                    'options': ['Snowball', 'CloudTrail', 'Athena', 'Elastic Beanstalk'],
                    'answer': 'Snowball',
                },
                {
                    'question': 'What is the main benefit of spot instances?',
                    'options': ['Predictable pricing', 'Low cost for interruptible workloads', 'Dedicated compliance', 'Persistent storage'],
                    'answer': 'Low cost for interruptible workloads',
                },
            ],
        },
    },
    {
        'title': 'Web Design with JavaScript',
        'description': 'JavaScript and front-end fundamentals.',
        'topic': 'Web Design with JavaScript',
        'difficulty_pools': {
            'easy': [
                {
                    'question': 'What does HTML stand for?',
                    'options': ['HyperText Markup Language', 'HighText Markdown Language', 'Hyperlink Markup Language', 'Home Tool Markup Language'],
                    'answer': 'HyperText Markup Language',
                },
                {
                    'question': 'Which tag wraps JavaScript inside HTML?',
                    'options': ['<script>', '<style>', '<js>', '<code>'],
                    'answer': '<script>',
                },
                {
                    'question': 'What does CSS control?',
                    'options': ['Structure', 'Behavior', 'Styling', 'Database'],
                    'answer': 'Styling',
                },
                {
                    'question': 'Which operator assigns a value?',
                    'options': ['=', '==', '===', ':='],
                    'answer': '=',
                },
                {
                    'question': 'Which keyword declares a block-scoped variable?',
                    'options': ['var', 'static', 'let', 'goto'],
                    'answer': 'let',
                },
            ],
            'medium': [
                {
                    'question': 'What does the DOM represent?',
                    'options': ['Visual layout', 'Document Object Model', 'Database map', 'Design-only mockup'],
                    'answer': 'Document Object Model',
                },
                {
                    'question': 'Which array method adds an element to the end?',
                    'options': ['shift()', 'unshift()', 'push()', 'pop()'],
                    'answer': 'push()',
                },
                {
                    'question': 'What does === compare?',
                    'options': ['Values only', 'Types only', 'Value and type', 'References only'],
                    'answer': 'Value and type',
                },
                {
                    'question': 'What is event delegation?',
                    'options': ['Binding every element', 'Handling events at a common ancestor', 'Preventing events', 'Random event firing'],
                    'answer': 'Handling events at a common ancestor',
                },
                {
                    'question': 'Which hook replaces componentDidMount in React?',
                    'options': ['useState', 'useEffect', 'useMemo', 'useReducer'],
                    'answer': 'useEffect',
                },
            ],
            'hard': [
                {
                    'question': 'What is a closure?',
                    'options': ['A CSS trick', 'A function bundled with references to its lexical scope', 'A database transaction', 'A loop construct'],
                    'answer': 'A function bundled with references to its lexical scope',
                },
                {
                    'question': 'Which pattern avoids deeply nested callbacks?',
                    'options': ['Event bubbling', 'Promises/async-await', 'Shadow DOM', 'Box model'],
                    'answer': 'Promises/async-await',
                },
                {
                    'question': 'What does virtual DOM improve?',
                    'options': ['Network access', 'DOM diffing performance', 'Database indexing', 'CSS specificity'],
                    'answer': 'DOM diffing performance',
                },
                {
                    'question': 'Which API allows drawing 2D graphics in JS?',
                    'options': ['Canvas API', 'Fetch API', 'WebRTC', 'Service Worker'],
                    'answer': 'Canvas API',
                },
                {
                    'question': 'What is tree shaking used for?',
                    'options': ['Removing unused code during bundling', 'Styling DOM nodes', 'Testing components', 'Cleaning databases'],
                    'answer': 'Removing unused code during bundling',
                },
            ],
        },
    },
    {
        'title': 'Data Structures',
        'description': 'Core data structure knowledge check.',
        'topic': 'Data Structures',
        'difficulty_pools': {
            'easy': [
                {
                    'question': 'Which structure uses FIFO?',
                    'options': ['Stack', 'Queue', 'Tree', 'Graph'],
                    'answer': 'Queue',
                },
                {
                    'question': 'Which uses LIFO?',
                    'options': ['Array', 'Stack', 'Graph', 'Queue'],
                    'answer': 'Stack',
                },
                {
                    'question': 'Which structure stores key-value pairs?',
                    'options': ['Array', 'Hash map', 'Stack', 'Queue'],
                    'answer': 'Hash map',
                },
                {
                    'question': 'An array provides?',
                    'options': ['Constant-time indexed access', 'Random node links', 'No order guarantee', 'Graph traversal'],
                    'answer': 'Constant-time indexed access',
                },
                {
                    'question': 'Which structure is hierarchical?',
                    'options': ['Stack', 'Queue', 'Tree', 'Array'],
                    'answer': 'Tree',
                },
            ],
            'medium': [
                {
                    'question': 'Which traversal visits nodes level by level?',
                    'options': ['DFS', 'BFS', 'In-order', 'Post-order'],
                    'answer': 'BFS',
                },
                {
                    'question': 'What is the time complexity of binary search on a sorted array?',
                    'options': ['O(n)', 'O(log n)', 'O(1)', 'O(n log n)'],
                    'answer': 'O(log n)',
                },
                {
                    'question': 'Which structure is best for implementing recursion tracking?',
                    'options': ['Queue', 'Stack', 'Heap', 'Graph'],
                    'answer': 'Stack',
                },
                {
                    'question': 'Which data structure is ideal for priority scheduling?',
                    'options': ['Hash table', 'Priority queue/heap', 'Linked list', 'Array'],
                    'answer': 'Priority queue/heap',
                },
                {
                    'question': 'What does amortized analysis explain?',
                    'options': ['Worst case only', 'Average performance over sequences of operations', 'Memory usage', 'Network latency'],
                    'answer': 'Average performance over sequences of operations',
                },
            ],
            'hard': [
                {
                    'question': 'A red-black tree maintains:',
                    'options': ['Exact balance', 'Approximate balance via recoloring/rotations', 'Min-heap invariant', 'Adjacency lists'],
                    'answer': 'Approximate balance via recoloring/rotations',
                },
                {
                    'question': 'What is the typical complexity of Dijkstra using a binary heap?',
                    'options': ['O(E + V)', 'O(E log V)', 'O(V^2)', 'O(log V)'],
                    'answer': 'O(E log V)',
                },
                {
                    'question': 'Which hash conflict technique keeps a linked list at each bucket?',
                    'options': ['Open addressing', 'Separate chaining', 'Double hashing', 'Quadratic probing'],
                    'answer': 'Separate chaining',
                },
                {
                    'question': 'What is the space complexity of storing a graph with adjacency matrix?',
                    'options': ['O(V)', 'O(E)', 'O(V^2)', 'O(log V)'],
                    'answer': 'O(V^2)',
                },
                {
                    'question': 'Which structure underpins union-find efficiency?',
                    'options': ['Union by rank with path compression', 'Plain arrays', 'Binary heaps', 'Skip lists'],
                    'answer': 'Union by rank with path compression',
                },
            ],
        },
    },
    {
        'title': 'Deep Learning',
        'description': 'Deep learning fundamentals and terminology.',
        'topic': 'Deep Learning',
        'difficulty_pools': {
            'easy': [
                {
                    'question': 'Which activation outputs values between 0 and 1?',
                    'options': ['ReLU', 'Sigmoid', 'Linear', 'Softmax'],
                    'answer': 'Sigmoid',
                },
                {
                    'question': 'What does GPU stand for?',
                    'options': ['General Processing Unit', 'Graphics Processing Unit', 'Graphical Programming Utility', 'Global Processing Unit'],
                    'answer': 'Graphics Processing Unit',
                },
                {
                    'question': 'What is the basic unit in a neural network?',
                    'options': ['Layer', 'Neuron', 'Batch', 'Epoch'],
                    'answer': 'Neuron',
                },
                {
                    'question': 'What is the purpose of a loss function?',
                    'options': ['Measure model error', 'Store data', 'Visualize layers', 'Compress inputs'],
                    'answer': 'Measure model error',
                },
                {
                    'question': 'Which library is commonly used for deep learning in Python?',
                    'options': ['NumPy', 'TensorFlow', 'Matplotlib', 'Selenium'],
                    'answer': 'TensorFlow',
                },
            ],
            'medium': [
                {
                    'question': 'What does backpropagation compute?',
                    'options': ['Forward pass', 'Gradient of loss wrt weights', 'Batch size', 'Activation outputs only'],
                    'answer': 'Gradient of loss wrt weights',
                },
                {
                    'question': 'Dropout is used to:',
                    'options': ['Speed up gradients', 'Reduce overfitting', 'Store parameters', 'Normalize batches'],
                    'answer': 'Reduce overfitting',
                },
                {
                    'question': 'Which layer is key in CNNs for spatial feature extraction?',
                    'options': ['Fully connected', 'Convolutional', 'Recurrent', 'Embedding'],
                    'answer': 'Convolutional',
                },
                {
                    'question': 'Batch normalization primarily helps by:',
                    'options': ['Converging faster and stabilizing training', 'Saving memory', 'Replacing dropout', 'Reducing dataset size'],
                    'answer': 'Converging faster and stabilizing training',
                },
                {
                    'question': 'Which optimizer adapts learning rates per parameter?',
                    'options': ['SGD', 'Adam', 'Momentum only', 'RMSProp only'],
                    'answer': 'Adam',
                },
            ],
            'hard': [
                {
                    'question': 'What does the attention mechanism allow models to do?',
                    'options': ['Ignore all context', 'Focus on relevant parts of the input sequence dynamically', 'Remove positional encoding', 'Train without gradients'],
                    'answer': 'Focus on relevant parts of the input sequence dynamically',
                },
                {
                    'question': 'Which architecture relies entirely on attention mechanisms?',
                    'options': ['CNN', 'Transformer', 'RNN', 'GAN'],
                    'answer': 'Transformer',
                },
                {
                    'question': 'What is the vanishing gradient problem?',
                    'options': ['Gradients grow uncontrollably', 'Gradients shrink to zero through deep layers', 'Weights explode', 'Batch sizes vanish'],
                    'answer': 'Gradients shrink to zero through deep layers',
                },
                {
                    'question': 'GAN training optimizes which two networks?',
                    'options': ['Autoencoder and decoder', 'Generator and discriminator', 'Encoder and classifier', 'Critic and transformer'],
                    'answer': 'Generator and discriminator',
                },
                {
                    'question': 'What does the softmax function output?',
                    'options': ['Unbounded values', 'Normalized probability distribution', 'Binary result', 'Gradients only'],
                    'answer': 'Normalized probability distribution',
                },
            ],
        },
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

            def add_question(question_data, difficulty_override=None):
                difficulty_value = question_data.get('difficulty') or difficulty_override or 'medium'
                if question_data['question'] in existing_questions and not force:
                    return
                question_record = Question(
                    quiz_id=quiz.id,
                    topic=quiz_data['topic'],
                    question_text=question_data['question'],
                    options=question_data['options'],
                    correct_answer=question_data['answer'],
                    time_limit_seconds=question_data.get('time_limit', 45),
                    difficulty=difficulty_value,
                )
                db.session.add(question_record)
                existing_questions.add(question_data['question'])

            if quiz_data.get('difficulty_pools'):
                for difficulty_level, question_list in quiz_data['difficulty_pools'].items():
                    for question_data in question_list:
                        add_question(question_data, difficulty_override=difficulty_level)
            else:
                for question_data in quiz_data.get('questions', []):
                    add_question(question_data)

        db.session.commit()
        logger.debug('Question pool seeded with %d quizzes', len(QUESTION_POOL_SEED))


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
            'difficulty': question.difficulty,
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
            current_difficulty='medium',
            question_history=[],
            active_session_answers=0,
        )
        db.session.add(progress)
        db.session.commit()

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
