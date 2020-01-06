# Global imports
import requests

# Local imports

# Objects containing metadata
class ReleaseInfo(object):

    def __init__(self, artist, title, genres, released, tracks, image_list, rid=None):
        self.rid = rid
        self.artist = artist   # Name of the artist/s, str
        self.title = title    # Title of this release, str
        self.genres = genres   # Genres/Styles, list of strings
        self.released = released # Release Year, int

        self.tracks = tracks
        
        self.image_list = image_list
        self.cover_image = None

class TrackInfo(object):

    def __init__(self, duration, side, position, title, extraartists):
        self.duration = duration
        self.side = side
        self.position = position
        self.title = title
        self.extraartists = extraartists


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
    def get(cid, load=True):
        instance = ReleaseCache.get_instance()
        return instance._get(cid, load=True)

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

    def _get(self, cid, load=True):
        result = self.cache.get(cid, None)
        if result is None and load:
            try:
                from vinrec.util.discogs import load_release_info
                result = load_release_info(cid, cache=True)
            except: # No discogs release
                pass
        
        return result
        