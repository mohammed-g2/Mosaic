import unittest
import time
import jwt
from app import create_app, db
from app.models import User, Role, Permission
from app.models.role import roles, default_role


class TestUserModel(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_ctx = self.app.app_context()
        self.app_ctx.push()
        db.create_all()
        Role.set_roles(roles, default_role)
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_ctx.pop()
    
    def test_create_users(self):
        u_1 = User()
        u_2 = User()
        db.session.add_all([u_1, u_2])
        db.session.commit()
        self.assertListEqual(User.query.all(), [u_1, u_2])
    
    def test_user_role_is_set(self):
        u = User()
        self.assertIsNotNone(u.role)
        self.assertEqual(u.role, Role.query.filter_by(default=True).first())
    
    def test_admin_role_is_set(self):
        admin = User(email=self.app.config['APP_ADMIN'])
        self.assertEqual(admin.role, Role.query.filter_by(name='administrator').first())
    
    def test_password_setter(self):
        u = User(password='pass')
        self.assertIsNotNone(u.password_hash)
    
    def test_password_is_not_readable(self):
        u = User(password='pass')
        with self.assertRaises(AttributeError):
            u.password
    
    def test_user_password_hashed(self):
        u_1 = User(password='pass')
        u_2 = User(password='pass')
        self.assertNotEqual(u_1.password_hash, u_2.password_hash)
        self.assertNotEqual(u_1.password_hash, 'pass')
        self.assertGreater(len(u_1.password_hash), 4)
    
    def test_user_role_relationship(self):
        r = Role()
        db.session.add(r)
        db.session.commit()
        u_1 = User(role=r)
        u_2 = User(role=r)
        db.session.add_all([u_1, u_2])
        db.session.commit()
        self.assertListEqual(r.users.all(), [u_1, u_2])
        self.assertEqual(u_1.role, r)
    
    def test_verify_password_method(self):
        u = User(password='pass')
        self.assertTrue(u.verify_password('pass'))
        self.assertFalse(u.verify_password('cats'))
    
    def test_can_method(self):
        u = User()
        self.assertTrue(u.can(Permission.WRITE))
        self.assertFalse(u.can(Permission.MODERATE))

    def test_is_admin_method(self):
        u = User()
        admin = User(email=self.app.config['APP_ADMIN'])
        self.assertFalse(u.is_admin())
        self.assertTrue(admin.is_admin())

    def test_generate_token_method(self):
        token = User().generate_token({'token': 1}, 600)
        payload = jwt.decode(
            token, self.app.config['SECRET_KEY'], algorithms='HS256')
        self.assertEqual(payload.get('token'), 1)
    
    def test_confirm_method(self):
        user = User()
        db.session.add(user)
        db.session.commit()
        token_1 = user.generate_token({'confirm': user.id})
        token_2 = user.generate_token({'confirm': user.id}) + 'A'
        token_3 = user.generate_token({'user_id': user.id})
        token_4 = user.generate_token({'confirm': user.id}, -1)

        self.assertTrue(user.confirm(token_1))
        
        self.assertFalse(user.confirm(token_2))
        self.assertFalse(user.confirm(token_3))
        self.assertFalse(user.confirm(token_4))

    def test_reset_password_method(self):
        user = User()
        token_1 = user.generate_token({'email': 'new@example.com'})
        token_2 = user.generate_token({'email': 'new@example.com'}) + 'A'
        token_3 = user.generate_token({'user_': 'new@example.com'})
        token_4 = user.generate_token({'email': 'new@example.com'}, -1)

        self.assertEqual(User.reset_password(token_1), 'new@example.com')

        self.assertFalse(User.reset_password(token_2))
        self.assertFalse(User.reset_password(token_3))
        self.assertFalse(User.reset_password(token_4))
    
    def test_update_email_method(self):
        user = User(email='email@example.com')
        token_1 = user.generate_token({'update-email': 'new@email.com'})
        token_2 = user.generate_token({'update-email': 'new@email.com'}) + 'A'
        token_3 = user.generate_token({'update-username': 'new@email.com'})
        token_4 = user.generate_token({'update-email': 'new@email.com'}, -1)

        self.assertTrue(user.update_email(token_1))

        self.assertFalse(user.update_email(token_2))
        self.assertFalse(user.update_email(token_3))
        self.assertFalse(user.update_email(token_4))
