# Flask imports
from flask import Blueprint
from flask import redirect
from flask import url_for
from flask import abort
from flask import send_file

# Local imports
from vinrec.util.data_management import get_unfinished_records
from vinrec.const import locations
from vinrec.const import formats

# Global imports
import os

# Blueprint
app = Blueprint("download", "vinrec.views.download")

# Routes
@app.route("/unfinished/<name>")
def unfinished_records(name):

    unfinished_records = get_unfinished_records()
    if not name in unfinished_records:
        print(".")
        abort(404)

    filename = name + "." + formats.WORK_FORMAT
    path = os.path.join(locations.UNFINISHED_RECORDS, filename)
    print(path)
    if not os.path.exists(path):
        print("..")
        abort(404)

    return send_file(path)
