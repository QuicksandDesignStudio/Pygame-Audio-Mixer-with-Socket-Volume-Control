# LBE Pygame Based Mixer. Volume control with UDP socket messages on Raspian

## Steps

- sudo apt-get update
- sudo apt-get upgrade
- sudo apt-get install alsa-utils
- sudo apt-get install python3-pygame
- sudo apt-get install libsdl2-mixer-2.0-0
- sudo apt install python3-venv
- python3 -m venv ven
- source venv/bin/activate
- pip install -r requirements.txt
- setup the path to your files in start.py with RELATIVE_FOLDER_PATH
- setup your audio file extension in start.py with FILE_TYPE_EXT
- To use mp3 or ogg
  - sudo apt-get install libmpg123-dev
  - sudo apt-get install libvorbis-dev

## Socket based audio handling and seeking to a time in the audio file

- This handles a track volume using socket messages
- The load_sounds method of the AudioPlayer class uses the method reshape_sound_buffer_by_start_time in utils.py to seek to a specific time in the audio file before playing. There is no direct way to do this in pygame and play several sounds simultaneously so buffers are manually altered to do this.
