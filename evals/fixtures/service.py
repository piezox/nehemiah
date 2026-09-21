import json
import urllib.request


def fetch_users(base_url, ids):
    users = []
    for user_id in ids:
        with urllib.request.urlopen(f"{base_url}/users/{user_id}") as resp:
            users.append(json.load(resp))
    return users
