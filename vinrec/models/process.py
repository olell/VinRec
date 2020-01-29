# Global imports
import peewee

# Local imports
from vinrec.util.database import Database
from vinrec.models.release_information import ReleaseInfo


class ProcessModel(peewee.Model):

    release = peewee.ForeignKeyField(ReleaseInfo)
    processed = peewee.BooleanField(default=False)
    output = peewee.TextField(null=True)

    def get_sides(self):
        return ProcessSide.select().where(ProcessSide.process_id==self.id).objects()

    def get_assigned_sides(self):
        return ProcessSide.select().where(ProcessSide.process==self.id, ProcessSide.record != None).objects()

    class Meta:
        database = Database.get()


class ProcessSide(peewee.Model):

    side = peewee.CharField(max_length=1)
    record = peewee.TextField(null=True) # Path to record audio
    processed = peewee.BooleanField(default=False)

    process = peewee.ForeignKeyField(ProcessModel)

    class Meta:
        database = Database.get()
