import random
import wave
import numpy as np

is_random = True
fixed_time_in_seconds = 150
random_range = (0, 150)


# Reshape the sound buffer to start at the start_time
# Take in file location and return the modified buffer
def reshape_sound_buffer_by_start_time(file_location, start_time):
    with wave.open(file_location, "rb") as wav_file:
        # get the number of channels and the frame rate
        channels = wav_file.getnchannels()
        framerate = wav_file.getframerate()

        # calculate the number of frames to skip based on the start time
        frames_to_skip = int(start_time * framerate)

        # set the file pointer to the correct frame
        wav_file.setpos(frames_to_skip)

        # read the frames from start to the start_time
        frames = wav_file.readframes(wav_file.getnframes() - frames_to_skip)

        # Go back to the beginning of the file
        wav_file.rewind()

        # get the skipped frames
        skipped_frames = wav_file.readframes(frames_to_skip)

    # add the skipped frames to the end of the frames
    combined_frames = frames + skipped_frames

    # conver the binary data to a numpy array
    samples = np.frombuffer(combined_frames, dtype=np.int16)

    # reshape the array to have the correct number of channels
    samples = samples.reshape(-1, channels)

    return samples


# get start time in either random mode or at a fixed time
def get_start_time():
    if is_random:
        return random.randint(random_range[0], random_range[1])
    else:
        return fixed_time_in_seconds
