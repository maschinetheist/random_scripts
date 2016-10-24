#!/usr/bin/env python

import sys
import paramiko
import getpass

''' 
Determine parameters from command line arguments; 
i.e. username and hostname
'''
uri = sys.argv[1]
if "@" in uri: 
	uri = uri.split("@")
	username = uri[0]
	hostname = uri[1]
else:
	username = raw_input("Username: ")
	hostname = uri
passwd = getpass.getpass()

'''
Establish the connection; don't forget to auto-add the host key
'''
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(
	paramiko.AutoAddPolicy())
ssh.connect(hostname, username=username, password=passwd)

''' Run some commands '''
command = sys.argv[2]
stdin, stdout, stderr = ssh.exec_command(command)
for line in stdout.readlines():
	print line.split('\n')