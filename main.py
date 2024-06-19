import requests
import getpass
import json
import pygetwindow
import pyautogui
import threading
import atexit
import time
import pynput
import sys
import math
import wave
import pyaudio
import numpy as np
pyautogui.FAILSAFE = False

import AwSnapUtil
AwSnapUtil.verbose_level = 2

TICK_SPEED = 0.05

ACTIONS_FILE = "actions.json"
VALORANT_TITLE = "VALORANT"

RICK_ROLL_FILE = "Audio/Rick Roll.wav"

IN_GAME_PIXEL = {"POS": (961, 131), "COLOUR": (240, 240, 240), "ABOVE_TOLERANCE": 15, "BELOW_TOLERANCE": 7}
DEAD_PIXEL = {"POS": (30, 797), "COLOUR": (254, 254, 254), "ABOVE_TOLERANCE": 1, "BELOW_TOLERANCE": 20}

keyboard_presser = pynput.keyboard.Controller()

events = {"EXIT": threading.Event(), "is_alive": threading.Event()}

def EXIT():
    events["EXIT"].set()

atexit.register(EXIT)

class ValorantInfo:
    alive_last_tick = False

    @staticmethod
    def color_within_tolerance(actual_color, expected_color, below_tolerance, above_tolerance):
        for actual, expected in zip(actual_color, expected_color):
            if not (expected - below_tolerance <= actual <= expected + above_tolerance):
                return False
        return True

    @staticmethod
    def get_active_window() -> str:
        active_window = pygetwindow.getActiveWindow()
        if active_window != None:
            return pygetwindow.getActiveWindow().title
        else:
            return None

    @classmethod
    def get_in_game(cls) -> bool:
        window_name = cls.get_active_window()
        if window_name != None and window_name.upper().strip() == VALORANT_TITLE:
            if cls.color_within_tolerance(AwSnapUtil.get_pixel_colour(IN_GAME_PIXEL["POS"]), IN_GAME_PIXEL["COLOUR"], IN_GAME_PIXEL["BELOW_TOLERANCE"], IN_GAME_PIXEL["ABOVE_TOLERANCE"]):
                return True
        return False

    @classmethod
    def get_alive(cls) -> bool:
        if cls.get_in_game() and not cls.color_within_tolerance(AwSnapUtil.get_pixel_colour(DEAD_PIXEL["POS"]), DEAD_PIXEL["COLOUR"], DEAD_PIXEL["BELOW_TOLERANCE"], DEAD_PIXEL["ABOVE_TOLERANCE"]):
            if cls.alive_last_tick:
                return True
            else:
                cls.alive_last_tick = True
                return False # Buffer for incorrect value read
        else:
            if cls.alive_last_tick:
                cls.alive_last_tick = False
                return True # Buffer for incorrect value read
            else:
                return False


class Actions():
    @staticmethod
    def inspect_gun():
        keyboard_presser.tap("y")
        return True
    
    @staticmethod
    def jump():
        keyboard_presser.tap(" ")
        return True
    
    @staticmethod
    def crouch():
        crouch_thread = threading.Thread(target=ActionsDependancies.hold_button, args=(events, keyboard_presser, 10, pynput.keyboard.Key.ctrl))
        crouch_thread.start()
        return True
    
    @staticmethod
    def rick_roll():
        rick_roll_thread = threading.Thread(target=ActionsDependancies.play_audio_with_fadeout, args=(events, RICK_ROLL_FILE, 61))
        rick_roll_thread.start()
        return True

    @staticmethod
    def drop_gun():
        keyboard_presser.tap("g")
        return True


class ActionsDependancies:
    actions_next_execute_time = {}

    @classmethod
    @AwSnapUtil.log_function(2)
    def execute_action(cls, action):
        action_function_name = action["Name"].lower().strip().replace(" ", "_").replace("+", "_")

        # DISPLAY USERS NAME

        if hasattr(Actions, action_function_name):
            action_function = getattr(Actions, action_function_name)
        else:
            print(f"{action_function_name} does not exist as an available function")
            return True # TEMPOARY NEEDS CHANGED TO FALSE

        result = action_function()

        return result
    
    @classmethod
    @AwSnapUtil.log_function(3)
    def execute_actions(cls, is_alive):
        executed_actions = []

        current_time = time.time()

        if is_alive:
            for action in ActionsHandler.get_actions():
                if action["Name"] not in executed_actions and (action["Name"] not in cls.actions_next_execute_time or current_time > cls.actions_next_execute_time[action["Name"]]):
                    result = cls.execute_action(action)

                    if result:
                        action["Fulfilled"] = 1

                        if action["IntervalSeconds"] > 0:
                            cls.actions_next_execute_time[action["Name"]] = current_time + action["IntervalSeconds"]

                        executed_actions.append(action["Name"])
        
        return bool(executed_actions)
    
    @staticmethod
    def hold_button(events, keyboard_presser, duration, key):
        def exit_hold_button():
            keyboard_presser.release(key)
            return False

        keyboard_presser.press(key)

        is_alive = False
        INTERVAL = 0.2

        for _ in range(math.floor(duration / INTERVAL)):
            if events["EXIT"].is_set():
                exit_hold_button()

            if not events["is_alive"].is_set():
                keyboard_presser.release(key)
                is_alive = False

            while not is_alive:
                time.sleep(INTERVAL)

                if events["EXIT"].is_set():
                    exit_hold_button()

                if events["is_alive"].is_set():
                    keyboard_presser.press(key)
                    is_alive = True

            keyboard_presser.press(key)

            time.sleep(INTERVAL)

        keyboard_presser.release(key)

        return True
    
    @staticmethod
    def play_audio_with_fadeout(events, file_path, duration):
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

        # Open two streams for two different devices
        stream1 = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True,
                        output_device_index=4)  # You can specify the device index

        stream2 = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True,
                        output_device_index=21)  # You can specify the device index

        buffer_size = 512
        volume = 1.0
        start_time = time.time()

        # Read and play audio data
        while stream1.is_active() and stream2.is_active():
            if events["EXIT"].is_set():
                break

            data = wf.readframes(buffer_size)
            if len(data) == 0:
                break

            # Calculate elapsed time
            elapsed_time = time.time() - start_time
            if elapsed_time < duration:
                volume = max(0.0, 0.5 * pow(1.5, -(elapsed_time + 1)) - (0.022 / 60) * elapsed_time + 0.022)

            # Convert audio data to numpy array
            audio_data = np.frombuffer(data, dtype=np.int16)
            # Apply volume
            audio_data = (audio_data * volume).astype(np.int16)
            # Write audio data to both streams
            stream1.write(audio_data.tobytes())
            stream2.write(audio_data.tobytes())

        # Stop and close the streams
        stream1.stop_stream()
        stream1.close()
        stream2.stop_stream()
        stream2.close()
        # Close PyAudio
        p.terminate()
        # Close the audio file
        wf.close()

class ActionsHandler:
    @classmethod
    def get_saved(cls):
        with open(ACTIONS_FILE, "r") as file:
            cls.actions = json.load(file)
    
    @classmethod
    def get_actions(cls):
        return cls.actions

    @classmethod
    @AwSnapUtil.log_function(3)
    def get_fulfilled_action_ids(cls):
        fulfilled_actions = []
        
        for action in cls.actions:
            fulfillment = action.get("Fulfilled")
            if fulfillment == 1:
                action_id = action.get("ActionID")
                fulfilled_actions.append(action_id)

        return fulfilled_actions

    @classmethod
    @AwSnapUtil.log_function(3)
    def save(cls):
        with open(ACTIONS_FILE, "w") as file:
            json.dump(cls.actions, file, indent=4)

    @classmethod
    def merge_new(cls, new_actions):
        """
        False if no change made. True if edit made.
        """
        if new_actions is None or not len(new_actions):
            return False

        edit_made = False
        existing_keys = {item["ActionID"] for item in cls.actions}

        for new_action in new_actions:
            new_action_id = new_action.get("ActionID")
            if new_action_id is not None and new_action_id not in existing_keys:
                new_action["Fulfilled"] = 0
                cls.actions.append(new_action)
                existing_keys.add(new_action_id)
                edit_made = True

        return edit_made

    @classmethod
    @AwSnapUtil.log_function(3)
    def remove(cls, fulfilled_action_ids):
        keep_actions = [action for action in cls.actions if action.get("ActionID") not in fulfilled_action_ids]

        if len(keep_actions) != len(cls.actions):
            cls.actions = keep_actions
            cls.save()


def main():
    ActionsHandler.get_saved()

    is_alive = False

    url = 'https://projectspace.nz/wrkvaxxi/ValorantStreamPoints/post/get_actions.php'
    password = getpass.getpass('Enter password: ')

    while True:
        fulfilled_action_ids = ActionsHandler.get_fulfilled_action_ids()

        # Data to be sent in the POST request
        body_data = {
            'password': password,
            'fulfilled_actions': str(fulfilled_action_ids)
        }

        response = requests.post(url, data=body_data)
        
        if response.status_code == 200:
            ActionsHandler.remove(fulfilled_action_ids)
        
        new_actions = AwSnapUtil.eval_message(response.text)

        edit_made = ActionsHandler.merge_new(new_actions)

        if is_alive != ValorantInfo.get_alive():
            is_alive = not is_alive

            if is_alive:
                events["is_alive"].set()
            else:
                events["is_alive"].clear()

        actions_executed = ActionsDependancies.execute_actions(is_alive)
        
        if actions_executed or edit_made:
            ActionsHandler.save()

        time.sleep(TICK_SPEED)

if __name__ == '__main__':
    main()