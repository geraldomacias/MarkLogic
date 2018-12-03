# services/users/manage.py

from flask.cli import FlaskGroup

from project import app

import unittest


cli = FlaskGroup(app)

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


if __name__ == '__main__':
    cli()