import csv
import json

from oauth2client import client

from dbmclient.models.base import Base


class InsertionOrder(Base):

    """
    DBM's v3 SDF
    """
    def find_by_advertiser(self, advertiser_id):
        service = self.get_service()
        request_body = {
            'filterType': 'ADVERTISER_ID',
            'filterIds': [advertiser_id],
            'fileTypes': ['INSERTION_ORDER']
        }

        try:
            request = service.sdf().download(body=request_body)
            response = request.execute()

            ios = response['insertionOrders']
            first = True
            io_rval = []
            ids = []
            #for raw_io in csv.reader(ios.encode('utf-8').split('\n')):
            for raw_io in csv.reader(ios.split('\n')):
                if len(raw_io) == 0:
                    continue

                if first:
                    first = False
                    continue

                insertionOrder = InsertionOrder(InsertionOrder.connection)
                hash_id = self.encode_for_id(raw_io[1])
                id = raw_io[0]
                if id in ids:
                    continue

                ids.append(id)
                insertionOrder['id'] = id
                insertionOrder['hash_id'] = hash_id
                insertionOrder['name'] = raw_io[2]
                insertionOrder['advertiser_name'] = ''

                ugly_budget_segments = raw_io[21]
                ugly_budget_segments = ugly_budget_segments.replace('(', '')
                ugly_budget_segments = ugly_budget_segments.split(');')

                budget_segments = []
                for budget_segment in ugly_budget_segments:
                    if budget_segment:
                        budget_segments.append(budget_segment)

                budget = 0.0
                for budget_segment in budget_segments:
                    if budget_segment:
                        segment = budget_segment.split(';')
                        if segment[0] != '':
                            value = segment[0].strip('" ').lstrip()
                            budget += float(value)

                insertionOrder['budget'] = float(budget)

                start_date = budget_segments[0].split(';')
                insertionOrder['start_date'] = start_date[1].lstrip()

                end_date = budget_segments[(len(budget_segments) - 1)].split(';')
                insertionOrder['end_date'] = end_date[2].lstrip()
                io_rval.append(insertionOrder)

            rval = {}
            rval["data"] = io_rval
            rval["request_body"] = request_body
            if len(io_rval) > 0:
                rval["msg_type"] = "success"
                rval["msg"] = "Success"
            else:
                rval["msg_type"] = "error"
                rval["msg"] = "No campaign was returned from the DSP"

        except Exception as e:
            rval = {}
            rval["msg_type"] = "error"
            rval["msg"] = "A fatal error has occurred. Please contact your administrator."
            rval["data"] = str(e)
            rval["request_body"] = request_body

        return json.dumps(rval)

    """
    DBM's v2 SDF
    """
    def find_by_advertiser_v1(self, advertiser_id):
        service = self.get_service()

        try:
            body = { 'filterType': 'ADVERTISER_ID', 'filterIds': [advertiser_id]}

            req = service.lineitems().downloadlineitems(body=body)
            resp = req.execute()

        except client.AccessTokenRefreshError:
            print ("The credentials have been revoked or expired, please re-run"
                   "the application to re-authorize")

        if 'lineItems' not in resp:
            return None
        
        lineitems = resp['lineItems']
        first = True
        rval = []
        ids = []
        #for raw_lineitem in csv.reader(lineitems.encode('utf-8').split('\n')):
        for raw_lineitem in csv.reader(lineitems.split('\n')):
            if len(raw_lineitem) == 0:
                continue

            if first:
                first = False
                continue

            insertionOrder = InsertionOrder(InsertionOrder.connection)
            id = self.encode_for_id(raw_lineitem[4])
            if id in ids:
                continue
            ids.append(id)
            insertionOrder['id'] = id
            insertionOrder['name'] = raw_lineitem[4]
            insertionOrder['advertiser_name'] = raw_lineitem[3]
            insertionOrder['budget'] = raw_lineitem[11]
            insertionOrder['start_date'] = raw_lineitem[8]
            insertionOrder['end_date'] = raw_lineitem[9]
            rval.append(insertionOrder)

        return rval
