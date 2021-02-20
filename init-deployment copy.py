#!/usr/bin/env python3
import boto3
import os
import json
import studentSettings

# MY CONFIG
alucloud31=studentSettings.SettingsAlucoud31()
#
# SESSION
#
session = boto3.Session(
    aws_access_key_id=alucloud31.aws_access_key_id, 
    aws_secret_access_key=alucloud31.aws_secret_access_key,
    region_name = 'us-east-1'
)


# List SQS queues
#response = q_client.list_queues()
#Show correctly a json object
#print(json.dumps(response, indent=4, sort_keys=True))
#print(response['QueueUrls'])

#
# SQS
#
q_client = session.client("sqs")
# Check if our SQS Queue exist
response = q_client.list_queues(QueueNamePrefix=alucloud31.SQSQueue)
if (response.get('QueueUrls') is None):
    print("[INFO] QUEUE {} not exist   -> [ADD]".format(alucloud31.SQSQueue))
    #Default attributes
    mAttributes={'DelaySeconds': '0',
            'MaximumMessageSize': '262144',
            'MessageRetentionPeriod': '345600',
            'ReceiveMessageWaitTimeSeconds': '0',
            'VisibilityTimeout': '0'}
    queue = q_client.create_queue(QueueName=alucloud31.SQSQueue,Attributes=mAttributes,tags={'owner': 'alcloud31'})
else:
    print("[SUCCES] QUEUE {} exist".format(alucloud31.SQSQueue))

#
# EVENTS
#
cloudwatch_events = session.client('events')

mresponse=cloudwatch_events.list_rules(NamePrefix=alucloud31.NameRule)
if ((mresponse.get('Rules') is None) or  (mresponse.get('Rules') is not None and len(mresponse['Rules'])==0) ):
    print("[INFO] RULE {} not exist   -> [ADD]".format(alucloud31.NameRule))
    response = cloudwatch_events.put_rule(
    Name=alucloud31.NameRule,
    EventPattern='{}'.format(json.dumps(alucloud31.eventPattern)),
    State='ENABLED',
    EventBusName="default",
    Description='Event for final Task alucloud31')
    # RoleArn not necessary due to session specification (region us-east-1), then it's created arn:aws:events:us-east-1:974349055189:rule/{name}
else:
    print("[SUCCES] RULE {} exist".format(alucloud31.NameRule))

#RULE INFO
'''response = cloudwatch_events.describe_rule(Name='alucloud-events-rule-s3-to-sqs-31')
print(json.dumps(response, indent=4, sort_keys=True))'''

#
#S3
#
s3 = session.client('s3')
s3resource = session.resource('s3') 
bucket = s3resource.Bucket(alucloud31.Bucket)
#  Check if folder username(id) exist
check_folder_resource=False
for object in bucket.objects.filter(Prefix="31/", Delimiter="/"):
    if(object.key == '{}/'.format(alucloud31.id)):
        check_folder_resource=True
        break
if(check_folder_resource):
    print("[SUCCES] FOLDER ({}/) on BUCKET ({})".format(alucloud31.id,alucloud31.Bucket))
else:
    print("[INFO] NOT FOLDER ({}/) on BUCKET ({})  -> [ADD]".format(alucloud31.id,alucloud31.Bucket))
    s3.put_object(Bucket=alucloud31.Bucket, Key=(alucloud31.id+'/'))

#
#Create lambda function
#
#Parent
lambdaManager=studentSettings.lambdaManager(alucloud31,alucloud31.configParent)
#Child is invoked when Parent putObject type .html tu Bucket S3
lambdaManagerChild=studentSettings.lambdaManager(alucloud31,alucloud31.configChild)
#Node Child is invoked by parent when he finish the task
lambdaManagerNodeChild=studentSettings.lambdaManager(alucloud31,alucloud31.configChildNode)

# FUNCTION LAMBDA
if(lambdaManager.check_already_exist_function()):
    print("[SUCCES] FUNCTION LAMBDA({}) exist".format(lambdaManager.nameFunction))
else:
    print("[INFO] FUNCTION LAMBDA({}) not exist".format(lambdaManager.nameFunction)) 
    lambdaManager.create_function()   
# ADD TRIGGER EVENT
if(lambdaManager.check_already_exist_trigger(alucloud31.Bucket)):
    print("[SUCCES] TRIGGER ON BUCKET({}) exist".format(alucloud31.Bucket))
    print("[INFO] CHECK OUR TRIGGER ON BUCKET({}) exist".format(alucloud31.BucketOut))
    if(lambdaManager.check_exist_my_trigger()):
        print("[SUCCES] TRIGGER ON BUCKET({}) exist".format(alucloud31.Bucket))
    else:
        print("[INFO] OUR TRIGGER ON BUCKET({}) not exist -> [ADD]".format(alucloud31.BucketOut))
        lambdaManager.add_trigger()
else:
    print("[INFO] TRIGGER ON BUCKET({}) not exist -> [ADD]".format(alucloud31.Bucket))  
    lambdaManager.add_trigger()


# CHILD FUNCTION LAMBDA
if(lambdaManagerChild.check_already_exist_function()):
    print("[SUCCES] FUNCTION LAMBDA({}) exist".format(lambdaManagerChild.nameFunction))
else:
    print("[INFO] FUNCTION LAMBDA({}) not exist  -> [ADD]".format(lambdaManagerChild.nameFunction)) 
    lambdaManagerChild.create_function()  #Create Child Function

# ADD TRIGGER EVENT
if(lambdaManagerChild.check_already_exist_trigger(alucloud31.BucketOut)):
    print("[INFO] TRIGGER ON BUCKET({}) exist".format(alucloud31.BucketOut))
    print("[INFO] CHECK OUR TRIGGER ON BUCKET({}) exist".format(alucloud31.BucketOut))
    if(lambdaManagerChild.check_exist_my_trigger()):
        print("[SUCCES] TRIGGER ON BUCKET({}) exist".format(alucloud31.Bucket))
    else:
        print("[INFO] OUR TRIGGER ON BUCKET({}) not exist  -> [ADD]".format(alucloud31.BucketOut))
        lambdaManagerChild.add_trigger()

else:
    print("[INFO] TRIGGER ON BUCKET({}) not exist  -> [ADD]".format(alucloud31.BucketOut))  
    lambdaManagerChild.add_trigger()

# ALLOW the ParentFunction to call the ChilNodedFunction

# NODE CHIELD FUNCTION LAMBDA
if(lambdaManagerNodeChild.check_already_exist_function()):
    print("[SUCCES] FUNCTION LAMBDA({}) exist".format(lambdaManagerNodeChild.nameFunction))
else:
    print("[INFO] FUNCTION LAMBDA({}) not exist  -> [ADD]".format(lambdaManagerNodeChild.nameFunction)) 
    lambdaManagerNodeChild.create_function()  #Create Child Function
    print("[INFO] ADD POLICY LAMBDA({}) for invoke other functions  -> [ADD]".format(lambdaManager.nameFunction))
    lambdaManagerNodeChild.add_policy_invoke_function(alucloud31.configParent['name'],alucloud31.configChildNode['name'])