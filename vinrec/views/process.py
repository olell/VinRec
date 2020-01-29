# Flask imports
from flask import Blueprint
from flask import render_template
from flask import redirect
from flask import url_for
from flask import abort
from flask import request

# Global imports
import time

# Local imports
from vinrec.models.release_information import ReleaseCache
from vinrec.models.release_information import ReleaseInfo
from vinrec.models.process import ProcessModel
from vinrec.models.process import ProcessSide
from vinrec.util.data_management import get_unfinished_records
from vinrec.util.process import guess_record

# Blueprint
app = Blueprint("process", "vinrec.views.process")

# Routes
@app.route("/use_release/<rid>")
def use_release(rid):
    release = ReleaseInfo.get_or_none(ReleaseInfo.rid==rid)
    
    if release is None:
        return redirect(url_for("index.index"))
    if release.cover_image is None:
        return redirect(url_for("release_information.select_cover", ref=rid))

    process = ProcessModel.get_or_none(ProcessModel.release==release)
    if process is None:
        process = ProcessModel(
            release=release
        )
        process.save()
    
    if len(process.get_assigned_sides()) == 0:
        return redirect(url_for("process.assign_sides", pid=process.id))

    return render_template("process/index.html", process=process, ts=time.time())

@app.route("/assign_sides/<pid>", methods=["GET", "POST"])
def assign_sides(pid):
    try:
        pid = int(pid)
    except ValueError:
        return abort(404)
    process = ProcessModel.get_or_none(ProcessModel.id==pid)
    if process is None:
        return abort(404)
    
    side_names = []
    for track in process.release.get_tracks():
        if track.side not in side_names:
            side_names.append(track.side)

    sides = {}
    for side_name in side_names:
        process_side = ProcessSide.get_or_none(ProcessSide.side==side_name, ProcessSide.process==process)
        if process_side is None:
            process_side = ProcessSide(
                side=side_name,
                process=process
            )
            process_side.save()
        sides.update({
            side_name: process_side
        })

    if request.method == "GET":
        records = get_unfinished_records()
        guessed = guess_record(process.release)

        return render_template("process/assign_sides.html", sides=sides, process=process, records=records, guessed=guessed)
    
    if request.method == "POST":
        for side in sides:
            side_record = request.form["side_" + side]
            sides[side].record = side_record
            sides[side].save()
        return redirect(url_for("process.use_release", rid=process.release.rid))