#!/usr/bin/env python

import smtplib
import sqlite3
import os
import configparser
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


databases = []
remote = []
modem = []
gateway = []


def open_database():
    'Open sqlite database'
    for item in os.listdir('.'):
        if '.db' in item:
            databases.append(item)

    databases.sort(reverse=True)
    database = databases.pop(0)
    conn = sqlite3.connect(database)
    c = conn.cursor()

    return c


def read_data(c):
    'Read data from sqlite databsase'
    for row in c.execute('''SELECT * FROM pings WHERE host="{}"'''.format(remote_host)):
        remote.append(row)

    for row in c.execute('''SELECT * FROM pings WHERE host="{}"'''.format(modem_host)):
        modem.append(row)

    for row in c.execute('''SELECT * FROM pings WHERE host="{}"'''.format(gateway_host)):
        gateway.append(row)


def get_averages(data):
    'Return average and highest and lowest ping in list'
    if not len(data) == 0:
        average_ping = sum([float(x[3]) for x in data]) / len(data)
        max_ping = max(data, key=lambda x: x[3])
        min_ping = min(data, key=lambda x: x[3])
    else:
        average_ping = ''
        max_ping = ''
        min_ping = ''

    return average_ping, max_ping, min_ping


def get_long_requests(data):
    'Return pings > 50 ms'
    if not len(data) == 0:
        for x in data:
            if float(x[3]) > float(40):
                return x


def send_email(email_message_text, email_message_data):
    'Send report email'
    message = MIMEMultipart('related')
    message['Subject'] = 'ISPMon Report'
    message['From'] = email_sender
    message['To'] = email_recipient
    message.preamble = 'This is a multi=part message in MIME format.'

    message_alternative = MIMEMultipart('alternative')
    message.attach(message_alternative)
    message_text = MIMEText('{}\n {}'.format(email_message_text,
                                             email_message_data))

    message_text = MIMEText('<h3>{}</h3><pre>{}</pre>'.format(email_message_text,
                                                              email_message_data))

    message_text.replace_header('Content-Type', 'text/html')
    message_alternative.attach(message_text)

    s = smtplib.SMTP(email_server, email_port)
    s.starttls()
    s.login(email_sender, email_password)
    s.sendmail(email_sender, email_recipient, message.as_string())
    s.quit()


# Load data from config file
parser = configparser.ConfigParser()
parser.read('config')

remote_host = parser.get('Hosts', 'remote')
modem_host = parser.get('Hosts', 'modem')
gateway_host = parser.get('Hosts', 'gateway')
email_recipient = parser.get('Email', 'recipient')
email_sender = parser.get('Email', 'sender')
email_password = parser.get('Email', 'password')
email_server = parser.get('Email', 'server')
email_port = parser.get('Email', 'port')

# Open sqlite database and load data
c = open_database()
read_data(c)

remote_average = get_averages(remote)
modem_average = get_averages(modem)
gateway_average = get_averages(gateway)

remote_long = get_long_requests(remote)
modem_long = get_long_requests(modem)
gateway_long = get_long_requests(gateway)

# Build email message
email_message_text = 'Daily ISPMon Report'
email_message_data = '''
Remote Host Average Response = {}
Remote Host Maximum Response = {} {}
Remote Host Minimum Response = {} {}

Modem Average Response = {}
Modem Maximum Reponse = {} {}
Modem Minimum Response = {} {}

Gateway Average Response = {}
Gateway Maximum Reponse = {} {}
Gateway Minimum Reponse = {} {}

Remote Responses > 50 ms
{}

Modem Responses > 50 ms
{}

Gateway Responses > 50 ms
{}
'''.format(remote_average[0], remote_average[1][0], remote_average[1][3],
           remote_average[2][0], remote_average[2][3], modem_average[0],
           modem_average[1][0], modem_average[1][3], modem_average[2][0],
           modem_average[2][3], gateway_average[0], gateway_average[1][0],
           gateway_average[1][3], gateway_average[2][0],
           gateway_average[2][3], remote_long, modem_long, gateway_long)

print(email_message_text)
print(email_message_data)

send_email(email_message_text, email_message_data)
