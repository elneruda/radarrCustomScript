import requests
import json

class RadarrApi:
    baseUrl = None
    apiKey = None

    indexer = ""
    year = ""

    def __init__(self, baseUrl, apiKey):
        self.baseUrl = baseUrl
        self.apiKey = apiKey

    def loadData(self, downloadId):
        if self.apiKey is None or self.baseUrl is None or downloadId is None:
            return

        payload = {"apikey": self.apiKey, "page": 1, "sortKey": "date", "sortDir": "desc", "pageSize": 20}
        response = requests.get(self.baseUrl + "/history", params=payload)
        if response.status_code != 200:
            raise ValueError(
                'Request to slack returned an error %s, the response is:\n%s'
                % (response.status_code, response.text)
            )
        data = dict(json.loads(response.text))
        for record in data["records"]:
            record = dict(record)
            recordDownloadId = record.get("downloadId")
            indexer = record.get("data", {}).get("indexer")
            if recordDownloadId == downloadId and indexer is not None:
                self.year = str(record.get("movie", {}).get("year", ""))
                self.indexer = indexer
        return