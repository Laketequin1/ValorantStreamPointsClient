import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'

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
import pygame
import win32api
import win32gui
import win32con
import random
from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume
from comtypes import CoInitialize, CoUninitialize

import AwSnapUtil
AwSnapUtil.verbose_level = 2

pyautogui.FAILSAFE = False

MAIN_LOOP_DELAY = 0.05
FRAME_RATE = 30

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


class Actions:
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
    
    @staticmethod
    def mute_game():
        mute_game_thread = threading.Thread(target=ActionsDependancies.mute_valorant, args=(events, "VALORANT-Win64-Shipping.exe", 20))
        mute_game_thread.start()
        return True


class ActionsDependancies:
    actions_next_execute_time = {}

    @classmethod
    @AwSnapUtil.log_function(2)
    def execute_action(cls, action):
        action_function_name = action["Name"].lower().strip().replace(" ", "_").replace("+", "_")

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
    
    @staticmethod # THREAD
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

    @staticmethod # THREAD
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

    @staticmethod
    def set_app_volume(app_name, volume_level):
        sessions = AudioUtilities.GetAllSessions()
        for session in sessions:
            if session.Process and session.Process.name().lower() == app_name.lower():
                volume = session._ctl.QueryInterface(ISimpleAudioVolume)
                volume.SetMasterVolume(volume_level, None)
                return True
        return False

    @staticmethod # THREAD
    def mute_valorant(events, app_name, duration):
        CoInitialize()
        
        def exit_mute_valorant():
            ActionsDependancies.set_app_volume(app_name, 1)
            return False

        INTERVAL = 0.2

        while not events["is_alive"].is_set():
            if events["EXIT"].is_set():
                exit_mute_valorant()

            time.sleep(INTERVAL)

        ActionsDependancies.set_app_volume(app_name, 0)

        for _ in range(math.floor(duration / INTERVAL)):
            if events["EXIT"].is_set():
                exit_mute_valorant()

            time.sleep(INTERVAL)

        ActionsDependancies.set_app_volume(app_name, 1)

        return True


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


class ActionOverlay:
    """
    ActionOverlay is a class to manage and display a transparent overlay window with text that slides out after a set duration.

    Attributes:
    -----------
    lines_of_text : list
        A list to store tuples of text and the time they were added.
    lock : threading.Lock
        A lock for thread-safe operations on lines_of_text.
    running : bool
        A flag to control the main loop.

    Methods:
    --------
    __init__():
        Initializes the overlay window and starts the main loop in a separate thread.

    add_text(text: str) -> None:
        Adds a line of text with a timestamp to the overlay.

    handle_events() -> bool:
        Handles pygame events and returns whether the main loop should continue.

    render() -> None:
        Renders the text onto the overlay window and handles the sliding animation.

    main_loop() -> None:
        The main loop of the overlay that handles events and rendering.
    """

    # Window size
    WINDOW_PERCENT_WIDTH = 0.3
    WINDOW_PERCENT_HEIGHT = 0.4

    # Colours
    WINDOW_BG_COLOR = (0, 0, 0)
    TEXT_COLOR = (255, 255, 255)
    TEXT_BG_COLOR = (0, 0, 20)

    # Text padding
    TEXT_PADDING_X = 10
    TEXT_PADDING_Y = 5
    TEXT_LINE_HEIGHT = 46
    FONT_SIZE = 48

    # Text settings
    MAX_LINES = 8
    TEXT_LIFETIME_SECONDS = 5
    ANIMATION_DURATION = 0.4

    def __init__(self, events):
        """Initializes the overlay window and sets its properties."""
        pygame.init()

        self.events = events

        self.clock = pygame.time.Clock()

        # Get the dimensions of the screen
        self.screen_width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
        self.screen_height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)

        # Calculate the window dimensions based on percentages
        self.window_width = round(self.screen_width * self.WINDOW_PERCENT_WIDTH)
        self.window_height = round(self.screen_height * self.WINDOW_PERCENT_HEIGHT)

        # Calculate the window position (bottom left)
        self.window_x = 0
        self.window_y = self.screen_height - self.window_height

        # Create the window with no frame
        self.screen = pygame.display.set_mode((self.window_width, self.window_height), pygame.NOFRAME)

        # Get the window handle (HWND)
        hwnd = pygame.display.get_wm_info()['window']

        # Set the title of the window
        pygame.display.set_caption("Pygame Window")

        # Make the window always on top
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, self.window_x, self.window_y, self.window_width, self.window_height, win32con.SWP_SHOWWINDOW)

        # Make the window transparent
        extended_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, extended_style | win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT)
        win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(0, 0, 0), 0, win32con.LWA_COLORKEY)

        # Variables for managing text
        self.lines_of_text = []
        self.lock = threading.Lock()

        # Start the main loop in a separate thread
        self.running = True
        self.thread = threading.Thread(target=self.main_loop)
        self.thread.start()

    def add_text(self, text: str) -> None:
        """
        Adds a line of text with a timestamp to the overlay.

        Parameters:
        -----------
        text : str
            The text to be added to the overlay.

        Example:
        --------
        >>> overlay.add_text("Hello, World!")
        """
        current_time = time.time()
        with self.lock:
            self.lines_of_text.append((text, current_time))
            if len(self.lines_of_text) > self.MAX_LINES:
                self.lines_of_text = self.lines_of_text[-self.MAX_LINES:]

    def handle_events(self) -> bool:
        """
        Handles pygame events and returns whether the main loop should continue.

        Returns:
        --------
        bool
            False if the quit event is detected, True otherwise.

        Example:
        --------
        >>> running = overlay.handle_events()
        >>> running
        True
        """
        try:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return False
            return True
        except Exception as e:
            print(f"Error handling events: {e}")
            return False

    def render(self) -> None:
        """
        Renders the text onto the overlay window and handles the sliding animation.

        Example:
        --------
        >>> overlay.render()
        """
        try:
            current_time = time.time()
            with self.lock:
                self.lines_of_text = [(text, t) for text, t in self.lines_of_text if current_time - t < (self.TEXT_LIFETIME_SECONDS + self.ANIMATION_DURATION)]
                local_lines_of_text = list(self.lines_of_text)

            # Fill the screen with a color (RGB)
            self.screen.fill(self.WINDOW_BG_COLOR)  # Must be black background

            # Render text on the screen with rounded border
            font = pygame.font.Font(None, self.FONT_SIZE)
            text_y = self.window_height - self.TEXT_LINE_HEIGHT
            for line, t in reversed(local_lines_of_text):
                elapsed_time = current_time - t

                # Calculate the text x position based on elapsed time
                if elapsed_time > self.TEXT_LIFETIME_SECONDS:
                    animation_progress = (elapsed_time - self.TEXT_LIFETIME_SECONDS) / self.ANIMATION_DURATION
                    text_x = int(self.TEXT_PADDING_X - self.window_width * animation_progress)
                else:
                    text_x = self.TEXT_PADDING_X

                # Render text surface
                text_surface = font.render(line, True, self.TEXT_COLOR)  # White text

                # Create rounded rectangle surface for text background
                text_rect = text_surface.get_rect()
                text_rect.left = text_x
                text_rect.top = text_y
                text_rect.width += self.TEXT_PADDING_X * 2  # Add padding
                text_rect.height += self.TEXT_PADDING_Y * 2  # Add padding
                pygame.draw.rect(self.screen, self.TEXT_BG_COLOR, text_rect, border_radius=10)  # Dark blue rounded rectangle

                # Blit text onto screen
                self.screen.blit(text_surface, (text_rect.left + self.TEXT_PADDING_X, text_rect.top + self.TEXT_PADDING_Y))  # Offset text slightly for padding

                # Adjust y position for next line
                text_y -= self.TEXT_LINE_HEIGHT  # Increase the spacing between lines

            # Update the display
            pygame.display.flip()
        except Exception as e:
            print(f"Error rendering: {e}")

    def main_loop(self) -> None:
        """
        The main loop of the overlay that handles events and rendering.

        Example:
        --------
        >>> overlay.main_loop()
        """
        try:
            while self.running:
                if events["EXIT"].is_set():
                    pygame.quit()
                    sys.exit(0)

                # Render the overlay
                self.render()

                # Cap the frame rate to 30 FPS (optional, adjust as needed)
                self.clock.tick(FRAME_RATE)
        except Exception as e:
            print(f"Error in main loop: {e}")
            self.running = False


def main():
    ActionsHandler.get_saved()

    is_alive = False

    url = 'https://projectspace.nz/wrkvaxxi/ValorantStreamPoints/post/get_actions.php'
    password = getpass.getpass('Enter password: ')

    overlay = ActionOverlay(events)

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

        # Add a random text line
        if random.randint(1, 5) == 1:
            msg = "HEY: " + str(random.randint(0, 10))
            overlay.add_text(msg)
            print(msg)

        running = overlay.handle_events()
        if not running:
            sys.exit(0)

        time.sleep(0.05)

if __name__ == '__main__':
    main()