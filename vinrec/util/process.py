# Global imports
import peewee

# Local imports
from vinrec.util.database import Database
from vinrec.util.release_information import ReleaseInfo


class ProcessModel(peewee.Model):

    release = peewee.ForeignKeyField(ReleaseInfo)

    def get_sides(self):
        return ProcessSide.select().where(ProcessSide.process==self).objects()

    class Meta:
        database = Database.get()


class ProcessSide(peewee.Model):

    side = peewee.CharField(max_length=1)
    record = peewee.TextField(null=True) # Path to record audio
    processed = peewee.BooleanField(default=False)

    process = peewee.ForeignKeyField(ProcessModel)

    class Meta:
        database = Database.get()
