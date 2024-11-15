import requests as r
from requests.auth import HTTPBasicAuth

from discord_lab.interactions.env import DISCORD_OAUTH2_TOKEN_URL, DISCORD_OAUTH2_CLIENT_ID, DISCORD_OAUTH2_CLIENT_SECRET, DISCORD_APP_BOT_AUTH_TOKEN

def get_oauth2_access_token(scopes: list[str]) -> str:

    req_auth = HTTPBasicAuth(DISCORD_OAUTH2_CLIENT_ID, DISCORD_OAUTH2_CLIENT_SECRET)

    req_data = {
        'grant_type': 'client_credentials',
        'scope': ' '.join(scopes)
    }

    req_headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    res: r.Response = r.post(DISCORD_OAUTH2_TOKEN_URL, auth=req_auth, headers=req_headers, data=req_data)
    res_data = res.json()

    if res.status_code != r.codes.ok:
        raise RuntimeError(f'Failed to authenticate: {res_data}')

    return res_data['access_token']


def get_oauth2_authn_header(scopes: list[str]) -> str:
    token = get_oauth2_access_token(scopes)

    return f"Bearer {token}"


def get_bot_auth_token() -> str:
    return DISCORD_APP_BOT_AUTH_TOKEN


def get_bot_auth_token_authn_header() -> str:
    return f"Bot {DISCORD_APP_BOT_AUTH_TOKEN}"