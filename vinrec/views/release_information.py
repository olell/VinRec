# Flask imports
from flask import Blueprint
from flask import render_template
from flask import redirect
from flask import url_for
from flask import request
from flask import abort

# Global imports
import os
import copy

# Local imports
from vinrec.util.discogs import search
from vinrec.util.discogs import SearchResultCache
from vinrec.util.discogs import load_release_info
from vinrec.util.discogs import store_cover
from vinrec.models.release_information import ReleaseCache
from vinrec.models.release_information import TrackInfo
from vinrec.models.release_information import ImageInfo

from vinrec.util.data_management import create_permanent_directories
from vinrec.const.locations import COVER_PATH

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

        sid, results = search(query)
        return redirect(url_for('release_information.discogs_results', sid=sid))
    
@app.route("/discogs_results/<sid>")
def discogs_results(sid):
    sid, results = SearchResultCache.get_by_id(sid)
    results = copy.deepcopy(results)
    for result in results:
        rid = result["uri"].split("/")[-1]
        result.update({"rid": rid})

        ri = ReleaseCache.get(rid)
        if ri is not None:
            result.update({
                "local_stored": True,
                "release_info": ri
            })
        
    return render_template("release_information/discogs_results.html", results=results)

@app.route("/create", methods=["GET", "POST"])
def create():
    if request.method == "GET":
        return render_template("release_information/create.html")
    
    else:
        return redirect(url_for('release_information.create'))

@app.route("/remove/<ref>")
def remove(ref):
    # Remove release from database
    ri = ReleaseCache.get(ref)
    TrackInfo.delete().where(TrackInfo.release==ri)
    ImageInfo.delete().where(ImageInfo.release==ri)
    ri.delete_instance()
    return "Deleted instance"

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
        create_permanent_directories()
        fname = "{0}_{1}.jpeg".format(ri.rid, "uc")
        path = os.path.join(COVER_PATH, fname)
        f = request.files.get("cover_file")
        f.save(path)
        ri.cover_image = fname
        ri.save()        
        return redirect(url_for("process.use_release", rid=ri.rid))

@app.route("/use_cover/<release>/<cover>")
def use_cover(release, cover):
    ri = ReleaseCache.get(release)
    cover = ImageInfo.get_or_none(ImageInfo.iid==cover and ImageInfo.release==ri)
    fname = store_cover(ri, cover)
    ri.cover_image = fname
    ri.save()
    return redirect(url_for("process.use_release", rid=ri.rid))