import random, string, time
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
    
    # After a table gets created there's a small window we must wait before sending requests.
    print("Create Table Request submitted. Sleeping for 20s for completion...")
    time.sleep(20)

except botocore.exceptions.ClientError as error:
    if error.response['Error']['Code'] == 'ResourceInUseException':
       print("Table already exists. Moving on!")

print("Ingestion begins...")
table = dynamodb.Table(TABLE_NAME)

count = 0
requests = []

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

    if len(requests) >= 20:
        response = dynamodb.batch_write_item(
                RequestItems={
                    TABLE_NAME: requests
                    }
                )
        requests = []
    requests.append({ 'PutRequest': { 'Item': d } })

    # table.put_item(Item=d)
    if key % 10000 == 0:
        count+= 1
        print(f"Ingested {key} records")
    # print(table.get_item(Key={'id': key})['Item'])


