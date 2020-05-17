import functools
import json

from flask import (Blueprint, request)
from jsonschema import (ValidationError, SchemaError)
from flask.json import jsonify

from flaskr.utils.catalog_validate_schema import catalog_validate_schema
from flaskr.utils.exceptions import (InvalidInputEntered, DatabaseWriteError)
from flaskr.utils.processor import Processor
from flaskr.utils.queries import Query
from flaskr.database import get_db



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

@catalog_bp.route('/catalog/restock', methods=['POST'])
def process_restock():
    pass
