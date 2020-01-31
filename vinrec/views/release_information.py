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
import uuid

# Local imports
from vinrec.util.discogs import search
from vinrec.util.discogs import SearchResultCache
from vinrec.util.discogs import load_release_info
from vinrec.util.discogs import store_cover
from vinrec.models.release_information import ReleaseCache
from vinrec.models.release_information import TrackInfo
from vinrec.models.release_information import ImageInfo
from vinrec.models.release_information import ReleaseInfo
from vinrec.models.process import ProcessModel
from vinrec.models.process import ProcessSide

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
        releases = ReleaseInfo.select().where(ReleaseInfo.is_external == False).objects()
        return render_template("release_information/create.html", releases=releases)
    
    else:
        artist = request.form["artist"]
        title = request.form["title"]
        released = request.form["year"]
        genres = request.form["styles"]
        
        _genres = genres.split(",")
        genres = []
        for genre in _genres:
            _genre = genre.strip()
            if _genre != "":
                genres.append(_genre)
        print(genres)

        ri = ReleaseInfo(
            rid = str(uuid.uuid1()).replace("-", ""),
            is_external = False,

            artist = artist,
            title = title,
            genres = ';'.join(genres),
            released = int(released)
        )
        ri.save()

        track_index = 0
        while request.form.get("track_{0}_side".format(track_index), None) is not None:
            side = request.form["track_{0}_side".format(track_index)]
            track = int(request.form["track_{0}_track".format(track_index)])
            title = request.form["track_{0}_title".format(track_index)]
            track_index += 1

            ti = TrackInfo(
                duration=0,
                side = side,
                position = int(track),
                title  = title,
                release = ri
            )
            ti.save()

        return redirect(url_for('process.use_release', rid=ri.rid))

@app.route("/remove/<ref>")
@app.route("/remove/<ref>/<url>")
def remove(ref, url=None):
    print(ref, url)
    # Remove release from database
    ri = ReleaseCache.get(ref)
    for track in ri.get_tracks():
        track.delete_instance()
    for image in ri.get_images():
        image.delete_instance()
    
    for process in ProcessModel.select().where(ProcessModel.release==ri).objects():
        for side in ProcessSide.select().where(ProcessSide.process==process).objects():
            side.delete_instance()
        process.delete_instance()

    ri.delete_instance()
    if url is None:
        return redirect(url_for("index.index"))
    else:
        return redirect(url.replace("%2F", "/"))

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
        if os.path.isfile(path):
            os.remove(path)
        f = request.files.get("cover_file")
        f.save(path)
        ri.cover_image = fname
        ri.save()        
        return redirect(url_for("process.use_release", rid=ri.rid))

@app.route("/use_cover/<release>/<cover>")
def use_cover(release, cover):
    ri = ReleaseCache.get(release)
    cover = ImageInfo.get_or_none(ImageInfo.iid==cover, ImageInfo.release==ri)
    fname = store_cover(ri, cover)
    ri.cover_image = fname
    ri.save()
    return redirect(url_for("process.use_release", rid=ri.rid))