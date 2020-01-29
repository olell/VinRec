# Global imports
import string

# Local imports
from vinrec.util.data_management import get_unfinished_records

def _get_words(text):
    words = ''.join([x for x in text if x in string.ascii_letters + '\'- ']).split(" ")
    ret = []
    for word in words:
        if word != '':
            ret.append(word)
    return ret
    

def _matching_words(text_a, text_b):
    b_words = _get_words(text_b)
    points = 0
    for word in b_words:
        if word in text_a:
            points += 1

    return points

def _guess_side(record):
    side_words = {
        "a": ["this_side", "this-side"],
        "b": ["that_side", "that-side"],
        "c": [],
        "d": [],
        "e": [],
        "f": [],
        "g": [],
        "h": [],
        "i": [],
        "j": []
    }
    common_words = [
        "{0}-side",
        "{0}_side"
        "{0} side",
        "side {0}",
        "side-{0}",
        "side_{0}",
        "{0}side",
        "side{0}"
    ]
    for word in common_words:
        for side in side_words:
            side_words[side].append(word.format(side))

    sides = {}
    for side in side_words:
        side_score = sides.get(side, 0)
        for word in side_words[side]:
            if word in record:
                side_score += 1
        sides.update({side: side_score})
    max_side = None
    max_score = 0
    for side in sides:
        if sides[side] > max_score:
            max_score = sides[side]
            max_side = side
    return max_side


def guess_record(release):
    records = get_unfinished_records()
    points = {}
    for record in records:
        rp = 0
        rp += _matching_words(record.lower(), release.artist.lower()) * 1
        rp += _matching_words(record.lower(), release.title.lower())  * 1
        if str(release.released) in record.lower():
            rp += 1

        side = _guess_side(record)
        cur = points.get(side, [])
        cur.append((record, rp))
        points.update({side: cur})

    sides = {}
    for side in points:
        max_record = None
        max_points = -1
        for r, p in points[side]:
            if p > max_points:
                max_points = p
                max_record = r
        sides.update({side: max_record})
    return sides