from flask import Flask
from flask import render_template
from flask import request
from flask import redirect, url_for
from flask import send_file

import os
import shutil
import requests
import urllib.parse
import urllib.request
import zipfile

from vinrec.thread_util import WorkerThread
from vinrec import discogs

app = Flask(__name__)

@app.route("/")
def index():
    try:
        files = os.listdir("./output_zips")
        names = []
        for filename in files:
            names.append(filename.replace(".zip", ""))
    except:
        names = []
    
    return render_template("index.html", av_records=names, busy=WorkerThread.get_busy())

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
    ri = discogs.ReleaseInfo.get(reference)
    return render_template("find_release.html", state="check", release=ri)

@app.route("/by_upload/<discogs_ref>")
@app.route("/by_upload", methods=["GET", "POST"])
def by_upload(discogs_ref=None):
    if request.method == "GET":
        release = discogs.ReleaseInfo(discogs_ref)
        return render_template("by_upload.html", state="upload", busy=WorkerThread.get_busy(), discogs_ref=discogs_ref, release=release)
    
    if request.method == "POST":

        letters = "ABCDEFGH"
        audios = {}
        for i in range(0, len(letters)):
            side = request.form.get("side_{0}".format(i), None)
            audio = request.files.get("audio_{0}".format(i), None)
            if side is None or audio is None:
                continue
            audios.update({
                side: audio
            })

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
        
        for side in audios:
            ending = audios[side].filename.split(".")[-1]
            path = ".vinrecinput/audio_side{0}.{1}".format(side, ending)
            audios[side].save(path)
            audios.update({
                side: path
            })

        cover_file = request.files.get("cover", None)
        if cover_file is None:
            cover_url = request.form.get("coverurl", None)
            if cover_url is not None:
                cover_ending = cover_url.split(".")[-1]
                cover_path = ".vinrecinput/cover.{0}".format(cover_ending)
                urllib.request.urlretrieve(cover_url, cover_path)
        else:
            cover_ending = cover_file.filename.split(".")[-1]
            cover_path = ".vinrecinput/cover.{0}".format(cover_ending)
            cover_file.save(cover_path)

        if WorkerThread.get_instance() is None:
            t = WorkerThread(audios, cover_path, discogs_ref)
            t.start()

        return redirect(url_for("status"))

@app.route("/status")
def status():
    inst = WorkerThread.get_instance()
    return render_template("status.html", thread=inst)

@app.route("/download/<file_name>")
def download(file_name):
    ls = os.listdir("./output_zips")
    if file_name + ".zip" in ls:
        return send_file(
            "./output_zips/{0}.zip".format(file_name),
            as_attachment=True,
            attachment_filename="{0}.zip".format(file_name))
    else:
        return redirect(url_for("status"))

if __name__ == "__main__":
    app.run()