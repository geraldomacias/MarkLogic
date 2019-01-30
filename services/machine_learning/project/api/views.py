# services/machine_learning/project/api/views.py

from flask import Blueprint, request, make_response, jsonify
from flask.views import MethodView
from flask_cors import CORS 

from project import db 
from project.api.models import BlacklistToken

ml_blueprint = Blueprint('ml', __name__)

CORS(ml_blueprint)