import json
import requests
import os

class TmdbApi:
    baseURL = "https://api.themoviedb.org/3"
    imageURL = "http://image.tmdb.org/t/p"
    imageSize = "w185"
    apiKey = ""

    networkName = ""
    networkLogoPath = ""

    movieProductionName = ""
    movieProductionLogoPath = ""

    def __init__(self, apiKey):
        if apiKey is None:
            return
        self.apiKey = apiKey

    def getShowId(self, tvdbId):
        if tvdbId is None:
            return None
        payload = {"api_key": self.apiKey, "external_source": "tvdb_id"}
        response = requests.get(self.baseURL + "/find/" + tvdbId, params=payload)
        if response.status_code != 200:
            raise ValueError(
                'Request to slack returned an error %s, the response is:\n%s'
                % (response.status_code, response.text)
            )
        data = dict(json.loads(response.text))
        return dict(next(iter(data.get("tv_results", [])), {})).get("id", None)

    def loadMovieData(self, tmdbId):
        if tmdbId is None:
            return None
        payload = {"api_key": self.apiKey}
        response = requests.get(self.baseURL + "/movie/" + tmdbId, params=payload)
        if response.status_code != 200:
            raise ValueError(
                'Request to slack returned an error %s, the response is:\n%s'
                % (response.status_code, response.text)
            )
        data = dict(json.loads(response.text))
        production = dict(next(iter(data.get("production_companies", [])), None))
        self.movieProductionName = production.get("name")
        self.movieProductionLogoPath = self.buildLogoPath(production.get("logo_path"))

    def loadShowData(self, showId):
        if showId is None or showId == str(None):
            return None
        payload = {"api_key": self.apiKey}
        response = requests.get(self.baseURL + "/tv/" + showId, params=payload)
        if response.status_code != 200:
            raise ValueError(
                'Request to slack returned an error %s, the response is:\n%s'
                % (response.status_code, response.text)
            )
        data = dict(json.loads(response.text))
        network = dict(next(iter(data.get("networks", [])), None))
        self.networkName = network.get("name")
        self.networkLogoPath = network.get("logo_path")
    
    def normalizeName(self, sourceFileName, targetFileName=None):
        if sourceFileName is None or targetFileName is None:
            return
        fileExtension = os.path.splitext(sourceFileName)[1]
        return str(targetFileName).lower().translate(None, "(){}<>[]").replace(" ", "-") + fileExtension

    def getNetworkLogoFullPath(self, tmdbId):
        showId = self.getShowId(tmdbId)
        self.loadShowData(str(showId))
        if not self.networkLogoPath:
            return None
        return self.buildLogoPath(self.networkLogoPath)

    def buildLogoPath(self, logoPath):
        if logoPath is None:
            return None
        return self.imageURL+"/"+self.imageSize+logoPath

    def downloadMovieProductionImage(self):
        if self.movieProductionLogoPath is None or self.movieProductionName is None:
            return
        filename = self.normalizeName(self.movieProductionLogoPath, self.movieProductionName)
        self.downloadImageIfNeeded(self.movieProductionLogoPath, filename, "productionImages/")
        

    def downloadImageIfNeeded(self, url, filename, relativePath="networkImages/"):
        if url is None or filename is None or relativePath is None:
            return
        absolutePath = os.path.dirname(__file__) + "/" + relativePath
        absolutePath = os.getcwd() + "/" + relativePath
        filepath = absolutePath+str(filename)
        if os.path.isfile(filepath):
            return
        self.downloadImage(url, filepath)
    
    def downloadImage(self, url, filepath):
        img_data = requests.get(url).content
        with open(filepath, 'wb') as handler:
            handler.write(img_data)