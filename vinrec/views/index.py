# Flask imports
from flask import Blueprint
from flask import render_template
from flask import session
from flask import redirect
from flask import url_for

# Local imports
from vinrec.util.data_management import get_finished_records
from vinrec.util.data_management import get_unfinished_records

# Blueprint
app = Blueprint("index", "vinrec.views.index")

# Routes
@app.route("/")
def index():

    finished_records = sorted(get_finished_records())
    unfinished_records = sorted(get_unfinished_records())

    return render_template("index.jinja", finished_records=finished_records, unfinished_records=unfinished_records)

@app.route("/theme/<value>")
def theme(value):
    if value not in ("dark", "bright"):
        raise Exception("TODO: Error handling: Unknown theme")
    else:
        session["theme"] = value
        return redirect(url_for('index.index'))
