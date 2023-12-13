import random, string
import boto3, botocore


ALTERNATOR_ENDPOINT = 'http://alternator:8080'
SOURCE_TABLE_NAME = 'source'
TARGET_TABLE_NAME = 'dest'

alternator = boto3.resource('dynamodb',endpoint_url=ALTERNATOR_ENDPOINT,
                  region_name='None', aws_access_key_id='None', aws_secret_access_key='None')

dynamodb = boto3.resource('dynamodb')

ddb_table = dynamodb.Table(SOURCE_TABLE_NAME)
alternator_table = alternator.Table(TARGET_TABLE_NAME)

count = 0
mismatch = 0
for key in range(1, 10000+1):
    if key % 100 == 0:
        count+= 1
        print(f"Compared {key} records. {mismatch} mismatches found.")
    ddb_record = ddb_table.get_item(Key={'id': key})['Item']
    try:
        alternator_record = alternator_table.get_item(Key={'id': key})['Item']
        if ddb_record != alternator_record:
            mismatch+=1
            print("Mismatch found:")
            print(f"Source {ddb_record}")
            print(f"Target {alternator_record}")

    except:
        mismatch+=1
        print("Alternator record not found.")
        print(f"Source: {ddb_record}")



