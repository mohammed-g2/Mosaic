import os
import os.path
from flask import Flask


def register_cli(app: Flask) -> None:
    """Register cli commands."""

    @app.cli.command('init')
    def init():
        """Initialize the application."""
        from app.models import Role
        from config import basedir
        if not os.path.exists(os.path.join(basedir, 'data')):
            os.makedirs(os.path.join(basedir, 'data'))
            print('Created [data] directory for data files.')

        print('Setting database.')
        os.system('flask db init')
        os.system('flask db migrate')
        os.system('flask db upgrade')
        Role.set_roles()
        print('Created user roles.')

    
    @app.cli.command('test')
    def test():
        """Run unit tests."""
        import unittest
        tests = unittest.TestLoader().discover('tests')
        unittest.TextTestRunner(verbosity=2).run(tests)
