import boto3
from botocore.config import Config

my_config = Config(
    region_name = 'us-east-2',
    signature_version = 's3v4'
)

def upload_file(file_name, bucket):
    """Upload file to S3 bucket""""

    object_name = file_name

    s3_client = boto3.client('s3', config=my_config)

    response = s3_client.upload_file(file_name, bucket, object_name)
    return response


def list_files(bucket):
    """List all items in S3 bucket"""

    s3_client = boto3.client('s3', config=my_config)

    contents = []
    try:
        for item in s3_client.list_objects(Bucket=bucket)['Contents']:
            contents.append(item)
    except Exception as e:
        pass
    return contents


def load_image(bucket, image):
    """Generate url for an item in the S3 bucket"""

    s3_client = boto3.client('s3', config=my_config)

    response = s3_client.generate_presigned_url('get_object', Params={'Bucket': bucket, 'Key': f'uploads/{image}'}, ExpiresIn=100)

    return response


def delete_image(bucket, image):
    """Delete an image in the S3 bucket"""

    s3_client = boto3.client('s3', config=my_config)

    response = s3_client.delete_object(
        Bucket=bucket,
        Key=f'uploads/{image}'
    )

    return response