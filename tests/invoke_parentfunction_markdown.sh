aws lambda invoke \
--invocation-type Event \
--function-name lambda-markdown-alucloud31 \
--region us-east-1 \
--payload file://${PWD}/test_deployment_parent.json \
outputfile.txt

#Succesfull output: 202

LOG_GROUP=/aws/lambda/lambda-markdown-alucloud31
aws logs get-log-events --log-group-name $LOG_GROUP --log-stream-name `aws logs describe-log-streams --log-group-name $LOG_GROUP --max-items 1 --order-by LastEventTime --descending --query logStreams[].logStreamName --output text | head -n 1` --query events[].message --output text

START RequestId: b8c1247a-89cc-460c-b4f9-6ebfc4e4745c Version: $LATEST
	Downloading markdown in bucket alucloud-lambda with key 31/Readme.md
	Basename: Readme.md
	Name: Readme
	path_not_format: /tmp/1b6000a4-48cb-41d0-8912-f314a65133d331/Readme
	Uploading html in bucket alucloud-lambda-out with key 31/Readme.html
	Changing ACLs for public-read for object in bucket alucloud-lambda-out with key 31/Readme.html
	Check and Summary HTML Created: File $31/ListOfResult.html with url: https://alucloud-lambda-out.s3.amazonaws.com/31/ListOfResult.html
	END RequestId: b8c1247a-89cc-460c-b4f9-6ebfc4e4745c
	REPORT RequestId: b8c1247a-89cc-460c-b4f9-6ebfc4e4745c	Duration: 4254.19 ms	Billed Duration: 4255 ms	Memory Size: 128 MB	Max Memory Used: 83 MB	Init Duration: 488.05 ms	
	START RequestId: 13182b61-83e8-4178-83af-f7f9c5ca75e5 Version: $LATEST
	Downloading markdown in bucket alucloud-lambda with key 31/Readme.md
	Basename: Readme.md
	Name: Readme
	path_not_format: /tmp/0cd69113-d4bb-4c3c-a2db-0f60e9ddec5b31/Readme
	Uploading html in bucket alucloud-lambda-out with key 31/Readme.html
	Changing ACLs for public-read for object in bucket alucloud-lambda-out with key 31/Readme.html
	Check and Summary HTML Created: File $31/ListOfResult.html with url: https://alucloud-lambda-out.s3.amazonaws.com/31/ListOfResult.html
	END RequestId: 13182b61-83e8-4178-83af-f7f9c5ca75e5
	REPORT RequestId: 13182b61-83e8-4178-83af-f7f9c5ca75e5	Duration: 1871.92 ms	Billed Duration: 1872 ms	Memory Size: 128 MB	Max Memory Used: 84 MB	
