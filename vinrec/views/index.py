# Flask imports
from flask import Blueprint
from flask import render_template

# Local imports
from vinrec.util.data_management import get_finished_records
from vinrec.util.data_management import get_unfinished_records

# Blueprint
app = Blueprint("index", "vinrec.views.index")

# Routes
@app.route("/")
def index():

    finished_records = get_finished_records()
    unfinished_records = get_unfinished_records()

    return render_template("index.html", finished_records=finished_records, unfinished_records=unfinished_records)