"""
From a DynamoDB stream, replicates records to another table, optionally adding a 'ttl' attribute.

@see https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Streams.html
@see https://docs.aws.amazon.com/lambda/latest/dg/with-ddb.html
@see https://github.com/techgaun/dynamodb-copy-table/blob/master/dynamodb-copy-table.py
@author Tim Malone <tim@timmalone.id.au>
"""

import sys
import logging

from os import getenv
from time import time
from boto3 import client

# REQUIRED: Alternator http://address:port
alternator_endpoint = 'http://alternator:8080'

# REQUIRED: The table name to copy records to.
destination_table = 'dest'

# The AWS region of the destination table - if not the same as where you're running this function.
destination_region = 'idk'

# @see https://docs.python.org/3/library/logging.html#logging-levels
LOGGING_LEVEL = getenv('LOGGING_LEVEL', 'INFO')

# Set up logging level, and stream stream to stdout if not running in Lambda.
# (We don't want to change the basicConfig if we ARE running in Lambda).
logger = logging.getLogger(__name__)
if getenv('AWS_EXECUTION_ENV') is None:
  logging.basicConfig(stream=sys.stdout, level=LOGGING_LEVEL)
else:
  logger.setLevel(LOGGING_LEVEL)

logger.info('Try to establish an Alternator session')
dynamodb = client('dynamodb', region_name=destination_region, endpoint_url=alternator_endpoint)

def lambda_handler(event, context):

  if destination_table is None:
    raise ValueError('Please supply the destination table as the env var DESTINATION_TABLE_NAME')

  if 'Records' not in event or len(event['Records']) == 0:
    raise KeyError('No records are available to copy')

  for item in event['Records']:

    if 'dynamodb' not in item:
      logger.error('Record does not have DynamoDB data')
      continue

    logger.debug(item['dynamodb'])

    if 'NewImage' not in item['dynamodb']:
      logger.info('Record does not have a NewImage to process')
      continue

    new_item = item['dynamodb']['NewImage']

    dynamodb.put_item(TableName=destination_table, Item=new_item)

    logger.debug(new_item)

  logger.info('Done.')
  return 'Done.'

# The following lambda_handler line is NOT needed to run this as a Lambda function, but you can
# uncomment it if you want to test the function locally. You'll need to replace 'id' with the name
# of your table's primary key, and then run something like:
#
#   $ DESTINATION_TABLE_NAME=your-table-name python lambda_function.py
#
#lambda_handler({'Records':[{'dynamodb':{'NewImage':{'id':{'S':'1'}}}}]}, {})
