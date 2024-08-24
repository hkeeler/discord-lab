import json

def handler(event, context):
    print(event)
    body = event.get('body', None)
    if body:
        print(body)
    else:
        print('no body')
    return {
        'statusCode': 200,
        'body': json.dumps(
            {'type': 1}
        )
    }
