# services/users/manage.py

import unittest

from flask.cli import FlaskGroup

from project import create_app, db
from project.api.models import User

app = create_app()
cli = FlaskGroup(create_app=create_app)

# adds new command line command called recreate_db
@cli.command()
def recreate_db():
    db.drop_all()
    db.create_all()
    db.session.commit()

# add command to discover and run tests
@cli.command()
def test():
    """Runs the tests without code coverage"""
    tests = unittest.TestLoader().discover('project/tests', pattern='test*.py')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        return 0
    return 1

# command to seed some users into database
@cli.command()
def seed_db():
    """Seeds the database."""
    db.session.add(User(email='spencer.schurk@gmail.com', password='test_password'))
    db.session.add(User(email='rocketeer555@gmail.com', password='test_password_2'))
    db.session.commit()


if __name__ == '__main__':
    cli()