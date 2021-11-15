"""User view tests."""

import os
import shutil
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

        user = User.query.filter_by(username="MrTurtle").first()
        if user and os.path.isdir(f"static/images/{user.id}"):
            shutil.rmtree(f"static/images/{user.id}")


    def test_signup_and_logout(self):

        with app.test_client() as client:

            res = client.get('/signup')
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn("""<h2 class="dark-title">Sign Up</h2>""", html)

            data = {
                "username": "MrTurtle",
                "password": "TEST_PASSWORD",
                "email": "turtle@test.com",
                "photo": (BytesIO(b'image data'), 'test_image.png')
            }

            res = client.post('/signup', content_type="multipart/form-data", data=data, follow_redirects=True)
            html = res.get_data(as_text=True)

            # test that search page is loaded 
            self.assertEqual(res.status_code, 200)
            self.assertIn("""<h2 class="light-title">Looking for something?</h2>""", html)
            self.assertIn("""<a class="nav-link" href="/users/profile">MrTurtle</a>""", html)

            res = client.get('/logout', follow_redirects=True)

            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn("""<h2 class="dark-title">Log In</h2>""", html)



    def test_signup_image(self):
        """"Test signup attempt with an incorrect image type."""
        
        with app.test_client() as client:

            res = client.get('/signup')
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn("""<h2 class="dark-title">Sign Up</h2>""", html)

            txt_file = {
                "username": "MrTurtle",
                "password": "TEST_PASSWORD",
                "email": "turtle@test.com",
                "photo": (BytesIO(b'image data'), 'test_image.txt')
            }

            res = client.post('/signup', content_type="multipart/form-data", data=txt_file, follow_redirects=True)
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn("""<h2 class="dark-title">Sign Up</h2>""", html)

            pdf_file = {
                "username": "MrTurtle",
                "password": "TEST_PASSWORD",
                "email": "turtle@test.com",
                "photo": (BytesIO(b'image data'), 'test_image.pdf')
            }

            res = client.post('/signup', content_type="multipart/form-data", data=pdf_file, follow_redirects=True)
            html = res.get_data(as_text=True)


            self.assertEqual(res.status_code, 200)
            self.assertIn("""<h2 class="dark-title">Sign Up</h2>""", html)


    # def test_log_in(self):
    #     """Test user log in."""

    #     with app.test_client() as client:

    #         res = client.get('/login')
    #         html = res.get_data(as_text=True)

    #         self.assertEqual(res.status_code, 200)
    #         self.assertIn("""<h2 class="dark-title">Log In</h2>""", html)

    #         data = {"username" : "testuser",
    #                 "password" : "Test_Password123"}

    #         res = client.post('/login', data=data, follow_redirects=True)

    #         html = res.get_data(as_text=True)

    #         self.assertEqual(res.status_code, 200)
    #         self.assertIn("""<a class="nav-link" href="/users/profile">testuser</a>""", html)

    #         res = client.get('/logout', follow_redirects=True)

    #         html = res.get_data(as_text=True)

    #         self.assertEqual(res.status_code, 200)
    #         self.assertIn("""<h2 class="dark-title">Log In</h2>""", html)


    # def test_wrong_password_login(self):
    #     """Test login attempt with wrong password"""

    #     with app.test_client() as client:

    #         wrong_password = {"username" : "testuser",
    #                 "password" : "bad_password"}

    #         # attempt login with incorrect password
    #         res = client.post('/login', data=wrong_password, follow_redirects=True)
    #         html = res.get_data(as_text=True)

    #         self.assertEqual(res.status_code, 200)
    #         self.assertIn("""<h2 class="dark-title">Log In</h2>""", html)


    # def test_wrong_username_login(self):
    #     """Test login attempt with wrong username"""

    #     with app.test_client() as client:

    #         wrong_username = {"username" : "bad_username",
    #                 "password" : "Test_Password123"}

    #         # attempt login with incorrect username
    #         res = client.post('/login', data=wrong_username, follow_redirects=True)
    #         html = res.get_data(as_text=True)

    #         self.assertEqual(res.status_code, 200)
    #         self.assertIn("""<h2 class="dark-title">Log In</h2>""", html)


    # def test_user_profile(self):
    #     """Test user's profile can be viewed"""

    #     with app.test_client() as client:

    #         data = {"username" : "testuser",
    #                     "password" : "Test_Password123"}

    #         res = client.post('/login', data=data, follow_redirects=True)

    #         html = res.get_data(as_text=True)

    #         self.assertEqual(res.status_code, 200)
    #         self.assertIn("""<a class="nav-link" href="/users/profile">testuser</a>""", html)

    #         res = client.get("/users/profile")
    #         html = res.get_data(as_text=True)

    #         self.assertEqual(res.status_code, 200)
    #         self.assertIn("""<p class="display-5">testuser</p>""", html)


    # def test_user_edit_profile(self):
    #     """Test that a user's profile can be edited."""

    #     with app.test_client() as client:

    #         data = {"username" : "testuser",
    #                     "password" : "Test_Password123"}

    #         res = client.post('/login', data=data, follow_redirects=True)

    #         html = res.get_data(as_text=True)

    #         self.assertEqual(res.status_code, 200)
    #         self.assertIn("""<a class="nav-link" href="/users/profile">testuser</a>""", html)

    #         res = client.get("/users/edit")
    #         html = res.get_data(as_text=True)

    #         self.assertEqual(res.status_code, 200)
    #         self.assertIn("""<h2 class="dark-title">Edit Profile</h2>""", html)

    #         data = {
    #             "username": "MrTurtle",
    #             "email": "mrturtle@test.com",
    #             "image_url" : "/static/images/default-pic.png",
    #             "bio" : "I am Mr Turtle",
    #             "photo": (BytesIO(b'image data'), '')}

    #         res = client.post('/users/edit', content_type="multipart/form-data", data=data, follow_redirects=True)
    #         html = res.get_data(as_text=True)

    #         self.assertEqual(res.status_code, 200)
    #         self.assertIn("""<p>I am Mr Turtle</p>""", html)


    # def test_profile_image_edit(self):
    #     """Test that a user's profile can be edited."""

    #     with app.test_client() as client:

    #         data = {
    #             "username": "MrTurtle",
    #             "password": "TEST_PASSWORD",
    #             "email": "turtle@test.com",
    #             "photo": (BytesIO(b'image data'), 'test_image.png')
    #         }
                
    #         client.post('/signup', content_type="multipart/form-data", data=data, follow_redirects=True)

    #         res = client.get("/users/edit")
    #         html = res.get_data(as_text=True)

    #         self.assertEqual(res.status_code, 200)
    #         self.assertIn("""    <h2 class="dark-title">Edit Profile</h2>""", html)

    #         user = User.query.filter_by(username="MrTurtle").first()

    #         # verify that image folder was created for this user
    #         image_folder = os.path.isdir(f"static/images/{user.id}")
    #         self.assertTrue(image_folder)

    #         data = {
    #             "username": "MrTurtle",
    #             "email": "mrturtle@test.com",
    #             "image_url" : "/static/images/default-pic.png",
    #             "bio" : "I am Mr Turtle",
    #             "photo": (BytesIO(b'image data'), 'new_image.png')}

    #         res = client.post('/users/edit', content_type="multipart/form-data", data=data, follow_redirects=True)
    #         html = res.get_data(as_text=True)

    #         self.assertEqual(res.status_code, 200)
    #         self.assertIn("""<p>I am Mr Turtle</p>""", html)

    #         user = User.query.filter_by(image_name="new_image.png").all()
    #         self.assertEqual(len(user), 1)

    #         data = {
    #             "username": "MrTurtle",
    #             "email": "mrturtle@test.com",
    #             "image_url" : "/static/images/default-pic.png",
    #             "bio" : "I am Mr Turtle",
    #             "photo": (BytesIO(b'image data'), 'new_image.txt')}

    #         res = client.post('/users/edit', content_type="multipart/form-data", data=data, follow_redirects=True)

    #         user = User.query.filter_by(image_name="new_image.txt").all()
    #         self.assertEqual(len(user), 0)


    # def test_logged_out_profile_edit(self):
    #     """Test a profile edit attempt while logged out."""

    #     with app.test_client() as client:

    #         res = client.get("/users/edit", follow_redirects=True)
    #         html = res.get_data(as_text=True)

    #         # test for redirect to home page
    #         self.assertEqual(res.status_code, 200)
    #         self.assertIn("""<h2 class="dark-title">Log In</h2>""", html)


    # def test_user_change_password(self):
    #     """Test changing a user's password."""

    #     with app.test_client() as client:

    #         data = {"username" : "testuser",
    #                     "password" : "Test_Password123"}

    #         res = client.post('/login', data=data, follow_redirects=True)

    #         html = res.get_data(as_text=True)

    #         self.assertEqual(res.status_code, 200)
    #         self.assertIn("""<a class="nav-link" href="/users/profile">testuser</a>""", html)

    #         res = client.get('/users/change_password', follow_redirects=True)

    #         html = res.get_data(as_text=True)

    #         self.assertEqual(res.status_code, 200)
    #         self.assertIn("""<h2 class="dark-title">Change Password</h2>""", html)

    #         data = {
    #         "curr_password": "Test_Password123",
    #         "new_password_one": "Massachusetts",
    #         "new_password_two": "Massachusetts"}
            
    #         res = client.post('/users/change_password', data=data, follow_redirects=True)

    #         html = res.get_data(as_text=True)

    #         self.assertEqual(res.status_code, 200)
    #         self.assertIn("""<p class="display-5">testuser</p>""", html)

    #         # logout, then log back in with new password to verify
    #         res = client.get('/logout', follow_redirects=True)

    #         html = res.get_data(as_text=True)

    #         self.assertEqual(res.status_code, 200)
    #         self.assertIn("""    <h2 class="dark-title">Log In</h2>""", html)

    #         data = {"username" : "testuser",
    #                     "password" : "Massachusetts"}

    #         res = client.post('/login', data=data, follow_redirects=True)

    #         html = res.get_data(as_text=True)

    #         self.assertEqual(res.status_code, 200)
    #         self.assertIn("""<a class="nav-link" href="/users/profile">testuser</a>""", html)

    #         wrong_data_one = {
    #         "curr_password": "Gibberish",
    #         "new_password_one": "Mississippi",
    #         "new_password_two": "Mississippi"}

    #         res = client.post('/users/change_password', data=wrong_data_one, follow_redirects=True)

    #         html = res.get_data(as_text=True)

    #         self.assertEqual(res.status_code, 200)
    #         self.assertIn("""<h2 class="dark-title">Change Password</h2>""", html)

    #         wrong_data_two = {
    #         "curr_password": "Test_Password123",
    #         "new_password_one": "Gibberish",
    #         "new_password_two": "Mississippi"}
            
    #         res = client.post('/users/change_password', data=wrong_data_two, follow_redirects=True)

    #         html = res.get_data(as_text=True)

    #         self.assertEqual(res.status_code, 200)
    #         self.assertIn("""<h2 class="dark-title">Change Password</h2>""", html)

    #         wrong_data_three = {
    #         "curr_password": "Test_Password123",
    #         "new_password_one": "Mississipi",
    #         "new_password_two": "Gibberish"}
            
    #         res = client.post('/users/change_password', data=wrong_data_three, follow_redirects=True)

    #         html = res.get_data(as_text=True)

    #         self.assertEqual(res.status_code, 200)
    #         self.assertIn("""<h2 class="dark-title">Change Password</h2>""", html)

    #         # logout, then attempt to change password
    #         res = client.get('/logout', follow_redirects=True)

    #         html = res.get_data(as_text=True)

    #         self.assertEqual(res.status_code, 200)
    #         self.assertIn("""<h2 class="dark-title">Log In</h2>""", html)

    #         res = client.get("/users/change_password", follow_redirects=True)
    #         html = res.get_data(as_text=True)

    #         self.assertEqual(res.status_code, 200)
    #         self.assertIn("""<h2 class="dark-title">Log In</h2>""", html)

            
    # def test_user_delete(self):
    #     """Test delete user."""
        
    #     with app.test_client() as client:

    #         data = {
    #             "username": "MrTurtle",
    #             "password": "TEST_PASSWORD",
    #             "email": "turtle@test.com",
    #             "photo": (BytesIO(b'image data'), 'test_image.png')}

    #         res = client.post('/signup', content_type="multipart/form-data", data=data, follow_redirects=True)
    #         html = res.get_data(as_text=True)

    #         self.assertEqual(res.status_code, 200)
    #         self.assertIn("""<a class="nav-link" href="/users/profile">MrTurtle</a>""", html)

    #         user = User.query.filter_by(username="MrTurtle").first()
    #         user_id = user.id

    #         res = client.post('/users/delete', follow_redirects=True)
    #         html = res.get_data(as_text=True)
    #         self.assertEqual(res.status_code, 200)
    #         self.assertIn("""<h2 class="dark-title">Sign Up</h2>""", html)
            
    #         user = User.query.filter_by(username="MrTurtle").all()
    #         self.assertEqual(len(user), 0)

    #         # verify that image folder was created for this user
    #         image_folder = os.path.isdir(f"static/images/{user_id}")

    #         self.assertFalse(image_folder)


