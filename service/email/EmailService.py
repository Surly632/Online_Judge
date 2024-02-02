import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from dotenv import load_dotenv
import os

import aiofiles

load_dotenv()


class EmailService:
    def __init__(self):
        self.__smtp_server = os.getenv("SMTP_SERVER")
        self.__smtp_port = os.getenv("SMTP_PORT")
        self.__smtp_username = os.getenv("SMTP_USERNAME")
        self.__smtp_password = os.getenv("SMTP_PASSWORD")

    
    async def send_email(self, receiver_email, subject, message_text, attachments=None):
        message = MIMEMultipart()

        message["From"] = os.getenv("SMTP_USERNAME")
        message["To"] = receiver_email
        message["Subject"] = subject
        message.attach(MIMEText(message_text, "plain"))

        if attachments:
            for attachment in attachments:
                async with aiofiles.open(attachment, "rb") as file:
                    part = MIMEApplication(await file.read(), Name=attachment)
                    part.add_header(
                        "content-disposition", f"attatchment;filename={attachment}"
                    )
                    message.attach(part)

        server = smtplib.SMTP(self.__smtp_server, int(self.__smtp_port))
        server.starttls()

        try:
            server.login(self.__smtp_username, self.__smtp_password)

            server.sendmail(self.__smtp_username, receiver_email, message.as_string())

        except Exception as e:
            print(e)
        finally:
            server.quit()
