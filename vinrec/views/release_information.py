# Flask imports
from flask import Blueprint
from flask import render_template
from flask import redirect
from flask import url_for
from flask import request
from flask import abort

# Local imports
from vinrec.util.discogs import search
from vinrec.util.discogs import load_release_info
from vinrec.util.discogs import store_cover
from vinrec.util.release_information import ReleaseCache
from vinrec.util.release_information import TrackInfo
from vinrec.util.release_information import ImageInfo

# Blueprint
app = Blueprint("release_information", "vinrec.views.release_information")

# Routes
@app.route("/search_discogs", methods=["GET", "POST"])
def search_discogs():
    if request.method == "GET":
        return render_template("release_information/search_discogs.html")
    
    else:
        query = request.form.get("query", None)
        if query is None:
            abort(422)

        results = search(query)
        return render_template("release_information/discogs_results.html", results=results)

@app.route("/create", methods=["GET", "POST"])
def create():
    if request.method == "GET":
        return render_template("release_information/create.html")
    
    else:
        return redirect(url_for('release_information.create'))

@app.route("/check/<ref>")
def check_release(ref):
    release = load_release_info(ref)
    return render_template("release_information/check.html", release=release)

@app.route("/edit/<ref>", methods=["GET", "POST"])
def edit_release(ref):
    ri = ReleaseCache.get(ref)
    if request.method == "GET":
        return render_template("release_information/edit.html", release=ri)
    else:
        ri.artist = request.form.get("artist", ri.artist)
        ri.title = request.form.get("title", ri.title)
        ri.released = request.form.get("year", ri.released)

        genres = request.form.get("styles", None)
        if genres is not None:
            _genres = genres.split(",")
            genres = []
            for genre in _genres:
                _genre = genre.strip()
                if _genre != "":
                    genres.append(_genre)
            
            ri.genres = ';'.join(genres)
        
        ri.save()

        for track in TrackInfo.select().where(TrackInfo.release==ri):
            track.title = request.form.get("track_" + track.side + str(track.position), track.title)
            track.save()

        return redirect(url_for("process.use_release", rid=ref))

@app.route("/select_cover/<ref>", methods=["GET", "POST"])
def select_cover(ref):
    ri = ReleaseCache.get(ref)
    if request.method == "GET":
        return render_template("release_information/select_cover.html", release=ri)
    else:
        return "HI"

@app.route("/use_cover/<release>/<cover>")
def use_cover(release, cover):
    ri = ReleaseCache.get(release)
    cover = ImageInfo.get_or_none(ImageInfo.iid==cover and ImageInfo.release==ri)
    fname = store_cover(ri, cover)
    ri.cover_image = fname
    ri.save()
    return redirect(url_for("process.use_release", rid=ri.rid))