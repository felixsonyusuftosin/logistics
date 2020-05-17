import functools
import json

from flask import (Blueprint, request)
from jsonschema import (ValidationError, SchemaError)
from flask.json import jsonify

from flaskr.utils.validate_catalog_schema import catalog_validate_schema
from flaskr.utils.exceptions import (InvalidInputEntered, DatabaseWriteError)
from flaskr.utils.processor import Processor
from flaskr.utils.queries import Query
from flaskr.database import get_db


class Catalog():
    def __init__(self):
        self.catalog_bp = Blueprint('catalog_bp', __name__)
        self.db = get_db()
        self.query = Query(db)
        self.processor = Processor()

    @catalog_bp.errorhandler(InvalidInputEntered)
    @catalog_bp.errorhandler(DatabaseWriteError)
    def handle_errors(self, error):
        ''' Register errors for this blueprint  '''
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response

    @catalog_bp.route('/catalog/init', methods=('GET', 'POST'))
    def init_catalog(self):
        if request.method == 'POST':
            ''' Initialize the database with default catalog provided by input  '''
            catalogs = self.processor.validate_json(request, catalog_validate_schema)
            success = self.query.load_all_catalogs(catalogs)
            response = self.processor.format_success_response(success)
            return response
        else:
            catalogs = self.query.read_all_catalogs()
            response = self.processor.format_success_response(catalogs)
            return response

    @catalog_bp.route('/catalog/restock', methods=('POST'))
    def process_restock(self):
        pass
