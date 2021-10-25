"""Models for GreenFlash app."""

from datetime import date, datetime
from enum import unique
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()


def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)


class User(db.Model):
    """User model."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.Text, nullable=False, unique=True)
    email = db.Column(db.Text,nullable=False,unique=True)
    password = db.Column(db.Text, nullable=False)
    bio = db.Column(db.Text)
    image_name = db.Column(db.Text)

    logs = db.relationship("Log", cascade="all, delete", backref="user")
    maintenance = db.relationship("Maintenance", cascade="all, delete", backref="user")
    places = db.relationship("Place", secondary="users_places")

    @classmethod
    def signup(cls, username, email, password):
        """Signup User."""

        hashed_pwd = bcrypt.generate_password_hash(password).decode("UTF-8")

        user = User(
            username=username,
            email=email,
            password=hashed_pwd,
            image_name="",
            bio=""
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

    @classmethod
    def change_password(cls, username, curr_password, new_password):

        user = cls.query.filter_by(username=username).first()

        is_auth = bcrypt.check_password_hash(user.password, curr_password)

        if is_auth:
            hashed_pwd = bcrypt.generate_password_hash(new_password).decode("UTF-8")
            user.password = hashed_pwd
            return user
        
        return False


class Log(db.Model):
    """Log model."""
    
    __tablename__ = "logs"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="cascade"))
    date = db.Column(db.Date, nullable=False)
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'))
    mileage = db.Column(db.Integer, nullable=True)
    title = db.Column(db.Text, nullable=False, unique=True)
    text = db.Column(db.Text, nullable=False)
    image_name = db.Column(db.Text)

    # user = db.relationship("User")
    # location = db.relationship("Location")


class Location(db.Model):
    """Location model."""

    __tablename__ = "locations"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # city = db.Column(db.Text, nullable=False)
    # state = db.Column(db.Text, nullable=False)
    location = db.Column(db.Text, nullable=False, unique=True)
    
    logs = db.relationship("Log", backref="location")
    maintenance = db.relationship("Maintenance", backref="location")

class Maintenance(db.Model):
    """Maintenance model."""

    __tablename__ = "maintenance"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    date = db.Column(db.Date, nullable=False)
    mileage = db.Column(db.Integer)
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'))
    title = db.Column(db.Text,nullable=False)
    description = db.Column(db.Text, nullable=False)
    image_name = db.Column(db.Text)

    # user = db.relationship("User")
    # location = db.relationship("Location")


class Place(db.Model):
    """Place model."""

    __tablename__ = "places"

    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    category = db.Column(db.String)
    url = db.Column(db.Text)
    image_url = db.Column(db.Text)
    price = db.Column(db.String)    
    phone = db.Column(db.String)
    address_0 = db.Column(db.Text)
    address_1 = db.Column(db.Text)
    rating = db.Column(db.String)

    # users = db.relationship("User", secondary="users_places")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "url": self.url,
            "address": self.address,
        }


class UsersPlaces(db.Model):
    """Table for user place relationship."""

    __tablename__ = "users_places"

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    place_id = db.Column(db.String, db.ForeignKey('places.id'), primary_key=True)

   
