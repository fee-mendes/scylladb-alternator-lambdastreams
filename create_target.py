import random, string, sys
import boto3, botocore

if len(sys.argv) > 1:
    ALTERNATOR_ENDPOINT = sys.argv[1]
else:
    ALTERNATOR_ENDPOINT = 'http://alternator:8080'


TABLE_NAME = 'dest'

dynamodb = boto3.resource('dynamodb',endpoint_url=ALTERNATOR_ENDPOINT,
                  region_name='None', aws_access_key_id='None', aws_secret_access_key='None')

dynamodb.create_table(
    AttributeDefinitions=[
    {
        'AttributeName': 'id',
        'AttributeType': 'N'
    },
    ],
    BillingMode='PAY_PER_REQUEST',
    TableName=TABLE_NAME,
    KeySchema=[
    {
        'AttributeName': 'id',
        'KeyType': 'HASH'
    },
    ])

print("Table successfully created")

