import os
import asyncio

from pygame_player import AudioPlayer
from pygame_player import SoundController
from socket_listener import SocketListener

RELATIVE_FOLDER_PATH = "longsamples"  # path to samples
FILE_TYPE_EXT = "wav"  # type of files


# stage the audio controllers and socket listeners
def main():
    audio_player = AudioPlayer(
        os.path.join(os.getcwd(), RELATIVE_FOLDER_PATH), FILE_TYPE_EXT
    )
    sounds = audio_player.start()
    sound_controller = SoundController(sounds)

    try:
        loop = asyncio.get_event_loop()
        socket_listener = SocketListener(sound_controller, loop)
        loop.run_until_complete(socket_listener.start())
    except KeyboardInterrupt:
        pass
    finally:
        print("Shutting Down")
        audio_player.stop()
        loop.close()


if __name__ == "__main__":
    main()
