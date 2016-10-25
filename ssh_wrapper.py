#!/usr/bin/env python
#
# Author:  Mike Pietruszka
# Date:    Oct 24th, 2016
# Summary: SSH wrapper
#
# TODO:
#

import sys
import paramiko
import getpass
import argparse
import multiprocessing
import socket

def ssh_op(host, username, password, port, command):
    '''
    Establish the connection; don't forget to auto-add the host key
    '''
    hostname = host

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(hostname, username=username, password=password, allow_agent=True)

        ''' Run some commands '''
        try:
            stdin, stdout, stderr = ssh.exec_command(command)
        except paramiko.SSHException:
            print "Could not execute remote command"
        finally:
            for line in stdout.readlines():
                print ''.join(line.encode('ascii', 'ignore').split())
    except paramiko.BadHostKeyException:
        print "SSH Host Key could not be verified"
    except paramiko.AuthenticationException:
        print "Authentication failed"
    except (paramiko.SSHException, socket.gaierror):
        print "Failed to connect to {hostname}".format(hostname=hostname)
    finally:
        ssh.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SSH Wrapper that runs commands against hosts in parallel")
    parser.add_argument('-H', action='append', dest='hosts', nargs='+', help="Hosts", required=True)
    parser.add_argument('-P', action='store_true', dest='parallel', help="Parallel processing")
    parser.add_argument('-u', action='store', dest='username', help="Username")
    parser.add_argument('-p', action='store', dest='port', help="SSH port")
    parser.add_argument('-k', action='store_true', dest='pki', help="Use ssh-agent and SSH key authentication")
    parser.add_argument('-a', action='store', dest='command', help="Remote command", required=True)
    parser.add_argument('-v', action='version', version='%(prog)s 1.3', help="Prints a version number")
    results = parser.parse_args()

    if not vars(results):
        parser.print_help()
        sys.exit(0)

    if results.username:
        username = results.username
        password = getpass.getpass()
    elif results.pki:
        username = getpass.getuser()
        password = None
    else:
        # get password from current running user
        username = getpass.getuser()
        password = getpass.getpass()

    if not results.port:
        port = 22

    if not results.command:
        print "Please specify a remote command to run. Exiting."
        sys.exit(1)
    else:
        command = results.command

    if results.parallel:
        print "Running in parallel"
        jobs = []
        for host in results.hosts:
            host = ''.join(host)
            print host + ":"
            p = multiprocessing.Process(
                target=ssh_op, args=(host, username, password, port, command))
            jobs.append(p)
            p.start()
    else:
        for host in results.hosts:
            host = ''.join(host)
            print host + ":"
            ssh_op(host, username, password, port, command)