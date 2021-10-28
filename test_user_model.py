"""User model tests."""

import os
from unittest import TestCase
from models import db, User
from sqlalchemy.exc import IntegrityError

os.environ['DATABASE_URL'] = "postgresql:///greenflash-test"

from app import app

db.create_all()

class UserModelTestCase(TestCase):
    """Test user model."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()

        self.client = app.test_client()

    def tearDown(self):
        """Clean up after tests."""

    def test_user_model(self):
        """Test basic model"""

        u = User(
            username="testuser",
            email="test@test.com",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        self.assertEqual(len(u.logs), 0)
        self.assertEqual(len(u.maintenance), 0)
        self.assertEqual(len(u.places), 0)

    def test_signup(self):

        user = User.signup(
            username="JohnnyTest",
            password="TEST_PASSWORD",
            email="johnny@test.com",
        )

        db.session.commit()

        self.assertEqual(f'<User #{user.id}: {user.username}, {user.email}>', str(user))


    def test_user_authenticate(self):

        user = User.signup(
            username="JohnnyTest",
            password="TEST_PASSWORD",
            email="johnny@test.com",
        )

        db.session.commit()

        auth_user = User.authenticate("JohnnyTest", "TEST_PASSWORD")

        self.assertEqual(f'<User #{user.id}: {user.username}, {user.email}>', str(auth_user))

        self.assertFalse(User.authenticate("JoeyTest", "TEST_PASSWORD"))
       
        self.assertFalse(User.authenticate("JohnnyTest", "THE_WRONG_TEST_PASSWORD"))