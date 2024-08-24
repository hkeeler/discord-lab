import json

from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError

DISCORD_PUBLIC_KEY='460f2fecfe0cbcea5df36ae25dfb0c974ad567ccf3e6f76d52323faad3a0b7a0'

def handler(event, context):
    print(event)
    body = event.get('body', None)
    headers = event['headers']

    verify_key = VerifyKey(bytes.fromhex(DISCORD_PUBLIC_KEY))

    signature = headers["X-Signature-Ed25519"]
    timestamp = headers["X-Signature-Timestamp"]

    response_code = 200
    response_body = json.dumps( {'type': 1} )

    try:
        verify_key.verify(f'{timestamp}{body}'.encode(), bytes.fromhex(signature))
    except BadSignatureError:
        response_code = 401
        response_body = 'invalid request signature'

    return {
        'statusCode': response_code,
        'body': response_body
    }
