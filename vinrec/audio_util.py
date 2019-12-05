"""
audio_util.py - part of VinRec an easy to use vinyl digitizing software
Copyright (C) 2019: Ole Lange

This module contains the function split_record, which loads an audio file from the given
path and splits it at silent moment in multiple AudioSegment objects and returns them.

"""

from pydub import AudioSegment
from pydub.playback import play

chunk_size = 500
silence_tresh = 500
min_song_length = 25 # min_song_length * chunk_size = minimumg length of songs in ms
pre_extend = 1 * silence_tresh

def split_record(path):
    song = AudioSegment.from_wav(path)

    # First, a list is created that specifies which chunk is quiet and which is loud.
    chunks = []
    for x in range(0, len(song), chunk_size):
        chunk = song[x: x + chunk_size]

        vols = list(map(lambda x: x.max, chunk))
        avg_vol = sum(vols) / len(vols)

        if avg_vol < silence_tresh:
            chunks.append(0)
        else:
            chunks.append(1)
    
    parts = []
    current = chunks[0]
    part = []
    idx = 0
    start = 0
    for chunk in chunks:
        if chunk == current:
            part.append(chunk)
        else:
            current = chunk
            if len(part) > min_song_length:
                parts.append((start, idx+1))
            start = idx
            part = [chunk]
        idx += 1

    songs = []
    for c in parts:
        start, end = c
        start *= chunk_size / 1000.
        end *= chunk_size / 1000.
        start -= pre_extend / 1000.
        end += pre_extend / 1000.
        songs.append((start, end))

    return songs

if __name__ == "__main__":
    print(split_record_new(sys.argv[1]))