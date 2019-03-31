import app
import boto3, botocore
from config import Config

s3 = boto3.client(
   "s3",
   aws_access_key_id=Config.S3_KEY,
   aws_secret_access_key=Config.S3_SECRET
)

def upload_images_to_s3(file, bucket_name, user_id, acl="public-read"):
    try:
        s3.upload_fileobj(
            file,
            bucket_name,
            'users/' + str(user_id) + '/images/' + file.filename,
            ExtraArgs={
                "ACL": acl,
                "ContentType": file.content_type
            }
        )

    except Exception as e:
        print("Something Happened: ", e)
        return e