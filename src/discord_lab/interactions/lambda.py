import json

from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError

DISCORD_PUBLIC_KEY='460f2fecfe0cbcea5df36ae25dfb0c974ad567ccf3e6f76d52323faad3a0b7a0'

INTERACTION_REQ_RES={
    1:1, # PING -> PONG
    2:4  # APPLICATION_COMMAND -> CHANNEL_MESSAGE_WITH_SOURCE
}

def handler(event, context):
    print(event)
    body = event['body']
    print(body)

    interaction_type = body['type']

    headers = event['headers']

    verify_key = VerifyKey(bytes.fromhex(DISCORD_PUBLIC_KEY))

    signature = headers["x-signature-ed25519"]
    timestamp = headers["x-signature-timestamp"]

    response_code = 200
    response_message = {
        'type': INTERACTION_REQ_RES[interaction_type],
        'content': 'Like, I know, right!?'
    }
    response_body = json.dumps(response_message)

    try:
        verify_key.verify(f'{timestamp}{body}'.encode(), bytes.fromhex(signature))
    except BadSignatureError:
        response_code = 401
        response_body = 'invalid request signature'

    return {
        'statusCode': response_code,
        'body': response_body
    }
