#!/usr/bin/python

import os, argparse
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        description="Little script for creating new WireGuard users(clients)")
    parser.add_argument('clients', metavar="NAME", type=str, nargs="+", help="names of new clients")
    parser.add_argument('-i', '--ip', metavar="IP", type=str, nargs=1, help="server ip",
                        required=True, dest="serverIp")
    parser.add_argument('-p', '--port', metavar="PORT", type=int, nargs=1,
                        help="custom server port (default - 51820)", default=[51820],
                        dest="serverPort")
    parser.add_argument('-d', '--dns', metavar="DNS", type=str, nargs=1,
                        help="custom dns server (default - 1.1.1.1)", default="1.1.1.1", dest="dns")
    args = parser.parse_args()

    for client in args.clients:
        privateName = f"{client}_privatekey"
        publicName = f"{client}_publickey"
        if (not isClientExists(client)):
            createKeys(client, privateName, publicName)
            privateKey = ""
            publicKey = ""
            with open(f"keys/{privateName}", 'r+') as privateKeyFile:
                privateKey = privateKeyFile.read().strip()
            with open(f"keys/{publicName}", 'r+') as publicKeyFile:
                publicKey = publicKeyFile.read().strip()
            ip = getIp()
            addWgConfig(client, publicKey, ip)
            createClientConfig(client=client, privateKey=privateKey, ip=ip, dns=args.dns,
                               serverIp=args.serverIp[0], serverPort=args.serverPort[0])
            print(f"Success! Client {client} created.")
        else:
            print(f"Client with name {client} already existing! Try another name.")


def isClientExists(client):
    if (os.path.isfile(f"keys/{client}_privatekey") or os.path.isfile(f"clients/wg-{client}.conf")):
        return True
    return False


def createKeys(client, privateName, publicName):
    print(f"Creating private key {privateName}...")
    print(f"Creating public key {publicName}...")
    Path("keys").mkdir(parents=True, exist_ok=True)
    os.system(f"wg genkey | tee keys/{client}_privatekey | wg pubkey | tee keys/{client}_publickey")
    # open(f"keys/{privateName}", "w+").write("some private key\n")
    # open(f"keys/{publicName}", "w+").write("some public key\n")
    print("Created!")


def getIp():
    ip = "10.0."
    with open("wg0.conf", "r") as config:
        configContent = config.read()
        if (configContent.count("AllowedIPs") == 0):
            return f"{ip}0.2/32"
        lastQuartet = configContent.split(" ")[-1].split("/")[0].split(".")[-1]
        prevQuartet = configContent.split(" ")[-1].split("/")[0].split(".")[-2]
        if (int(lastQuartet) + 1 > 255):
            lastQuartet = 1
            prevQuartet = int(prevQuartet) + 1
        else:
            lastQuartet = int(lastQuartet) + 1
        return f"{ip}{prevQuartet}.{lastQuartet}/32"


def addWgConfig(client, publicKey, ip):
    print(f"Adding {client} to WireGuard config...")
    wgConfig = f'''[Peer]
PublicKey = {publicKey}
AllowedIPs = {ip}
'''
    with open("wg0.conf", "a") as config:
        config.write(f"\n{wgConfig}")
    print("Added!")


def getServerPublicKey():
    if (os.path.isfile("server_publickey")):
        with open("server_publickey", "r") as serverPubKey:
            return serverPubKey.read().strip()
    return ""


def createClientConfig(client, privateKey, ip, dns, serverIp, serverPort):
    print(f"Creating client {client} config...")
    serverPublicKey = getServerPublicKey()
    if (serverPublicKey == ""):
        print("server_publickey not found! Aborting...")
        return
    clientConfig = f'''[Interface]
PrivateKey = {privateKey}
Address = {ip}
DNS = {dns}

[Peer]
PublicKey = {serverPublicKey}
Endpoint = {serverIp}:{serverPort}
AllowedIPs = 0.0.0.0/0
PersistentKeepalive = 20
'''
    Path("clients").mkdir(parents=True, exist_ok=True)
    with open(f'clients/wg-{client}.conf', 'w+') as config:
        config.write(f"{clientConfig}")
    print(f"Created!\nConfig saved at '{os.getcwd()}/clients/wg-{client}.conf'")


main()
