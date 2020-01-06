# Flask imports
from flask import Blueprint
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for

# Global imports
from werkzeug.utils import secure_filename
import os
import ffmpeg

# Local imports
from vinrec.util.data_management import create_permanent_directories
from vinrec.util.data_management import create_temporary_directories
from vinrec.util.data_management import clear_temporary_directories
from vinrec.const import locations

# Blueprint
app = Blueprint("upload", "vinrec.views.upload")

# Routes
@app.route("/record", methods=["GET", "POST"])
def record():
    if request.method == "GET":
        return render_template("upload/record.html")

    elif request.method == "POST":

        create_permanent_directories()
        create_temporary_directories()

        # Save and convert all files
        files = request.files.getlist("files")
        for f in files:
            # Save file to temporary directory
            filename = secure_filename(f.filename)
            path = os.path.join(locations.TMP, filename)
            f.save(path)

            # Convert file and write to permanent directory
            input_path = path
            new_filename = '.'.join(filename.split(".")[:-1]) + ".wav" # Change file extension to .wav
            output_path = os.path.join(locations.UNFINISHED_RECORDS, new_filename)
            (
                ffmpeg
                .input(input_path)
                .output(output_path)
                .run(overwrite_output=True)
            )

        clear_temporary_directories()

        return redirect(url_for("index.index"))
