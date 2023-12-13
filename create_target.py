import random, string
import boto3, botocore


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

