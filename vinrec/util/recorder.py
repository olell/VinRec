from pydub import AudioSegment

from threading import Thread
import subprocess
import os
import time

from vinrec.const.locations import UNFINISHED_RECORDS
from vinrec.util.data_management import create_permanent_directories

def split_to_chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

class Recorder(Thread):

    instance = None

    @staticmethod
    def get_instance():
        return Recorder.instance

    @staticmethod
    def clear_instance():
        Recorder.instance = None

    def __init__(self, name, stereo=True, sample_rate=192000, sample_format="S32_LE"):

        if Recorder.instance != None:
            raise Exception("There is already a recorder object")

        Recorder.instance = self

        super(Recorder, self).__init__()

        self.name = name
        self.file_name = "{0}/{1}.wav".format(UNFINISHED_RECORDS, self.name)

        create_permanent_directories()

        if os.path.exists(self.file_name):
            raise FileExistsError()

        self.sample_format = sample_format
        self.sample_rate = sample_rate
        self.stereo = True

        self.running = False
        self.process = None

    def run(self):
        self.running = True
        self.process = subprocess.Popen([
            "arecord",
            "-f", self.sample_format,
            "-r", str(self.sample_rate),
            "-c", "2" if self.stereo else "1",
            self.file_name
        ])
        stdout, stderr = self.process.communicate()
        self.running = False

    def stop(self):
        if self.running and self.process is not None:
            self.process.send_signal(2)  # SIGINT -> CTRL + C

    def get_status(self, max_waveform_points=20000, chunklen=100):
        status = {}
        if os.path.exists(self.file_name):
            segment = AudioSegment.from_wav(self.file_name)
            status.update({
                "record_length": len(segment),
                "name": self.name,
                "filename": self.file_name
            })

            waveform_points = []
            if len(segment) >= max_waveform_points:
                subseg = segment[-max_waveform_points:]
                for ms in subseg:
                    waveform_points.append(ms.max)
            else:
                for ms in segment:
                    waveform_points.append(ms.max)
                while len(waveform_points) < max_waveform_points:
                    waveform_points.append(0)

            new_points = []
            chunks = split_to_chunks(waveform_points, chunklen)
            for chunk in chunks:
                new_points.append(sum(chunk) / len(chunk))

            waveform_times = []
            for i in range(0, len(new_points)):
                t = (max_waveform_points) - (i * chunklen)
                waveform_times.append(t)

            mx = max(waveform_points)
            status.update({
                "waveform": list(map(lambda x: x / mx, new_points)),
                "times": waveform_times
            })

        else:
            status.update({"error": "file doesn't exist (yet)"})

        return status