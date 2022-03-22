#!/usr/bin/python

import os, argparse


def main():
    parser = argparse.ArgumentParser(
        description="Little script for installing and setting up WireGuard")
    parser.add_argument('-p', '--port', metavar="PORT", type=int, nargs=1,
                        help="custom server port (default - 51820)", default=51820,
                        dest="port")
    args = parser.parse_args()

    createServerKeys()
    privateKey = ""
    with open("server_privatekey", "r+") as privateKeyFile:
        privateKey = privateKeyFile.read().strip()
    createWgConf(privateKey, args.port)
    setUpIpForward()
    enableSystemctl()


def createServerKeys():
    print("Creating server private key...")
    print("Creating server public key...")
    os.system("wg genkey | tee server_privatekey | wg pubkey | tee server_publickey")
    os.system("chmod 600 server_privatekey")
    # open("server_privatekey", "w+").write("some private key\n")
    # open("server_publickey", "w+").write("some public key\n")
    print("Created!")


def createWgConf(privateKey, port):
    print(f"Creating WireGuard config...")
    wgConfig = f'''[Interface]
PrivateKey = {privateKey}
Address = 10.0.0.1/24
ListenPort = {port}
PostUp = iptables -A FORWARD -i %i -j ACCEPT; iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
PostDown = iptables -D FORWARD -i %i -j ACCEPT; iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE
'''
    with open("wg.conf", "w+") as config:
        config.write(f"{wgConfig}")
    print("Created!")


def setUpIpForward():
    print("Setting up IP forwarding...")
    os.system('echo "net.ipv4.ip_forward=1" >> /etc/sysctl.conf')
    print("Done!")


def enableSystemctl():
    print("Enabling systemd demon...")
    os.system("systemctl enable wg-quick@wg0.service")
    os.system("systemctl start wg-quick@wg0.service")
    print("Done!")


main()
