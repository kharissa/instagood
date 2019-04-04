from rq import get_current_job
from app import app
from models.task import Task
from database import db
import sendgrid
import os
import sys
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, Personalization, Content
app.app_context().push()

# def example(seconds):
#     job = get_current_job()
#     print('Starting task')
#     for i in range(seconds):
#         job.meta['progress'] = 100.0 * i / seconds
#         job.save_meta()
#         print(i)
#     job.meta['progress'] = 100
#     job.save_meta()
#     print('Task completed')


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
    try:
      _set_task_progress(0)
      sg = sendgrid.SendGridAPIClient(apikey=os.environ.get('SENDGRID_API_KEY'))
      from_email = Email("transactions@instagood.com")
      to_email = Email(recipient.email)
      subject = "Your Instagood Donation Receipt"
      content = Content("text/html", html_content)
      mail = Mail(from_email, subject, to_email, content)
      response = sg.client.mail.send.post(request_body=mail.get())
      _set_task_progress(100)
      print(response.status_code)
      print(response.body)
      print(response.headers)
    except:
      _set_task_progress(100)
      app.logger.error('Unhandled exception', exc_info=sys.exc_info())


def _set_task_progress(progress):
    job = get_current_job()
    if job:
        job.meta['progress'] = progress
        job.save_meta()
        task = Task.get(Task.redis_job_id == job.get_id())
        if progress >= 100:
            task.complete = True
            task.save()
        job.save()


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
  try:
    _set_task_progress(0)
    sg = sendgrid.SendGridAPIClient(apikey=os.environ.get('SENDGRID_API_KEY'))
    from_email = Email("requests@instagood.com")
    to_email = Email(following.email)
    subject = f"New Follow Request on Instagood"
    content = Content("text/html", html_content)
    mail = Mail(from_email, subject, to_email, content)
    response = sg.client.mail.send.post(request_body=mail.get())
    _set_task_progress(100)
    print(response.status_code)
    print(response.body)
    print(response.headers)
  except:
    _set_task_progress(100)
    app.logger.error('Unhandled exception', exc_info=sys.exc_info())

