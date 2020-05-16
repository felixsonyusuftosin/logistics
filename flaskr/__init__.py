import os

from dotenv import load_dotenv
from flask import Flask
from distutils.tests import test_config
from .settings import init_env
from  .database import db

def create_app(ttest_config=None):
  init_env()
  # Configure and create app.
  app = Flask(__name__, instance_relative_config=True)
  db.init_app(app)
  app.config.from_mapping(
    SECRET_KEY='dev',
    DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite')
  )

  # if test_config is None:
  #   # load the instance config, if it exists, when not testing
  #       app.config.from_pyfile('config.py', silent=True)
  # else:
  #       # load the test config if passed in
  #       app.config.from_mapping(test_config)

    # ensure the instance folder exists
  try:
      os.makedirs(app.instance_path)
  except OSError:
      pass

    # a simple page that says hello
  @app.route('/hello')
  def hello():
      return 'Hello, World!'

  return app