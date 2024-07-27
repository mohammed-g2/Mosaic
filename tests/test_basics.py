import unittest
from flask import current_app
from app import create_app


class TestBasics(unittest.TestCase):
    def setUp(self) -> None:
        self.app = create_app('testing')
        self.app_ctx = self.app.app_context()
        self.app_ctx.push()
    
    def tearDown(self) -> None:
        self.app_ctx.pop()

    def test_app_exists(self):
        self.assertIsNotNone(current_app)
    
    def test_app_is_testing(self):
        self.assertTrue(current_app.config['TESTING'])
    
    def test_app_using_in_memory_db(self):
        self.assertEqual(current_app.config['SQLALCHEMY_DATABASE_URI'], 'sqlite://')
