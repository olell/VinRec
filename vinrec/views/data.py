# Flask imports
from flask import Blueprint
from flask import send_from_directory
from flask import abort

# Local imports
from vinrec.util.data_management import get_finished_records
from vinrec.util.data_management import get_unfinished_records
from vinrec.const.locations import COVER_PATH
from vinrec.models.release_information import ReleaseInfo

# Blueprint
app = Blueprint("data", "vinrec.views.data")

# Routes
@app.route("/")
def index():
    return "" # Todo: Something like a data overview

@app.route("/cover_image/<rid>/<nc>")
def cover_image(rid, nc):
    release = ReleaseInfo.get_or_none(ReleaseInfo.rid==rid)
    if release is None:
        abort(404)
    
    path = release.cover_image
    return send_from_directory(COVER_PATH, path)