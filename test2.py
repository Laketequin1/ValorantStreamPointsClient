import pyaudio

def list_audio_devices():
    """
    Lists available audio output devices with their indexes.
    """
    p = pyaudio.PyAudio()
    for i in range(p.get_device_count()):
        device_info = p.get_device_info_by_index(i)
        if device_info['maxOutputChannels'] > 0:
            print(f"Index: {i}, Name: {device_info['name']}")
    p.terminate()

# List available audio devices
list_audio_devices()
