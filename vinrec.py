"""
vinrec.py - part of VinRec an easy to use vinyl digitizing software
Copyright (C) 2019: Ole Lange

This is the main file, just start it there will be helping output.
"""

import discogs
import os
import magic
import audio_util
import shutil


def process_sides(audios, cover, discogs_reference, output_format="flac", status={}):

    # Prerequisites
    data_folder = ".vinrec/"
    try:
        os.mkdir(data_folder)
    except FileExistsError:
        shutil.rmtree(data_folder)
        os.mkdir(data_folder)

    # Release Info
    release_info = discogs.ReleaseInfo(discogs_reference)
    status.update({
        "release_info": release_info
    })

    # Create output folder
    folder_name = "{artist} - {title}".format(
        artist = release_info.artists[0]["name"],
        title = release_info.title
    )
    try:
        os.mkdir(folder_name)
    except FileExistsError:
        pass

    # Splitting sides
    for side in audios:
        audio_path = audios[side]

        # Split side
        songs = audio_util.split_record(audio_path)
        index = 0
        for song in songs:
            index += 1
            filename = ".vinrec/{side}{index}.wav".format(side=side.upper(), index=index)
            start, end = song
            os.system("ffmpeg -i {0} -ss {1} -to {2} -c copy {3}".format(audio_path, start, end, filename))

    # Assign files
    audio_files = {}
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
    

    # Metadata & Conversion
    for f in use_audios:
        file_name = "./{folder_name}/{name}.flac".format(folder_name=folder_name, **use_audios[f])

        os.system("ffmpeg -i \"{cover}\" \"./{folder_name}/cover.jpg\"".format(cover=cover, folder_name=folder_name))
        cover = "./{folder_name}/cover.jpg".format(folder_name=folder_name)
        os.system("ffmpeg -i \"{path}\" \"{file_name}\"".format(folder_name=folder_name, file_name=file_name, **use_audios[f]))
        os.system("metaflac --import-picture-from=\"{image_path}\" \"{file_name}\"".format(image_path=cover, file_name=file_name))

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

        out_name = "./{folder_name}/{pos} - {name}.flac".format(folder_name=folder_name, pos=f, name=track.title)
        os.rename(
            file_name,
            out_name
        )

        if output_format != "flac":
            os.system("ffmpeg -i \"{0}\" \"{1}\"".format(
                out_name,
                out_name[:-4] + output_format
            ))
            os.remove(out_name)

    # STEP 6: Follow Up
    shutil.rmtree(data_folder)

    status.update({
        "FOLDER": "./{0}".format(folder_name)
    })