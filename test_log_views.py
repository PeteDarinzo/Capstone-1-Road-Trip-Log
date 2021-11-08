"""Log entry view tests."""

import os
from io import BytesIO
from unittest import TestCase
from flask import url_for

from models import db, connect_db, User, Log, Maintenance, Location

os.environ['DATABASE_URL'] = "postgresql:///greenflash-test"

from app import app, CURR_USER_KEY

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False

class LogViewTestCase(TestCase):
    """Test views for log entries."""
    
    def setUp(self):
        """Create test client, add sample data."""
        
        self.client = app.test_client()

        User.query.delete()
        Maintenance.query.delete()
        Log.query.delete()
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

        
        self.first_test_log = Log(
            user_id=self.test_user_one.id,
            date='2021-5-1',
            location_id=salt_lake_city.id,
            mileage=56000,
            title="First Test Title.",
            text="First test log.",
            image_name="")

        self.second_test_log = Log(
            user_id=self.test_user_two.id,
            date='2020-6-9',
            location_id=las_vegas.id,
            mileage=58000,
            title="Second Test Title.",
            text="Second test log.",
            image_name="")

        self.third_test_log = Log(
            user_id=self.test_user_one.id,
            date='2020-8-9',
            location_id=las_vegas.id,
            mileage=56800,
            title="Third Test Title.",
            text="Third test log.",
            image_name="")

        db.session.add(self.first_test_log)
        db.session.add(self.second_test_log)
        db.session.add(self.third_test_log)

        self.first_test_log_id = 101
        self.first_test_log.id = self.first_test_log_id

        self.second_test_log_id = 202
        self.second_test_log.id = self.second_test_log_id

        self.third_test_log_id = 303
        self.third_test_log.id = self.third_test_log_id

        db.session.commit()


    def tearDown(self):
        """Clean up after tests."""

        db.session.rollback()


    def test_enter_log(self):
        """Test log entry."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.test_user_one.id
 
            res = c.get('/logs/new', follow_redirects=True)

            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn("""<h2 class="dark-title">New Log Entry</h2>""", html)

            data = {
                "title": "my test log",
                "location": "Chicago, IL",
                "mileage" : 59000,
                "date": "2020-10-26",
                "photo": (BytesIO(b'image data'), ''),
                "text": "This is a test log."}

            res = c.post('/logs/new', content_type="multipart/form-data", data=data)

            self.assertEqual(res.status_code, 302)

            log = Log.query.filter_by(title="my test log").first()

            self.assertEqual(log.user_id, self.test_user_one.id)
            self.assertEqual(log.text, "This is a test log.")

            res = c.get(f'/logs/{log.id}', follow_redirects=True)
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn("""<h2 class="dark-title">my test log</h2>""", html)

            
    def test_view_log(self):
        """Test view log."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.test_user_two_id

            res = c.get(f'/logs/{self.second_test_log_id}')
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn("""<h2 class="dark-title">Second Test Title.</h2>""", html)
            self.assertIn("""<p class="rounded mt-2 p-3 border text-bg">Second test log.</p>""", html)

    
    def test_edit_log(self):
        """Test edit log."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.test_user_one_id

            res = c.get(f'/logs/{self.first_test_log_id}/edit')
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn("""<h2 class="dark-title">Edit Log</h2>""", html)

            data = {
                "title": "New title for first log.",
                "location": "Los Angeles, CA",
                "mileage" : 59000,
                "date": "2020-10-26",
                "photo": (BytesIO(b'image data'), ''),
                "text": "This is the edited test log."}

            res = c.post(f'/logs/{self.first_test_log_id}/edit', data=data, follow_redirects=True)
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)

            self.assertIn("""<h2 class="dark-title">New title for first log.</h2>""", html)
            self.assertIn("""<p class="rounded mt-2 p-3 border text-bg">This is the edited test log.</p>""", html)


    def test_delete_log(self):
        """Test that a log can be deleted."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.test_user_one_id

            res = c.post(f'/logs/{self.third_test_log_id}/delete', follow_redirects=True)
            html = res.get_data(as_text=True)
            self.assertEqual(res.status_code, 200)
            self.assertIn("""<h2 class="dark-title">New Log Entry</h2>""", html)

            # verify log is gone
            log = Log.query.filter_by(id=self.third_test_log_id).all()
            self.assertEqual(len(log), 0)


    def test_view_other_user_log(self):
        """Test view attempt on a different user's log."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.test_user_two_id

            res = c.get(f'/logs/{self.first_test_log_id}', follow_redirects=True)
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn("""<h2 class="dark-title">New Log Entry</h2>""", html)


    def test_delete_other_user_log(self):
        """Test delete attempt on a different user's log."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.test_user_one_id

            res = c.post(f'/logs/{self.second_test_log_id}/delete', follow_redirects=True)
            html = res.get_data(as_text=True)
            self.assertEqual(res.status_code, 200)
            self.assertIn("""<h2 class="dark-title">New Log Entry</h2>""", html)

            # verify log still exists
            log = Log.query.filter_by(id=self.second_test_log_id).all()
            self.assertEqual(len(log), 1)


    def test_edit_other_user_log(self):
        """Test edit attempt different user's log."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.test_user_one_id

            data = {
                "title": "New title for second log.",
                "location": "Los Angeles, CA",
                "mileage" : 59000,
                "date": "2020-10-26",
                "photo": (BytesIO(b'image data'), ''),
                "text": "This is an edit for another user's log."}

            res = c.post(f'/logs/{self.second_test_log_id}/edit', data=data, follow_redirects=True)
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn("""<h2 class="dark-title">New Log Entry</h2>""", html)


    def test_logged_out_submit(self):
        """Attempt log submit while logged out."""

        with self.client as c:
            
            data = {
                "title": "another new log",
                "location": "Chicago, IL",
                "mileage" : 59000,
                "date": "2020-10-27",
                "photo": (BytesIO(b'image data'), ''),
                "text": "This is another test log."}

            res = c.post('/logs/new', content_type="multipart/form-data", data=data)

            self.assertEqual(res.status_code, 302)


    def test_logged_out_view(self):
        """Attempt view log while logged out."""

        with self.client as c:
            
            res = c.get('/logs/101')

            self.assertEqual(res.status_code, 302)


    def test_logged_out_delete(self):
        """Attempt delete log while logged out."""
        
        with self.client as c:
            
            res = c.post('/logs/101/delete')

            self.assertEqual(res.status_code, 302)

            # log in as user one and verify the log still exists
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.test_user_one_id

            res = c.get('/logs/101')
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn("""<h2 class="dark-title">First Test Title.</h2>""", html)

            log = Log.query.filter_by(id=self.first_test_log_id).all()
            self.assertEqual(len(log), 1)