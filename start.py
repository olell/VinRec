"""
Vinrec - vinrec.py

Copyright (C) 2019 Ole Lange
~~ LICENSE WILL FOLLOW ~~
"""

# Imports
## Flask imports
from flask import Flask

## Local imports
from vinrec.views.index import app as index_view_blueprint
from vinrec.views.upload import app as upload_view_blueprint

# Creating Flask app
app = Flask(__name__)

## Blueprints
app.register_blueprint(index_view_blueprint)
app.register_blueprint(upload_view_blueprint, url_prefix="/upload")