from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.auth.exceptions import RefreshError
from googleapiclient.discovery import build
from pathlib import Path
import base64, os
import json, asyncio
import sys
from ..bitget import BitgetClient

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..', '..')))

class EmailSender(BitgetClient):
    def __init__(self, token_path, creds_path, sender_email):
        BitgetClient.__init__(self)
        self.token_path = Path(token_path)
        self.creds_path = Path(creds_path)
        self.sender_email = sender_email
        self.creds = self.auth()

    def auth(self):
        creds = None
        # Check if the token file exists
     
        with open(os.path.join(os.getcwd(), "services/schedule_taks/credentials/emailtoken.json"), 'r') as token_file:
            creds = Credentials.from_authorized_user_info(json.load(token_file))

        # If there are no (valid) credentials available, prompt the user to authenticate.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except RefreshError:
                    raise Exception("Failed to refresh credentials. Please re-authenticate.")
            else:
                from google_auth_oauthlib.flow import InstalledAppFlow
                flow = InstalledAppFlow.from_client_secrets_file(
                    os.path.join(os.getcwd(), "services/schedule_taks/credentials/credentials.json"), scopes=['https://www.googleapis.com/auth/gmail.send'])
                creds = flow.run_local_server(port=0)

            # Save the credentials for the next run
            with open(self.token_path, 'w') as token_file:
                token_file.write(creds.to_json())

        return creds

    def send_email(self, receiver_email, subject, message_html):
        try:
            # Build the service
            service = build('gmail', 'v1', credentials=self.creds)

            # Set up the email structure, To, Subject, and email text
            message = MIMEMultipart('alternative')
            message['To'] = receiver_email
            message['From'] = self.sender_email
            message['Subject'] = subject

            # Attach the HTML version
            part_html = MIMEText(message_html, 'html')
            message.attach(part_html)

            # Encode message
            encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            create_message = {"raw": encoded_message}

            # Send the message
            send_message = (
                service.users()
                .messages()
                .send(userId="me", body=create_message)
                .execute()
            )
            print(f'Message Id: {send_message["id"]}')

        except HttpError as error:
            # Handle errors from Gmail API
            print(f"An error occurred: {error}")

    def normal_email(self, receiver_email, subject, content):
        message_html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6; background-color: #f9f9f9; margin: 0; padding: 0;">
                <header style="background: #4CAF50; color: white; padding: 20px 0; text-align: center;">
                    <h1 style="margin: 0; font-size: 24px;">Crypto Project - Normal Update</h1>
                </header>
                <main style="padding: 20px;">
                    <section style="background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);">
                        <h2 style="color: #4CAF50; margin-top: 0;">Normal Update</h2>
                        <p>{content}</p>
                    </section>
                    <section style="margin-top: 20px;">
                        <h2>Stay Updated</h2>
                        <p>Stay updated with the latest news and updates on our project. For more information, visit our <a href="#" style="color: #4CAF50; text-decoration: none;">website</a>.</p>
                        <p>If you have any questions, feel free to reach out to our support team.</p>
                    </section>
                    <footer style="margin-top: 20px; padding-top: 10px; border-top: 1px solid #ddd; text-align: center;">
                        <p>Thank you for being a valued member of our community.</p>
                        <p style="font-size: 0.9em;">&copy; 2024 Crypto Project. All rights reserved.</p>
                    </footer>
                </main>
            </body>
        </html>
        """
        self.send_email(receiver_email, subject, message_html)

    def advise_email(self, receiver_email, subject, advice):



        
        message_html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6;">
                <header style="background: #FFA500; color: white; padding: 10px 0; text-align: center;">
                    <h1 style="margin: 0;">Crypto Project - Advisory Notice</h1>
                </header>
                <main style="padding: 20px;">
                    <h2>Advisory Notice</h2>
                    <p>{advice}</p>
                    <p>We highly recommend taking the following actions to ensure your investments are safe and optimized.</p>
                    <ul>
                        <li>Review your current portfolio.</li>
                        <li>Stay informed about market trends.</li>
                        <li>Consider diversifying your investments.</li>
                    </ul>
                    <p>For more detailed advice, please consult with our expert team or visit our <a href="#">advisory page</a>.</p>
                    <footer style="margin-top: 20px; padding-top: 10px; border-top: 1px solid #ddd;">
                        <p>Thank you for being a valued member of our community.</p>
                        <p style="font-size: 0.9em;">&copy; 2024 Crypto Project. All rights reserved.</p>
                    </footer>
                </main>
            </body>
        </html>
        """
        self.send_email(receiver_email, subject, message_html)

    async def recommendation_email(self, receiver_email, subject, recommendation: dict):
        crypto_name = recommendation.get("crypto_name", "")
        headline = recommendation.get("headline", "")
        subtitle = recommendation.get("subtitle", "")
        details = recommendation.get("details", "")
        investment_advice = recommendation.get("investment_advice", "")
        image_url = recommendation.get("image_url", [])

        image_html = f'<img src="{image_url}" alt="Image" style="max-width: 100%; height: auto; margin-top: 20px;">' if image_url else ''

        message_html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6; background-color: #f9f9f9; margin: 0; padding: 0;">
                <header style="background: #008CBA; color: white; padding: 20px 0; text-align: center;">
                    <h1 style="margin: 0; font-size: 24px;">{headline}</h1>
                </header>
                <main style="padding: 20px;">
                    <section style="background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);">
                        <h2 style="color: #008CBA; font-size: 22px; margin-top: 0;">{subtitle}</h2>
                        <p style="color: #333; font-size: 18px; margin-top: 0;">{details}</p>
                        {image_html}
                    </section>
                    <section style="margin-top: 20px;">
                        <h2>Investment Advice for {crypto_name}</h2>
                        <ul style="padding-left: 20px; margin-top: 0;">
                            {"".join([f"<li>{item}</li>" for item in investment_advice])}
                        </ul>
                        <p style="margin-top: 20px;">Based on our recent analysis, we suggest considering the above recommendations to enhance your portfolio.</p>
                        <p>For a more detailed report, please visit our <a href="#" style="color: #008CBA; text-decoration: none;">recommendations page</a> or contact our support team.</p>
                    </section>
                    <footer style="margin-top: 20px; padding-top: 10px; border-top: 1px solid #ddd; text-align: center;">
                        <p>Thank you for being a valued member of our community.</p>
                        <p style="font-size: 0.9em;">&copy; 2024 Crypto Project. All rights reserved.</p>
                    </footer>
                </main>
            </body>
        </html>
        """
        self.send_email(receiver_email, subject, message_html)



    def alert_email(self, receiver_email, subject, alert):
        message_html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6;">
                <header style="background: #FF0000; color: white; padding: 10px 0; text-align: center;">
                    <h1 style="margin: 0;">Crypto Project - Alert</h1>
                </header>
                <main style="padding: 20px;">
                    <h2>Alert</h2>
                    <p>{alert}</p>
                    <p>We urge you to take immediate action to address this alert. Please follow the steps below:</p>
                    <ul>
                        <li>Check your account for any suspicious activity.</li>
                        <li>Update your security settings.</li>
                        <li>Contact our support team if you need assistance.</li>
                    </ul>
                    <p>For more details, visit our <a href="#">alert page</a>.</p>
                    <footer style="margin-top: 20px; padding-top: 10px; border-top: 1px solid #ddd;">
                        <p>Thank you for being a valued member of our community.</p>
                        <p style="font-size: 0.9em;">&copy; 2024 Crypto Project. All rights reserved.</p>
                    </footer>
                </main>
            </body>
        </html>
        """
        self.send_email(receiver_email, subject, message_html)

        async def advise_emai(self, receiver_email, subject, message: dict):
            headline = message["headline"]
            subtitle = message["subtitle"]
            rest_message = message["rest_message"]

            try:
                # Get other values
                positions = await self.get_positions()
                future_assets_ps = await self.get_future_possitions()

                # Calculate required values
                usdt_used = sum(float(tot['marginSize']) for tot in positions['data'])
                total_assets = float(future_assets_ps['data'][0]['usdtEquity'])
                available = total_assets - usdt_used
            except TypeError:
                total_assets = None
                usdt_used = None
                available = None        

            message_html = f"""
                <html>
                    <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6; background-color: #f9f9f9; margin: 0; padding: 0;">
                        <header style="background: #FFA500; color: white; padding: 20px 0; text-align: center;">
                            <h1 style="margin: 0; font-size: 24px;">Crypto Project - Advisory Notice</h1>
                        </header>
                        <main style="padding: 20px;">
                            <section style="background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);">
                                <h2 style="color: #FFA500; margin-top: 0;">{headline.upper()}</h2>
                                <h3 style="color: #333; margin-top: 0;">{subtitle}</h3>
                                <p>{rest_message}</p>
                            </section>
                            <section style="margin-top: 20px;">
                                <h2>Financial Overview</h2>
                                <p>Total Assets: <strong>${total_assets:.2f} USDT</strong></p>
                                <p>USDT Used: <strong>${usdt_used:.2f} USDT</strong></p>
                                <p>Available Balance: <strong>${available:.2f} USDT</strong></p>
                            </section>
                            <section style="margin-top: 20px;">
                                <h2>Actions to Consider</h2>
                                <ul style="padding-left: 20px;">
                                    <li>Review your current portfolio.</li>
                                    <li>Stay informed about market trends.</li>
                                    <li>Consider diversifying your investments.</li>
                                </ul>
                                <p>For more detailed advice, please check out the <a href="https://www.investing.com/economic-calendar/" style="color: #FFA500; text-decoration: none;">economic calendar</a>.</p>
                            </section>
                            <footer style="margin-top: 20px; padding-top: 10px; border-top: 1px solid #ddd; text-align: center;">
                                <p>Thank you for being a valued member of our community.</p>
                                <p style="font-size: 0.9em;">&copy; 2024 Crypto Project. All rights reserved.</p>
                            </footer>
                        </main>
                    </body>
                </html>
            """ if total_assets is not None and usdt_used is not None and available is not None else f"""
                <html>
                    <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6; background-color: #f9f9f9; margin: 0; padding: 0;">
                        <header style="background: #FFA500; color: white; padding: 20px 0; text-align: center;">
                            <h1 style="margin: 0; font-size: 24px;">Crypto Project - Advisory Notice</h1>
                        </header>
                        <main style="padding: 20px;">
                            <section style="background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);">
                                <h2 style="color: #FFA500; margin-top: 0;">{headline.upper()}</h2>
                                <h3 style="color: #333; margin-top: 0;">{subtitle}</h3>
                                <p>{rest_message}</p>
                            </section>
                            <section style="margin-top: 20px;">
                                <h2>Allow our IP to your Bitget API configuration!</h2>
                                <img src="https://travel360-images-handle.s3.eu-north-1.amazonaws.com/images/image_example.jpg" alt="Italian Trulli" style="width: 50%; height: auto;">
                                <p>Our IP address is <b>{"18.227.161.231"}</b></p>
                            </section>
                            <section style="margin-top: 20px;">
                                <h2>Actions to Consider</h2>
                                <ul style="padding-left: 20px;">
                                    <li>Review your current portfolio.</li>
                                    <li>Stay informed about market trends.</li>
                                    <li>Consider diversifying your investments.</li>
                                </ul>
                                <p>For more detailed advice, please check out the <a href="https://www.investing.com/economic-calendar/" style="color: #FFA500; text-decoration: none;">economic calendar</a>.</p>
                            </section>
                            <footer style="margin-top: 20px; padding-top: 10px; border-top: 1px solid #ddd; text-align: center;">
                                <p>Thank you for being a valued member of our community.</p>
                                <p style="font-size: 0.9em;">&copy; 2024 Crypto Project. All rights reserved.</p>
                            </footer>
                        </main>
                    </body>
                </html>
            """
            self.send_email(receiver_email, subject, message_html)

    async def error_email(self, subject, message):
        receiver_email = "paumat17@gmail.com"
        message_html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6; background-color: #f9f9f9; margin: 0; padding: 0;">
                <header style="background: #d9534f; color: white; padding: 30px 0; text-align: center;">
                    <h1 style="margin: 0; font-size: 28px;">Error Notification</h1>
                </header>
                <main style="padding: 30px;">
                    <section style="background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);">
                        <h2 style="color: #d9534f; font-size: 24px; margin-top: 0;">{subject}</h2>
                        <p style="color: #333; font-size: 18px; margin-top: 10px;">{message}</p>
                    </section>
                    <footer style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; text-align: center;">
                        <p style="font-size: 16px;">Thank you for your attention to this matter.</p>
                        <p style="font-size: 14px;">&copy; 2024 Your Company. All rights reserved.</p>
                    </footer>
                </main>
            </body>
        </html>
        """
        self.send_email(receiver_email, subject, message_html)

# Example usage:
email_sender = EmailSender(
    token_path=os.path.join(os.getcwd(), "services/schedule_taks/credentials/emailtoken.json"),
    creds_path=os.path.join(os.getcwd(), "services/schedule_taks/credentials/credentials.json"), 
    sender_email='devtravel36o@gmail.com'
)

async def main_test():
    message_body = {
            "crypto_name": "FEAR AND GREED",
            "headline": "Fear and Greed Notification",
            "subtitle": "Maybe it's time to invest in bitcoin",
            "details": "Bitcoin it's falling for 5 months, and its price it's in a good point to buy, but keep in mind that it hasn't fallen a 70% to consider invest",
            "investment_advice": []
        }
    
    await email_sender.recommendation_email("paumat17@gmail.com", "Fear and Gredd today's notification", message_body)

if __name__ == "__main__":
    asyncio.run(main_test())