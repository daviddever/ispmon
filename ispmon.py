#!/usr/bin/env python

import datetime
import pingparser
import subprocess
import shlex
import sqlite3
import sys
import time
import configparser


def ping(address):
    'Ping address and return the parsed results'
    command = 'ping -c 1 ' + address
    args = shlex.split(command)
    try:
        output = subprocess.check_output(args, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError:
        print('Error pinging address. Check hosts in config file.')
        sys.exit(1)

    output = str(output).strip()
    results = pingparser.parse(output)

    return results


def log(data):
    'Write ping data to database'
    ping_time = str(datetime.datetime.now())
    ping_host = data['host']
    ping_packet_loss = data['packet_loss']
    ping_average = data['avgping']

    c.execute('INSERT INTO pings (datetime, host, packet_loss, ping) VALUES'
              + ' (?,?,?,?)', (ping_time, ping_host, ping_packet_loss,
                               ping_average))
    conn.commit()
    print(ping_time + ping_host + ping_packet_loss + ping_average)


def create_db(db_name):
    'Create sqlite database with db_name'
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS pings
                 (datetime text, host text, packet_loss text, ping)''')


# Load Values fomr Config file
parser = configparser.ConfigParser()
parser.read('config')

remote_address = parser.get('Hosts', 'remote')
modem_address = parser.get('Hosts', 'modem')
gateway_address = parser.get('Hosts', 'gateway')

addresses = [remote_address, modem_address, gateway_address]

# Create sqlite database named with current time
db_creation_time = time.time()
current_db = str(db_creation_time) + '.db'
create_db(current_db)
conn = sqlite3.connect(current_db)
c = conn.cursor()

# Ping hosts each second and record results to database, if the database is
# older than 21600 create and load a new database file
while True:
    if time.time() >= db_creation_time + 21600:
        conn.close()
        db_creation_time = time.time()
        current_db = str(db_creation_time)
        create_db(current_db)

    for address in addresses:
        log(ping(address))

    time.sleep(1)
