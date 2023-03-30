import json
import boto3
import base64

def lambda_handler(event, context):
    
    instances = event['InstanceID']
    region = "us-east-1"
    ec2 = boto3.client('ec2', region_name=region)
    ec2.stop_instances(InstanceIds=instances)
    ##SNS Code

    snsclient = boto3.client('sns')
    response = snsclient.publish(
        TopicArn='arn:aws:sns:us-east-1:116060500502:atcsevents',
        Message= 'EC2 instance ' + instances + ' is above current budget and has been terminated.',
        Subject='New EC2 Terminated',
        MessageStructure='string',
    )