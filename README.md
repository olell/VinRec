# VinRec

VinRec is an easy to use vinyl/tape digitizing software. \
It will help you to make digital music from your analog sound carrier within two simple steps!

## Features
* Record input from your soundcard or upload custom audio files
* Automatic splitting of recorded audio into single tracks
* Automatic assigment of metadata from Discogs database to the tracks
* Cover Image assigment

## Setup

**1.** Run this to setup VinRec:
```sh
# Clone git repo and go into the git folder
git clone https://github.com/olell/VinRec
cd VinRec

# Install sytem requirements
sudo apt install python3 python3-pip ffmpeg alsa-utils

# Install python requirements
sudo pip3 install -r requirements.txt

# Copy example configuration
cp example_config.ini config.ini
```

**2.** Edit the config file `config.ini`\
**3.** Run Vinrec:
```sh
env FLASK_APP=start.py VINREC_CFG=config.ini flask run --host=0.0.0.0 --port=8080
```
Now you can reach vinrec at `http://localhost:8080` or `http://your_device:8080`

## How to use
### First step
First you need to record or upload your audiofiles. If you want to record your audio with vinrec you first need to configure your soundcard in `config.ini`. Then you can select `create new audio files by recording them` or `upload existing audio files` on the startpage. The rest should be intuitive enough.

### Second step
In the second step you must find your record in the Discogs database or create your own record. **ToDo!**