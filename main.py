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
import keyboard
from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume
from comtypes import CoInitialize, CoUninitialize

import AwSnapUtil
AwSnapUtil.verbose_level = 2

pygame.init()
pyautogui.FAILSAFE = False

MAIN_LOOP_DELAY = 0.05
FRAME_RATE = 60

ACTIONS_FILE = "actions.json"

VALORANT_TITLE = "VALORANT"
VALORANT_EXE = "VALORANT-Win64-Shipping.exe"

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
    def get_active_window():
        active_window = pygetwindow.getActiveWindow()
        if active_window != None:
            return active_window.title, active_window._hWnd
        else:
            return None, None

    @classmethod
    def get_in_game(cls) -> bool:
        window_name, window_hwnd = cls.get_active_window()
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
        crouch_thread = threading.Thread(target=ActionsDependancies.hold_buttons, args=(events, keyboard_presser, 10, [pynput.keyboard.Key.ctrl]))
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
        mute_game_thread = threading.Thread(target=ActionsDependancies.mute_valorant, args=(events, VALORANT_EXE, 20))
        mute_game_thread.start()
        return True
    
    @staticmethod
    def knife_only():
        spam_thread = threading.Thread(target=ActionsDependancies.spam_button, args=(events, keyboard_presser, 10, "g"))
        spam_thread.start()
        return True
    
    @staticmethod
    def ad_popup(overlay):
        overlay.add_ads(9)
        return True
    
    @staticmethod
    def disable_wasd():
        disable_wasd_thread = threading.Thread(target=ActionsDependancies.disable_buttons, args=(events, 10, ["w", "a", "s", "d"]))
        disable_wasd_thread.start()
        return True
    
    @staticmethod
    def alt___f4(overlay):
        kill_valorant_thread = threading.Thread(target=ActionsDependancies.kill_valorant, args=(overlay, 5))
        kill_valorant_thread.start()
        return True
    
    @staticmethod
    def shutdown(overlay):
        shutdown_thread = threading.Thread(target=ActionsDependancies.shutdown, args=(overlay, 5))
        shutdown_thread.start()
        return True


class ActionsDependancies:
    actions_next_execute_time = {}

    @classmethod
    @AwSnapUtil.log_function(2)
    def execute_action(cls, action, overlay):
        action_function_name = action["Name"].lower().strip().replace(" ", "_").replace("+", "_")

        if hasattr(Actions, action_function_name):
            action_function = getattr(Actions, action_function_name)
        else:
            print(f"{action_function_name} does not exist as an available function")
            return False

        if action_function_name in ["alt___f4", "ad_popup", "shutdown"]:
            result = action_function(overlay)
        else:
            result = action_function()
        return result
    
    @classmethod
    @AwSnapUtil.log_function(3)
    def execute_actions(cls, is_alive, overlay):
        executed_actions = []

        current_time = time.time()

        if is_alive:
            for action in ActionsHandler.get_actions():
                if action["Name"] not in executed_actions and (action["Name"] not in cls.actions_next_execute_time or current_time > cls.actions_next_execute_time[action["Name"]]):
                    result = cls.execute_action(action, overlay)

                    if result:
                        msg = f"{action['Username']} executed {action['Name']}"
                        overlay.add_text(msg)

                        action["Fulfilled"] = 1

                        if action["IntervalSeconds"] > 0:
                            cls.actions_next_execute_time[action["Name"]] = current_time + action["IntervalSeconds"]

                        executed_actions.append(action["Name"])
        
        return bool(executed_actions)
    
    @staticmethod # THREAD
    def spam_button(events, keyboard_presser, duration, key):
        def exit_hold_button():
            keyboard_presser.release(key)
            return False

        is_alive = False
        INTERVAL = 0.1

        for _ in range(math.floor(duration / INTERVAL)):
            if events["EXIT"].is_set():
                exit_hold_button()

            if not events["is_alive"].is_set():
                is_alive = False

            while not is_alive:
                time.sleep(INTERVAL)

                if events["EXIT"].is_set():
                    exit_hold_button()

                if events["is_alive"].is_set():
                    is_alive = True

            keyboard_presser.tap(key)

            time.sleep(INTERVAL)

        keyboard_presser.release(key)

        return True
    
    @staticmethod # THREAD
    def hold_buttons(events, keyboard_presser, duration, keys):
        def exit_hold_button():
            for key in keys:
                keyboard_presser.release(key)
            return False

        for key in keys:
            keyboard_presser.press(key)

        is_alive = False
        INTERVAL = 0.2

        for _ in range(math.floor(duration / INTERVAL)):
            if events["EXIT"].is_set():
                exit_hold_button()

            if not events["is_alive"].is_set():
                for key in keys:
                    keyboard_presser.release(key)
                is_alive = False

            while not is_alive:
                time.sleep(INTERVAL)

                if events["EXIT"].is_set():
                    exit_hold_button()

                if events["is_alive"].is_set():
                    for key in keys:
                        keyboard_presser.press(key)
                    is_alive = True

            for key in keys:
                keyboard_presser.press(key)

            time.sleep(INTERVAL)

        for key in keys:
            keyboard_presser.release(key)

        return True
    
    @staticmethod # THREAD
    def disable_buttons(events, duration, keys):
        def exit_disable_button():
            for key in keys:
                keyboard.unblock_key(key)
            return False

        for key in keys:
            keyboard.block_key(key)

        is_alive = False
        INTERVAL = 0.2

        for _ in range(math.floor(duration / INTERVAL)):
            if events["EXIT"].is_set():
                exit_disable_button()

            if not events["is_alive"].is_set():
                for key in keys:
                    keyboard.unblock_key(key)
                is_alive = False

            while not is_alive:
                time.sleep(INTERVAL)

                if events["EXIT"].is_set():
                    exit_disable_button()

                if events["is_alive"].is_set():
                    for key in keys:
                        keyboard.block_key(key)
                    is_alive = True

            time.sleep(INTERVAL)

        for key in keys:
            keyboard.unblock_key(key)

        return True

    @staticmethod # THREAD
    def kill_valorant(overlay, delay):
        for x in range(delay):
            overlay.add_text(f"Alt + F4 in {delay - x}...")
            time.sleep(1)

        exit_code = os.system(f'taskkill /F /IM {VALORANT_EXE}')

        if exit_code == 0:
            print("VALORANT has been forcefully closed.")
            overlay.add_text("VALORANT forcefully closed")
        else:
            print(f"Error {exit_code}: Could not close VALORANT.")

    @staticmethod # THREAD
    def shutdown(overlay, delay):
        for x in range(delay):
            overlay.add_text(f"Shutdown in {delay - x}...")
            time.sleep(1)

        exit_code = os.system(f'shutdown /s /f /t 0')

        if exit_code == 0:
            print("Shutdown complete.")
            overlay.add_text("Shutdown complete")
        else:
            print(f"Error {exit_code}: Could not shutdown.")

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
    TEXT_WINDOW_PERCENT_WIDTH = 0.3
    TEXT_WINDOW_PERCENT_HEIGHT = 0.4

    # Colours
    WINDOW_BG_COLOR = (0, 0, 0)
    TEXT_COLOR = (255, 255, 255)
    TEXT_BG_COLOR = (0, 0, 20)

    LIGHT_GREY = (230, 230, 230)
    BLACK = (1, 1, 1)

    # Text padding
    TEXT_PADDING_X = 10
    TEXT_PADDING_Y = 5
    FONT_SIZE = 36
    TEXT_LINE_HEIGHT = 44

    # Ads
    AD_WIDTH = 0.4
    AD_HEIGHT = 0.35

    AD_BORDER = 3 #px

    # Text settings
    MAX_LINES = 8
    TEXT_LIFETIME_SECONDS = 15
    ANIMATION_DURATION = 0.4

    def __init__(self, events):
        """Initializes the overlay window and sets its properties."""
        self.events = events

        self.clock = pygame.time.Clock()

        # Get the dimensions of the screen
        self.screen_width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
        self.screen_height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)

        # Calculate the window dimensions based on percentages
        self.text_window_width = round(self.screen_width * self.TEXT_WINDOW_PERCENT_WIDTH)
        self.text_window_height = round(self.screen_height * self.TEXT_WINDOW_PERCENT_HEIGHT)

        # Calculate the window position
        self.window_x = 0
        self.window_y = self.screen_height - self.text_window_height

        # Create the window with no frame
        #self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.NOFRAME)
        self.screen = pygame.display.set_mode((self.text_window_width, self.text_window_height), pygame.NOFRAME)

        # Get the window handle (HWND)
        self.hwnd = pygame.display.get_wm_info()['window']

        # Set the title of the window
        pygame.display.set_caption("VSP Action Overlay")

        # Make the window always on top
        win32gui.SetWindowPos(self.hwnd, win32con.HWND_TOPMOST, self.window_x, self.window_y, self.text_window_width, self.text_window_height, win32con.SWP_SHOWWINDOW)

        # Make the window transparent
        extended_style = win32gui.GetWindowLong(self.hwnd, win32con.GWL_EXSTYLE)
        win32gui.SetWindowLong(self.hwnd, win32con.GWL_EXSTYLE, extended_style | win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT)
        win32gui.SetLayeredWindowAttributes(self.hwnd, win32api.RGB(0, 0, 0), 0, win32con.LWA_COLORKEY)

        # Variables for text
        self.lines_of_text = []
        self.lock = threading.Lock()

        self.font = pygame.font.Font(None, self.FONT_SIZE)

        # Variables for ads
        self.ads = []

        self.ad_width = round(self.screen_width * self.AD_WIDTH)
        self.ad_height = round(self.screen_height * self.AD_HEIGHT)

        ad_button_size = 50
        self.ad_button_width = min(ad_button_size, self.ad_width)
        self.ad_button_height = min(ad_button_size, self.ad_height)

        self.passthrough = True
        self.previous_mouse_state = False

        image_folder_path = "Images"
        self.images = {}

        img_width = self.ad_width
        img_height = self.ad_height - self.ad_button_height

        self.ad_font = pygame.font.Font(None, round(self.ad_button_height))

        # Loop through all Images
        for filename in os.listdir(image_folder_path):
            file_path = os.path.join(image_folder_path, filename)
            
            if os.path.isfile(file_path) and filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                image = pygame.image.load(file_path)

                resized_image = pygame.transform.scale(image, (img_width, img_height))
                
                image_name = os.path.splitext(filename)[0]
                self.images[image_name] = resized_image

        # Start the main loop in a separate thread
        self.running = True
        self.thread = threading.Thread(target=self.main_loop)
        self.thread.start()

    def disable_clickthrough(self):
        """Disables clickthrough, making the Pygame window clickable."""
        with self.lock:
            self.passthrough = False

        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.NOFRAME)
        win32gui.SetWindowPos(self.hwnd, win32con.HWND_TOPMOST, 0, 0, self.screen_width, self.screen_height, win32con.SWP_SHOWWINDOW)

        extended_style = win32gui.GetWindowLong(self.hwnd, win32con.GWL_EXSTYLE)
        win32gui.SetWindowLong(self.hwnd, win32con.GWL_EXSTYLE, extended_style & ~win32con.WS_EX_TRANSPARENT)
    
    def enable_clickthrough(self):
        """Enables clickthrough, allowing mouse clicks to pass through the window."""
        with self.lock:
            self.passthrough = True

        self.screen = pygame.display.set_mode((self.text_window_width, self.text_window_height), pygame.NOFRAME)
        win32gui.SetWindowPos(self.hwnd, win32con.HWND_TOPMOST, self.window_x, self.window_y, self.text_window_width, self.text_window_height, win32con.SWP_SHOWWINDOW)

        extended_style = win32gui.GetWindowLong(self.hwnd, win32con.GWL_EXSTYLE)
        win32gui.SetWindowLong(self.hwnd, win32con.GWL_EXSTYLE, extended_style | win32con.WS_EX_TRANSPARENT)

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

    def add_ads(self, ad_count) -> None:
        """
        Adds new fake ad windows which the user has to close.

        Parameters:
        -----------
        text : int
            Number of new ads to create.

        Example:
        --------
        >>> overlay.add_ad(3)
        """

        avalable_height = self.screen_height - self.ad_height
        avalable_width = self.screen_width - self.ad_width

        ad_sections = ad_count + 1

        y_change = math.floor(avalable_height / ad_sections)
        y_random_max = 2 * y_change // ad_sections
        y_positions = []
        y = random.randint(0, y_random_max)

        x_change = math.floor(avalable_width / ad_sections)
        x_random_max = 2 * x_change // ad_count
        x_positions = []
        x = random.randint(0, x_random_max)

        for _ in range(ad_count):
            y_positions.append(y)
            y += y_change + random.randint(0, y_random_max)

            x_positions.append(x)
            x += x_change + random.randint(0, x_random_max)

        random.shuffle(y_positions)
        random.shuffle(x_positions)

        for i in range(ad_count):
            x = x_positions[i]
            y = y_positions[i]

            surface = pygame.Surface((self.ad_width, self.ad_height))
            surface.fill(self.LIGHT_GREY)

            left = self.ad_width - self.ad_button_width

            ad_description, ad_image = random.choice(list(self.images.items()))

            surface.blit(ad_image, (0, self.ad_button_height))

            text_surface = self.ad_font.render(ad_description, True, self.BLACK)
            surface.blit(text_surface, (self.ad_button_width * 0.2, self.ad_button_height * 0.2))

            pygame.draw.rect(surface, (255, 8, 8), (left, 0, self.ad_button_width, self.ad_button_height))
            pygame.draw.line(surface, self.BLACK, (left + 0.1 * self.ad_button_width, 0.1 * self.ad_button_height), (left - 0.1 * self.ad_button_width + self.ad_button_width, self.ad_button_height - 0.1 * self.ad_button_height), self.AD_BORDER)
            pygame.draw.rect(surface, self.BLACK, (0, 0, self.ad_width, self.ad_height), self.AD_BORDER)

            ad = {"Position": (x, y), "Surface": surface}

            with self.lock:
                self.ads.append(ad)

        self.disable_clickthrough()

    def is_running(self) -> bool:
        """
        Returns if window is running. Running is False when window is closed.

        Returns:
        --------
        bool
            False if window not running, True otherwise.

        Example:
        --------
        >>> running = overlay.is_running()
        >>> running
        True
        """

        with self.lock:
            return self.running

    @staticmethod
    def pos_in_rectangle(pos, left, top, right, bottom) -> bool:
        """
        Returns whether a position is in the given rectangle.

        Returns:
        --------
        bool
            True if position is within rectangle, False otherwise.

        Example:
        --------
        >>> overlay.pos_in_rectangle((50, 50), 40, 40, 60, 60)
        True
        """

        top_left_x = min(left, right)
        top_left_y = min(top, bottom)
        bottom_right_x = max(left, right)
        bottom_right_y = max(top, bottom)

        if top_left_x <= pos[0] <= bottom_right_x and top_left_y <= pos[1] <= bottom_right_y:
            return True
        return False

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

        with self.lock:
            do_enable_clickthrough = not self.ads and not self.passthrough
                
        if do_enable_clickthrough:
            self.enable_clickthrough()

        try:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    with self.lock:
                        self.running = False
        except Exception as e:
            print(f"Error handling events: {e}")
            with self.lock:
                self.running = False

    def handle_ads(self) -> None:
        with self.lock:
            ads = self.ads[:]

        if not ads:
            return

        current_mouse_state, mouse_pos = AwSnapUtil.get_mouse_state()

        if current_mouse_state and not self.previous_mouse_state:
            for ad in ads:
                right = ad["Position"][0] + self.ad_width
                top = ad["Position"][1]

                left = right - self.ad_button_width
                bottom = top + self.ad_button_height

                if self.pos_in_rectangle(mouse_pos, left, top, right, bottom):
                    with self.lock:
                        self.ads.remove(ad)

        self.previous_mouse_state = current_mouse_state

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
                local_lines_of_text = self.lines_of_text[:]

                local_ads = self.ads[:]
                passthrough = self.passthrough

            # Fill the screen with a color (RGB)
            self.screen.fill(self.WINDOW_BG_COLOR) # Must be black background

            for ad in local_ads:
                self.screen.blit(ad["Surface"], ad["Position"])

            # Render text on the screen with rounded border
            if passthrough:
                text_y = self.text_window_height - self.TEXT_LINE_HEIGHT
            else:
                text_y = self.screen_height - self.TEXT_LINE_HEIGHT
                self.screen.set_at(IN_GAME_PIXEL["POS"], self.WINDOW_BG_COLOR)

            for line, t in reversed(local_lines_of_text):
                elapsed_time = current_time - t

                # Calculate the text x position based on elapsed time
                if elapsed_time > self.TEXT_LIFETIME_SECONDS:
                    animation_progress = (elapsed_time - self.TEXT_LIFETIME_SECONDS) / self.ANIMATION_DURATION
                    text_x = int(self.TEXT_PADDING_X - self.text_window_width * animation_progress)
                else:
                    text_x = self.TEXT_PADDING_X

                # Render text surface
                text_surface = self.font.render(line, True, self.TEXT_COLOR)  # White text

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
                    print("ActionOverlay Quit")
                    pygame.quit()
                    sys.exit(0)

                self.handle_ads()

                # Render the overlay
                self.render()

                # Cap the frame rate
                self.clock.tick(FRAME_RATE)
        except Exception as e:
            print(f"Error in main loop: {e}")
            with self.lock:
                self.running = False


def main():
    is_alive = False

    url = 'https://projectspace.nz/wrkvaxxi/ValorantStreamPoints/post/get_actions.php'
    password_path = "C:\\Passwords\\ValorantStreamPoints.txt"

    if os.path.exists(password_path):
        with open(password_path, "r") as file:
            password = file.read()
        print("Password sourced from file")
    else:
        password = getpass.getpass('Enter password: ')

    ActionsHandler.get_saved()

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

        is_alive = ValorantInfo.get_alive()
        if is_alive:
            events["is_alive"].set()
        else:
            events["is_alive"].clear()

        actions_executed = ActionsDependancies.execute_actions(is_alive, overlay)
        
        if actions_executed or edit_made:
            ActionsHandler.save()

        overlay.handle_events()
        running = overlay.is_running()
        if not running:
            sys.exit(0)

        time.sleep(0.05)

if __name__ == '__main__':
    main()