import functools
import json

from flask import (Blueprint, request)
from jsonschema import (ValidationError, SchemaError)
from flask.json import jsonify

from flaskr.utils.catalog_validate_schema import (
    catalog_validate_schema, restock_validate_schema ,process_order_schema)
from flaskr.utils.exceptions import (InvalidInputEntered, DatabaseWriteError)
from flaskr.utils.processor import Processor
from flaskr.utils.process_order import ProcessOrder
from flaskr.utils.queries import Query
from flaskr.database import get_db
from flaskr.utils import get_order_state

catalog_bp = Blueprint('catalog_bp', __name__)


@catalog_bp.errorhandler(InvalidInputEntered)
@catalog_bp.errorhandler(DatabaseWriteError)
def handle_errors(error):
    ''' Register errors for this blueprint  '''
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@catalog_bp.route('/catalog/init', methods=('GET', 'POST'))
def init_catalog():
    db = get_db()
    query = Query(db)
    processor = Processor()
    if request.method == 'POST':
        ''' Initialize the database with default catalog provided by input  '''
        catalogs = processor.validate_json(request, catalog_validate_schema)
        success = query.load_all_catalogs(catalogs)
        response = processor.format_success_response(success)
        return response

    else:
        catalogs = query.read_all_catalogs()
        response = processor.format_success_response(catalogs)
        return response


@catalog_bp.route('/catalog/restock', methods=['GET', 'POST'])
def process_restock():
    db = get_db()
    query = Query(db)
    processor = Processor()
    process_order = get_order_state()
    if request.method == 'POST':
        stocks = processor.validate_json(request, restock_validate_schema)
        success = query.update_stocks(stocks)
        process_order.process_backlog_queue()
        response = processor.format_success_response(success)
        return response

    else:
        stocks = query.read_all_stocks()
        response = processor.format_success_response(stocks)
        return response


@catalog_bp.route('/order/process', methods=['POST', 'GET'])
def process_order():
    processor = Processor()
    process_order = get_order_state()
    if request.method == 'POST':
      order = processor.validate_json(request, process_order_schema)
      success = process_order.initiate_order(order)
      process_order.process_ship_queue()
      response = processor.format_success_response(success)
      return response

    else:
      return repr(process_order)

@catalog_bp.route('/order/ship', methods=['POST','GET'])
def ship_package():
  processor = Processor()
  process_order = get_order_state()
  if request.method == 'POST':
    process_order.process_ship_queue()
    package = request.get_json()
    success =  processor.format_success_response(package)
    return success
    
  else:
    return repr(process_order)
    





