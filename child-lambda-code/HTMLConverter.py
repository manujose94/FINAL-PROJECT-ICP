import html2text
import sys
import os
import uuid
import boto3
s3_client = boto3.client('s3')

def lambda_handler(event, context):
    #1 Read the input parameters
    buket_out    = event['buket_out']
    key   = event['key']
    #2 Generate the Order Transaction ID
    transactionId   = str(uuid.uuid1())
    #4 Format and return the result
    return {
        'OperationID': transactionId,
        'Operation':   "Get oly text of HTML",
        'buket_out':   buket_out,
        'TransformTo': '{}.txt'.format(key.split('.')[0])
    }
 
def converter_html(path_html):
    base=os.path.basename(path_html)
    name=os.path.splitext(base)[0]
    path_not_format=path_html.split(".")[0]
    htmlforsaveas = open(path_html).read()
    text = (html2text.html2text(htmlforsaveas)).encode('utf-8')
    # Open a file and write to it
    output='{}.txt'.format(path_not_format)
    with open(output, 'wb+') as f:
        f.write(text)
    return output, '{}.txt'.format(name)
    

def handler(event, context):
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key'] 
        operation_id=uuid.uuid4()
        download_path = '/tmp/{}{}'.format(operation_id, key)
                
        print ("[1] Downloading markdown in bucket {} with key {}".format(bucket,key))          
        os.makedirs(os.path.dirname(download_path), exist_ok = True)
        s3_client.download_file(bucket, key, download_path)
        download_new_path, new_file=converter_html(download_path)
        #Here the same bucket out
        bucket_out = bucket
        
        new_file_out='{}/{}'.format(key.split('/')[0],new_file)
        print ("[2] Uploading html in bucket {} with key {}".format(bucket_out,new_file_out))          
        s3_client.upload_file(download_new_path, '{}'.format(bucket_out), new_file_out)
        
        print ("[3] Changing ACLs for public-read for object in bucket {} with key {}".format(bucket_out,new_file_out))          
        s3_resource = boto3.resource('s3')
        obj = s3_resource.Object(bucket_out,new_file_out)
        obj.Acl().put(ACL='public-read')
        return {'message': "Crado {}".format(new_file), 'event': event, 'success': True, 'buket_out':bucket_out, 'key':new_file_out, 'operation_id':str(operation_id)}

if __name__ == '__main__':
  converter_html(sys.argv[1])