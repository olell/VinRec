from flask import Flask
from flask import render_template
from flask import request
from flask import redirect, url_for

import os
import shutil
import requests
import urllib.parse
import discogs

from thread_util import WorkerThread

app = Flask(__name__)

@app.route("/")
def index():
    return redirect("find_release")

@app.route("/find_release", methods=["GET", "POST"])
def find_release():
    if request.method == "GET":
        return render_template("find_release.html", state="search")
    else:
        query = request.form["query"]
        
        q = urllib.parse.quote_plus(query)
        response = requests.get("https://www.discogs.com/de/search/ac?searchType=all&q={q}&type=a_m_r_13".format(q=q))

        return render_template("find_release.html", state="results", results=response.json())

@app.route("/check_release/<reference>")
def check_release(reference):
    
    ri = discogs.ReleaseInfo(reference)
    
    return render_template("find_release.html", state="check", release=ri)

@app.route("/by_upload/<discogs_ref>")
@app.route("/by_upload", methods=["GET", "POST"])
def by_upload(discogs_ref=None):
    if request.method == "GET":
        return render_template("by_upload.html", state="upload", busy=WorkerThread.get_busy(), discogs_ref=discogs_ref)
    
    if request.method == "POST":
        audio_file = request.files["audio"]
        cover_file = request.files["cover"]

        side = request.form["side"]
        discogs_ref = request.form["discogs_reference"]

        if WorkerThread.get_instance() is not None:
            if WorkerThread.get_instance().status["STATE"] == "FINISHED":
                WorkerThread.instance = None
            else:
                return redirect("index")

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