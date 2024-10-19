from os import environ

DISCORD_API_URL_BASE='https://discord.com/api/v10'

try:
    # App settings
    DISCORD_APP_ID = environ['DISCORD_APP_ID']
    DISCORD_APP_PUBLIC_KEY = environ['DISCORD_APP_PUBLIC_KEY']
    DISCORD_APP_BOT_AUTH_TOKEN = environ['DISCORD_APP_BOT_AUTH_TOKEN']

    # Auth settings
    DISCORD_OAUTH2_TOKEN_URL = 'https://discord.com/api/v10/oauth2/token'
    DISCORD_OAUTH2_CLIENT_ID = DISCORD_APP_ID
    DISCORD_OAUTH2_CLIENT_SECRET = environ['DISCORD_OAUTH2_CLIENT_SECRET']
except KeyError:
    raise RuntimeError('One or more envvars not set: DISCORD_APP_ID, DISCORD_APP_PUBLIC_KEY, DISCORD_APP_BOT_AUTH_TOKEN, DISCORD_OAUTH2_CLIENT_SECRET')
