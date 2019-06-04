import os
import requests
import json
import base64

from oauth2client.service_account import ServiceAccountCredentials
import httplib2

class DBMP12FileDoesNotExist(Exception):
    pass

class Connection:

    authorization_token = None
    # use Accuen DBM as the p12, NOT API Project!
    # key_file = os.path.dirname(os.path.realpath(__file__)) + "/Accuen-DBM-9cf79343fc42.p12"

    def __init__(self, p12=None):
        Connection.username = '342021153007-se0r0lv1a0sckq581ko2cnkre12cce9b@developer.gserviceaccount.com'
        try:
            if p12:
                self.key_file = p12
            else:
                key_file = os.environ['P12FILEDBM']

            with open(self.key_file, 'rb') as f:
                Connection.password = f.read()
        except:
            raise DBMP12FileDoesNotExist

    def connect(self):
        Connection.get_authorization()

    def get_authorization(self):
        if Connection.authorization_token is None:
            Connection.authorization_token = self.authorize()
        return Connection.authorization_token

    def authorize(self):

        credentials = ServiceAccountCredentials.from_p12_keyfile(Connection.username, self.key_file, scopes=['https://www.googleapis.com/auth/doubleclickbidmanager', 'https://www.googleapis.com/auth/cloud-platform'])
        _API_VERSION = 'v1'

        # Create an httplib2.Http object to handle our HTTP requests and authorize it
        # with our good Credentials.
        http = httplib2.Http()
        Connection.authorization_token = credentials.authorize(http)
        return Connection.authorization_token
