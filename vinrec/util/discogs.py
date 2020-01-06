# Global imports
import requests
import json
import urllib.parse

# Local imports
from vinrec.util.release_information import ReleaseCache
from vinrec.util.release_information import ReleaseInfo
from vinrec.util.release_information import TrackInfo

def search(query):
    q = urllib.parse.quote_plus(query)
    response = requests.get("https://www.discogs.com/de/search/ac?searchType=all&q={q}&type=a_m_r_13".format(q=q))
    if response.status_code != 200:
        raise Exception("Failed to request search data from discogs.")

    result = response.json()
    return result

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

    image_list = get_image_list(reference)

    release_info = ReleaseInfo(
        artist = data.get("artists", [None])[0]["name"],
        title = data.get("title", None),
        genres = data.get("styles", data.get("genres", [])),
        released = released_year,
        tracks = track_infos,
        image_list = image_list,
        rid = reference
    )


    if cache:
        ReleaseCache.add(release_info, reference)

    return release_info
