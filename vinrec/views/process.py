# Flask imports
from flask import Blueprint
from flask import render_template
from flask import redirect
from flask import url_for

# Local imports
from vinrec.models.release_information import ReleaseCache

from vinrec.models.process import ProcessModel
from vinrec.models.process import ProcessSide

# Blueprint
app = Blueprint("process", "vinrec.views.process")

# Routes
@app.route("/use_release/<rid>")
def use_release(rid):
    release = ReleaseCache.get(rid)
    if release is None:
        return redirect(url_for("index.index"))
    if release.cover_image is None:
        return redirect(url_for("release_information.select_cover", ref=rid))

    return ""