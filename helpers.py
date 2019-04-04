import os
import app
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

def send_transaction_email(recipient, amount, card_type, last_four_digits, photographer, transaction_id):
    html_content = f"""
    <html>
  <body>
    <table align="center" border="0" cellpadding="0" cellspacing="0" width="90%" style="border: 1px solid #cccccc; margin-bottom: 20px; font-family: Arial, sans-serif; font-size: 16px; line-height: 1.6em; color: #153643;">
      <tr>
        <td align="center" bgcolor="#F8F8F8" style="padding: 40px 0 30px 0;">
          <img src="https://s3.amazonaws.com/instagood-images/static/logo_instagood.png" alt="Instagood logo" width="350" style="display: block;">
        </td>
      </tr>
      <tr>
        <td bgcolor="#ffffff" style="padding: 40px 30px 40px 30px;">
          <table border="0" cellpadding="0" cellspacing="0" width="100%">
            <tr>
              <td>
              <h3>Thank you, {recipient.name}!</h3>
              </td>
            </tr>
            <tr>
              <td style="padding: 20px 0 30px 0;">
                Your donation of {amount} USD has been sent to {photographer.name}. Thank you for supporting creators and their work.
              </td>
            </tr>
            <tr>
              <td>
                <b>Payment Details</b>
                <ul>
                  <li>Transaction Id: {transaction_id}</li>
                  <li>Payment Method: {card_type}-{last_four_digits}</li>
                  <li>Total Amount: {amount} USD</li>
                </ul>
              </td>
            </tr>
          </table>
        </td>
      </tr>
      <tr>
        <td bgcolor="#28a745" style="padding: 30px 30px 30px 30px; color: #ffffff; font-size: 13px;">
          &reg; Instagood, 2019<br/>
          Building a community to support art.
        </td>
      </tr>
    </table>
  </body>
</html>"""
    sg = sendgrid.SendGridAPIClient(apikey=os.environ.get('SENDGRID_API_KEY'))
    from_email = Email("transactions@instagood.com")
    to_email = Email(recipient.email)
    subject = "Your Instagood Donation Receipt"
    content = Content("text/html", html_content)
    mail = Mail(from_email, subject, to_email, content)
    response = sg.client.mail.send.post(request_body=mail.get())
    print(response.status_code)
    print(response.body)
    print(response.headers)


def send_follow_request_email(following, follower, requests_url):
    html_content = f"""
    <html>
  <body>
    <table align="center" border="0" cellpadding="0" cellspacing="0" width="90%" style="border: 1px solid #cccccc; margin-bottom: 20px; font-family: Arial, sans-serif; font-size: 16px; line-height: 1.6em; color: #153643;">
      <tr>
        <td align="center" bgcolor="#F8F8F8" style="padding: 40px 0 30px 0;">
          <img src="https://s3.amazonaws.com/instagood-images/static/logo_instagood.png" alt="Instagood logo" width="350" style="display: block;">
        </td>
      </tr>
      <tr>
        <td bgcolor="#ffffff" style="padding: 40px 30px 40px 30px;">
          <table border="0" cellpadding="0" cellspacing="0" width="100%">
            <tr>
              <td>
              <h3>{follower.name} is requesting to follow you.</h3>
              </td>
            </tr>
            <tr>
              <td style="padding: 20px 0 30px 0;">
                If confirmed, {follower.name} will be able to see your photos on Instagood. To confirm or reject the request, login to Instagood and visit your inbox, or click the link below:
              </td>
            </tr>
            <tr>
              <td>
                <a href="http://localhost:5000/users/requests">{requests_url}</a>
              </td>
            </tr>
          </table>
        </td>
      </tr>
      <tr>
        <td bgcolor="#28a745" style="padding: 30px 30px 30px 30px; color: #ffffff; font-size: 13px;">
          &reg; Instagood, 2019<br/>
          Building a community to support art.
        </td>
      </tr>
    </table>
  </body>
</html>"""
    sg = sendgrid.SendGridAPIClient(apikey=os.environ.get('SENDGRID_API_KEY'))
    from_email = Email("requests@instagood.com")
    to_email = Email(following.email)
    subject = f"New Follow Request on Instagood"
    content = Content("text/html", html_content)
    mail = Mail(from_email, subject, to_email, content)
    response = sg.client.mail.send.post(request_body=mail.get())
    print(response.status_code)
    print(response.body)
    print(response.headers)
