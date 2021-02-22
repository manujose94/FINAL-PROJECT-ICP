#!/usr/bin/env python3
import io
import json
import os
from os.path import basename
from datetime import datetime,timedelta
import botocore
import yaml
from boto3.session import Session
from decouple import config

#python-decouple

class SettingsAlucoud31:
    def __init__(self):
        self.course = 'ICP'
        self.id=config('ID')
        self.username = '{}'.format(config('USERNAME_AWS'))
        self.aws_access_key_id=config('KEY_ID')
        self.aws_secret_access_key=config('ACCES_KEY')
        self.eventPattern={
        "source": [
            "aws.s3"
        ],
        "detail-type": [
            "AWS API Call via CloudTrail"
        ],
        "detail": {
            "eventSource": [
            "s3.amazonaws.com"
            ],
            "eventName": [
            "PutObject",
            "DeleteObject"
            ],
            "requestParameters": {
            "bucketName": [
                "alucloud-lambda"
            ]
            }
        }
        }
        self.NameRule='alucloud-events-rule-s3-to-sqs-{}'.format(config('ID'))
        self.NameTrail='trails-s3-data-events-alucloud{}'.format(config('ID'))
        self.FolderBucket='alucloud{}-lambda'.format(config('ID'))
        self.SQSQueue='sqs-alucloud{}'.format(config('ID'))
        self.Bucket='alucloud-lambda'
        self.BucketOut='alucloud-lambda-out'
        self.FolderBucket="markdown-{}".format(config('ID'))
        self.ParentLambdaFunction='lambda-markdown-alucloud{}'.format(config('ID'))
        self.ChildLambdaFunction='lambda-html-alucloud{}'.format(config('ID'))
        self.ChildNodeLambdaFunction='lambda-check-alucloud{}'.format(config('ID'))
        self.mysession=Session(
            aws_access_key_id=config('KEY_ID'), #Environment variables
            aws_secret_access_key=config('ACCES_KEY'),
            region_name = 'us-east-1'
        )
        self.configParent=yaml.load("""
            role: lambda-s3-execution-role
            name: lambda-markdown-alucloud31
            zip: lambda-markdown-alucloud31.zip
            path: parent-lambda-code
            handler: MarkdownConverter.handler
            runtime: python3.6
            description: Convert mardownk documents to html
            suffix: .md
            statementid: '1-lambda'
            bucket: {}
            arn_bucket: arn:aws:s3:::alucloud-lambda
            """.format(self.Bucket), 
            Loader=yaml.FullLoader)
        self.configChild=yaml.load("""
            role: lambda-s3-execution-role
            name: lambda-html-alucloud31
            zip: lambda-html-alucloud31.zip
            path: child-lambda-code
            handler: HTMLConverter.handler
            runtime: python3.6
            description: Just gets the text from the html and generates a txt file
            suffix: .html
            statementid: '2-lambda'
            bucket: {}
            arn_bucket: arn:aws:s3:::alucloud-lambda-out
            """.format(self.BucketOut), 
            Loader=yaml.FullLoader)

        self.configChildNode=yaml.load("""
            role: lambda-s3-execution-role
            name: lambda-check-alucloud31
            zip: lambda-check-alucloud31.zip
            path: childnode-lambda-code
            handler: CheckMyResults.handler
            runtime: nodejs12.x
            description: Invoke by Parent and list his work results.
            suffix: .html,.txt
            statementid: '22-lambda'
            bucket: {}
            arn_bucket: arn:aws:s3:::alucloud-lambda-out
            """.format(self.BucketOut), 
            Loader=yaml.FullLoader)


class lambdaManager:

    def __init__(self,mSettingsAlucoud31,config):
        self.alucloud=mSettingsAlucoud31
        self.config=config
        self.nameFunction=self.config['name']

    def get_logs(self,hours=5):
        startTime=int((datetime.now() - timedelta(hours)).timestamp())
        
        """ Returns all logs related to the invocations of this lambda function. """
        log = self.alucloud.mysession.client('logs')
        return log.filter_log_events(logGroupName=f'/aws/lambda/{self.config["name"]}',
        startTime=int((datetime.now() - timedelta(hours)).timestamp())*1000,
        endTime=int(datetime.now().timestamp())*1000)
        
    #
    #   Create lambda function specified via config of type yaml
    #
    def create_function(self):
        """ Creates and uploads the lambda function. """

        lam = self.alucloud.mysession.client('lambda')
        iam = self.alucloud.mysession.client('iam')
       
        # Creates a zip file containing our handler code.
        self.zip_folder(self.config['zip'],self.config['path'])

        # Loads the zip file as binary code. 
        with open(self.config['zip'], 'rb') as f: 
            code = f.read()

        role = iam.get_role(RoleName=self.config['role'])
        return lam.create_function(
            Description=self.config['description'],
            FunctionName=self.config['name'],
            Runtime='{}'.format(self.config['runtime']),
            Timeout=123,
            Tags={'owner': '{}'.format(self.alucloud.username)},
            Role=role['Role']['Arn'],
            Handler=self.config['handler'],
            Code={'ZipFile':code})


    def update_function(self):
        """ Updates the function. """

        lam = self.alucloud.mysession.client('lambda')

        # Creates a zip file containing our handler code.
        import zipfile
        with zipfile.ZipFile(self.config['zip'], 'w') as z:
            z.write(self.config['path'])

        # Loads the zip file as binary code. 
        with open(self.config['zip'], 'rb') as f: 
            code = f.read()

        return lam.update_function_code( 
            FunctionName=self.config['name'],
            ZipFile=code)
    #
    # Add polocy to be invoked by another lambda function
    #
    def add_policy_invoke_function(self,call_function,invoke_function):
        invoked_lamda_arn=self.get_function_arn(invoke_function)
        if(invoked_lamda_arn):
            lam = self.alucloud.mysession.client('lambda')
            try:
                response = lam.add_permission(
                FunctionName=call_function,
                StatementId='3',
                Action='lambda:InvokeFunction',
                Principal='lambda.amazonaws.com',
                SourceArn=invoked_lamda_arn,
                )

            except botocore.errorfactory.ClientError:
                print('[INFO] THE POLICY ({}) WITH ID ({}) ALREADY EXISTS FOR THE FUNCTION: {}'.format('lambda:InvokeFunction',self.config['statementid'],self.config['name']))
            try:
                response = lam.add_permission(
                FunctionName=call_function,
                StatementId='4',
                Action='lambda:InvokeAsync',
                Principal='lambda.amazonaws.com',
                SourceArn=invoked_lamda_arn,
                )

            except botocore.errorfactory.ClientError:
                print('[INFO] THE POLICY ({}) WITH ID ({}) ALREADY EXISTS FOR THE FUNCTION: {}'.format('lambda:InvokeFunction',self.config['statementid'],self.config['name']))
        else:
            print('[ERROR] WITHOUT ADDING NEW INVOCATION POLICY: func lamba({}) not found'.format(self.config['name']))
   
    #
    # Add trigger to our bucket declarated via config yaml
    #
    def add_trigger(self):
        s3=self.alucloud.mysession.client('s3')
        lamda_arn=self.get_function_arn(self.config['name'])
        lam = self.alucloud.mysession.client('lambda')
        try:
            response = lam.add_permission(
                FunctionName=self.config['name'],
                StatementId=self.config['statementid'],
                Action='lambda:InvokeFunction',
                Principal='s3.amazonaws.com',
                SourceArn=self.config['arn_bucket'],
            )
        except botocore.errorfactory.ClientError:
            print('[INFO] THE POLICY ({}) WITH ID ({}) ALREADY EXISTS FOR THE FUNCTION: {}'.format('lambda:InvokeFunction',self.config['statementid'],self.config['name']))
        response = s3.put_bucket_notification_configuration(
        Bucket=self.config['bucket'],
        NotificationConfiguration= {
                'LambdaFunctionConfigurations':[{'LambdaFunctionArn': '{}'.format(lamda_arn), 
                'Events': ['s3:ObjectCreated:Put'] , 
                'Filter': {
                    'Key': {
                        'FilterRules': [
                            {
                                'Name': 'prefix',
                                'Value': '{}/'.format(self.alucloud.id)
                            },
                            {
                                'Name': 'suffix',
                                'Value': '{}'.format(self.config['suffix'])
                            }
                        ]
                    }
                }
            }]
        }
        )
    #
    # Get the RNA of a lambda function specified by name
    #
    def check_already_exist_function(self):
        lam = self.alucloud.mysession.client('lambda')
        #Please note that not all current functions are always listed.
        #response = lam.list_functions()
        '''
        finded=False
        f = response['Functions']
        for each in f:
            if(each['FunctionName']==self.config['name']):
                finded=True
        return finded
        '''
        #Other Method
        try:
            role_response = (lam.get_function_configuration(
                FunctionName = self.config['name'])
            )
            return (role_response and role_response.get('FunctionArn'))
        except botocore.exceptions.ClientError:
            return False
        
    def get_function_arn(self,namefunction):
        lam = self.alucloud.mysession.client('lambda')
        role_response = (lam.get_function_configuration(
            FunctionName = namefunction)
        )
        #print(json.dumps(role_response, indent=4, sort_keys=True))
        if(role_response and role_response.get('FunctionArn')):
            return role_response['FunctionArn']
        else:
            return None
    #
    #check that there is already at least one trigger assigned to a specific bucket.
    #
    def check_already_exist_trigger(self,bucket):
        s3=self.alucloud.mysession.client('s3')
        response = s3.get_bucket_notification_configuration(Bucket=bucket)
        if ((response.get('LambdaFunctionConfigurations') is None) 
            or  (response.get('LambdaFunctionConfigurations') is not None 
            and len(response['LambdaFunctionConfigurations'])==0) ):
            return False
        else:
            return True
    #
    # Check if there is our trigger assigned to a specific bucket
    #
    def check_exist_my_trigger(self):
        s3=self.alucloud.mysession.client('s3')
        response = s3.get_bucket_notification_configuration(Bucket=self.config['bucket'])
        if ((response.get('LambdaFunctionConfigurations') is None) 
            or  (response.get('LambdaFunctionConfigurations') is not None 
            and len(response['LambdaFunctionConfigurations'])==0) ):
            return False
        else:
            LambdaFunctionArn =self.get_function_arn(self.config['name'])
            listFuncConfig = response['LambdaFunctionConfigurations']
            finded=False
            for each in listFuncConfig:
                if(each['LambdaFunctionArn']==LambdaFunctionArn):
                    finded=True
                    break
            return finded
            

    def invoke_function(self,first, last):
        """ Invokes the function. """
        lam = self.alucloud.mysession.client('lambda')
        resp = lam.invoke(
            FunctionName=self.config['name'],
            InvocationType='RequestResponse',# SYNC, for ASYNC InvocationType='Event'
            LogType='Tail',
            Payload=json.dumps({'first_name': first, 'last_name': last}))
        print(resp['Payload'].read())
        return resp

    #
    #   Compress the entire contents of a folder
    #
    def zip_folder(self,zip_name,folder):
        import zipfile
        filePaths= self.retrieve_file_paths(folder)
        path_prefix=folder
     
        with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as myzip:
            for f in filePaths:               
                myzip.write(f, f[len(path_prefix):] if f.startswith(path_prefix) else f)
    
    # Declare the function to return all file paths of the particular directory
    def retrieve_file_paths(self,dirName):
        filePaths = []
        for root, directories, files in os.walk(dirName):
            for filename in files:
                # Create the full filepath by using os module.
                filePath = os.path.join(root, filename)
                filePaths.append(filePath)
        return filePaths
