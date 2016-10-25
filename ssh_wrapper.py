#!/usr/bin/env python
#
# Author:  Mike Pietruszka
# Date:    Oct 24th, 2016
# Summary: SSH wrapper
#

import sys
import paramiko
import getpass
import argparse
import multiprocessing

def ssh_op(host, username, password, port, command):
	'''
	Establish the connection; don't forget to auto-add the host key
	'''
	hostname = host

	ssh = paramiko.SSHClient()
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	ssh.connect(hostname, username=username, password=password, allow_agent=True)

	''' Run some commands '''
	stdin, stdout, stderr = ssh.exec_command(command)
	for line in stdout.readlines():
		print ''.join(line.encode('ascii', 'ignore').split())

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="SSH Wrapper that runs commands against hosts in parallel")
	parser.add_argument('-H', action='append', dest='hosts', nargs='+', help="Hosts", required=True)
	parser.add_argument('-P', action='store_true', dest='parallel', help="Parallel processing")
	parser.add_argument('-u', action='store', dest='username', help="username")
	parser.add_argument('-p', action='store', dest='port', help="SSH port")
	parser.add_argument('-k', action='store_true', dest='pki', help="Use ssh-agent and SSH key authentication")
	parser.add_argument('-a', action='store', dest='command', help="remote command", required=True)
	parser.add_argument('-v', action='version', version='%(prog)s 1.0', help="Prints a version number")
	results = parser.parse_args()

	if not vars(results):
		parser.print_help()
		sys.exit(0)

	if results.username:
		password = getpass.getpass()
	if results.pki:
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