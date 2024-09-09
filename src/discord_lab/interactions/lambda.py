import json

from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError

from discord_lab.dice import *

DISCORD_PUBLIC_KEY='460f2fecfe0cbcea5df36ae25dfb0c974ad567ccf3e6f76d52323faad3a0b7a0'
DEV_MODE = False

EMOJI_ID_BY_CODE = {
    'd4_1':'<:d4_1:1282216833335955467>',
    'd4_2':'<:d4_2:1282216846401208331>',
    'd4_3':'<:d4_3:1282216862834495520>',
    'd4_4':'<:d4_4:1282216878072135720>',
    'd6_1':'<:d6_1:1282212244398276640>',
    'd6_2':'<:d6_2:1282212258780418158>',
    'd6_3':'<:d6_3:1282212272265232448>',
    'd6_4':'<:d6_4:1282212289310621717>',
    'd6_5':'<:d6_5:1282212308982169653>',
    'd6_6':'<:d6_6:1282212638297817198>',
    'd8_8':'<:d8_8:1282224447620776058>',
    'd8_7':'<:d8_7:1282224433448091659>',
    'd8_6':'<:d8_6:1282224414439641119>',
    'd8_5':'<:d8_5:1282224400380203008>',
    'd8_4':'<:d8_4:1282224384655757396>',
    'd8_3':'<:d8_3:1282224372081233981>',
    'd8_2':'<:d8_2:1282224356134617098>',
    'd8_1':'<:d8_1:1282224323486023731>',
    'd10_10':'<:d10_10:1282232213064253440>',
    'd10_9':'<:d10_9:1282232197952045119>',
    'd10_8':'<:d10_8:1282232181506183198>',
    'd10_7':'<:d10_7:1282232165744246804>',
    'd10_6':'<:d10_6:1282232150413803540>',
    'd10_5':'<:d10_5:1282232135176159284>',
    'd10_4':'<:d10_4:1282232120257019926>',
    'd10_3':'<:d10_3:1282232104855408701>',
    'd10_2':'<:d10_2:1282232090938708035>',
    'd10_1':'<:d10_1:1282232071707824140>',
    'd10_0':'<:d10_0:1282479588311830629>',
    'd10_00':'<:d10_00:1282474745606049865>',
    'd10_90':'<:d10_90:1282474994336796692>',
    'd10_80':'<:d10_80:1282474906071728158>',
    'd10_70':'<:d10_70:1282474883162574919>',
    'd10_60':'<:d10_60:1282474867303907361>',
    'd10_50':'<:d10_50:1282474851503706157>',
    'd10_40':'<:d10_40:1282474836551139380>',
    'd10_30':'<:d10_30:1282474822055624776>',
    'd10_20':'<:d10_20:1282474763754803240>',
    'd12_12':'<:d12_12:1282232530807951421>',
    'd12_11':'<:d12_11:1282232516375478346>',
    'd12_10':'<:d12_10:1282232497718951968>',
    'd12_9':'<:d12_9:1282232461941669888>',
    'd12_8':'<:d12_8:1282232418627227689>',
    'd12_7':'<:d12_7:1282232395625664553>',
    'd12_6':'<:d12_6:1282232379829780520>',
    'd12_5':'<:d12_5:1282232364835016704>',
    'd12_4':'<:d12_4:1282232349295247360>',
    'd12_3':'<:d12_3:1282232328462270485>',
    'd12_2':'<:d12_2:1282232312729305119>',
    'd12_1':'<:d12_1:1282232295973195787>',
    'd20_20':'<:d20_20:1282233169256382545>',
    'd20_19':'<:d20_19:1282233139774623805>',
    'd20_18':'<:d20_18:1282233124310356069>',
    'd20_17':'<:d20_17:1282233108376059914>',
    'd20_16':'<:d20_16:1282233092240703539>',
    'd20_15':'<:d20_15:1282233077233615000>',
    'd20_14':'<:d20_14:1282233060858789888>',
    'd20_13':'<:d20_13:1282233045105119242>',
    'd20_12':'<:d20_12:1282232901949198409>',
    'd20_11':'<:d20_11:1282232844088774707>',
    'd20_10':'<:d20_10:1282232824602034249>',
    'd20_9':'<:d20_9:1282232803181723740>',
    'd20_8':'<:d20_8:1282232786778066946>',
    'd20_7':'<:d20_7:1282232770705358869>',
    'd20_6':'<:d20_6:1282232755173855294>',
    'd20_5':'<:d20_5:1282232739386363935>',
    'd20_4':'<:d20_4:1282232728754061323>',
    'd20_3':'<:d20_3:1282232708482863115>',
    'd20_2':'<:d20_2:1282232694108979221>',
    'd20_1':'<:d20_1:1282232679512805467>',
}

def ping(req_body: dict) -> tuple[int,dict]:
    return 200, {'type':1}

# TODO: Improve exception handling
def slash_command(req_body: dict) -> tuple[int,dict]:
    die_mult_str: str = req_body['data']['options'][0]['value']
    try:
        die_mult = DieMultiplier.parse(die_mult_str)
        die_type = die_mult.type
        total, rolls = die_mult.roll()

        print(f"die_mult_str: {die_mult_str}, die_type: {die_type}")

        if die_type == DieType.D100:
            emoji_pairs = []
            for roll in rolls:
                if roll.value == 100:
                    emoji_pairs.append((roll.value, EMOJI_ID_BY_CODE["d10_00"], EMOJI_ID_BY_CODE["d10_0"]))
                else:
                    tens_val, ones_val = divmod(roll.value, 10)
                    tens_val *= 10

                    tens_emoji_id = EMOJI_ID_BY_CODE[f"d10_{tens_val}"] if tens_val else EMOJI_ID_BY_CODE["d10_00"]
                    ones_emoji_id = EMOJI_ID_BY_CODE[f"d10_{ones_val}"]

                    emoji_pairs.append((roll.value, tens_emoji_id, ones_emoji_id))

            if len(emoji_pairs) == 1:
                ep = emoji_pairs[0]
                content = f"{ep[1]}{ep[2]} ({ep[0]})"
            else:
                rolls_str = ' '.join([f"{ep[1]}{ep[2]} ({ep[0]})" for ep in emoji_pairs])
                content = f"# {total}\n# {rolls_str}"
            
        else:
            emoji_ids = [
                EMOJI_ID_BY_CODE[f"{r.type.name.lower()}_{r.value}"] for r in rolls
            ]

            if len(emoji_ids) == 1:
                content = emoji_ids[0]
            else:
                rolls_str = ' '.join(emoji_ids)
                content = f"# {total}\n# {rolls_str}"
        
    except DieParseException as dpe:
        content = f'# ???\n{dpe}'

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
