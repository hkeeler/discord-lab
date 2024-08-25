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
    req_body_str = event['body']
    print(req_body_str)

    req_body = json.loads(req_body_str)

    interaction_type = req_body['type']

    headers = event['headers']

    res_code = 200
    res_body = {
        'type': INTERACTION_REQ_RES[interaction_type],
        'data': {
            'content': 'Like, I know, right!?'
        }
    }

    res_body_str = json.dumps(res_body)

    try:
        signature = headers["x-signature-ed25519"]
        timestamp = headers["x-signature-timestamp"]

        verify_key = VerifyKey(bytes.fromhex(DISCORD_PUBLIC_KEY))
        verify_key.verify(f'{timestamp}{req_body_str}'.encode(), bytes.fromhex(signature))
    except BadSignatureError:
        res_code = 401
        res_body_str = 'invalid request signature'

    return {
        'statusCode': res_code,
        'body': res_body_str
    }
