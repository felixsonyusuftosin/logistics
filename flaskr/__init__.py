import os

from dotenv import load_dotenv
from flask import Flask
from distutils.tests import test_config
from flaskr.settings import init_env
from flaskr.database import init_app
from flaskr.views.catalog import catalog_bp

def create_app(test_config=None):
  init_env()
  # Configure and create app.
  app = Flask(__name__, instance_relative_config=True)
  app.config.from_mapping(
    SECRET_KEY='dev',
    DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite')
  )
  init_app(app)
  try:
      os.makedirs(app.instance_path)
  except OSError:
      pass

  app.register_blueprint(catalog_bp)
  
  return app