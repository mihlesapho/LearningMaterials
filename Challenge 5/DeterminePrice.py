import json
import requests
import boto3
import base64
from decimal import Decimal
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    
    #Secrete manager code starts here
    
    secret_name = "Infracost_Key"
    region_name = "us-east-1"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    # In this sample we only handle the specific exceptions for the 'GetSecretValue' API.
    # See https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
    # We rethrow the exception by default.

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'DecryptionFailureException':
            # Secrets Manager can't decrypt the protected secret text using the provided KMS key.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InternalServiceErrorException':
            # An error occurred on the server side.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            # You provided an invalid value for a parameter.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            # You provided a parameter value that is not valid for the current state of the resource.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'ResourceNotFoundException':
            # We can't find the resource that you asked for.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
    else:
        # Decrypts secret using the associated KMS key.
        # Depending on whether the secret is a string or binary, one of these fields will be populated.
        if 'SecretString' in get_secret_value_response:
            secret = get_secret_value_response['SecretString']
        else:
            decoded_binary_secret = base64.b64decode(get_secret_value_response['SecretBinary'])
   
    # Secret manager code ends here
     
    # My Code       
    
    APIKey1 = secret ##Infracost API key
    record = event['Records'][0] #Message from SQS
    payload = json.loads(record['body'])
    ec2InstanceType = payload['detail']['requestParameters']['instanceType']
    ec2InstanceID = payload['detail']['responseElements']['instancesSet']['items'][0]['instanceId']

    headers = {
        'X-Api-Key': APIKey1,
        # Already added when you pass json= but not when you pass data=
        # 'Content-Type': 'application/json',
    }
    
    json_data = {
        'query': '{products(filter: {vendorName: "aws", service: "AmazonEC2", region: "us-east-1", attributeFilters: [{key: "instanceType", value: "'+ ec2InstanceType +'"}, {key: "operatingSystem", value: "Linux"}, {key: "tenancy", value: "Shared"}, {key: "capacitystatus", value: "Used"}, {key: "preInstalledSw", value: "NA"}]}) { prices(filter: {purchaseOption: "on_demand"}) { USD } } } ',
    }
    
    response = requests.post('https://pricing.api.infracost.io/graphql', headers=headers, json=json_data)
    
    responseObj = json.dumps(response.text)
   
    pricing = responseObj[50:61:1]
    OverPrice = False
    
    if(Decimal(pricing)>=0.1):
        OverPrice = True
        
    result = {
        "InstanceID": ec2InstanceID,
        "Price" : pricing,
        "OverPrice": OverPrice
    }
    
    print("###THis is the instanceID to be terminated or not###")
    print(result['InstanceID'])
    
    print("###THis is the pricing of instance to be terminated or not###")
    print(result['Price'])

    print("###THis indicates if the spun up instance is over budget or not")
    print(result['OverPrice'])
        
    return result
