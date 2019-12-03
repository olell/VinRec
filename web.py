from flask import Flask
from flask import render_template
from flask import request
from flask import redirect, url_for

import os
import shutil
import threading

from vinrec import process_side

app = Flask(__name__)

class WorkerThread(threading.Thread):

    instance = None

    @staticmethod
    def get_instance():
        return WorkerThread.instance

    @staticmethod
    def get_busy():
        if WorkerThread.instance is None:
            return False
        else:
            status = WorkerThread.instance.status
            if status["STATE"] == "FINISHED":
                return False
        return True

    def __init__(self, audio_file, side, cover_file, discogs_ref):
        super(WorkerThread, self).__init__()
        
        if WorkerThread.instance == None:
            WorkerThread.instance = self

        self.audio_file = audio_file
        self.side = side
        self.cover_file = cover_file
        self.discogs_ref = discogs_ref

        self.status = {
            "STATE": "NOT STARTED",
            "AUDIO_FILE": audio_file,
            "SIDE": side,
            "COVER_FILE": cover_file,
            "DISCOGS_REF": discogs_ref
        }
        self.output_path = None

    def run(self):
        self.status.update({
            "STATE": "STARTED"
        })
        print(self.status)
        self.output_path = process_side(
            self.audio_file,
            self.side,
            self.cover_file,
            self.discogs_ref,
            status=self.status
        )
        self.status.update({
            "STATE": "FINISHED"
        })
        



@app.route("/")
def index():
    return redirect(url_for("by_upload"))
    return render_template("index.html", busy=WorkerThread.get_busy())

@app.route("/by_upload", methods=["GET", "POST"])
def by_upload():
    if request.method == "GET":
        return render_template("by_upload.html", state="upload", busy=WorkerThread.get_busy())
    
    if request.method == "POST":
        audio_file = request.files["audio"]
        cover_file = request.files["cover"]

        side = request.form["side"]
        discogs_ref = request.form["discogs_reference"]

        try:
            os.mkdir(".vinrecinput")
        except FileExistsError:
            shutil.rmtree(".vinrecinput")
            os.mkdir(".vinrecinput")
        
        audio_ending = audio_file.filename.split(".")[-1]
        cover_ending = cover_file.filename.split(".")[-1]

        audio_path = ".vinrecinput/audio_side{0}.{1}".format(side, audio_ending)
        cover_path = ".vinrecinput/cover.{0}".format(cover_ending)

        audio_file.save(audio_path)
        cover_file.save(cover_path)

        info = {
            "side_{0}".format(side): audio_path,
            "cover": cover_path,
            "discogs_ref": discogs_ref
        }

        if WorkerThread.get_instance() is None:
            t = WorkerThread(audio_path, side, cover_path, discogs_ref)
            t.start()

        return redirect(url_for("status"))

@app.route("/status")
def status():
    inst = WorkerThread.get_instance()
    return render_template("status.html", thread=inst)


if __name__ == "__main__":
    app.run()