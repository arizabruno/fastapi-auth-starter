import boto3
from botocore.exceptions import ClientError

from dotenv import load_dotenv
import os

load_dotenv()
SES_SENDER = os.getenv("SES_SENDER")

def send_email(recipient, subject, body_text):
    print("Sending email from {} to {} with subject: {}".format(SES_SENDER, recipient, subject))

    AWS_REGION = "sa-east-1"
    CHARSET = "UTF-8"
    client = boto3.client('ses',region_name=AWS_REGION)
    try:
        response = client.send_email(
            Destination={
                'ToAddresses': [
                    recipient,
                ],
            },
            Message={
                'Body': {
                    'Text': {
                        'Charset': CHARSET,
                        'Data': body_text,
                    },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': subject,
                },
            },
            Source=SES_SENDER,
        )
    except ClientError as e:
        return False
    else:
        return True
