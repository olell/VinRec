# Flask imports
from flask import Blueprint
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import jsonify

# Global imports
from werkzeug.utils import secure_filename
import os
import subprocess
import ffmpeg
import time

# Local imports
from vinrec.util.data_management import create_permanent_directories
from vinrec.const import locations
from vinrec.const import formats
from vinrec.util.recorder import Recorder

# Blueprint
app = Blueprint("recorder", "vinrec.views.recorder")

# Routes
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        instance = Recorder.get_instance()
        status = "not_recording"
        if instance is not None:
            if instance.running is False and instance.process is not None:
                Recorder.clear_instance()
            else:
                status = "recording"

        return render_template("recorder/index.html", status=status, instance=instance)

    elif request.method == "POST":

        action = request.form.get("action", None)
        if action == "start_record":
            instance = Recorder.get_instance()
            if instance is None:
                name = request.form.get("name", None)
                if len(name.strip()) == 0: name = None
                Recorder(name=name).start()

        if action == "stop_record":
            instance = Recorder.get_instance()
            if instance is not None:
                instance.stop()
                while instance.running:
                    time.sleep(0.1)

        return redirect(url_for("recorder.index"))

@app.route("/status")
def status():
    instance = Recorder.get_instance()
    if instance is None:
        return jsonify({
            "error": "Recorder isn't running"
        })

    status = instance.get_status()
    return jsonify(status)


@app.route("/delete/<name>")
def delete(name):
    name = secure_filename(name)
    filename = "{0}.{1}".format(name, formats.WORK_FORMAT)
    if filename in os.listdir(locations.UNFINISHED_RECORDS):
        os.remove(os.path.join(locations.UNFINISHED_RECORDS, filename))
    return redirect(url_for("index.index"))
