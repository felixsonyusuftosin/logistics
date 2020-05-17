# Define application defined exceptions

class InvalidInputEntered(Exception):
  ''' This is the exception class for invalid input. '''
  status_code = 400
  def __init__(self, message, status_code=None, payload=None ):
    Exception.__init__(self)
    self.message = message
    if status_code is not None:
      self.status_code = status_code
    self.payload = payload

  def to_dict(self):
    rv = dict(self.payload or ())
    rv['message'] = self.message
    return rv

class DatabaseWriteError(Exception):
  ''' This is the exception class for database write error. '''
  status_code = 500
  def __init__(self, message, status_code=None, payload=None ):
    Exception.__init__(self)
    self.message = message
    if status_code is not None:
      self.status_code = status_code
    self.payload = payload

  def to_dict(self):
    rv = dict(self.payload or ())
    rv['message'] = self.message
    return rv