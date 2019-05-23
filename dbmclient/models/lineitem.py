import csv
import sys
csv.field_size_limit(sys.maxsize)
import json
import base64

from oauth2client import client

from dbmclient.models.base import Base


class Lineitem(Base):

    def __init__(self, connection, raw_lineitem=None):
        super(Lineitem, self).__init__(connection)

        if raw_lineitem:
            # Uses SDF v3
            self['id'] = raw_lineitem[0]
            self['campaign_id'] = raw_lineitem[1]
            self['name'] = raw_lineitem[4]
            self['status'] = raw_lineitem[6]
            self['start_date'] = raw_lineitem[7]
            self['end_date'] = raw_lineitem[8]
            self['budget'] = raw_lineitem[10]

            """
            # Uses SDF v2
            self['id'] = raw_lineitem[0]
            self['name'] = raw_lineitem[5]
            self['active'] = raw_lineitem[5]
            self['budget'] = raw_lineitem[18]
            self['start_date'] = raw_lineitem[15]
            self['end_date'] = raw_lineitem[16]
            self['status'] = raw_lineitem[7]
            self['campaign_name'] = raw_lineitem[4]
            self['campaign_id'] = self.encode_for_id(raw_lineitem[4])
            """

# EJJ: Mappings for SDF format. We would use this but the API fails sometimes when we use this format.
#            self['id'] = raw_lineitem[0]
#            self['io_id'] = raw_lineitem[1]
#            self['type'] = raw_lineitem[2]
#            self['name'] = raw_lineitem[3]
#            self['timestamp'] = raw_lineitem[4]
#            self['status'] = raw_lineitem[5]
#            self['start_date'] = raw_lineitem[6]
#            self['end_date'] = raw_lineitem[7]
#            self['budget_type'] = raw_lineitem[8]
#            self['budget'] = raw_lineitem[9]
#            self['pacing'] = raw_lineitem[10]
#            self['pacing_rate'] = raw_lineitem[11]
#            self['pacing_amount'] = raw_lineitem[12]
#            self['frequency_enabled'] = raw_lineitem[13]
#            self['frequency_exposures'] = raw_lineitem[14]
#            self['frequency_period'] = raw_lineitem[15]
#            self['frequency_amount'] = raw_lineitem[16]
#            self['partner_revenue_model'] = raw_lineitem[17]
#            self['partner_revenue_amount'] = raw_lineitem[18]
#            self['conversion_counting_type'] = raw_lineitem[19]
#            self['conversion_counting_pct'] = raw_lineitem[20]
#            self['conversion_pixel_ids'] = raw_lineitem[21]
#            self['fees'] = raw_lineitem[22]
#            self['integration_code'] = raw_lineitem[23]
#            self['details'] = raw_lineitem[24]
#            self['bid_strategy_type'] = raw_lineitem[25]
#            self['bid_strategy_value'] = raw_lineitem[26]
#            self['bid_strategy_unit'] = raw_lineitem[27]
#            self['creative_assignments'] = raw_lineitem[28]
#            self['geo_targeting_include'] = raw_lineitem[29]
#            self['geo_targeting_exclude'] = raw_lineitem[30]
#            self['lang_targeting_include'] = raw_lineitem[31]
#            self['lang_targeting_exclude'] = raw_lineitem[32]
#            self['device_targeting_include'] = raw_lineitem[33]
#            self['device_targeting_exclude'] = raw_lineitem[34]
#            self['browser_targeting_include'] = raw_lineitem[35]
#            self['browser_targeting_exclude'] = raw_lineitem[36]
#            self['brand_safety_labels'] = raw_lineitem[37]
#            self['brand_safety_sensitivity'] = raw_lineitem[38]
#            self['brand_safety_custom'] = raw_lineitem[39]
#            self['channel_targeting_include'] = raw_lineitem[40]
#            self['channel_targeting_exclude'] = raw_lineitem[41]
#            self['site_targeting_include'] = raw_lineitem[42]
#            self['site_targeting_exclude'] = raw_lineitem[43]
#            self['app_targeting_include'] = raw_lineitem[44]
#            self['app_targeting_exclude'] = raw_lineitem[45]
#            self['cat_targeting_include'] = raw_lineitem[46]
#            self['cat_targeting_exclude'] = raw_lineitem[47]
#            self['keyword_targeting_include'] = raw_lineitem[48]
#            self['keyword_targeting_exclude'] = raw_lineitem[49]
#            self['audience_targeting_similar'] = raw_lineitem[50]
#            self['audience_targeting_include'] = raw_lineitem[51]
#            self['audience_targeting_exclude'] = raw_lineitem[52]
#            self['inventory_targeting_include'] = raw_lineitem[53]
#            self['inventory_targeting_exclude'] = raw_lineitem[54]
#            self['daypart_targeting'] = raw_lineitem[55]
#            self['env_targeting'] = raw_lineitem[56]

    def find_by_advertiser(self, advertiser_id):
        return self.find_by_object(advertiser_id, 'ADVERTISER_ID')

    """
    SDF v3
    """
    def find_by_campaign(self, campaign_id):
        return self.find_by_object(campaign_id, 'INSERTION_ORDER_ID')

    def find_by_object(self, object_id, filter_type):
        service = self.get_service()
        request_body = {
            'filterType': filter_type,
            'filterIds': [object_id],
            'fileTypes': ['LINE_ITEM']
        }

        try:
            request = service.sdf().download(body=request_body)
            response = request.execute()

            lineitems = response['lineItems']
            first = True
            lineitem_rval = []
            #for raw_lineitem in csv.reader(lineitems.encode('utf-8').split('\n')):
            for raw_lineitem in csv.reader(lineitems.split('\n')):
                if len(raw_lineitem) == 0:
                    continue

                if first:
                    first = False
                    continue

                lineitem = Lineitem(Lineitem.connection, raw_lineitem)
                lineitem_rval.append(lineitem)

            rval = {}
            rval["data"] = lineitem_rval
            if len(lineitem_rval) > 0:
                rval["msg_type"] = "success"
                rval["msg"] = ""
            else:
                rval["msg_type"] = "error"
                rval["msg"] = "No line item object was returned from the DSP"

        except Exception as e:
            rval = {}
            rval["msg_type"] = "error"
            rval["msg"] = "A fatal error has occurred. Please contact your administrator."
            rval["data"] = str(e)
            rval["request_body"] = request_body

        return json.dumps(rval)

    """
    SDF V2
    """
    def find_by_campaign_v1(self, campaign_id):
        return self.find_by_object(campaign_id, 'IO_ID')

    def find_by_object_v1(self, object_id, filter_type):
        service = self.get_service()

        try:
            body = { 'filterType': filter_type, 'filterIds': [object_id]}
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
        #for raw_lineitem in csv.reader(lineitems.encode('utf-8').split('\n')):
        for raw_lineitem in csv.reader(lineitems.split('\n')):
            if len(raw_lineitem) == 0:
                continue

            if first:
                first = False
                continue

            lineitem = Lineitem(Lineitem.connection, raw_lineitem)
            rval.append(lineitem)

        return rval


    @property
    def id(self):
        return self.get('id')

    @id.setter
    def id(self, id):
        self.data['id'] = id

    @property
    def name(self):
        return self.get('name')

    @name.setter
    def name(self, name):
        self['name'] = name

    @property
    def active(self):
        # return same as status for now.
        return self.get('status') == "Active"

    @property
    def budget(self):
        return self.get('budget')

    @budget.setter
    def budget(self, budget):
        self['budget_type'] = 'amount'
        self['budget'] = budget

    @property
    def start_date(self):
        return self['start_date']

    @start_date.setter
    def start_date(self, start_date):
        self['start_date'] = start_date

    @property
    def end_date(self):
        return self.get('end_date')

    @end_date.setter
    def end_date(self, end_date):
        self['end_date'] = end_date

    @property
    def status(self):
        return self.get('status')

    @status.setter
    def status(self, status):
        if status not in ["Active", "Paused", "Deleted"]:
            return
        self['status'] = status

    @property
    def campaign_id(self):
        # SDF v3
        return self['campaign_id']
        # SDF v2
        #return self.encode_for_id(self['campaign_name'])

    def save(self):
        return
        service = self.get_service()

        header = "Line Item Id,Partner Name,Partner Id,Advertiser Name,Io Name,Line Item Name,Line Item Timestamp,Line Item Status,Io Start Date,Io End Date,Io Budget Type,Io Budget Amount,Io Pacing,Io Pacing Rate,Io Pacing Amount,Line Item Start Date,Line Item End Date,Line Item Budget Type,Line Item Budget Amount,Line Item Pacing,Line Item Pacing Rate,Line Item Pacing Amount,Line Item Frequency Enabled,Line Item Frequency Exposures,Line Item Frequency Period,Line Item Frequency Amount,Bid Price,Partner Revenue Model,Partner Revenue Amount,Current Audience Targeting Ids,Current Audience Targeting Names"
        
        lineitem = ",".join(self.raw_lineitem)

        try:
            
            body = { 'lineItems': "{0}\n{1}".format(header, lineitem) }

            req = service.lineitems().uploadlineitems(body=body)
            resp = req.execute()

            print (resp)

        except client.AccessTokenRefreshError:
            print ("The credentials have been revoked or expired, please re-run"
                   "the application to re-authorize")

