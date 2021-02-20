#Example to Event on Bucket alucloud-lambda, it's the same as it was alucloud-lambda-out

aws s3 cp ${PWD}/example-data/cuda.md s3://alucloud-lambda/$ID/cudatest.md
#Successful output: 
#   upload: example-data/cuda.md to s3://alucloud-lambda-out/31/cudatest.md


aws s3 ls s3://alucloud-lambda-out/$ID/  | grep --color=always 'cuda'

#Successful output:
#   2021-02-17 21:10:22      13197 cudatest.md

LOG_GROUP=/aws/lambda/lambda-markdown-alucloud31
sleep 10
aws logs get-log-events --log-group-name $LOG_GROUP --log-stream-name `aws logs describe-log-streams --log-group-name $LOG_GROUP --max-items 1 --order-by LastEventTime --descending --query logStreams[].logStreamName --output text | head -n 1` --query events[].message --output text


##Succellfull output

#START RequestId: 94a00782-071a-4e9e-8cdb-c0cff840d565 Version: $LATEST
#	Downloading markdown in bucket alucloud-lambda with key 31/cudatest.md
#	Basename: cudatest.md
#	Name: cudatest
#	path_not_format: /tmp/6d01e010-4489-44f4-ad91-08c89a3affbf31/cudatest
#	Uploading html in bucket alucloud-lambda-out with key 31/cudatest.html
#	Changing ACLs for public-read for object in bucket alucloud-lambda-out with key 31/cudatest.html
#	Check and Summary HTML Created: File $31/ListOfResult.html with url: https://alucloud-lambda-out.s3.amazonaws.com/31/ListOfResult.html
#	END RequestId: 94a00782-071a-4e9e-8cdb-c0cff840d565
#	REPORT RequestId: 94a00782-071a-4e9e-8cdb-c0cff840d565	Duration: 3535.60 ms	Billed Duration: 3536 ms	Memory Size: 128 MB	Max Memory Used: 83 MB	Init Duration: 414.47 ms
