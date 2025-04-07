from flask import Blueprint

bp = Blueprint('collector', __name__)

from app.collector import routes