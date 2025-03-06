import os

import requests

from discord_lab.interactions import env
from discord_lab.interactions.auth import get_oauth2_access_token
from discord_lab.dice import DieExprMultiRollType

API_URL_BASE='https://discord.com/api/v10'
INTERACTION_SCOPES=[
    'applications.commands',
    'applications.commands.update'
]

def list_global_app_cmds(app_id):
    endpoint = f'{API_URL_BASE}/applications/{app_id}/commands'

    access_token = get_oauth2_access_token(INTERACTION_SCOPES)

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

    access_token = get_oauth2_access_token(INTERACTION_SCOPES)

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

    access_token = get_oauth2_access_token(INTERACTION_SCOPES)

    req_headers = {
        'Authorization': f'Bearer {access_token}'
    }

    res = requests.delete(endpoint, headers=req_headers)

    if res.status_code != 204:
        res_data = res.json()
        raise RuntimeError(f'Failed to authenticate: {res_data}')


app_id = env.DISCORD_APP_ID

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
        },
        {
            'type': 3,
            'name': 'multi-roll',
            'description': "Take best/worst of multiple rolls. Use for advantage/disadvantage.",
            'required': False,
            'choices': [
                {
                    "name": "Best / Advantage",
                    "value": DieExprMultiRollType.BEST.name
                },
                {
                    "name": "Worst / Disadvantage",
                    "value": DieExprMultiRollType.WORST.name
                },
            ],
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
            'type': 4,
            'name': 'must-beat',
            'description': "Must beat?",
            'required': False,
            'min_value': 1,
            'max_value': 100
        },
        {
            'type': 3,
            'name': 'message-text',
            'description': "Message text",
            'required': False,
            'min_length': 5,
            'max_length': 100
        },
        {
            'type': 11,
            'name': 'message-image',
            'description': "Message image",
            'required': False,
        },
        {
            'type': 3,
            'name': 'success-text',
            'description': "Success text",
            'required': False,
            'min_value': 3,
            'max_value': 100
        },
        {
            'type': 11,
            'name': 'success-image',
            'description': "Success image",
            'required': False,
        },
        {
            'type': 3,
            'name': 'failure-text',
            'description': "Failure text",
            'required': False,
            'min_value': 3,
            'max_value': 100
        },
        {
            'type': 11,
            'name': 'failure-image',
            'description': "Failure image",
            'required': False,
        },
    ]
}
sync_global_app_cmd(app_id, askroll_cmd)