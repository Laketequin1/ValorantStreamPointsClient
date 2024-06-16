import requests
import getpass
import json

import AwSnapUtil

ACTIONS_FILE = "actions.json"

def complete_action(action):
    return True

def merge_actions(actions, new_actions):
    existing_keys = {item["ActionID"] for item in actions}

    for new_action in new_actions:
        new_action_id = new_action.get("ActionID")
        if new_action_id is not None and new_action_id not in existing_keys:
            new_action["Fulfilled"] = 0
            actions.append(new_action)
            existing_keys.add(new_action_id)
    
    return actions

def get_actions():
    with open(ACTIONS_FILE, "r") as file:
        return json.load(file)

def save_actions(actions):
    with open(ACTIONS_FILE, "w") as file:
        json.dump(actions, file, indent=4)

def update_actions(actions, new_actions):
    if new_actions == None or not len(new_actions):
        return actions

    prev_actions = list(actions)
    actions = merge_actions(actions, new_actions)

    if prev_actions != actions:
        save_actions(actions)
        
    return actions

def remove_actions():
    

def get_fulfilled_actions(actions):
    fulfilled_actions = []
    
    for action in actions:
        action_id = action.get("ActionID")
        if action_id == 1:
            fulfilled_actions.append(action_id)

    return fulfilled_actions

def main():
    actions = get_actions()

    url = 'https://projectspace.nz/wrkvaxxi/ValorantStreamPoints/post/get_actions.php'
    password = getpass.getpass('Enter password: ')

    fulfilled_actions = get_fulfilled_actions(actions)

    # Data to be sent in the POST request
    body_data = {
        'password': password,
        'fulfilled_actions': str(fulfilled_actions)
    }

    # Sending POST request and capturing the response
    response = requests.post(url, data=body_data)
    
    remove_actions(fulfilled_actions)
    
    new_actions = AwSnapUtil.eval_message(response.text)

    actions = update_actions(actions, new_actions)

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