import pyttsx3, time, wave, pyaudio
import numpy as np
engine = pyttsx3.init() # object creation

engine.setProperty('rate', 200)
engine.setProperty('volume', 1.0)

def play_audio(file_path, volume = 1.0):
    """
    Plays an audio file with a fade-out effect over the specified duration on two sound devices.

    Args:
        events (dict): Dictionary containing threading events.
        file_path (str): Path to the audio file.
        duration (float): Duration for the fade-out effect in seconds.
    """

    # Open the audio file
    wf = wave.open(file_path, 'rb')

    # Create a PyAudio instance
    p = pyaudio.PyAudio()

    audio_format = p.get_format_from_width(wf.getsampwidth())

    # Open two streams for two different devices
    stream1 = p.open(format=audio_format,
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True,
                    output_device_index=4)  # You can specify the device index

    
    stream2 = p.open(format=audio_format,
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True,
                    output_device_index=8)  # You can specify the device index

    buffer_size = 512

    # Read and play audio data
    while stream1.is_active(): #and stream2.is_active():
        data = wf.readframes(buffer_size)
        if len(data) == 0:
            break

        # Convert audio data to numpy array
        audio_data = np.frombuffer(data, dtype=np.int16)
        # Apply volume
        audio_data = (audio_data * volume).astype(np.int16)
        # Write audio data to both streams
        stream1.write(audio_data.tobytes())
        #stream2.write(audio_data.tobytes())

    # Stop and close the streams
    stream1.stop_stream()
    stream1.close()
    stream2.stop_stream()
    stream2.close()
    # Close PyAudio
    p.terminate()
    # Close the audio file
    wf.close()

old = time.time()
engine.save_to_file('Hello World, omg, this is crazy!!', 'Temp/Test.wav')
engine.runAndWait()

print(f"Elapsed time: {round(time.time() - old, 4)}")

play_audio("Temp/Test.wav")