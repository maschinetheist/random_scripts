#!/usr/bin/env python

import paramiko
import getpass
import sys
import argparse
import difflib

def sftp_op(host, username, password, port, remote_file, local_path):
	''' Establish ssh connection to pull the remote file locally '''
	hostname = host

	ssh = paramiko.SSHClient()
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	ssh.connect(hostname, username=username, password=password, allow_agent=True)

	sftp = ssh.open_sftp()
	sftp.get(remote_file, local_path)

	sftp.close()
	ssh.close()


def compare(local_file, local_path, remote_file):
	remote_file = local_path
	remote_file_contents = None
	local_file_contents = None

	with open(remote_file, 'r') as rf:
		remote_file_contents = rf.readline()
	rf.close()

	with open(local_file, 'r') as lf:
		local_file_contents = lf.readline()
	lf.close()

	local_file_contents = local_file_contents.splitlines()	
	remote_file_contents = remote_file_contents.splitlines()	

	#d = difflib.Differ()
	#diff = d.compare(local_file_contents, remote_file_contents)
	diff = difflib.unified_diff(local_file_contents, remote_file_contents, lineterm='')
	print '\n'.join(list(diff))

host = sys.argv[1]
username = getpass.getuser()
password = getpass.getpass()
port = 22
local_file = "/tmp/testfile"
local_path = "/tmp/testfile2"
remote_file = "/tmp/test"

sftp_op(host, username, password, port, remote_file, local_path)
compare(local_file, local_path, remote_file)