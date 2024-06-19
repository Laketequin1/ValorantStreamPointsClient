import pyaudio
import wave
import numpy as np
import time

def play_audio_with_fadeout(file_path, duration):
    """
    Plays an audio file with a fade-out effect over the specified duration.

    Args:
        file_path (str): Path to the audio file.
        duration (float): Duration for the fade-out effect in seconds.
    """

    # Open the audio file
    wf = wave.open(file_path, 'rb')

    # Create a PyAudio instance
    p = pyaudio.PyAudio()

    # Open a stream
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)

    buffer_size = 1024
    volume = 1.0

    start_time = time.time()

    # Read and play audio data
    while stream.is_active():
        data = wf.readframes(buffer_size)
        if len(data) == 0:
            break

        # Calculate elapsed time
        elapsed_time = time.time() - start_time
        if elapsed_time < duration:
            volume = max(0.0, 0.5 * pow(1.5, -(elapsed_time + 1)) - (0.022 / 60) * elapsed_time + 0.022)
            print(volume)

        # Convert audio data to numpy array
        audio_data = np.frombuffer(data, dtype=np.int16)
        # Apply volume
        audio_data = (audio_data * volume).astype(np.int16)
        # Write audio data to stream
        stream.write(audio_data.tobytes())

    # Stop and close the stream
    stream.stop_stream()
    stream.close()
    # Close PyAudio
    p.terminate()
    # Close the audio file
    wf.close()

# Path to the audio file
audio_file = 'Audio/Rick Roll.wav'

# Play the audio file with fade out over 60 seconds
play_audio_with_fadeout(audio_file, 60)
