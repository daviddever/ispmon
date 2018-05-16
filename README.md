ispmon
============

A small tool for logging ping requests from your gateway, modem and a remote site.
Pings are sent each second to all three destinations and then logged in a sqlite database.

The OS's ping utilty is used to send the ping requests so the script does not need to be run as root.

After 24 hours a new database is created.

Information from databases can be printed on screen and sent via email.

Installation
------------

The following assumes Ubuntu and Python 3

### Install pip

```
sudo apt-get install python-pip sqlite3
sudo pip install -U pip
```

### Setup Virtualenv

```
sudo pip install virtualenv
virtualenv -p /usr/local/bin/python3 venv
source venv/bin/activate
```

### Install script requirements

```
pip install -r requirements.txt
```


### Edit values in config file
```
vim config
```

### ispmon.py
This script creates a sqlite database and then uses the OS's ping utility to send ping requests to the gateway, modem inside address, and a remote site (all defined in the config file).

New databases are created after running for 24 hours

### reporter.py
Pulls information from the most recent database file and then prints and sends a report to the email address configured in the config file.
