# Global imports
import os
import shutil

# Local imports
from vinrec.const import locations
from vinrec.const import formats


# Directory creating and clearing
def create_permanent_directories():
    if not os.path.isdir(locations.DATA_DIR):
        os.makedirs(locations.DATA_DIR)

    for path in locations.PERMANENT_DIRS:
        if not os.path.isdir(path):
            os.makedirs(path)

def create_temporary_directories():
    for path in locations.TEMPORARY_DIRS:
        if not os.path.isdir(path):
            os.makedirs(path)

def clear_temporary_directories():
    for path in locations.TEMPORARY_DIRS:
        if os.path.isdir(path):
            shutil.rmtree(path)

# Lists from directories
def get_unfinished_records():
    dir_list = os.listdir(locations.UNFINISHED_RECORDS)
    files = []
    for filename in dir_list:
        if filename.endswith("." + formats.WORK_FORMAT):
            files.append(filename.split("." + formats.WORK_FORMAT)[0])
    files.sort()
    return files

def get_finished_records():
    dir_list = os.listdir(locations.UNFINISHED_RECORDS)
    files = []
    for filename in dir_list:
        if filename.endswith(".zip"):
            files.append(filename.split(".zip")[0])
    files.sort()
    return files
