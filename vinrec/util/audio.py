# Global imports
from pydub import AudioSegment
from pydub.playback import play
from copy import deepcopy
import os
import time

def split_record(path, expected_songs=None):

    chunk_size = 500
    silence_tresh = 500
    min_song_length = 25 # min_song_length * chunk_size = minimumg length of songs in ms
    min_silence_length = 10
    pre_extend = 1 * silence_tresh

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

    orig_chunks = deepcopy(chunks)
    
    while True:
        chunks = deepcopy(orig_chunks)
        parts = []
        current = chunks[0]
        part = []
        for chunk in chunks:
            if chunk == current:
                part.append(chunk)
            else:
                current = chunk
                parts.append(part)
                part = [chunk]

        for i in range(0, len(parts)):
            if i > 0 and i < len(parts)-1:
                part = parts[i]
                if part[0] == 0:
                    if len(part) < min_silence_length:
                        for j in range(0, len(part)):
                            part[j] = 1

        run_again = True
        while run_again:
            run_again = False
            for i in range(0, len(parts)-1):
                part = parts[i]
                next_part = parts[i+1]
                if part[0] == next_part[0]:
                    part += next_part
                    parts.pop(i+1)
                    run_again = True
                    break

        idx = 0
        start = 0
        times = []
        for part in parts:
            idx += len(part)
            if len(part) > min_song_length:
                times.append((start, idx+1))
            start = idx


        songs = []
        for c in times:
            start, end = c
            start *= chunk_size / 1000.
            end *= chunk_size / 1000.
            start -= pre_extend / 1000.
            end += pre_extend / 1000.
            songs.append((start, end))
        
        if len(songs) == expected_songs:
            break
        elif len(songs) > expected_songs:
            min_silence_length += 1
        elif len(songs) < expected_songs:
            min_silence_length -= 1
            if min_silence_length < 0:
                raise Exception("Cannot find correct amount of songs")

    return songs