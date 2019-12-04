from vinrec import process_side
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

    def __init__(self, audio_file, side, cover_file, discogs_ref):
        super(WorkerThread, self).__init__()
        
        if WorkerThread.instance == None:
            WorkerThread.instance = self

        self.audio_file = audio_file
        self.side = side
        self.cover_file = cover_file
        self.discogs_ref = discogs_ref

        self.status = {
            "STATE": "NOT STARTED",
            "AUDIO_FILE": audio_file,
            "SIDE": side,
            "COVER_FILE": cover_file,
            "DISCOGS_REF": discogs_ref
        }
        self.output_path = None

    def run(self):
        self.status.update({
            "STATE": "STARTED"
        })
        self.output_path = process_side(
            self.audio_file,
            self.side,
            self.cover_file,
            self.discogs_ref,
            status=self.status
        )
        self.status.update({
            "STATE": "FINISHED"
        })
        