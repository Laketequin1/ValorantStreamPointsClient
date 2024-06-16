import requests
import getpass
import json

import AwSnapUtil
AwSnapUtil.show_verbose = False

ACTIONS_FILE = "actions.json"

def complete_action(action):
    return True

def get_actions():
    with open(ACTIONS_FILE, "r") as file:
        return json.load(file)

@AwSnapUtil.log_function
def save_actions(actions):
    with open(ACTIONS_FILE, "w") as file:
        json.dump(actions, file, indent=4)

def merge_actions(actions, new_actions):
    if new_actions == None or not len(new_actions):
        return actions

    prev_actions = list(actions)
    existing_keys = {item["ActionID"] for item in actions}

    for new_action in new_actions:
        new_action_id = new_action.get("ActionID")
        if new_action_id is not None and new_action_id not in existing_keys:
            new_action["Fulfilled"] = 0
            actions.append(new_action)
            existing_keys.add(new_action_id)

    if prev_actions != actions:
        save_actions(actions)
        
    return actions

@AwSnapUtil.log_function
def remove_actions(actions, fulfilled_action_ids):
    keep_actions = [action for action in actions if action.get("ActionID") not in fulfilled_action_ids]

    if len(keep_actions) != len(actions):
        save_actions(keep_actions)

    return keep_actions

@AwSnapUtil.log_function
def get_fulfilled_action_ids(actions):
    fulfilled_actions = []
    
    for action in actions:
        fulfillment = action.get("Fulfilled")
        if fulfillment == 1:
            action_id = action.get("ActionID")
            fulfilled_actions.append(action_id)

    return fulfilled_actions

def main():
    actions = get_actions()

    url = 'https://projectspace.nz/wrkvaxxi/ValorantStreamPoints/post/get_actions.php'
    password = getpass.getpass('Enter password: ')

    fulfilled_action_ids = get_fulfilled_action_ids(actions)

    # Data to be sent in the POST request
    body_data = {
        'password': password,
        'fulfilled_actions': str(fulfilled_action_ids)
    }

    response = requests.post(url, data=body_data)
    
    if response.status_code == 200:
        actions = remove_actions(actions, fulfilled_action_ids)
    
    new_actions = AwSnapUtil.eval_message(response.text)

    actions = merge_actions(actions, new_actions)

    actions_edited = False
    for action in actions:
        result = complete_action(action)

        if result:
            action["Fulfilled"] = 1
            actions_edited = True
    
    if actions_edited:
        save_actions(actions)    

if __name__ == '__main__':
    main()