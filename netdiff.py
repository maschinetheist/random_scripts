#!/usr/bin/env python
#
# Author:  Mike Pietruszka
# Date:    Oct 25th, 2016
# Summary: SSH-based net diff implementation to be used to compare files on 
#          different hosts
#
# TODO:
#

import paramiko
import getpass
import sys
import os
import tempfile
import argparse
import difflib
import socket

def sftp_op(host, username, password, port, remote_file, local_path):
    ''' Establish ssh connection to pull the remote file locally '''
    hostname = host

    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname, username=username, password=password, 
            allow_agent=True)

        sftp = ssh.open_sftp()
        sftp.get(remote_file, local_path)
    except paramiko.BadHostKeyException:
        print "SSH Host Key could not be verified"
        sys.exit(1)
    except paramiko.AuthenticationException:
        print "Authentication failed"
        sys.exit(1)
    except (paramiko.SSHException, socket.gaierror):
        print "Could not connect to remote host {hostname}".format(
            hostname=hostname)
        sys.exit(1)
    finally:
        sftp.close()
        ssh.close()


def compare(local_file, local_path, remote_file):
    remote_file = local_path
    remote_file_contents = None
    local_file_contents = None

    with open(remote_file, 'r') as rf:
        remote_file_contents = rf.read()
    rf.close()

    with open(local_file, 'r') as lf:
        local_file_contents = lf.read()
    lf.close()

    local_file_contents = local_file_contents.splitlines()  
    remote_file_contents = remote_file_contents.splitlines()    

    diff = difflib.unified_diff(local_file_contents, remote_file_contents,
        lineterm='')
    print '\n'.join(list(diff))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Diff local files against files on remote hosts")
    parser.add_argument('-p', '--port', action='store', dest='port', help="SSH port")
    parser.add_argument('-k', action='store_true', dest='pki', 
        help="Use ssh-agent and SSH key authentication")
    parser.add_argument('local_file', nargs=1, help="local file")
    parser.add_argument('remote_file', nargs='*', help="[USER@]HOST:file")
    parser.add_argument('-v', action='version', version='%(prog)s 1.3', 
        help="Prints a version number")
    results, extras = parser.parse_known_args()
    results.local_file.extend(extras)
    results.remote_file.extend(extras)

    if not vars(results):
        parser.print_help()
        sys.exit(0)
    
    if results.pki:
        # force ssh pubkey auth
        password = None
    else:
        # ask for password
        password = getpass.getpass()

    if not results.port:
        port = 22

    for remote_uri in results.remote_file:
        print remote_uri + ":"

        local_file = ''.join(results.local_file)
        remote_uri = ''.join(remote_uri)

        if "@" in remote_uri:
            username = remote_uri.split("@")[0]
            remote_uri = remote_uri.split("@")[1]
        else:
            # if we didn't supply username in uri, get local username
            username = getpass.getuser()
        host = remote_uri.split(":")[0]
        remote_file = remote_uri.split(":")[1]

        try:
            # Need to create a named temporary file. It'll be removed
            # when we close it. Make sure to use local_path.name as we
            # can't reference an instance object of the temporary file.
            local_path = tempfile.NamedTemporaryFile()

            sftp_op(host, username, password, port, remote_file, local_path.name)
            local_path.seek(0)
            compare(local_file, local_path.name, remote_file)
            print ''
        finally:
            local_path.close()