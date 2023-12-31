import random, string
import boto3, botocore


TABLE_NAME = 'source'

# Not needed, but left here in case you want to test ingesting to Alternator directly.
# 
# dynamodb = boto3.resource('dynamodb',endpoint_url='http://localhost:8080',
#                  region_name='None', aws_access_key_id='None', aws_secret_access_key='None')

dynamodb = boto3.resource('dynamodb')

try:
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
except botocore.exceptions.ClientError as error:
    if error.response['Error']['Code'] == 'ResourceInUseException':
       print("Table already exists. Moving on!")

table = dynamodb.Table(TABLE_NAME)

count = 0
for key in range(1, int(5E4)+1):
    cols = ['id']
    for x in range(1, random.randrange(50)+1):
        cols.append('col_' + str(x))

    d = dict.fromkeys(cols)
    for x in d:
        d[x] = ''.join((random.choice(string.ascii_lowercase) for x in range(10)))

    d['id'] = key

    # for k, v in d.items():
    #   print(k, v)

    table.put_item(Item=d)
    if key % 10000 == 0:
        count+= 1
        print(f"Ingested {key} records")
    # print(table.get_item(Key={'id': key})['Item'])

