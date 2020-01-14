"""
Vinrec - vinrec.py

Copyright (C) 2019 Ole Lange
~~ LICENSE WILL FOLLOW ~~
"""

# Imports
## Flask imports
from flask import Flask

## Database
from vinrec.util.database import Database
db = Database.get()

### Create tables
from vinrec.util.release_information import ReleaseInfo
from vinrec.util.release_information import TrackInfo
from vinrec.util.release_information import ImageInfo
db.create_tables([
    ReleaseInfo,
    TrackInfo,
    ImageInfo
])

## Local imports
from vinrec.views.index import app as index_view_blueprint
from vinrec.views.upload import app as upload_view_blueprint
from vinrec.views.recorder import app as recorder_view_blueprint
from vinrec.views.download import app as download_view_blueprint
from vinrec.views.release_information import app as release_information_view_blueprint
from vinrec.views.process import app as process_view_blueprint

# Create folder structure
from vinrec.util.data_management import create_permanent_directories
create_permanent_directories()

# Creating Flask app
app = Flask(__name__)
app.secret_key = "the key must not be secret in this case"

## Blueprints
app.register_blueprint(index_view_blueprint)
app.register_blueprint(upload_view_blueprint, url_prefix="/upload")
app.register_blueprint(recorder_view_blueprint, url_prefix="/recorder")
app.register_blueprint(download_view_blueprint, url_prefix="/download")
app.register_blueprint(release_information_view_blueprint, url_prefix="/release_information")
app.register_blueprint(process_view_blueprint, url_prefix="/process")