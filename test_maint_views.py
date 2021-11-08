"""Maintenance record view tests."""

import os
from io import BytesIO
from unittest import TestCase
from flask import url_for

from models import db, connect_db, User, Maintenance, Location

os.environ['DATABASE_URL'] = "postgresql:///greenflash-test"

from app import app, CURR_USER_KEY

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False

class MaintenanceViewTestCase(TestCase):
    """Test views for maintenance records."""
    
    def setUp(self):
        """Create test client, add sample data."""
        
        self.client = app.test_client()

        User.query.delete()
        Maintenance.query.delete()
        Location.query.delete()

        self.test_user_one = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="Test_Password123")

        self.test_user_two = User.signup(username="MrTurtle",
                                    email="turtle@test.com",
                                    password="Turtle")

        self.test_user_one_id = 100
        self.test_user_one.id = self.test_user_one_id
        self.test_user_two_id = 200
        self.test_user_two.id = self.test_user_two_id
                                    
        db.session.commit()

        salt_lake_city = Location(
            location="Salt Lake City, UT")

        las_vegas = Location(
            location="Las Vegas, NV")

        db.session.add(salt_lake_city)
        db.session.add(las_vegas)
        db.session.commit()

        
        self.first_test_maintenance = Maintenance(
            user_id=self.test_user_one.id,
            date='2021-5-1',
            location_id=salt_lake_city.id,
            mileage=56000,
            title="First Test Title.",
            description="First test record.",
            image_name="")

        self.second_test_maintenance = Maintenance(
            user_id=self.test_user_two.id,
            date='2020-6-9',
            location_id=las_vegas.id,
            mileage=58000,
            title="Second Test Title.",
            description="Second test record.",
            image_name="")

        self.third_test_maintenance = Maintenance(
            user_id=self.test_user_one.id,
            date='2020-8-9',
            location_id=las_vegas.id,
            mileage=56800,
            title="Third Test Title.",
            description="Third test record.",
            image_name="")

        db.session.add(self.first_test_maintenance)
        db.session.add(self.second_test_maintenance)
        db.session.add(self.third_test_maintenance)

        self.first_test_maintenance_id = 101
        self.first_test_maintenance.id = self.first_test_maintenance_id

        self.second_test_maintenance_id = 202
        self.second_test_maintenance.id = self.second_test_maintenance_id

        self.third_test_maintenance_id = 303
        self.third_test_maintenance.id = self.third_test_maintenance_id

        db.session.commit()


    def tearDown(self):
        """Clean up after tests."""

        db.session.rollback()


    def test_enter_maintenance(self):
        """Test maintenance entry."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.test_user_one.id
 
            res = c.get('/maintenance/new', follow_redirects=True)

            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn("""<h2 class="dark-title">New Maintenance Record</span></h2>""", html)

            data = {
                "title": "new test record title",
                "location": "Chicago, IL",
                "mileage" : 59000,
                "date": "2020-10-26",
                "photo": (BytesIO(b'image data'), ''),
                "description": "This is a test maintenance record."}

            res = c.post('/maintenance/new', content_type="multipart/form-data", data=data)

            self.assertEqual(res.status_code, 302)

            maintenance = Maintenance.query.filter_by(title="new test record title").first()

            self.assertEqual(maintenance.user_id, self.test_user_one.id)
            self.assertEqual(maintenance.description, "This is a test maintenance record.")

            res = c.get(f'/maintenance/{maintenance.id}', follow_redirects=True)
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn("""<h2 class="dark-title">new test record title</span></h2>""", html)

            
    def test_view_maintenance(self):
        """Test view maintenance."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.test_user_two_id

            res = c.get(f'/maintenance/{self.second_test_maintenance_id}')
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn("""<h2 class="dark-title">Second Test Title.</span></h2>""", html)
            self.assertIn("""<p class="rounded mt-2 p-3 text-bg border">Second test record.</p>""", html)

                
    def test_edit_maintenance(self):
        """Test edit maintenance."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.test_user_one_id

            res = c.get(f'/maintenance/{self.first_test_maintenance_id}/edit')
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn("""<h2 class="dark-title">Edit Maintenance</h2>""", html)

            data = {
                "title": "New title for first record.",
                "location": "Los Angeles, CA",
                "mileage" : 59000,
                "date": "2020-10-26",
                "photo": (BytesIO(b'image data'), ''),
                "description": "This is the edited test maintenance."}

            res = c.post(f'/maintenance/{self.first_test_maintenance_id}/edit', data=data, follow_redirects=True)
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)

            self.assertIn("""<h2 class="dark-title">New title for first record.</span></h2>""", html)
            self.assertIn("""<p class="rounded mt-2 p-3 text-bg border">This is the edited test maintenance.</p>""", html)


    def test_delete_maintenance(self):
        """Test that maintenance can be deleted."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.test_user_one_id

            res = c.post(f'/maintenance/{self.third_test_maintenance_id}/delete', follow_redirects=True)
            html = res.get_data(as_text=True)
            self.assertEqual(res.status_code, 200)
            self.assertIn("""<h2 class="dark-title">New Maintenance Record</span></h2>""", html)

            # verify log is gone
            maintenance = Maintenance.query.filter_by(id=self.third_test_maintenance_id).all()
            self.assertEqual(len(maintenance), 0)


    def test_view_other_user_maintenance(self):
        """Test view attempt on a different user's maintenance record."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.test_user_two_id

            res = c.get(f'/maintenance/{self.first_test_maintenance_id}', follow_redirects=True)
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn("""<h2 class="dark-title">New Maintenance Record</span></h2>""", html)


    def test_delete_other_user_maintenance(self):
        """Test delete attempt on a different user's maintenance record."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.test_user_one_id

            res = c.post(f'/maintenance/{self.second_test_maintenance_id}/delete', follow_redirects=True)
            html = res.get_data(as_text=True)
            self.assertEqual(res.status_code, 200)
            self.assertIn("""<h2 class="dark-title">New Maintenance Record</span></h2>""", html)

            # verify maintenance still exists
            maintenance = Maintenance.query.filter_by(id=self.second_test_maintenance_id).all()
            self.assertEqual(len(maintenance), 1)


    def test_edit_other_user_maintenance(self):
        """Test edit attempt different user's maintenance record."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.test_user_one_id

            data = {
                "title": "New title for second maintenance record.",
                "location": "Los Angeles, CA",
                "mileage" : 59000,
                "date": "2020-10-26",
                "photo": (BytesIO(b'image data'), ''),
                "description": "This is an edit for another user's maintenance record."}

            res = c.post(f'/maintenance/{self.second_test_maintenance_id}/edit', data=data, follow_redirects=True)
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn("""<h2 class="dark-title">New Maintenance Record</span></h2>""", html)


    def test_logged_out_submit(self):
        """Attempt maintenance record submit while logged out."""
        
        with self.client as c:
            
            data = {
                "title": "another new record",
                "location": "Chicago, IL",
                "mileage" : 59000,
                "date": "2020-10-27",
                "photo": (BytesIO(b'image data'), ''),
                "text": "This is another test maintenance record."}

            res = c.post('/maintenance/new', content_type="multipart/form-data", data=data)

            self.assertEqual(res.status_code, 302)


    def test_logged_out_view(self):
        """Attempt view log while logged out."""

        with self.client as c:
            
            res = c.get('/maintenance/101')

            self.assertEqual(res.status_code, 302)


    def test_logged_out_delete(self):
        """Attempt delete log while logged out."""
        
        with self.client as c:
            
            res = c.post('/maintenance/101/delete')

            self.assertEqual(res.status_code, 302)

            # log in as user one and verify the log still exists
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.test_user_one_id

            res = c.get('/maintenance/101')
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn("""<h2 class="dark-title">First Test Title.</span></h2>""", html)
            self.assertIn("""<p class="rounded mt-2 p-3 text-bg border">First test record.</p>""", html)

            maintenance = Maintenance.query.filter_by(id=self.first_test_maintenance_id).all()
            self.assertEqual(len(maintenance), 1)