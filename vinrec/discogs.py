"""
discogs.py - part of VinRec an easy to use vinyl digitizing software
Copyright (C) 2019: Ole Lange

The ReleaseInfo objects requests and parses information about an record from discogs

TODO: This file is hacky but works, maybe I should rewrite this.
"""

import requests

class ReleaseInfo(object):

    def __init__(self, discogs_reference):
        self.discogs_reference = discogs_reference

        # Get data from discogs api
        _url = "https://api.discogs.com/releases/{0}".format(self.discogs_reference)
        response = requests.get(_url)
        if response.status_code != 200:
            try:
                data = response.json()
                data.update({"origin": "discogs"})
                if data.get("message", None) is None:
                    data.update({"message": ""})
            except:
                data = {"message": "Request failed with status code {0}".format(response.status_code), "origin": "vinrec"}
            
            # Todo: Raise something different
            raise Exception("Failed to fetch data from discogs api, {origin}: {message}".format(**data))
        
        try:
            data = response.json()
        except:
            # Todo: Raise something different
            raise Exception("Discogs api probably didn't return json")

        _status = data.get("status", None)
        _tracklist = data.get("tracklist", None)
        self.artists = data.get("artists", None)
        self.genres = data.get("genres", None)
        self.styles = data.get("styles", None) # Prefer these
        self.uri = data.get("uri", None)
        self.data_quality = data.get("data_quality", None)
        self.title = data.get("title", None)
        self.released = data.get("released", None)
        if self.released:
            self.released_year = self.released.split("-")[0]
        else:
            self.released_year = None

        if _tracklist is None:
            raise Exception("Discogs data doesn't contain any tracklist.. This is a problem")

        self.tracklist = []
        for track in _tracklist:
            self.tracklist.append(TrackInfo(track))


class TrackInfo(object):
    def __init__(self, track_data):
        self._track_data = track_data
        self.duration = self._track_data.get("duration", None)
        self.position = self._track_data.get("position", None)
        self.type = self._track_data.get("type_", None)
        self.title = self._track_data.get("title", None)
        self.extraartists = self._track_data.get("extraartists", None)

    