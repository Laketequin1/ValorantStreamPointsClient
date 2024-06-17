import requests
import getpass
import json
import pygetwindow
import pyautogui
import time
import pynput
pyautogui.FAILSAFE = False

import AwSnapUtil
AwSnapUtil.verbose_level = 2

TICK_SPEED = 0.05

ACTIONS_FILE = "actions.json"
VALORANT_TITLE = "VALORANT"

IN_GAME_PIXEL = {"POS": (961, 131), "COLOUR": (240, 240, 240), "ABOVE_TOLERANCE": 15, "BELOW_TOLERANCE": 7}
DEAD_PIXEL = {"POS": (30, 797), "COLOUR": (254, 254, 254), "ABOVE_TOLERANCE": 1, "BELOW_TOLERANCE": 20}

keyboard_presser = pynput.keyboard.Controller()

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
        keyboard_presser.tap("y") # CREATE MAX EXECUTIONS PER TICK
        time.sleep(0.1)
        return True

    @classmethod
    @AwSnapUtil.log_function(2)
    def execute_action(self, action):
        action_function_name = action["Action"].lower().strip().replace(" ", "_").replace("+", "_")

        # DISPLAY USERS NAME

        if hasattr(self, action_function_name):
            action_function = getattr(self, action_function_name)
        else:
            print(f"{action_function_name} does not exist as an available function")
            return True # TEMPOARY NEEDS CHANGED TO FALSE

        result = action_function()

        return result
    
    @classmethod
    @AwSnapUtil.log_function(3)
    def execute_actions(self):
        actions_executed = False
        if ValorantInfo.get_alive():
            for action in ActionsHandler.get_actions():
                result = Actions.execute_action(action)

                if result:
                    action["Fulfilled"] = 1
                    actions_executed = True
        
        return actions_executed

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

        actions_executed = Actions.execute_actions()
        
        if actions_executed or edit_made:
            ActionsHandler.save()

        time.sleep(TICK_SPEED)

if __name__ == '__main__':
    main()