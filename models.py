"""Models for GreenFlash app."""

from datetime import date, datetime
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()


def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)


class User(db.model):
    """User model."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.Text, nullable=False, unique=True)
    password = db.Colum(db.Text, nullable=False)
    first_name = db.Column(db.Text, nullable=False)
    last_name = db.Column(db.Text, nullable=False)

    logs = db.relationship("Log", cascade="all, delete")

    @classmethod
    def signup(cls, username, first_name, last_name, password):
        """Signup User."""

        hashed_pwd = bcrypt.generate_password_hash(password).decode("UTF-8")

        user = User(
            username=username,
            first_name=first_name,
            last_name=last_name,
            password=hashed_pwd
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Find user with 'username' and 'password'.
        
        Search for a user with a password hash matching this password. If found, return that user object.

        If not found, return False.
        """

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user
        
        return False


class Log(db.model):
    """Log model."""
    
    __tablename__ = "logs"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="cascade"))
    date = db.Column(db.DateTime)
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'))
    mileage = db.Column(db.Integer, nullable=True)
    text = db.Column(db.Text, nullable=False)

    user = db.relationship("User")


class Location(db.model):
    """Location model."""

    __tablename__ = "locations"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    location = db.Column(db.Text, nullable=False, unique=True)
    
    logs = db.relationship("Logs")


class Maintenance(db.Model):
    """Maintenance model."""

    __tablename__ = "maintenance"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    log_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    date = db.Column(db.DateTime)
    mileage = db.Column(db.Integer)
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'))
    description = db.Column(db.Text, nullable=False)


class Image(db.Model):
    """Image model."""

    __tablename__ = "images"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    file_path = db.Column(db.Text)
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'))

