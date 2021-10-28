"""Maintenance record model tests."""

import os
from unittest import TestCase

from models import db, User, Location, Maintenance

os.environ['DATABASE_URL'] = "postgresql:///greenflash-test"

from app import app

db.create_all()

class MaintenanceModelTestCase(TestCase):
    """Test maintenance model."""

    def setUp(self):
        """Create test client."""

        User.query.delete()
        Maintenance.query.delete()
        Location.query.delete()

        self.client = app.test_client()


    def tearDown(self):
        """Clean up after tests."""

        db.session.rollback()

    def test_maintenance_model(self):
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

        m = Maintenance(
            user_id=u.id,
            date="2021-1-1",
            mileage=56123,
            location_id=salt_lake_city.id,
            title="Oil",
            description="Changed oil to 5W30. Checked tire pressure.",
            image_name=""
        )

        db.session.add(m)
        db.session.commit()

        user = m.user
        loc = m.location
        
        self.assertEqual(f"<User #{u.id}: {u.username}, {u.email}>", str(user)) 
        self.assertEqual(f"<Location #{salt_lake_city.id}: {salt_lake_city.location}>", str(loc))       
