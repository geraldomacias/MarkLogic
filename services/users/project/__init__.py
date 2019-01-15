# services/users/project/__init__.py

# QUESTION: When installing flask-s3, how do I ensure
# build_and_run.sh also does this?

import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_s3 import FlaskS3

# instantiate the db
db = SQLAlchemy()

def create_app(script_info=None):

    # instantiate the app
    app = Flask(__name__)

    # enable CORS
    CORS(app)  # new

    # set config
    app_settings = os.getenv('APP_SETTINGS')
    app.config.from_object(app_settings)

    # set up extensions
    db.init_app(app)

    # register blueprints
    from project.api.users import users_blueprint
    app.register_blueprint(users_blueprint)

    # enable s3
    app.config['FLASKS3_BUCKET_NAME'] = 'bucket_name'
    s3 = FlaskS3(app)


    # shell context for flask cli
    # this is used to register the app and db to the shell
    @app.shell_context_processor
    def ctx():
        return {'app': app, 'db': db}

    return app
