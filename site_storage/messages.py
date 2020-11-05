import enum
class ResponseStatus(str, enum.Enum):
    error = 'error'
    info = 'info'
    success = 'success'

class SiteDeleteResponse():
    def __init__(self, message, status, id=None):
        self.id = id
        self.message = message
        self.status = status