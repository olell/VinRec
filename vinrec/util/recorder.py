import wavio
import numpy as np

from threading import Thread
import subprocess
import os
import time

from vinrec.const.locations import UNFINISHED_RECORDS
from vinrec.util.data_management import create_permanent_directories
from vinrec.util.config import Config

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

    def __init__(self, name):

        if Recorder.instance != None:
            raise Exception("There is already a recorder object")

        Recorder.instance = self

        super(Recorder, self).__init__()

        self.name = name
        self.file_name = "{0}/{1}.wav".format(UNFINISHED_RECORDS, self.name)

        create_permanent_directories()

        if os.path.exists(self.file_name):
            raise FileExistsError()

        conf = Config.get()

        self.sample_format = conf["RECORDING"]["Format"]
        self.sample_rate = conf["RECORDING"]["SampleRate"]
        self.bitdepth = int(conf["RECORDING"]["BitDepth"])
        self.channels = conf["RECORDING"]["Channels"]
        self.device = conf["RECORDING"]["Device"]

        self.running = False
        self.process = None

    def run(self):
        self.running = True
        self.process = subprocess.Popen([
            "arecord",
            "-f", self.sample_format,
            "-r", str(self.sample_rate),
            "-c", str(self.channels),
            "-D", self.device,
            self.file_name
        ])
        stdout, stderr = self.process.communicate()
        self.running = False

    def stop(self):
        if self.running and self.process is not None:
            self.process.send_signal(2)  # SIGINT -> CTRL + C

    def get_status(self, seconds=20, pps=100):
        status = {}
        if os.path.exists(self.file_name):
            
            wav = wavio.read(self.file_name)
            rate = wav.rate
            data = wav.data

            status.update({
                "record_length": (len(data) / rate) * 1000,
                "name": self.name,
                "filename": self.file_name
            })

            waveform_points = []
            waveform_times = []
            
            points = seconds * pps

            samples = int(seconds * rate)
            data0 = data[:, 0][-samples:]
            parts = np.array_split(data0, points)
            waveform_points = np.average(parts, 1)
            waveform_points = list(waveform_points / ((2**self.bitdepth)/2))
            waveform_times = list(np.arange(seconds, 0, -(seconds/points)))
            
            status.update({
                "waveform": waveform_points,
                "times": waveform_times
            })

        else:
            status.update({"error": "file doesn't exist (yet)"})

        return status