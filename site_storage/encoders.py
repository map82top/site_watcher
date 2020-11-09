from sqlalchemy.ext.declarative import DeclarativeMeta
import json
from datetime import date, datetime



class AlchemyEncoder(json.JSONEncoder):

    def default(self, obj):
        cl = obj.__class__
        # an SQLAlchemy class
        fields = {}
        for field in [x for x in dir(obj) if not x.startswith('_') and x != 'metadata']:
            data = obj.__getattribute__(field)
            try:
                if isinstance(data, (datetime, date)):
                    data = data.isoformat()
                else:
                    json.dumps(data)
                fields[field] = data
            except TypeError:
                fields[field] = None
        # a json-encodable dict
        return fields
