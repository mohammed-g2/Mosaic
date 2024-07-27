import unittest
from app import create_app, db
from app.models import Role, Permission


class TestRoleModel(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_ctx = self.app.app_context()
        self.app_ctx.push()
        db.create_all()
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_ctx.pop()
    
    def test_create_roles(self):
        r_1 = Role(name='r1')
        r_2 = Role(name='r2')
        db.session.add_all([r_1, r_2])
        db.session.commit()
        self.assertListEqual(Role.query.all(), [r_1, r_2])
    
    def test_permissions_are_set_to_0(self):
        r = Role()
        self.assertEqual(r.permissions, 0)

    def test_add_permission_method(self):
        r = Role()
        self.assertFalse(r.has_permission(Permission.WRITE))
        r.add_permission(Permission.WRITE)
        self.assertEqual(r.permissions, Permission.WRITE)
    
    def test_remove_permission(self):
        r = Role()
        r.permissions += Permission.WRITE
        r.permissions += Permission.COMMENT
        r.remove_permission(Permission.WRITE)
        self.assertTrue(r.has_permission(Permission.COMMENT))
        self.assertFalse(r.has_permission(Permission.WRITE))
        self.assertEqual(r.permissions, Permission.COMMENT)
    
    def test_reset_permissions_method(self):
        r = Role()
        r.add_permission(Permission.WRITE)
        r.add_permission(Permission.MODERATE)
        r.reset_permissions()
        self.assertEqual(r.permissions, 0)
    
    def test_has_permission_method(self):
        r = Role()
        r.add_permission(Permission.ADMIN)
        r.add_permission(Permission.MODERATE)
        self.assertFalse(r.has_permission(Permission.WRITE))
        self.assertTrue(r.has_permission(Permission.MODERATE))
        self.assertTrue(r.has_permission(Permission.ADMIN))
    
    def test_set_roles_method(self):
        Role.set_roles({
            'role_1': [Permission.WRITE], 
            'role_2': [Permission.WRITE, Permission.MODERATE]}, default_role='role_1')
        role_1 = Role.query.filter_by(name='role_1').first()
        role_2 = Role.query.filter_by(name='role_2').first()
        
        self.assertEqual(Role.query.count(), 2)
        self.assertIsNotNone(role_1)
        self.assertIsNotNone(role_2)
        self.assertTrue(role_1.default)
        self.assertTrue(role_1.has_permission(Permission.WRITE))
        self.assertFalse(role_1.has_permission(Permission.MODERATE))
        self.assertFalse(role_2.default)
        self.assertTrue(role_2.has_permission(Permission.WRITE))
        self.assertTrue(role_2.has_permission(Permission.MODERATE))
        self.assertFalse(role_2.has_permission(Permission.COMMENT))
