import json
import re
import collections
from io import StringIO

from googleapiclient import discovery
from googleapiclient import http

class SupportedExchange:

    GS_DBM_BUCKET = "gdbm-public"
    GS_DBM_BUCKET_PREFIX = "entity/"
    GS_DBM_RPT_RE = GS_DBM_BUCKET_PREFIX + r"(?P<yyyy>\d{4})(?P<mm>\d\d)(?P<dd>\d\d)\.0\.SupportedExchange\.json"

    def __init__(self, connection):
        SupportedExchange.connection = connection

    def get_service(self):
        auth = SupportedExchange.connection.get_authorization()
        return discovery.build('storage', 'v1', http=auth)

    def _get_latest_file(self):
        service = self.get_service()

        max_pages = 100

        files = []
        req = service.objects().list(bucket=SupportedExchange.GS_DBM_BUCKET, prefix=SupportedExchange.GS_DBM_BUCKET_PREFIX)
        count = 0
        while req is not None:
            if count == max_pages:
                print ("more than max pages")
                break
            count += 1
            resp = req.execute()
            files.extend(resp.get('items', []))
            req = service.objects().list_next(req, resp)

        data = {}
        for key in files:
            # Only sync files matching the known pattern.
            match = re.match(SupportedExchange.GS_DBM_RPT_RE, key['name'])
            if match:
                data[key['name']] = key

        ordered = collections.OrderedDict(sorted(data.items()))
        latest_file = ordered.popitem()

        return latest_file[1]

    def load_all(self):
        latest_file = self._get_latest_file()
        service = self.get_service()

        req = service.objects().get_media(bucket=SupportedExchange.GS_DBM_BUCKET, object=latest_file['name'])
        
        out_file = StringIO()
        downloader = http.MediaIoBaseDownload(out_file, req)
        
        done = False
        while done is False:
            status, done = downloader.next_chunk()

        return json.loads(out_file.getvalue())
