import requests
import getpass
import json
import pygetwindow
import time

import AwSnapUtil
AwSnapUtil.show_verbose = True

ACTIONS_FILE = "actions.json"
VALORANT_TITLE = "VALORANT"

def get_focused_window() -> str:
    return pygetwindow.getActiveWindow().title

def get_ingame() -> bool:
    if (get_focused_window().upper() == VALORANT_TITLE):
        # TODO check if in the game
        return True
    return False

def get_alive() -> bool:
    if (get_ingame()):
        # TODO check if alive
        return True
    return False

print(AwSnapUtil.get_pixel_colour(20, 20))
print(get_focused_window())
exit()

class ItemActions:
    @staticmethod
    def do_something(cls):
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
    @AwSnapUtil.log_function
    def get_fulfilled_action_ids(cls):
        fulfilled_actions = []
        
        for action in cls.actions:
            fulfillment = action.get("Fulfilled")
            if fulfillment == 1:
                action_id = action.get("ActionID")
                fulfilled_actions.append(action_id)

        return fulfilled_actions

    @classmethod
    @AwSnapUtil.log_function
    def save(cls):
        with open(ACTIONS_FILE, "w") as file:
            json.dump(cls.actions, file, indent=4)

    @classmethod
    def merge_new(cls, new_actions):
        if new_actions is None or not len(new_actions):
            return

        existing_keys = {item["ActionID"] for item in cls.actions}

        for new_action in new_actions:
            new_action_id = new_action.get("ActionID")
            if new_action_id is not None and new_action_id not in existing_keys:
                new_action["Fulfilled"] = 0
                cls.actions.append(new_action)
                existing_keys.add(new_action_id)

    @classmethod
    @AwSnapUtil.log_function
    def remove(cls, fulfilled_action_ids):
        keep_actions = [action for action in cls.actions if action.get("ActionID") not in fulfilled_action_ids]

        if len(keep_actions) != len(cls.actions):
            cls.actions = keep_actions
            cls.save()

def main():
    ActionsHandler.get_saved()

    url = 'https://projectspace.nz/wrkvaxxi/ValorantStreamPoints/post/get_actions.php'
    password = getpass.getpass('Enter password: ')

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

    ActionsHandler.merge_new(new_actions)

    actions_edited = False
    for action in ActionsHandler.get_actions():
        result = ItemActions.do_something(action)

        if result:
            action["Fulfilled"] = 1
            actions_edited = True
    
    if actions_edited:
        ActionsHandler.save()

if __name__ == '__main__':
    main()