from app import db


class Permission:
    BANNED = 0
    COMMENT = 1
    FOLLOW = 2
    WRITE = 4
    MODERATE = 8
    ADMIN = 16


roles = {
    'user': [Permission.COMMENT, Permission.WRITE, Permission.FOLLOW],
    'moderator': [
        Permission.COMMENT, Permission.WRITE, Permission.FOLLOW,
        Permission.MODERATE],
    'administrator': [
        Permission.COMMENT, Permission.WRITE, Permission.FOLLOW,
        Permission.MODERATE, Permission.ADMIN]
}
default_role = 'user'


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), unique=True)
    default = db.Column(db.Boolean(), default=False)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return f'<Role {self.name}>'

    def __init__(self, *args, **kwargs):
        super(Role, self).__init__(*args, **kwargs)
        if self.permissions is None:
            self.permissions = 0

    def add_permission(self, perm: int):
        """add given permission to the role"""
        if not self.has_permission(perm):
            self.permissions += perm
    
    def remove_permission(self, perm: int):
        """remove given permission from the role"""
        if self.has_permission(perm):
            self.permissions -= perm
    
    def has_permission(self, perm: int) -> bool:
        """check if role have the given permission"""
        return self.permissions & perm == perm
    
    def reset_permissions(self):
        """remove all permissions from role"""
        self.permissions = 0
    
    @staticmethod
    def set_roles(roles: dict=roles, default_role: str=default_role):
        """insert given roles and update existing ones"""
        for role_name in roles:
            role = Role.query.filter_by(name=role_name).first()
            if not role:
                role = Role(name=role_name)
            role.reset_permissions()

            for permission in roles[role_name]:
                role.add_permission(permission)
            role.default = (role_name == default_role)

            db.session.add(role)
        db.session.commit()
