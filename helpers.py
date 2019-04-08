import os
from app import app
import jwt
import datetime
import braintree
import boto3, botocore
from config import Config
from dotenv import load_dotenv
import sendgrid
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, Personalization, Content

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

def encode_auth_token(self):
    try:
        payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=2),
            'iat': datetime.datetime.utcnow(),
            'sub': self.id
        }
        return jwt.encode(
            payload,
            app.config.get('SECRET_KEY'),
            algorithm='HS256'
        ).decode('utf-8')
    except Exception as e:
        return e

def decode_auth_token(auth_token):
    try:
        payload = jwt.decode(auth_token, app.config.get('SECRET_KEY'))
        return payload['sub']
    except jwt.ExpiredSignatureError:
        return 'Signature expired. Please log in again.'
    except jwt.InvalidTokenError:
        return 'Invalid token. Please log in again.'
