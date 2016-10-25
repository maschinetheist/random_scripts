#!/usr/bin/env python
#
# Author:  Mike Pietruszka
# Date:    Oct 25th, 2016
# Summary: SSH-based net diff implementation to be used to compare files on 
#		   different hosts
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

	diff = difflib.unified_diff(local_file_contents, remote_file_contents, lineterm='')
	print '\n'.join(list(diff))

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Diff local files against remote files")
	parser.add_argument('-H', action='store', nargs='+', dest='hosts', required=True)
	parser.add_argument('-u', action='store', dest='username', help="Username")
	parser.add_argument('-p', action='store', dest='port', help="SSH port")
	parser.add_argument('-k', action='store_true', dest='pki', help="Use ssh-agent and SSH key authentication")
	parser.add_argument('files', nargs='*') #, action='append')
	parser.add_argument('-v', action='version', version='%(prog)s 1.1', help="Prints a version number")
	results, extras = parser.parse_known_args()
	results.files.extend(extras)

	if not vars(results):
		parser.print_help()
		sys.exit(0)

	if results.hosts: 
		if results.username:
			username = results.username
			password = getpass.getpass()
		elif results.pki:
			username = getpass.getuser()
			password = None
		else:
			username = getpass.getuser()
			password = getpass.getpass()

		if not results.port:
			port = 22

		for host in results.hosts:
			print results.files
			local_file = results.files[0]
			remote_file = results.files[1]

			try:
				# Need to create a named temporary file. It'll be removed
				# when we close it. Make sure to use local_path.name as we
				# can't reference an instance object of the temporary file.
				local_path = tempfile.NamedTemporaryFile()

				sftp_op(host, username, password, port, remote_file, local_path.name)
				local_path.seek(0)
				compare(local_file, local_path.name, remote_file)
			finally:
				local_path.close()