import os

import requests
from requests import Response
from requests.auth import HTTPBasicAuth

API_URL_BASE='https://discord.com/api/v10'
INTERACTION_SCOPES=[
    'applications.commands',
    'applications.commands.update'
]


def get_access_token(scopes: list[str]) -> str:
    endpoint = f'{API_URL_BASE}/oauth2/token'

    client_id = os.environ.get('DISCORD_APP_ID', None)
    client_secret = os.environ.get('DISCORD_CLIENT_SECRET', None)

    if not (client_id and client_secret):
        raise RuntimeError('DISCORD_APP_ID and/or DISCORD_CLIENT_SECRET envvars not set.')

    req_auth = HTTPBasicAuth(client_id, client_secret)

    req_data = {
        'grant_type': 'client_credentials',
        'scope': ' '.join(scopes)
    }

    req_headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    res: Response = requests.post(endpoint, auth=req_auth, headers=req_headers, data=req_data)
    res_data = res.json()

    if res.status_code != requests.codes.ok:
        raise RuntimeError(f'Failed to authenticate: {res_data}')

    return res_data['access_token']


def list_global_app_cmds(app_id):
    endpoint = f'{API_URL_BASE}/applications/{app_id}/commands'

    access_token = get_access_token(INTERACTION_SCOPES)

    req_headers = {
        'Authorization': f'Bearer {access_token}'
    }

    res = requests.get(endpoint, headers=req_headers)
    res_data = res.json()

    if res.status_code != 200:
        raise RuntimeError(f'Could not get global app commands: {res_data}')

    return res_data


def get_global_app_cmd(app_id, cmd_name:str):
    cmds = list_global_app_cmds(app_id)
    cmd = [c for c in cmds if c['name'] == cmd_name][0]

    return cmd


def sync_global_app_cmd(app_id: str, cmd_json: dict):
    endpoint = f'{API_URL_BASE}/applications/{app_id}/commands'

    access_token = get_access_token(INTERACTION_SCOPES)

    req_headers = {
        'Authorization': f'Bearer {access_token}'
    }

    res = requests.post(endpoint, headers=req_headers, json=cmd_json)
    res_data = res.json()

    if res.status_code not in [200,201]:
        raise RuntimeError(f'Could not sync global app commands: {res_data}')
    
    return res_data


def delete_global_app_cmd(app_id: str, cmd_name: str):
    cmd = get_global_app_cmd(app_id, cmd_name)
    cmd_id = cmd['id']

    endpoint = f'{API_URL_BASE}/applications/{app_id}/commands/{cmd_id}'

    access_token = get_access_token(INTERACTION_SCOPES)

    req_headers = {
        'Authorization': f'Bearer {access_token}'
    }

    res = requests.delete(endpoint, headers=req_headers)

    if res.status_code != 204:
        res_data = res.json()
        raise RuntimeError(f'Failed to authenticate: {res_data}')


app_id = os.environ['DISCORD_APP_ID']

# `/roll` command
roll_cmd = {
    'name': 'roll',
    'description': "Let's roll some dice!",
    'options': [
        {
            'type': 3,
            'name': 'dice',
            'description': "Dice expression",
            'required': True,
            'min_length': 2,
            'max_length': 100
        }
    ]
}
sync_global_app_cmd(app_id, roll_cmd)


# `/askroll` command
askroll_cmd = {
    'name': 'askroll',
    'description': "Ask someone to roll some dice!",
    'options': [
        {
            'type': 6,
            'name': 'user',
            'description': "User",
            'required': True
        },
        {
            'type': 3,
            'name': 'dice',
            'description': "Dice expression",
            'required': True,
            'min_length': 2,
            'max_length': 100
        },
        {
            'type': 3,
            'name': 'description',
            'description': "Description",
            'required': False,
            'min_length': 5,
            'max_length': 100
        },
        {
            'type': 4,
            'name': 'must-beat',
            'description': "Must beat?",
            'required': False,
            'min_value': 1,
            'max_value': 100
        }
    ]
}
sync_global_app_cmd(app_id, askroll_cmd)