"""
audio_util.py - part of VinRec an easy to use vinyl digitizing software
Copyright (C) 2019: Ole Lange

This module contains the function split_record, which loads an audio file from the given
path and splits it at silent moment in multiple AudioSegment objects and returns them.

TODO: This module is very hacky at the moment, it works but may have bad influences on quality. 
So maybe I should rewrite this, but im to lazy at the moment...
TODO: The params down there are trash too, make this thingy better!

"""

from pydub import AudioSegment
from pydub.playback import play
import sys

chunk_size = 500
silence_tresh = 500
silence_min = 2 # silence_min * chunk_size = minimum length of silence in ms
min_song_length = 25 # min_song_length * chunk_size = minimumg length of songs in ms

def split_record(path):
    song = AudioSegment.from_wav(path)

    songs = []
    cur_song = []
    for x in range(0, len(song), chunk_size):
        chunk = song[x: x + chunk_size]
        
        vols = list(map(lambda x: x.max, chunk))
        avg_vol = sum(vols) / len(vols)

        if avg_vol < silence_tresh:  # silence
            cur_song.append(("SILENCE", chunk))
            
            if len(cur_song) > silence_min:
                cut = True
                for i in range(1, silence_min+1):
                    if cur_song[-i][0] != "SILENCE":
                        cut = False
                

                if cut:
                    songs.append([])
                    cur_song = cur_song[:-silence_min]
                    is_first_silence = True
                    for e in cur_song:
                        if e[0] == "SILENCE" and is_first_silence:
                            pass
                        elif e[0] == "SOUND":
                            is_first_silence = False
                            songs[-1].append(e[1])
                    cur_song = []




        else: # sound
            cur_song.append(("SOUND", chunk))

    output_songs = []
    for e in songs:
        if len(e) > min_song_length:
            new_song = AudioSegment.empty()
            for x in e:
                new_song += x
            output_songs.append(new_song)
    return output_songs