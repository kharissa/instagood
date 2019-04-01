import os
import braintree
from dotenv import load_dotenv
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


gateway = braintree.BraintreeGateway(
    braintree.Configuration(
        braintree.Environment.Sandbox,
        merchant_id=os.environ['BT_MERCHANT_ID'],
        public_key=os.environ['BT_PUBLIC_KEY'],
        private_key=os.environ['BT_PRIVATE_KEY']
    )
)

def generate_client_token():
    return gateway.client_token.generate()


def transact(options):
    return gateway.transaction.sale(options)


def find_transaction(transaction_id):
    return gateway.transaction.find(transaction_id)
