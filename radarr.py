import requests
import json

class RadarrApi:
    baseUrl = None
    apiKey = None

    indexer = ""
    year = ""
    tmdbId = None

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
                'Request returned an error %s, the response is:\n%s'
                % (response.status_code, response.text)
            )
        data = dict(json.loads(response.text))
        for record in data["records"]:
            record = dict(record)
            recordDownloadId = record.get("downloadId")
            indexer = record.get("data", {}).get("indexer")
            if recordDownloadId == downloadId and indexer is not None:
                movie = record.get("movie", {})
                self.year = str(movie.get("year", ""))
                self.indexer = indexer
                self.tmdbId = str(movie.get("tmdbId", ""))
                return
        return

    def getMovie(self, movieId):
        payload = {"apikey": self.apiKey}
        response = requests.get(self.baseUrl + "/movie/" + movieId, params=payload)
        if response.status_code != 200:
            raise ValueError(
                'Request returned an error %s, the response is:\n%s'
                % (response.status_code, response.text)
            )
        return json.loads(response.text)

    def unmonitorMovie(self, movie):
        movie["monitored"] = False
        headers = {'Content-type': 'application/json', 'X-Api-Key': self.apiKey}
        response = requests.put(self.baseUrl + "/movie/" + str(movie["id"]), data=json.dumps(movie), headers=headers)
        if response.status_code != 202:
            raise ValueError(
                'Request returned an error %s, the response is:\n%s'
                % (response.status_code, response.text)
            )

    def unmonitorMovieIfNeeded(self, movieId, event):
        if event == "Download":
            movie = self.getMovie(movieId)
            if movie.get("monitored", False):
                self.unmonitorMovie(movie)