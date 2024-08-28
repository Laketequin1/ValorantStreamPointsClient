from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume, IAudioSessionManager2, IAudioSessionControl2, ISimpleAudioVolume
from comtypes import CLSCTX_ALL
from ctypes import cast, POINTER

# Function to set the volume of an application
def set_app_volume(app_name, volume_level):
    sessions = AudioUtilities.GetAllSessions()
    for session in sessions:
        if session.Process and session.Process.name().lower() == app_name.lower():
            volume = session._ctl.QueryInterface(ISimpleAudioVolume)
            volume.SetMasterVolume(volume_level, None)
            return True
    return False

# Set the volume for Valorant (application name is usually 'VALORANT-Win64-Shipping.exe')
if set_app_volume('VALORANT-Win64-Shipping.exe', 1):  # Set volume to 50%
    print("Volume set successfully")
else:
    print("Application not found")
