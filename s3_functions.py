import boto3
from botocore.config import Config

my_config = Config(
    region_name = 'us-west-2',
    signature_version = 'v4'
)

def upload_file(file_name, bucket):
    object_name = file_name
    # s3_client = boto3.client('s3')
    s3_client = boto3.client('s3', config=my_config)
    response = s3_client.upload_file(file_name, bucket, object_name)
    return response

def list_files(bucket):
    # s3_client = boto3.client('s3')
    s3_client = boto3.client('s3', config=my_config)

    contents = []
    try:
        for item in s3_client.list_objects(Bucket=bucket)['Contents']:
            contents.append(item)
    except Exception as e:
        pass
    return contents

def show_image(bucket):
    s3_client = boto3.client('s3', config=my_config)
    public_urls = []
    try:
        for item in s3_client.list_objects(Bucket=bucket)['Contents']:
            presigned_url = s3_client.generate_presigned_url('get_object', Params = {'Bucket': bucket, 'Key': item['Key']}, ExpiresIn = 100)
            public_urls.append(presigned_url)
    except Exception as e:
        pass
    # print("[DATA] : The contents inside show_image = ", public_urls)
    return public_urls
    

def load_image(bucket, image):

    # s3_client = boto3.client('s3')
    s3_client = boto3.client('s3', config=my_config)

    response = s3_client.generate_presigned_url('get_object', Params={'Bucket': bucket, 'Key': f'uploads/{image}'}, ExpiresIn=100)

    return response


def delete_image(bucket, image):

    # s3_client = boto3.client('s3')
    s3_client = boto3.client('s3', config=my_config)

    response = s3_client.delete_object(
        Bucket=bucket,
        Key=f'uploads/{image}'
    )

    return response