Response
{
  "message": "Crado Readme.txt",
  "event": {
    "Records": [
      {
        "eventVersion": "2.0",
        "eventSource": "aws:s3",
        "awsRegion": "us-west-2",
        "eventTime": "1970-01-01T00:00:00.000Z",
        "eventName": "ObjectCreated:Put",
        "userIdentity": {
          "principalId": "AIDAJDPLRKLG7UEXAMPLE"
        },
        "requestParameters": {
          "sourceIPAddress": "127.0.0.1"
        },
        "responseElements": {
          "x-amz-request-id": "C3D13FE58DE4C810",
          "x-amz-id-2": "FMyUVURIY8/IgAtTv8xRjskZQpcIZ9KG4V5Wp6S7S/JRWeUWerMUE5JgHvANOjpD"
        },
        "s3": {
          "s3SchemaVersion": "1.0",
          "configurationId": "testConfigRule",
          "bucket": {
            "name": "alucloud-lambda-out",
            "ownerIdentity": {
              "principalId": "A3NL1KOZZKExample"
            },
            "arn": "arn:aws:s3:::alucloud-lambda-out"
          },
          "object": {
            "key": "31/Readme.html",
            "size": 1024,
            "eTag": "d41d8cd98f00b204e9800998ecf8427e",
            "versionId": "096fKKXTRTtl3on89fVO.nfljtsv6qko"
          }
        }
      }
    ]
  },
  "success": true,
  "buket_out": "alucloud-lambda-out",
  "key": "31/Readme.txt",
  "operation_id": "5d8af597-d71a-49c0-a169-73d9a10089d9"
}

Function Logs
START RequestId: 8aaebca5-e71a-4fcf-aa94-60648572df66 Version: $LATEST
Downloading markdown in bucket alucloud-lambda-out with key 31/Readme.html
Basename: Readme.html
Name: Readme
Uploading html in bucket alucloud-lambda-out with key 31/Readme.txt
Changing ACLs for public-read for object in bucket alucloud-lambda-out with key 31/Readme.txt
END RequestId: 8aaebca5-e71a-4fcf-aa94-60648572df66
REPORT RequestId: 8aaebca5-e71a-4fcf-aa94-60648572df66	Duration: 1542.06 ms	Billed Duration: 1543 ms	Memory Size: 128 MB	Max Memory Used: 78 MB	Init Duration: 379.51 ms

Request ID
8aaebca5-e71a-4fcf-aa94-60648572df66