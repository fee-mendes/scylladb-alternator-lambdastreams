# scylladb-alternator-lambdastreams

A simple repository showing example code on how to ingest DynamoDB Stream events to ScyllaDB Alternator using AWS Lambda.

Disclaimer:
> dynamodb-copy and its contents were originally made by @tdmalone:
> https://github.com/tdmalone/dynamodb-copy/


1. Create a source DynamoDB table. Ensure you have enough RCU/WCUs to make it minimally performant.
  - I used 500 RCUs and 300 WCUs
  - Do not enable DynamoDB Streams just yet (if you are using it for learning, at least)! 
2. Edit `create_source_and_ingest.py` according to your needs. By default, the program will create a DynamoDB table named `source` in the local region, with a key named `id` (Integer) and use DynamoDB defaults for the rest.
  - The program will ingest 50K records, each one with a random amount of columns (up to 50).
  - It should take some minutes to fully ingest it, specially if your WCUs were the default or too low.
3. Past the initial ingestion, create your Alternator table. There's a `create_target.py` file to help you with that.
  - You may create a different table name. Ideally, keep the Key name and types the same.
4. At this point, enable DynamoDB Streams. Then, proceed with creating a Lambda trigger:

<img width="1408" alt="image" src="https://github.com/fee-mendes/scylladb-alternator-lambdastreams/assets/82817126/e46264e4-b07e-4478-a5cf-c326b4ba1cd1">

- Be sure to give your Lambda function permissions to query DynamoDB Streams. The `AWSLambdaInvocation-DynamoDB` policy (managed by AWS) should have everything you may need. Or if you prefer a manual IAM policy:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "dynamodb:ListStreams",
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:GetShardIterator",
        "dynamodb:DescribeStream",
        "dynamodb:GetRecords"
      ],
      "Resource": "arn:aws:dynamodb:SOURCE_REGION_ID:ACCOUNT_ID:table/SOURCE_TABLE_NAME/stream/*"
    }
  ]
}
```
- Expand **Advanced Settings**, and select **Enable VPC**. Select the **VPC**, **Subnets** and relevant **Security Group** relevant to your ScyllaDB deployment
- Ensure your **Security Group** allows for incoming traffic to ScyllaDB Alternator port
- Past the function creation, navigate to **Configuration** > **General Configuration** and increase the Timeout to a reasonable value. You want it to high enough to allow you to process a series of events, in such a way that upon hitting the timeout limit DynamoDB Streams won't the Stream to have failed processing, effectively ending up in an infinite loop.
<img width="826" alt="image" src="https://github.com/fee-mendes/scylladb-alternator-lambdastreams/assets/82817126/5ec8758a-e816-471b-89fd-e2a6dc23f16b">

5. Edit the `dynamodb-copy/lambda_function.py` with your relevant changes. You probably should be using Environment variables instead, rather than using hardcoded values.
6. Within the `dynamodb-copy/` directory, run the `deploy.sh <lambda-name>` script. This will package the local code and update your Lambda function you just created. Should it fail, review both your user as well as Lambda function IAM settings.
7. Re-run the `create_source_and_ingest.py` code, this will upsert all 50K records. If you prefer, you may write less records instead just to ensure things are properly set-up.
8. Should everything be set-up properly, you should see data flowing to ScyllaDB Alternator!
9. You may watch progress via AWS CloudWatch logs (or tail via `awscli`), though you may simply count() the number of items in Alternator should the number of records be relatively small.
10. Once Lambda finishes replicating data, you may run `compare.py` to check the results. Remember that for an application actively writing you may have some temporary mismatches, but at this point we reached our goal of understanding how the overall process works!
