<!--
layout: Doc
framework: v2
platform: AWS
language: Python
-->
# Dumpert.nl RSS Enhancer

Enhances experience of dumpert.nl own RSS by embedding Videos (`<video><source/></video>` tag) and Images (`<img/>` tag) along with descriptions, tags, kudos and views directly into contents.

Deployed as `AWS API Gateway` + `AWS Lambda` with help of https://serverless.com Framework

All Rights are Lefts

Kudos to 
 - https://feedly.com for being the new Google Reader
 - `Palabre RSS Reader` and http://nextmatters.com (for Windows Support)
 - http://9gagrss.com for the idea and provided convenience

## Deploy

In order to deploy the endpoint you simply run

```bash
npx serverless deploy --stage=stage_name --aws-profile=profile_name
```

The expected result should be similar to:

```bash
Serverless: Packaging service...
Serverless: Uploading CloudFormation file to S3...
Serverless: Uploading service .zip file to S3 (758 B)...
Serverless: Updating Stack...
Serverless: Checking Stack update progress...
..........
Serverless: Stack update finished...
```

## Usage

You can now invoke the Lambda directly and even see the resulting log via

```bash
serverless invoke --function currentTime --log
```

The expected result should be similar to:

```bash
{
    "body": "{\"message\": \"Hello, the current time is 15:40:19.009371\"}",
    "statusCode": 200
}
--------------------------------------------------------------------
START RequestId: a26699d3-b3ee-11e6-98f33f952e8294 Version: $LATEST
END RequestId: a26699d3-b3ee-11e6-98f33f952e8294
REPORT RequestId: a26699d3-b3ee-11e6-98f33f952e8294	Duration: 0.23 ms	Billed Duration: 100 ms 	Memory Size: 1024 MB	Max Memory Used: 15 MB
```

Finally you can send an HTTP request directly to the endpoint using a tool like curl

```bash
curl https://XXXXXXX.execute-api.us-east-1.amazonaws.com/dev/ping
```

The expected result should be similar to:

```bash
{"message": "Hello, the current time is 15:38:53.668501"}%  
```

## Scaling

By default, AWS Lambda limits the total concurrent executions across all functions within a given region to 100. The default limit is a safety limit that protects you from costs due to potential runaway or recursive functions during initial development and testing. To increase this limit above the default, follow the steps in [To request a limit increase for concurrent executions](http://docs.aws.amazon.com/lambda/latest/dg/concurrent-executions.html#increase-concurrent-executions-limit).
