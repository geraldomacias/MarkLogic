# services/file_system/manage.py

import unittest

from flask.cli import FlaskGroup
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from project import create_app, db

app = create_app()
cli = FlaskGroup(create_app=create_app)

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)

# add command to discover and run tests
@cli.command()
def test():
    """Runs the tests without code coverage"""
    tests = unittest.TestLoader().discover('project/tests', pattern='test*.py')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        return 0
    return 1

@cli.command()
def recreate_db():
    db.drop_all()
    db.create_all()
    db.session.commit()

if __name__ == '__main__':
    manager.run()
    cli()
