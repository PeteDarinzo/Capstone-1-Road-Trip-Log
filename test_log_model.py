"""Log entry model tests."""

import os
from re import T
from unittest import TestCase

from models import db, User, Log, Location

os.environ['DATABASE_URL'] = "postgresql:///greenflash-test"

from app import app

db.create_all()

class LogModelTestCase(TestCase):
    """Test log model."""

    def setUp(self):
        """Create test client."""

        User.query.delete()
        Log.query.delete()
        Location.query.delete()

        self.client = app.test_client()


    def tearDown(self):
        """Clean up after tests."""

        db.session.rollback()

    def test_log_model(self):
        """Test basic model."""

        salt_lake_city = Location(
            location="Salt Lake City, UT"
        )

        u = User(
            username="testuser",
            email="test@test.com",
            password="HASHED_PASSWORD"
        )

        db.session.add(salt_lake_city)
        db.session.add(u)
        db.session.commit()

        l = Log(
            user_id=u.id,
            date='2020-1-1',
            location_id=salt_lake_city.id,
            mileage=10000,
            title="Test Title",
            text="Test content",
            image_name=""
        )

        db.session.add(l)
        db.session.commit()

        user = l.user
        loc = l.location
        
        self.assertEqual(f"<User #{u.id}: {u.username}, {u.email}>", str(user)) 
        self.assertEqual(f"<Location #{salt_lake_city.id}: {salt_lake_city.location}>", str(loc))       
