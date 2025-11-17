from datetime import datetime
from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    progress_records = db.relationship(
        "UserProgress", back_populates="user", cascade="all, delete-orphan"
    )
    forum_posts = db.relationship("ForumPost", backref="author", cascade="all, delete-orphan")
    badges = db.relationship("UserBadge", back_populates="user", cascade="all, delete-orphan")

    # Password methods
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.id} - {self.username}>"


class Module(db.Model):
    __tablename__ = 'modules'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=True)
    duration = db.Column(db.Integer, nullable=True)
    order = db.Column(db.Integer, nullable=True)

    # Relationships
    progress_records = db.relationship(
        "UserProgress", back_populates="module", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Module {self.id} - {self.title}>"


class Quiz(db.Model):
    __tablename__ = "quizzes"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)

    # Relationships
    progress_records = db.relationship(
        "UserProgress", back_populates="quiz", cascade="all, delete-orphan"
    )
    questions = db.relationship(
        "Question", back_populates="quiz", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Quiz {self.id} - {self.title}>"


class Question(db.Model):
    __tablename__ = "questions"

    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey("quizzes.id"), nullable=False)
    topic = db.Column(db.String(100), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    options = db.Column(db.JSON, nullable=False)
    correct_answer = db.Column(db.String(255), nullable=False)
    time_limit_seconds = db.Column(db.Integer, nullable=False, default=60)
    difficulty = db.Column(db.String(20), nullable=True)

    quiz = db.relationship("Quiz", back_populates="questions")

    def __repr__(self):
        return f"<Question {self.id} quiz_id={self.quiz_id}>"


class UserProgress(db.Model):
    __tablename__ = "user_progress"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey("quizzes.id"), nullable=True)
    module_id = db.Column(db.Integer, db.ForeignKey("modules.id"), nullable=True)

    status = db.Column(db.String(20), nullable=False)
    score = db.Column(db.Float, nullable=True)
    streak_count = db.Column(db.Integer, nullable=False, default=0)
    completed = db.Column(db.DateTime, nullable=True)
    current_difficulty = db.Column(db.String(20), nullable=False, default='medium')
    question_history = db.Column(db.JSON, nullable=True, default=list)
    active_session_answers = db.Column(db.Integer, nullable=False, default=0)

    # Relationships
    user = db.relationship("User", back_populates="progress_records")
    quiz = db.relationship("Quiz", back_populates="progress_records")
    module = db.relationship("Module", back_populates="progress_records")

    def __repr__(self):
        return f"<UserProgress user_id={self.user_id} module_id={self.module_id} status={self.status}>"


class ForumPost(db.Model):
    __tablename__ = 'forum_posts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    thread_id = db.Column(db.Integer, db.ForeignKey('forum_posts.id'), nullable=True)
    topic = db.Column(db.String(100), nullable=False, default='General')
    content = db.Column(db.Text, nullable=False)
    post_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    likes = db.Column(db.Integer, nullable=False, default=0)


class Badge(db.Model):
    __tablename__ = 'badges'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    icon = db.Column(db.String(50), nullable=True)
    criteria = db.Column(db.JSON, nullable=True)

    users = db.relationship("UserBadge", back_populates="badge", cascade="all, delete-orphan")


class UserBadge(db.Model):
    __tablename__ = 'user_badges'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    badge_id = db.Column(db.Integer, db.ForeignKey('badges.id'), nullable=False)
    awarded_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    level = db.Column(db.Integer, nullable=False, default=1)
    next_level_date = db.Column(db.DateTime, nullable=True)

    user = db.relationship("User", back_populates="badges")
    badge = db.relationship("Badge", back_populates="users")
