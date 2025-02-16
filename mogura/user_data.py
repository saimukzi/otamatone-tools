import json
import os

def get_user_data_path():
    ret = os.path.join(os.getenv('LOCALAPPDATA'), 'mogura', 'user_data.json')
    print(ret)
    return ret

def save_user_data(data):
    user_data_path = get_user_data_path()
    if not os.path.exists(os.path.dirname(user_data_path)):
        os.makedirs(os.path.dirname(user_data_path))
    with open(user_data_path, 'w') as f:
        json.dump(data, f, sort_keys=True, indent=2)

def load_user_data():
    user_data_path = get_user_data_path()
    if not os.path.exists(user_data_path):
        return None
    with open(get_user_data_path(), 'r') as f:
        return json.load(f)
