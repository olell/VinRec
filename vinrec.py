"""
Vinrec - vinrec.py

Copyright (C) 2019 Ole Lange
~~ LICENSE WILL FOLLOW ~~
"""

# Imports
## Flask imports
from flask import Flask
from flask import render_template
from flask import redirect

## Local imports

## Global imports


# Creating Flask app
app = Flask(__name__)

# Routes
@app.route("/")
def index():
    return render_template("index.html")