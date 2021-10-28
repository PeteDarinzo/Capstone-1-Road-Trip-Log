"""User view tests."""

import os
from io import BytesIO
from unittest import TestCase
from flask import url_for

from models import db, connect_db, User, Log, Location

os.environ['DATABASE_URL'] = "postgresql:///greenflash-test"

from app import app, CURR_USER_KEY

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False

class UserViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Log.query.delete()
        Location.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="Test_Password123")

        db.session.commit()

    def tearDown(self):
        """Clean up after tests."""

        db.session.rollback()

    def test_signup_and_logout(self):

        with app.test_client() as client:

            res = client.get('/signup')
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn("""<h2>Sign Up</h2>""", html)

            data = {
                "username": "MrTurtle",
                "password": "TEST_PASSWORD",
                "email": "turtle@test.com",
                "photo": (BytesIO(b'image data'), 'test_image.png')
            }

            res = client.post('/signup', content_type="multipart/form-data", data=data, follow_redirects=True)
            html = res.get_data(as_text=True)

            # test that search page is laoded 
            self.assertEqual(res.status_code, 200)
            self.assertIn("""<h2 style="color: #EDF5E1;">Looking for something?</h2>""", html)

            res = client.get('/logout', follow_redirects=True)

            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn("""<h2>Welcome back</h2>""", html)



    def test_log_in(self):
        """Test user log in."""

        with app.test_client() as client:

            res = client.get('/login')
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn("""<h2>Welcome back</h2>""", html)

            data = {"username" : "testuser",
                    "password" : "Test_Password123"}

            res = client.post('/login', data=data, follow_redirects=True)

            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn("""<a class="nav-item nav-link" href="/users/profile">testuser</a>""", html)

            res = client.get('/logout', follow_redirects=True)

            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn("""<h2>Welcome back</h2>""", html)

    def test_wrong_password_login(self):
        """Test login attempt with wrong password"""

        with app.test_client() as client:

            wrong_password = {"username" : "testuser",
                    "password" : "bad_password"}

            # attempt login with incorrect password
            res = client.post('/login', data=wrong_password, follow_redirects=True)
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn("""<h2>Welcome back</h2>""", html)


    def test_wrong_password_login(self):
        """Test login attempt with wrong username"""

        with app.test_client() as client:

            wrong_username = {"username" : "bad_username",
                    "password" : "Test_Password123"}

            # attempt login with incorrect username
            res = client.post('/login', data=wrong_username, follow_redirects=True)
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn("""<h2>Welcome back</h2>""", html)


    def test_user_profile(self):

        with app.test_client() as client:

            data = {"username" : "testuser",
                        "password" : "Test_Password123"}

            res = client.post('/login', data=data, follow_redirects=True)

            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn("""<a class="nav-item nav-link" href="/users/profile">testuser</a>""", html)

            res = client.get("/users/profile")
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn("""<h1>Your Profile</h1>""", html)


    def test_user_edit_profile(self):
        """Test that a user's profile can be edited."""

        with app.test_client() as client:

            data = {"username" : "testuser",
                        "password" : "Test_Password123"}

            res = client.post('/login', data=data, follow_redirects=True)

            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn("""<a class="nav-item nav-link" href="/users/profile">testuser</a>""", html)

            res = client.get("/users/edit")
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn("""<h2>Edit Profile</h2>""", html)

            data = {
                "username": "MrTurtle",
                "email": "mrturtle@test.com",
                "image_url" : "/static/images/default-pic.png",
                "bio" : "I am Mr Turtle",
                "photo": (BytesIO(b'image data'), '')}

            res = client.post('/users/edit', content_type="multipart/form-data", data=data, follow_redirects=True)
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn("""<p>I am Mr Turtle</p>""", html)


    def test_logged_out_profile_edit(self):
        """Test a profile edit attempt while logged out."""

        with app.test_client() as client:

            res = client.get("/users/edit", follow_redirects=True)
            html = res.get_data(as_text=True)

            # test for redirect to home page
            self.assertEqual(res.status_code, 200)
            self.assertIn("""<h2>Welcome back</h2>""", html)


    def test_user_change_password(self):

         with app.test_client() as client:

            data = {"username" : "testuser",
                        "password" : "Test_Password123"}

            res = client.post('/login', data=data, follow_redirects=True)

            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn("""<a class="nav-item nav-link" href="/users/profile">testuser</a>""", html)

            res = client.get('/users/change_password', follow_redirects=True)

            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn("""<h2>Change Password</h2>""", html)

            data = {
            "curr_password": "Test_Password123",
            "new_password_one": "Massachusetts",
            "new_password_two": "Massachusetts"}
            
            res = client.post('/users/change_password', data=data, follow_redirects=True)

            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn("""<h1>Your Profile</h1>""", html)

            # logout, then log back in with new password to verify
            res = client.get('/logout', follow_redirects=True)

            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn("""<h2>Welcome back</h2>""", html)

            data = {"username" : "testuser",
                        "password" : "Massachusetts"}

            res = client.post('/login', data=data, follow_redirects=True)

            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn("""<a class="nav-item nav-link" href="/users/profile">testuser</a>""", html)

            wrong_data_one = {
            "curr_password": "Gibberish",
            "new_password_one": "Mississippi",
            "new_password_two": "Mississippi"}

            res = client.post('/users/change_password', data=wrong_data_one, follow_redirects=True)

            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn("""<h2>Change Password</h2>""", html)

            wrong_data_two = {
            "curr_password": "Test_Password123",
            "new_password_one": "Gibberish",
            "new_password_two": "Mississippi"}
            
            res = client.post('/users/change_password', data=wrong_data_two, follow_redirects=True)

            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn("""<h2>Change Password</h2>""", html)

            wrong_data_three = {
            "curr_password": "Test_Password123",
            "new_password_one": "Mississipi",
            "new_password_two": "Gibberish"}
            
            res = client.post('/users/change_password', data=wrong_data_three, follow_redirects=True)

            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn("""<h2>Change Password</h2>""", html)

            # logout, then attempt to change password
            res = client.get('/logout', follow_redirects=True)

            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn("""<h2>Welcome back</h2>""", html)

            res = client.get("/users/change_password", follow_redirects=True)
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn("""<h2>Welcome back</h2>""", html)

            
    def test_user_delete(self):
        """Test delete user."""
        
        with app.test_client() as client:

            data = {"username" : "testuser",
                        "password" : "Test_Password123"}

            res = client.post('/login', data=data, follow_redirects=True)

            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn("""<a class="nav-item nav-link" href="/users/profile">testuser</a>""", html)

            res = client.post('/users/delete', follow_redirects=True)
            html = res.get_data(as_text=True)
            self.assertEqual(res.status_code, 200)
            self.assertIn("""<h2>Sign Up</h2>""", html)
            
            user = User.query.filter_by(username="testuser").all()
            self.assertEqual(len(user), 0)