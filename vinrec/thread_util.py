from . import process_sides
import threading

class WorkerThread(threading.Thread):

    instance = None

    @staticmethod
    def get_instance():
        return WorkerThread.instance

    @staticmethod
    def get_busy():
        if WorkerThread.instance is None:
            return False
        else:
            status = WorkerThread.instance.status
            if status["STATE"] == "FINISHED":
                return False
        return True

    def __init__(self, audios, cover_file, discogs_ref, output_format):
        super(WorkerThread, self).__init__()
        
        if WorkerThread.instance == None:
            WorkerThread.instance = self

        self.audios = audios
        self.cover_file = cover_file
        self.discogs_ref = discogs_ref
        self.output_format = output_format

        self.status = {
            "STATE": "NOT STARTED",
            "AUDIOS": audios,
            "COVER_FILE": cover_file,
            "DISCOGS_REF": discogs_ref
        }
        self.output_path = None

    def run(self):
        self.status.update({
            "STATE": "STARTED"
        })
        self.output_path = process_sides(
            self.audios,
            self.cover_file,
            self.discogs_ref,
            output_format=self.output_format,
            status=self.status
        )
        self.status.update({
            "STATE": "FINISHED"
        })
        