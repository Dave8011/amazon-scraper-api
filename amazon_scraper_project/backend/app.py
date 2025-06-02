# app.py

import os
import pandas as pd
from datetime import datetime
import csv
import smtplib
import mimetypes
from email.message import EmailMessage
from dotenv import load_dotenv
from bot import amazon_main

load_dotenv()

def send_email(output_filename, recipient_email, pincodes, company):
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_PASSWORD")
    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = int(os.getenv("SMTP_PORT"))

    timestamp_now = datetime.now().strftime("Date: %d-%m-%Y TIME:%H:%M:%S")
    subject = f"Amazon Scraped Data CSV - {company} - {timestamp_now}"
    body = f"Attached is the Amazon data for {company}.\nPincodes: {pincodes}\nTime: {timestamp_now}"

    msg = EmailMessage()
    msg["From"] = sender_email
    msg["To"] = recipient_email
    msg["Subject"] = subject
    msg.set_content(body)

    with open(output_filename, "rb") as file:
        file_data = file.read()
        file_name = os.path.basename(output_filename)
        msg.add_attachment(file_data, maintype="application", subtype="octet-stream", filename=file_name)

    try:
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)
        print(f"Email sent to {recipient_email}")
    except Exception as e:
        print(f"Error sending email: {e}")

def main(company, pincodes, city_map, sendMailFlag, recipient_email, getCompetitorFlag, getProductTitleFlag):
    os.makedirs("./amazon_data", exist_ok=True)
    csv_file_path = f'./{company}.csv'

    if not os.path.exists(csv_file_path):
        print(f"File not found: {csv_file_path}")
        return

    try:
        df = pd.read_csv(csv_file_path)
        asin_list = df.iloc[:, 0].tolist()
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return

    host_url = "https://www.amazon.in/dp/"
    timestamp_now = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
    output_filename = f"./amazon_data/{company}_{timestamp_now}.csv"

    with open(output_filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        if getProductTitleFlag:
            writer.writerow(['Asin','buy_box_flag','Timestamp','Pincode','City','Seller','Price','coupon_text','Free Delivery','Fastest Delivery','seller count','Minimum Price','product_title'])
        else:
            writer.writerow(['Asin','buy_box_flag','Timestamp','Pincode','City','Seller','Price','coupon_text','Free Delivery','Fastest Delivery','seller count','Minimum Price'])

    amazon_main(pincodes, asin_list, host_url, output_filename, city_map, getCompetitorFlag, getProductTitleFlag)

    print(f"All data written to {output_filename}")

    if sendMailFlag and recipient_email:
        send_email(output_filename, recipient_email, pincodes, company)
