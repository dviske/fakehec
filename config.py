import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SERVER_NAME = os.environ.get('SERVER_NAME') or 'localhost:5000'
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'lol-very-secure-key-omegalul'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
      'sqlite:///' + os.path.join(basedir, 'app.db')