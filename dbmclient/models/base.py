import base64
import json
import requests

from apiclient import discovery

_API_VERSION = 'v1'

class Base(dict):

    connection = None

    def __init__(self, connection):
        Base.connection = connection
        super(Base, self).__init__()

    def get_service(self):
        auth = Base.connection.get_authorization()
        return discovery.build('doubleclickbidmanager', _API_VERSION, http=auth)

    def encode_for_id(self, id):
        # TERRIBLE!!!!! BUT GOOGLE DOESNT SEND US AN ID.
        # remove '=' because it messes up urls. we never decode so its not a big deal.
        return base64.b64encode(id.encode('utf-8')).strip('=')

    def decode_id(self, id):
        # TERRIBLE!!!!! BUT GOOGLE DOESNT SEND US AN ID.
        # add '=' because we remove it when encoding to not mess up urls.
        
        missing_padding = 4 - len(id) % 4
        if missing_padding:
            id += b'='* missing_padding
        return base64.b64decode(id.decode('utf-8'))

    def get_object(self, data):
        new_obj = self.__class__(Base.connection)
        new_obj.import_props(data)
        return new_obj

    def import_props(self, props):
        for key, value in props.iteritems():
            self[key] = value
