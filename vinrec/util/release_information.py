# Global imports
import requests

# Local imports

# Objects containing metadata
class ReleaseInfo(object):

    def __init__(self, artist, title, genres, released, tracks):
        self.artist = artist   # Name of the artist/s, str
        self.title = title    # Title of this release, str
        self.genres = genres   # Genres/Styles, list of strings
        self.released = released # Release Year, int

        self.tracks = tracks

class TrackInfo(object):

    def __init__(self, duration, side, position, title, extraartists):
        duration = duration
        side = side
        position = position
        title = title
        extraartists = extraartists


# Cache release objects
class ReleaseCache(object):

    instance = None

    @staticmethod
    def get_instance():
        if ReleaseCache.instance is None:
            instance = ReleaseCache()
            ReleaseCache.instance = instance

        return ReleaseCache.instance

    @staticmethod
    def get(cid):
        instance = ReleaseCache.get_instance()
        return instance._get(cid)

    @staticmethod
    def add(object, cid=None):
        instance = ReleaseCache.get_instance()
        return instance._add(object, cid)

    def __init__(self):
        self.cache = {}
        self._id = 0

    def _add(self, object, _id=None):
        if _id is None:
            self._id += 1
            _id = self._id

        self.cache.update({
            _id: object
        })

        return _id

    def _get(self, cid):
        return self.cache.get(cid, None)


def load_from_discogs(reference, cache=True):

    # Try to load from cache
    if cache:
        release_info = ReleaseCache.get(reference)
        if release_info is not None:
            return release_info

    # Get data from discogs api
    _url = "https://api.discogs.com/releases/{0}".format(reference)
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


    track_infos = []
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
                extraartists = track.get("extraartists", None)
            )
            track_infos.append(ti)

    released_date = data.get("released", None)
    released_year = None
    if released_date:
        released_year = released_date.split("-")[0]
    release_info = ReleaseInfo(
        artist = data.get("artists", [None])[0],
        title = data.get("title", None),
        genres = data.get("styles", data.get("genres", [])),
        released = released_year,
        tracks = track_infos
    )

    if cache:
        ReleaseCache.add(release_info, reference)

    return release_info
