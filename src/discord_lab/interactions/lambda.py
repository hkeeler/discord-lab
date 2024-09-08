import json

from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError

from discord_lab.dice import *

DISCORD_PUBLIC_KEY='460f2fecfe0cbcea5df36ae25dfb0c974ad567ccf3e6f76d52323faad3a0b7a0'
DEV_MODE = False

def ping(req_body: dict) -> tuple[int,dict]:
    return 200, {'type':1}

# TODO: Improve exception handling
def slash_command(req_body: dict) -> tuple[int,dict]:
    die_mult_str: str = req_body['data']['options'][0]['value']
    try:
        die_mult = DieMultiplier.parse(die_mult_str)
        total, rolls = die_mult.roll()

        if len(rolls) == 1:
            content = f":{die_mult.type.name.lower()}_{total}:"
        else:
            rolls_str = '+'.join([f":{r.type.name.lower()}_{r.value}:" for r in rolls])
            
            #content = f'## {total}\n{die_mult_str.upper()}: {rolls_str}'
            content = f"# {rolls_str}= {total}"
    except DieParseException as dpe:
        content = f'### ???\n{dpe}'

    res_data = {
        'type':4,
        'data': {
            'content': content
        }
    }

    return 200, res_data

interaction_type_dispatch={
    1:ping,
    2:slash_command
}


def handler(event, context):
    print(event)
    req_body_str = event['body']
    print(req_body_str)

    req_body = json.loads(req_body_str)

    if not DEV_MODE:
        try:
            headers = event['headers']
            signature = headers["x-signature-ed25519"]
            timestamp = headers["x-signature-timestamp"]

            verify_key = VerifyKey(bytes.fromhex(DISCORD_PUBLIC_KEY))
            verify_key.verify(f'{timestamp}{req_body_str}'.encode(), bytes.fromhex(signature))
        except BadSignatureError:
            print('WARN: Request failed signature verification')
            return {
                'statusCode': 401,
                'body': 'invalid request signature'
            }

    interaction_type = req_body['type']
    res_code, res_body = interaction_type_dispatch[interaction_type](req_body)
    res_body_str = json.dumps(res_body)
    print(res_body_str)

    return {
        'statusCode': res_code,
        'body': res_body_str
    }
