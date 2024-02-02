# Restore from S3 bucket to DynamoDB table
# customize the settings here and run: python3 load.py

# Originally from https://github.com/aws-samples/aws-dynamodb-examples/tree/master/LoadS3toDynamoDB
# Adapted to work with ScyllaDB

import boto3
from botocore.exceptions import ClientError
import json
import gzip


bucketName  = 'source-table'
exportName  = '01706834981181-a5d17203'
s3Prefix = 'full'
tableName   = 'dest'
tableRegion = 'sa-east-1'

s3 = boto3.resource(
    's3',
    region_name='sa-east-1'
)

dynamodb = boto3.client('dynamodb', region_name=tableRegion, endpoint_url='http://localhost:8080')

def execute_put_item(dynamodb_client, input):
    try:

        itemInput = {"TableName":tableName, "Item": input}

        response = dynamodb_client.put_item(**itemInput)

        # Handle response

    except ClientError as error:
        print(error)
    except BaseException as error:
        print("Unknown error while putting item: " + error.response['Error']['Message'])


def process_gzfile(bucket, obj):
    object = s3.Object(bucketName, obj)

    with gzip.GzipFile(fileobj=object.get()["Body"]) as gzipfile:
        content = gzipfile.read().decode('utf-8')
        itemList = content.split('\n')

        for item in itemList:
            if item:
                itemDict = json.loads(item)['Item']
                execute_put_item(dynamodb, itemDict)

def main():

    object = s3.Object(bucketName, s3Prefix + '/AWSDynamoDB/' + exportName + '/manifest-files.json')
    manifest = object.get()['Body'].read().decode('utf-8')

    manifestList = manifest.split('\n')

    for fileEntry in manifestList:
        if fileEntry:
            file = json.loads(fileEntry)
            itemCount = file['itemCount']
            dataFileS3Key = file['dataFileS3Key']
            if(itemCount > 0):

                print(f"Processing {dataFileS3Key} with {itemCount} items.")
                process_gzfile(bucketName, dataFileS3Key)


if __name__ == "__main__":
    main()

