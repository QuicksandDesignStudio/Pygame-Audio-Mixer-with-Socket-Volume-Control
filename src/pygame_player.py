import asyncio
import glob
import pygame


# Control Audio Spotlighting with Volume Controls
class SoundController:
    def __init__(self, sounds):
        self.sounds = sounds  # The list of pygame sounds in the mixer
        self.states = [True for _ in sounds]  # A state list to track sound states
        self.high_volume = 1.0  # Max volume for a sound
        self.low_volume = 0.1  # Min volume for a sound
        self.fade_time_in_seconds = 1  # Time taken to fade in and out
        self.fade_time_intervals = 0.1  # fade intervals. Total steps to fade = fade_time_in_seconds / fade_time_intervals

    # removes all spotlights and sets the volumes of all clips to max
    async def remove_audio_spotlight(self):
        print(f"Current State : {self.states}")

        # steps, delta per step and current volume tracker
        steps = self.fade_time_in_seconds / self.fade_time_intervals
        delta = (self.high_volume - self.low_volume) / steps
        current_vol = self.low_volume

        # fade in by step
        while current_vol < self.high_volume:
            for i in range(len(self.sounds)):
                if not self.states[
                    i
                ]:  # only fade in those sounds which are not already high
                    self.sounds[i].set_volume(current_vol + delta)
            current_vol = current_vol + delta
            await asyncio.sleep(self.fade_time_intervals)  # sleep for the fade interval

        # set the state list
        self.states = [True for _ in self.states]

    # fades out every sound except the one represented by index in the sounds array
    # note that two sounds cannot be high at the same time
    # TODO : See if this behaviour needs to change
    async def fade_audio_spotlight(self, index):
        print(f"Current State : {self.states}")
        print(f"Spotlighting clip : {index}")

        # steps, delta per step and current volume tracker
        steps = self.fade_time_in_seconds / self.fade_time_intervals
        delta = (self.high_volume - self.low_volume) / steps
        current_vol = self.high_volume

        # fade in by step
        while current_vol > self.low_volume:
            for i in range(len(self.sounds)):
                if i != index:  # all the sounds other than index
                    if self.states[i]:  # all the sounds that are not already low
                        self.sounds[i].set_volume(current_vol - delta)
                else:  # index sounds
                    if not self.states[i]:  # if index is not already high
                        self.sounds[i].set_volume(
                            self.high_volume - current_vol - delta
                        )
            current_vol = current_vol - delta
            await asyncio.sleep(0.1)  # sleep for the fade interval

        # set the state list
        self.states = [False for _ in self.states]
        self.states[index] = True


# Control Audio Playback with Pygame Mixer
class AudioPlayer:
    def __init__(self, path, file_type, max_channels=6):
        self.sounds = []  # list to hold pygame sounds
        self.path = path  # the path to the sound clips
        self.file_type = file_type  # the type of files (wav)
        self.max_channels = max_channels  # the maximum number of channels in the mixer

        # Initialize pygame
        pygame.mixer.init()
        pygame.init()

        # Set the number of available audio channels
        pygame.mixer.set_num_channels(max_channels)

    # Get all the files of file_type from the path
    # Only put those sounds in the folder that you want to be loaded into the mixer
    # Sounds beyond the maximum number of channels (max_channels) will be dropped
    def get_all_files_in_folder(self):
        wav_files = glob.glob(f"{self.path}/*.{self.file_type}")
        return wav_files

    # create the pygame mixer sound obejcts
    def load_sounds(self):
        all_wave_files = self.get_all_files_in_folder()  # get the sounds
        all_wave_files.sort()  # sort by name
        all_wave_files = all_wave_files[
            : self.max_channels
        ]  # drop those beyond the index of max_channels

        self.sounds = [
            pygame.mixer.Sound(file) for file in all_wave_files
        ]  # create pygame mixer sound objects

    # Play the sounds simultaneously with looping
    def play_sounds(self):
        for sound in self.sounds:
            sound.set_volume(1.0)
            sound.play(loops=-1)  # Set loops=-1 for infinite looping

    # Stop the mixer and quit pygame
    def stop(self):
        # Stop the sounds
        for sound in self.sounds:
            sound.stop()

        # Clean up and quit
        pygame.quit()

    # start the sound mixer
    def start(self):
        self.load_sounds()
        self.play_sounds()
        return self.sounds
