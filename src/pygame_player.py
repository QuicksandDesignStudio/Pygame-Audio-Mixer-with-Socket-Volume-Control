import asyncio
import glob
import pygame

from utils import reshape_sound_buffer_by_start_time, get_start_time


# Control Audio Spotlighting with Volume Controls
class SoundController:
    def __init__(self, sounds):
        self.sounds = sounds  # The list of pygame sounds in the mixer
        self.states = [True for _ in sounds]  # A state list to track sound states
        self.high_volume = 1.0  # Max volume for a sound
        self.low_volume = 0.1  # Min volume for a sound
        self.fade_time_in_seconds = 1  # Time taken to fade in and out
        self.fade_time_intervals = 0.1  # fade intervals. Total steps to fade = fade_time_in_seconds / fade_time_intervals

    # Handles a socket message and adjusts volumes of the sound clips
    # If none of the sounds are low then an on messages sets all but the index to low -> spotlight
    # If all the sounds except the index are low and the message is low then all sounds are set to high -> remove spotlight
    # Otherwise turns on and off based on index and type
    # For behviour where only one clip can be high at a time go to main branch in the repo
    async def handle_message(self, sensor_state):
        target_state = self.states[:]  # copy

        # if all the sensors are off
        if True not in sensor_state:
            # target state should be all on
            target_state = [True for _ in self.states]
        else:
            # target state should be the sensor state
            target_state = sensor_state[:]

        print(f"Current State : {self.states}")
        print(f"Sensor State : {sensor_state}")
        print(f"Target State : {target_state}")

        # steps, delta per step and current volume tracker
        steps = self.fade_time_in_seconds / self.fade_time_intervals
        delta = (self.high_volume - self.low_volume) / steps
        current_vol = self.high_volume

        # fade in by step
        while current_vol > self.low_volume:
            for i in range(len(self.sounds)):
                if target_state[i]:
                    # is the target state different from current state
                    if target_state[i] != self.states[i]:
                        self.sounds[i].set_volume(
                            self.high_volume - (current_vol - delta)
                        )
                else:
                    # is the target state different from current state
                    if target_state[i] != self.states[i]:
                        self.sounds[i].set_volume(current_vol - delta)

            current_vol = current_vol - delta
            await asyncio.sleep(0.1)

        self.states = target_state[:]


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

        for f in all_wave_files:
            # Modify the sound buffer so the clips start at the required time
            # Either random or a fixed time for all
            # See utils.py for the function definition of reshape_sound_buffer_by_start_time
            modifiedBuffer = reshape_sound_buffer_by_start_time(f, get_start_time())

            # Load the modified buffers as Sounds into the mixer
            # Note the buffers are loaded into memory
            # Tested with Raspberyy Pi 3B+
            # Amazingly the the pygame.mixer.Sound() constructor takes in a numpy.ndarray array as a buffer
            # How convenient is that!
            self.sounds.append(pygame.mixer.Sound(modifiedBuffer))

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
