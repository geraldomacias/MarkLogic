# services/users/manage.py

from flask.cli import FlaskGroup

from project import app


cli = FlaskGroup(app)

# adds new command line command called recreate_db
@cli.command()
def recreate_db():
    db.drop_all()
    db.create_all()
    db.session.commit()


if __name__ == '__main__':
    cli()