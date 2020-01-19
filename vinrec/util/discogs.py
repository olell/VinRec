# Global imports
import requests
import json
import urllib.parse
import os
import time
import uuid

# Local imports
from vinrec.models.release_information import ReleaseCache
from vinrec.models.release_information import ReleaseInfo
from vinrec.models.release_information import TrackInfo
from vinrec.models.release_information import ImageInfo

from vinrec.util.data_management import create_permanent_directories
from vinrec.const.locations import COVER_PATH


class SearchResultCache(object):

    instance = None
    
    @staticmethod
    def _getinstance():
        if SearchResultCache.instance is not None:
            return SearchResultCache.instance
        else:
            cache = SearchResultCache()
            SearchResultCache.instance = cache
            return cache

    @staticmethod
    def get(query):
        return SearchResultCache._getinstance()._get(query)

    @staticmethod
    def get_by_id(sid):
        return SearchResultCache._getinstance()._get_by_id(sid)

    @staticmethod
    def add(query, results):
        return SearchResultCache._getinstance()._add(query, results)

    def __init__(self):
        self.cache = {}

    def _add(self, query, results):
        sid = str(len(self.cache) + 1)
        self.cache.update({
                query: {
                    "results": results,
                    "timestamp": time.time(),
                    "id": sid
                }
            })
        return sid
    
    def _get(self, query):
        cached = self.cache.get(query, None)
        if cached is not None:
            timestamp = cached["timestamp"]
            if time.time() - timestamp > 1800:
                self.cache.pop(query)
                return None
            else:
                return cached["id"], cached["results"]
        else:
            return None

    def _get_by_id(self, sid):
        for key in self.cache:
            entry = self.cache[key]
            if entry["id"] == sid:
                return sid, entry["results"]
        else:
            return None



def search(query, cache=True):
    cached = SearchResultCache.get(query)
    if cached is not None:
        print("Use cached")
        return cached
    
    q = urllib.parse.quote_plus(query)
    response = requests.get("https://www.discogs.com/de/search/ac?searchType=all&q={q}&type=a_m_r_13".format(q=q))
    if response.status_code != 200:
        raise Exception("Failed to request search data from discogs.")

    result = response.json()
    sid = SearchResultCache.add(query, result)
    return sid, result

def get_image_list(ref):
    response = requests.get("https://www.discogs.com/release/{0}".format(ref))
    if response.status_code != 200:
        raise Exception("Failed to request release page.")

    page = response.text
    start = page.find("data-images='") + len("data-images='")
    end = page.find("'", start+1)
    raw = page[start:end]
    image_list = json.loads(raw)
    
    return image_list


def load_release_info(reference, cache=True):
    """
    Returns a ReleaseInfo object filled with data from given
    discogs entry
    """

    # Try to load from cache
    if cache:
        release_info = ReleaseCache.get(reference)
        if release_info is not None:
            return release_info

    # Get data from discogs api
    _url = "https://api.discogs.com/releases/{0}".format(reference)
    response = requests.get(_url, headers={
        "User-Agent": "-"
    })
    print(response)
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

    released_date = data.get("released", None)
    released_year = None
    if released_date:
        released_year = released_date.split("-")[0]



    release_info = ReleaseInfo(
        artist = data.get("artists", [None])[0]["name"],
        title = data.get("title", None),
        genres = ';'.join(data.get("styles", data.get("genres", []))),
        released = released_year,
        rid = reference,
        is_external = True
    )

    release_info.save()

    image_list = get_image_list(reference)
    for image in image_list:
        ii = ImageInfo(
            full = image["full"],
            thumb = image["thumb"],
            iid = str(image["id"]),
            release = release_info
        )
        ii.save()

    for track in data.get("tracklist", []):
        if track.get("type_", None) == "track":
            _position = track.get("position", None)
            if _position is None:
                raise Exception("Missing position on tracks")

            side = _position[0].upper()
            position = int(_position[1:])

            ti = TrackInfo(
                duration = track.get("duration", None),
                side = side,
                position = position,
                title = track.get("title", None),
                release = release_info
            )

            ti.save()


    if cache:
        ReleaseCache.add(release_info, reference)

    return release_info

def store_cover(release, image):
    create_permanent_directories()
    fname = "{0}_{1}.jpeg".format(release.rid, image.iid)
    path = os.path.join(COVER_PATH, fname)
    with open(path, 'wb') as target:
        response = requests.get(image.full, stream=True)
        for block in response.iter_content(1024):
            if not block:
                break

            target.write(block)
    return fname