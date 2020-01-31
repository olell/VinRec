# Flask imports
from flask import Blueprint
from flask import send_from_directory
from flask import abort
from flask import render_template
from flask import url_for

# Local imports
from vinrec.util.data_management import get_finished_records
from vinrec.util.data_management import get_unfinished_records
from vinrec.const.locations import COVER_PATH
from vinrec.models.release_information import ReleaseInfo
from vinrec.models.process import ProcessModel

# Blueprint
app = Blueprint("data", "vinrec.views.data")

# Routes
@app.route("/")
def index():

    finished_records = sorted(get_finished_records())
    unfinished_records = sorted(get_unfinished_records())

    external = []
    internal = []
    try:
        releases = ReleaseInfo.select().objects()

        for rel in releases:
            if rel.is_external:
                external.append(rel)
            else:
                internal.append(rel)
    except:
        pass

    processes = []
    try:
        processes = ProcessModel.select().objects()
    except:
        pass

    return render_template("data/index.html", finished_records=finished_records, unfinished_records=unfinished_records, external=external, internal=internal, processes=processes)

@app.route("/cover_image/<rid>/<nc>")
def cover_image(rid, nc):
    release = ReleaseInfo.get_or_none(ReleaseInfo.rid==rid)
    if release is None:
        abort(404)
    
    path = release.cover_image
    return send_from_directory(COVER_PATH, path)