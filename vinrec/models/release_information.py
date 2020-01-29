# Global imports
import requests
import peewee

# Local imports
from vinrec.util.database import Database

# Objects containing metadata
class ReleaseInfo(peewee.Model):

    rid = peewee.TextField()
    is_external = peewee.BooleanField(default=False)
    is_edited = peewee.BooleanField(default=False)

    artist = peewee.TextField()
    title = peewee.TextField()
    genres = peewee.TextField()
    released = peewee.IntegerField()

    cover_image = peewee.TextField(null=True) # filename of cover image

    def get_tracks(self):
        return TrackInfo.select().where(TrackInfo.release==self).objects()

    def get_images(self):
        return ImageInfo.select().where(ImageInfo.release==self).objects()

    def get_genres(self):
        return self.genres.split(";")

    class Meta:
        database = Database.get()

class TrackInfo(peewee.Model):

    duration = peewee.IntegerField()
    side = peewee.CharField(max_length=1)
    position = peewee.IntegerField()
    title = peewee.TextField()

    release = peewee.ForeignKeyField(ReleaseInfo)

    class Meta:
        database = Database.get()

class ImageInfo(peewee.Model):

    thumb = peewee.TextField()
    full = peewee.TextField()
    iid = peewee.CharField()

    release = peewee.ForeignKeyField(ReleaseInfo)

    class Meta:
        database = Database.get()

# Cache release objects
class ReleaseCache(object):

    @staticmethod
    def get(rid):
        return ReleaseInfo.get_or_none(ReleaseInfo.rid==rid)

    @staticmethod
    def add(object, cid=None):
        pass