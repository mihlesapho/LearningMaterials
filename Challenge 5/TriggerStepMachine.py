import json
import boto3

def lambda_handler(event, context):

    client = boto3.client('stepfunctions')
    print("Attempting to start State Machine")
    response = client.start_execution(
        stateMachineArn='aws:states:.......',
        input= json.dumps(event)
    )
    print(response)