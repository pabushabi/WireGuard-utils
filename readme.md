# WireGuard-utils
This is a simple set of python scripts that will help you to set up your WireGuard server  
## Usage:  
### Install WireGuard 
First you need to install WireGuard
Depending on your OS you should run:
#### Ubuntu
```
sudo apt install wireguard
```
#### Debian
```
apt install wireguard
```
#### CentOS 8
```
sudo yum install elrepo-release epel-release
sudo yum install kmod-wireguard wireguard-tools
```
See all distros [here](https://www.wireguard.com/install/)
### Configure
Now all you need is run this scripts
```
python3 install.py [--port 51830(optionally)]
```
Then to add a new user(s) you should run 
```
python3 addclient.py username1 username2... --ip <your-server-ip-here>
```
Then you need to import WireGuard tunnel config file from `clients/wg-<username>.conf` to your WireGuard client app on your phone (laptop, PC, whatever...)
### Usage 
##### Install script
```
usage: install.py [-h] [-p PORT]

Little script for setting up WireGuard

optional arguments:
  -h, --help            show this help message and exit
  -p PORT, --port PORT  custom server port (default - 51820)
```
##### Client addition script
```
usage: addclient.py [-h] -i IP [-p PORT] [-d DNS] NAME [NAME ...]

Little script for creating new WireGuard users(clients)

positional arguments:
  NAME                  names of new clients

optional arguments:
  -h, --help            show this help message and exit
  -i IP, --ip IP        server ip
  -p PORT, --port PORT  custom server port (default - 51820)
  -d DNS, --dns DNS     custom dns server (default - 1.1.1.1)
```
##### Telegram bot
usage: bot.py

Little telegram bot for wg management. Supports client addition, getting list of existing configs, downloading configs, checking and restarting systemctl status. Works only for whitelisted users.

Configuring .env is required:
```
TELEGRAM_BOT_TOKEN=<YOUR-TELEGRAM-BOT-TOKEN>
WHITELIST_USER_IDS=<USER-ID>,<USER-ID>,...
CLIENTS_DIR=/wireguard/clients
SERVICE_NAME=wg-quick@wg.service
SCRIPT_PATH=/wireguard/addclient.py
```

Run bot any method you prefer (nohup, tmux, systemd)