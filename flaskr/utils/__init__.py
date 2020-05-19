from flask import  g
from flaskr.utils.process_order import ProcessOrder
from flask.cli import with_appcontext

def get_order_state():
  if 'process_order' not in g:
    g.process_order =  ProcessOrder()
  return g.process_order
