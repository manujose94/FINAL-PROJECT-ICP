from __future__ import print_function
import boto3
import os
import sys
import uuid
import json
import markdown     
s3_client = boto3.client('s3')
lambda_client = boto3.client('lambda')     
def converter_doc(doc_path):
    base=os.path.basename(doc_path)
    name=os.path.splitext(base)[0]
    path_not_format=doc_path.split(".")[0]
    markdown.markdownFromFile(
    input=doc_path,
    output='{}.html'.format(path_not_format),
    encoding='utf8',extensions=['fenced_code', 'codehilite']
    )
    return '{}.html'.format(path_not_format), '{}.html'.format(name)

'''def makepdf(html,name):
    # Make a PDF straight from HTML in a string.
    # Make a PDF straight from HTML in a string.
    html = open(html, 'r').read()
    pdf = HTML(string=html, base_url="").write_pdf()
    dirname = os.path.dirname(__file__)
    if os.path.exists(dirname):
        f = open(os.path.join(dirname, '{}.pdf'.format(name)), 'wb+')
        f.write(pdf)'''

def handler(event, context):
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key'] 
        operation_id=uuid.uuid4()
        download_path = '/tmp/{}{}'.format(operation_id, key)
                
        print ("[1] Downloading markdown in bucket {} with key {}".format(bucket,key))          
        os.makedirs(os.path.dirname(download_path), exist_ok = True)
        s3_client.download_file(bucket, key, download_path)
        download_new_path, new_file=converter_doc(download_path)
        bucket_out = bucket + '-out'
        
        new_file_out='{}/{}'.format(key.split('/')[0],new_file)
        print ("[2] Uploading html in bucket {} with key {}".format(bucket_out,new_file_out))          
        s3_client.upload_file(download_new_path, '{}'.format(bucket_out), new_file_out,ExtraArgs={'ContentType': 'text/html'})
        
        print ("[3] Changing ACLs for public-read for object in bucket {} with key {}".format(bucket_out,new_file_out))          
        s3_resource = boto3.resource('s3')
        obj = s3_resource.Object(bucket_out,new_file_out)
        obj.Acl().put(ACL='public-read')
        myrequest={'message': "Crado {}".format(new_file), 'event': event, 'success': True, 'buket_out':bucket_out, 'key':new_file_out, 'operation_id':str(operation_id), 'invokeby':'lambda-markdown-alucloud31'}

        print ("[4] Invoke the lambda function {}".format('lambda-check-alucloud31'))   
        response = lambda_client.invoke(
            FunctionName = 'arn:aws:lambda:us-east-1:974349055189:function:lambda-check-alucloud31',
            InvocationType = 'RequestResponse',
            Payload = json.dumps(myrequest)
        )
        
        response_from_child = json.load(response['Payload'])
        print('{}: File ${} with url: {}'.format(response_from_child['message'],response_from_child['key'],response_from_child['Location']))
        return '{}: File ${} with url: {}'.format(response_from_child['message'],response_from_child['key'],response_from_child['Location'])
        
if __name__ == '__main__':
  converter_doc(sys.argv[1])