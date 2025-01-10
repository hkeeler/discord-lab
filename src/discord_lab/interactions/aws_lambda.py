import json
from typing import Any

from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError

import boto3

import requests

from discord_lab.dice import *
from discord_lab.interactions.env import *

DEV_MODE = False

EMOJI_ID_BY_CODE = {
    'D4_1':'<:d4_1:1282216833335955467>',
    'D4_2':'<:d4_2:1282216846401208331>',
    'D4_3':'<:d4_3:1282216862834495520>',
    'D4_4':'<:d4_4:1282216878072135720>',
    'D6_1':'<:d6_1:1282212244398276640>',
    'D6_2':'<:d6_2:1282212258780418158>',
    'D6_3':'<:d6_3:1282212272265232448>',
    'D6_4':'<:d6_4:1282212289310621717>',
    'D6_5':'<:d6_5:1282212308982169653>',
    'D6_6':'<:d6_6:1282212638297817198>',
    'D8_8':'<:d8_8:1282224447620776058>',
    'D8_7':'<:d8_7:1282224433448091659>',
    'D8_6':'<:d8_6:1282224414439641119>',
    'D8_5':'<:d8_5:1282224400380203008>',
    'D8_4':'<:d8_4:1282224384655757396>',
    'D8_3':'<:d8_3:1282224372081233981>',
    'D8_2':'<:d8_2:1282224356134617098>',
    'D8_1':'<:d8_1:1282224323486023731>',
    'D10_10':'<:d10_10:1282232213064253440>',
    'D10_9':'<:d10_9:1282232197952045119>',
    'D10_8':'<:d10_8:1282232181506183198>',
    'D10_7':'<:d10_7:1282232165744246804>',
    'D10_6':'<:d10_6:1282232150413803540>',
    'D10_5':'<:d10_5:1282232135176159284>',
    'D10_4':'<:d10_4:1282232120257019926>',
    'D10_3':'<:d10_3:1282232104855408701>',
    'D10_2':'<:d10_2:1282232090938708035>',
    'D10_1':'<:d10_1:1282232071707824140>',
    'D10_0':'<:d10_0:1282479588311830629>',
    'D10_00':'<:d10_00:1282474745606049865>',
    'D10_90':'<:d10_90:1282474994336796692>',
    'D10_80':'<:d10_80:1282474906071728158>',
    'D10_70':'<:d10_70:1282474883162574919>',
    'D10_60':'<:d10_60:1282474867303907361>',
    'D10_50':'<:d10_50:1282474851503706157>',
    'D10_40':'<:d10_40:1282474836551139380>',
    'D10_30':'<:d10_30:1282474822055624776>',
    'D10_20':'<:d10_20:1282474763754803240>',
    'D12_12':'<:d12_12:1282232530807951421>',
    'D12_11':'<:d12_11:1282232516375478346>',
    'D12_10':'<:d12_10:1282232497718951968>',
    'D12_9':'<:d12_9:1282232461941669888>',
    'D12_8':'<:d12_8:1282232418627227689>',
    'D12_7':'<:d12_7:1282232395625664553>',
    'D12_6':'<:d12_6:1282232379829780520>',
    'D12_5':'<:d12_5:1282232364835016704>',
    'D12_4':'<:d12_4:1282232349295247360>',
    'D12_3':'<:d12_3:1282232328462270485>',
    'D12_2':'<:d12_2:1282232312729305119>',
    'D12_1':'<:d12_1:1282232295973195787>',
    'D20_20':'<:d20_20:1282233169256382545>',
    'D20_19':'<:d20_19:1282233139774623805>',
    'D20_18':'<:d20_18:1282233124310356069>',
    'D20_17':'<:d20_17:1282233108376059914>',
    'D20_16':'<:d20_16:1282233092240703539>',
    'D20_15':'<:d20_15:1282233077233615000>',
    'D20_14':'<:d20_14:1282233060858789888>',
    'D20_13':'<:d20_13:1282233045105119242>',
    'D20_12':'<:d20_12:1282232901949198409>',
    'D20_11':'<:d20_11:1282232844088774707>',
    'D20_10':'<:d20_10:1282232824602034249>',
    'D20_9':'<:d20_9:1282232803181723740>',
    'D20_8':'<:d20_8:1282232786778066946>',
    'D20_7':'<:d20_7:1282232770705358869>',
    'D20_6':'<:d20_6:1282232755173855294>',
    'D20_5':'<:d20_5:1282232739386363935>',
    'D20_4':'<:d20_4:1282232728754061323>',
    'D20_3':'<:d20_3:1282232708482863115>',
    'D20_2':'<:d20_2:1282232694108979221>',
    'D20_1':'<:d20_1:1282232679512805467>',
}

dynamodb_client = boto3.client('dynamodb')

def die_roll_to_md(roll: DieRoll) -> str:
    if roll.type == DieType.D100:       
        if roll.value == 100:
            tens_emoji_id = EMOJI_ID_BY_CODE["D10_00"]
            ones_emoji_id = EMOJI_ID_BY_CODE["D10_0"]
        else:
            tens_val, ones_val = divmod(roll.value, 10)
            tens_val *= 10

            tens_emoji_id = EMOJI_ID_BY_CODE[f"D10_{tens_val}"] if tens_val else EMOJI_ID_BY_CODE["D10_00"]
            ones_emoji_id = EMOJI_ID_BY_CODE[f"D10_{ones_val}"]

        md = tens_emoji_id + ones_emoji_id

    else:
        md = EMOJI_ID_BY_CODE[f"{roll.type.name}_{roll.value}"]

    return md


def render_single_die_roll(roll: DieRoll) -> str:
    return die_roll_to_md(roll)


def render_multidie_roll(rolls: MultiDieRoll, include_total: bool) -> str:
    roll_details = rolls.details
    if len(roll_details) == 1:
        return render_single_die_roll(roll_details[0])
    else:
        die_md = ' '.join([die_roll_to_md(roll) for roll in rolls.details])
        if include_total:
            die_md += f' {rolls.value}'
        return die_md



def render_expr_roll(die_expr_str: str, rolls: DieExprRoll, include_total: bool) -> str:
    roll_results = rolls.results

    # If only a single die is rolled, just show that roll without the math bits
    # TODO: Move this one-off logic to its own function
    if len(roll_results) == 1:
        single_result = roll_results[0]

        match single_result:
            case MultiDieTermOperationResult():
                single_roll_details = single_result.rolls.details
                if len(single_roll_details) == 1:
                    return render_single_die_roll(single_roll_details[0])

    rr_mds = []

    for rr in roll_results:        
        match rr:
            case IntTermOperationResult():
                rr_md = str(rr.value)
            case MultiDieTermOperationResult():
                include_subtotals = len(roll_results) > 1
                rr_md = render_multidie_roll(rr.rolls, include_subtotals)

        op_symbol = rr.term_op.operation.value
        if op_symbol:
            rr_md = f"{op_symbol} {rr_md}"

        label = rr.term_op.labeled_term.label
        if label:
            rr_md += f" ({label})"

        rr_mds.append(rr_md)

    md = " ".join(rr_mds)

    if include_total:
         md += f"\n# {rolls.value}"

    return md


def option_name_to_value(req_body: dict, option_name: str, required: bool = True) -> Any:
    try:
        for option in req_body['data']['options']:
            if option['name'] == option_name:
                return option['value']            
    except KeyError:
        raise ValueError(f"Invalid slash command request format. Could not retrieve option: {option_name}")

    if required:
        raise ValueError(f"Required option not in request: {option_name}")
    else:
        return None


def embed_field_to_value(embeds: list[dict], field_name, required: bool = True) -> Any:
    for embed in embeds:
        if embed['name'] == field_name:
            return embed['value']            
        
    if required:
        raise ValueError(f"Required embed field not present: {field_name}")
    else:
        return None


def get_interaction_message(interaction_token: str) -> dict:
    message_url = f'{DISCORD_API_URL_BASE}/webhooks/{DISCORD_APP_ID}/{interaction_token}/messages/@original'

    orig_msg_resp = requests.get(message_url)
    orig_msg = orig_msg_resp.json()
    orig_msg_resp.raise_for_status()

    return orig_msg


def roll_cmd(req_body: dict) -> tuple[int,dict]:
    die_expr_str = option_name_to_value(req_body, 'dice')
    try:
        die_expr_roll = DieExpr.parse(die_expr_str).roll()
        content = render_expr_roll(die_expr_str, die_expr_roll, True)
    except DieParseException as dpe:
        content = f'# ???\n{dpe}'

    res_data = {
        'type':4,
        'data': {
            'content': content
        }
    }

    return 200, res_data


def askroll_cmd(req_body: dict) -> tuple[int,dict]:
    interaction_id = req_body['id']
    from_user_id = req_body['member']['user']['id']
    to_user_id = option_name_to_value(req_body, 'user')
    die_expr_str = option_name_to_value(req_body, 'dice')
    roll_desc = option_name_to_value(req_body, 'description', False)
    must_beat = option_name_to_value(req_body, 'must-beat', False)
    success_message = option_name_to_value(req_body, 'success-message', False)
    failure_message = option_name_to_value(req_body, 'failure-message', False)

    fields = [
        { "name": "Roller", "value": f"<@{to_user_id}>", "inline": True},
        { "name": "Dice", "value": die_expr_str, "inline": True},
    ]

    if must_beat:
        fields.append({"name": "Must Beat", "value": must_beat, "inline": True})

    res_data = {
        'type': 4,
        'data': {
            'embeds': [
                {
                    "description": roll_desc,
                    "color": 9807270, # Grey
                    "fields": fields,
                }
            ],
            'components': [
                {
                    'type': 1,
                    'components': [
                        {
                            'type': 2, # Button
                            'label': 'Roll!',
                            'style': 1, # Primary
                            'custom_id': 'roll_click'
                        },
                        {
                            'type': 2, # Button
                            'label': 'Adjust',
                            'style': 2, # Secondary
                            'custom_id': 'adjust_roll_click'
                        },
                    ]
                }
            ]
        }
    }

    dynamodb_item = {
        "interaction_id": {"N":  interaction_id},
        "from_user_id": {"N": from_user_id},
        "to_user_id": {"N": to_user_id},
        "die_expr": {"S": die_expr_str },
    }

    if roll_desc:
        dynamodb_item['roll_desc'] = {"S": roll_desc }

    if must_beat:
        dynamodb_item['must_beat'] = {"N": str(must_beat) }

    if success_message:
        dynamodb_item['success_message'] = {"S": success_message }

    if failure_message:
        dynamodb_item['failure_message'] = {"S": failure_message }

    dynamodb_client.put_item(
        TableName="rollit-askroll-queue",
        Item=dynamodb_item,
    )

    return 200, res_data


def slash_command(req_body: dict) -> tuple[int,dict]:
    cmd_name = req_body['data']['name']

    return cmd_name_dispatch[cmd_name](req_body)


def roll_click(req_body: dict) -> tuple[int,dict]:
    embeds = req_body['message']['embeds']
    req_embed_fields = embeds[0]['fields']
    interaction_id = req_body['message']['interaction']['id']
    button_clicker_user_id = req_body['member']['user']['id']

    res_embed_color = embeds[0]['color']

    # Required options
    die_expr_str = embed_field_to_value(req_embed_fields, 'Dice')
    requested_roller_user_id = embed_field_to_value(req_embed_fields, 'Roller')

    # Optional options
    must_beat = embed_field_to_value(req_embed_fields, 'Must Beat', False)
    adjust_expr_str: str = embed_field_to_value(req_embed_fields, 'Adjustment', False) or ''

    # Get roll req data from db
    roll_req = dynamodb_client.get_item(
        TableName='rollit-askroll-queue',
        Key={
            'interaction_id': {
                'N': interaction_id,
            }
        },
        ConsistentRead=True
    )['Item']

    success_message = roll_req.get('success_message', {}).get('S', None)
    failure_message = roll_req.get('failure_message', {}).get('S', None)

    # NOTE: button_clicker_user_id is an int, which requested_player_user_id is of for form <@{int}>
    if button_clicker_user_id not in requested_roller_user_id:
        res_data = {
            'type': 4,
            'data': {
                'content': "Not yer roll, bruh!",
                'flags': 64 # Ephemeral
            }
        }

        return 200, res_data

    res_message = None

    try:
        # FIXME: Improve merge of two expr strings
        die_expr_with_adjust = f"{die_expr_str} {adjust_expr_str}"
        die_expr_roll = DieExpr.parse(die_expr_with_adjust).roll()
        result_md_no_total = render_expr_roll(die_expr_str, die_expr_roll, False)

        if must_beat:
            if die_expr_roll.value > int(must_beat):
                res_embed_color = 5763719 # Green
                res_message = success_message
            else:
                res_embed_color = 15548997 # Red
                res_message = failure_message

    except DieParseException as dpe:
        result_md_no_total = str(dpe)

    embeds.append(
        {
            "color": res_embed_color,
            "description": res_message,
            "fields": [
                { "name": "Result", "value": die_expr_roll.value, "inline": True},
                { "name": "Details", "value": result_md_no_total, "inline": True},
            ],
        }
    )

    res_data = {
        'type': 7, # UPDATE_MESSAGE
        'data': {
            'embeds': embeds,
            'components': [],
        }
    }

    return 200, res_data



def adjust_roll_click(req_body: dict) -> tuple[int,dict]:
    interaction_id = req_body['message']['interaction']['id']

    # TODO: Check to make sure user allowed to make adjustments
    button_clicker_user_id = req_body['member']['user']['id']

    # Get roll req data from db
    roll_req = dynamodb_client.get_item(
        TableName='rollit-askroll-queue',
        Key={
            'interaction_id': {
                'N': interaction_id,
            }
        },
        ConsistentRead=True
    )['Item']

    player_roll_adjust = roll_req.get('player_roll_adjust', {}).get('S', None)

    res_data = {
        'type': 9, # Modal
        'data': {
            "title": f"Adjust roll",
            "custom_id": "adjust_roll_save",
            "components": [
                {
                    "type": 1,
                    "components": [
                        {
                            "type": 4,
                            "custom_id": "adjust_roll_exp",
                            "label": "Roll expression",
                            "style": 1,
                            "min_length": 2,
                            "max_length": 100,
                            "placeholder": "Example: +2 (Bless) -1 (Wisdom)",
                            "required": True,
                            "value": player_roll_adjust
                        }
                    ]
                }
            ]
        }
    }

    return 200, res_data


# FIXME: Make this flexible enough to accomidate other commands/components
def message_component(req_body: dict) -> tuple[int,dict]:
    cmd_name = req_body['message']['interaction']['name']
    comp_id = req_body['data']['custom_id']

    if cmd_name == 'askroll':
        if comp_id == 'roll_click':
            return roll_click(req_body)
        if comp_id == 'adjust_roll_click':
            return adjust_roll_click(req_body)
        
    raise ValueError(f"Component `{comp_id}` not implemented for command `{cmd_name}`")


def adjust_roll_modal_submit(req_body: dict) -> tuple[int,dict]:
    message = req_body['message']
    embeds = message['embeds']
    components = message['components']
    req_embed_fields = embeds[0]['fields']
    interaction_id = req_body['message']['interaction']['id']
    player_roll_adjust = req_body['data']['components'][0]['components'][0]['value']

    dynamodb_client.update_item(
        TableName="rollit-askroll-queue",
        Key={
            'interaction_id': {
                'N': interaction_id,
            }
        },
        AttributeUpdates={
            'player_roll_adjust': {
                'Value': {
                    'S': player_roll_adjust,
                },
                'Action': 'PUT'
            }
        },
    )

    prev_adj_val = embed_field_to_value(req_embed_fields, 'Adjustment', False)

    if prev_adj_val:
        for field in req_embed_fields:
            if field['name'] == 'Adjustment':
                field['value'] = player_roll_adjust
    else:
        req_embed_fields.append(
            { "name": "Adjustment", "value": player_roll_adjust, "inline": True},
        )

    #res_data = {
    #    'type': 4,
    #    'data': {
    #        'content': f"**{player_roll_adjust}** set to `player_roll_adjust`. ",
    #        'flags': 64 # Ephemeral
    #    }
    #}

    res_data = {
        'type': 7, # UPDATE_MESSAGE
        'data': {
            'embeds': embeds,
            'components': components,
        }
    }

    return 200, res_data


def modal_submit(req_body: dict) -> tuple[int,dict]:
    cmd_name = req_body['message']['interaction']['name']
    comp_id = req_body['data']['custom_id']

    if cmd_name == 'askroll':
        if comp_id == 'adjust_roll_save':
            return adjust_roll_modal_submit(req_body)

    raise ValueError(f"Modal `{comp_id}` not implemented for command `{cmd_name}`")

    
def ping(req_body: dict) -> tuple[int,dict]:
    return 200, {'type':1}


cmd_name_dispatch={
    'roll':roll_cmd,
    'askroll':askroll_cmd
}

interaction_type_dispatch={
    1:ping,
    2:slash_command,
    3:message_component,
    5:modal_submit,
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

            verify_key = VerifyKey(bytes.fromhex(DISCORD_APP_PUBLIC_KEY))
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
