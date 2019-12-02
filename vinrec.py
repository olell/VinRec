"""
vinrec.py - part of VinRec an easy to use vinyl digitizing software
Copyright (C) 2019: Ole Lange

This is the main file, just start it there will be helping output.
"""

from argparse import ArgumentParser
import discogs
import os
import magic
import autil
import shutil

# Read command line arguments
parser = ArgumentParser()
parser.add_argument("audio", help="audio file with x-side audio")
parser.add_argument("side", help="Side letter, e.g. A,B,C,D,E,F...")
parser.add_argument("cover", help="Cover image file")
parser.add_argument("discogs_ref", help="Discogs release code, see docs for more information")
parser.add_argument("--format", help="Output format", default="flac")
args = parser.parse_args()

data_folder = ".vinrec/"
try:
    os.mkdir(data_folder)
except FileExistsError:
    shutil.rmtree(data_folder)
    os.mkdir(data_folder)

discogs_reference = args.discogs_ref
output_format = args.format

# Split record
songs = autil.split_record(args.audio)
index = 0
for song in songs:
    index += 1
    song.export(".vinrec/{side}{index}.wav".format(side=args.side.upper(), index=index))

# Release Info
release_info = discogs.ReleaseInfo(discogs_reference)

# Finding folder structure:
audio_files = {}
cover = {}
for fname in os.listdir(data_folder):
    path = os.path.join(data_folder, fname)
    
    name = '.'.join(fname.split(".")[:-1])
    ext = fname.split(".")[-1]

    mime = magic.Magic(mime=True)
    mime_type = mime.from_file(path)

    mime_class, mime_type = mime_type.split("/")

    if mime_class.lower() == "audio":
        audio_files.update({
            name: {
                "path": path,
                "name": name,
                "ext": ext,
                "mime_class": mime_class,
                "mime_type": mime_type
            }
        })

# Filter matching audio files:
tracks = {}
av_names = []
for track in release_info.tracklist:
    av_names.append(track.position)
    tracks.update({
        track.position: track
    })

use_audios = {}
for f in audio_files:
    if f in av_names:
        use_audios.update({f:audio_files[f]})

# Create output folder
folder_name = "{artist} - {title}".format(
    artist = release_info.artists[0]["name"],
    title = release_info.title
)
os.mkdir(folder_name)

# 1. Convert all audio files to flac
# 2. Assing cover art to all files
# 3. Assing metadata to all files
# 4. Rename all files
# (5. Convert to output format)
for f in use_audios:
    file_name = "./{folder_name}/{name}.flac".format(folder_name=folder_name, **use_audios[f])
    # 1.
    os.system("ffmpeg -i \"{path}\" \"{file_name}\"".format(folder_name=folder_name, file_name=file_name, **use_audios[f]))
    # 2.
    i_p = args.cover
    os.system("metaflac --import-picture-from=\"{image_path}\" \"{file_name}\"".format(image_path=i_p, file_name=file_name))
    # 3.
    track = tracks[f]
    flags = [
        ("TITLE", track.title),
        ("ALBUM", release_info.title),
        ("TRACKNUMBER", f),
        ("RELEASED", release_info.released_year)
    ]
    for artist in release_info.artists:
        flags.append(
            ("ARTIST", artist["name"])
        )
    for style in release_info.styles:
        flags.append(
            ("GENRE", style)
        )
    for flag in flags:
        if flag[1] != None:
            os.system("metaflac --set-tag=\"{0}={1}\" \"{2}\"".format(flag[0], flag[1], file_name))
    
    # 4.
    out_name = "./{folder_name}/{pos} - {name}.flac".format(folder_name=folder_name, pos=f, name=track.title)
    os.rename(
        file_name,
        out_name
    )

    # 5.
    if output_format != "flac":
        os.system("ffmpeg -i \"{0}\" \"{1}\"".format(
            out_name,
            out_name[:-4] + output_format
        ))
        os.remove(out_name)

shutil.rmtree(data_folder)