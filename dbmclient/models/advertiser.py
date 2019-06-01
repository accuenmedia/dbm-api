import csv
import sys
csv.field_size_limit(sys.maxsize)
import json

from oauth2client import client

from dbmclient.models.base import Base


class Advertiser(Base):

    def find(self, id):
        service = self.get_service()
        
        try:
            body = { 'filterType': 'ADVERTISER_ID', 'filterIds': [id]}

            req = service.lineitems().downloadlineitems(body=body)
            resp = req.execute()

        except client.AccessTokenRefreshError:
            print ("The credentials have been revoked or expired, please re-run"
                   "the application to re-authorize")

        if 'lineItems' not in resp:
            print ("NO DATA")
            return None
        
        lineitems = resp['lineItems']
        first = True
        adv = Advertiser(Advertiser.connection)
        for lineitem in csv.reader(lineitems.split('\n')):
            if first:
                first = False
                continue
            adv['id'] = id
            adv['name'] = lineitem[3]
            return adv

        return None
