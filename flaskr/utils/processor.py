import json
from jsonschema import (validate, ValidationError, SchemaError)
from flask.json import jsonify

from flaskr.utils.exceptions import (InvalidInputEntered, DatabaseWriteError)

class Processor():
    ''' Processor required for validation and cleaning up input data. '''

    def validate_json(self, incomming_request, validation_schema):
        ''' Validate the incoming request.'''
        try:
            catalogs = incomming_request.get_json()
            validate(catalogs, schema=validation_schema)
            return catalogs

        except (ValidationError, SchemaError) as e:
            ''' Typically this represents errors involving the json validation. '''
            raise InvalidInputEntered(
                'validation failed: Reason {}'.format(e), status_code=400)

        except Exception as e:
            ''' This error is called if there is a structural mismatch in the json passed in '''
            raise InvalidInputEntered(
                'The input json is malformed {}'.format(e), status_code=400)

    def format_success_response(self, data):
        ''' Format response to be returned to user as a response object. '''
        response = jsonify(data)
        response.status_code = 200
        return response
