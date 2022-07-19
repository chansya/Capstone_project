from unittest import TestCase
from app import app
from model import connect_to_db, db, example_data
from flask import session


class FlaskTestsBasic(TestCase):
    """Flask tests."""

    def setUp(self):
        """Stuff to do before every test."""

        # Get the Flask test client
        self.client = app.test_client()

        # Show Flask errors that happen during tests
        app.config['TESTING'] = True
    
    def test_index(self):
        """Test homepage page."""

        result = self.client.get("/")
        self.assertIn(b"Log in", result.data)




class FlaskTestsLoggedIn(TestCase):
    """Flask tests that use the database.."""

    def setUp(self):
        """Stuff to do before every test."""

        self.client = app.test_client()
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'key'
        
        # Connect to test database
        connect_to_db(app, "postgresql:///testdb")

        # Create tables and add sample data
        db.create_all()
        example_data()

        # Simulate user logging in 
        with self.client as c:
            with c.session_transaction() as sess:
                sess['user_email'] = 'jane@doe.com'


    def test_login(self):
        """Test login page."""

        result = self.client.post("/login",
                                  data={"email": "jane@doe.com", 
                                        "password": "test123"},
                                        follow_redirects=True)
        self.assertIn(b"Overview", result.data)
        self.assertNotIn(b"Log in", result.data)

    def test_progress_page(self):
        """Test that user can progress page when logged in."""

        result = self.client.get("/progress", follow_redirects=True)
        self.assertIn(b"Overview", result.data)
        self.assertNotIn(b"This Time Let's Make It STICK", result.data)

    def test_progress_page(self):
        """Test that user can progress page when logged in."""

        result = self.client.get("/progress", follow_redirects=True)
        self.assertIn(b"Overview", result.data)
        self.assertNotIn(b"This Time Let's Make It STICK", result.data)

    def test_manage_page(self):
        """Test that user can profile page when logged in."""

        result = self.client.get("/manage", follow_redirects=True)
        self.assertIn(b"jane@doe.com", result.data)
        self.assertNotIn(b"Overview", result.data)

    def test_logout_page(self):
        """Test profile page."""

        result = self.client.get("/logout", follow_redirects=True)
        self.assertIn(b"Log in", result.data)
        self.assertNotIn(b"Overview", result.data)


    def tearDown(self):
        """Do at end of every test."""

        db.session.remove()
        db.drop_all()
        db.engine.dispose()




# class FlaskTestsLogInLogOut(TestCase):  # Bonus example. Not in lecture.
#     """Test log in and log out."""

#     def setUp(self):
#         """Before every test"""

#         app.config['TESTING'] = True
#         self.client = app.test_client()

#     def test_login(self):
#         """Test log in form.

#         Unlike login test above, 'with' is necessary here in order to refer to session.
#         """

#         with self.client as c:
#             result = c.post('/login',
#                             data={'user_id': '42', 'password': 'abc'},
#                             follow_redirects=True
#                             )
#             self.assertEqual(session['user_id'], '42')
#             self.assertIn(b"You are a valued user", result.data)

#     def test_logout(self):
#         """Test logout route."""

#         with self.client as c:
#             with c.session_transaction() as sess:
#                 sess['user_id'] = '42'

#             result = self.client.get('/logout', follow_redirects=True)

#             self.assertNotIn(b'user_id', session)
#             self.assertIn(b'Logged Out', result.data)


if __name__ == "__main__":
    import unittest

    unittest.main()
