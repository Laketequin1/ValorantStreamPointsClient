import pyaudio
import wave
import numpy as np
import threading
import time

# Function to play audio with volume control
def play_audio_with_fadeout(file_path, duration):
    # Open the audio file
    wf = wave.open(file_path, 'rb')

    # Create a PyAudio instance
    p = pyaudio.PyAudio()

    # Open a stream
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)

    # Total number of frames
    total_frames = wf.getnframes()
    # Frames per second
    frame_rate = wf.getframerate()

    # Buffer size
    buffer_size = 1024

    # Start the stream
    stream.start_stream()

    volume = 1.0

    # Function to fade out the volume
    def fade_out():
        nonlocal volume
        start_time = time.time()
        while time.time() - start_time < duration:
            elapsed_time = time.time() - start_time
            volume = max(0.0, pow(1.5, -(elapsed_time + 1)) - (0.022/60) * elapsed_time + 0.022)
            time.sleep(0.1)
            print(round(elapsed_time), round(volume, 4))
        stream.stop_stream()
        stream.close()
        p.terminate()

    # Create a thread for the fade-out function
    fade_out_thread = threading.Thread(target=fade_out)
    fade_out_thread.start()

    # Read and play audio data
    while stream.is_active():
        data = wf.readframes(buffer_size)
        if len(data) == 0:
            break

        # Convert audio data to numpy array
        audio_data = np.frombuffer(data, dtype=np.int16)
        # Apply volume
        audio_data = (audio_data * volume).astype(np.int16)
        # Write audio data to stream
        stream.write(audio_data.tobytes())

    # Wait for fade out to complete
    fade_out_thread.join()

    # Stop and close the stream
    stream.stop_stream()
    stream.close()
    # Close PyAudio
    p.terminate()
    # Close the audio file
    wf.close()

# Path to the audio file
audio_file = 'Audio/Rick Roll.wav'

# Play the audio file with fade out over 45 seconds
play_audio_with_fadeout(audio_file, 60)
