#!/usr/bin/python
import paramiko
import sys
import subprocess
import logging
import re
import time
import os
import traceback
import telnetlib
import socket
import atexit
import json
import select
from datetime import datetime,timedelta
import sqlite3

def runRemoteCmd(host, cmd, filename, user='username', pw='password',fwrite="yes"):
	ssh = paramiko.SSHClient()
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	stdin = stdout = stderr = ''
	status = -1
	try:
		ssh.connect(host, username=user, password=pw)
		channel = ssh.get_transport().open_session()
		logging.debug("Running cmd:%r on host:%r" % (cmd, host))
		print "Running cmd:%r on host:%r" % (cmd, host)
		channel.exec_command(cmd)
		status = channel.recv_exit_status()
		buf = ''
		while channel.recv_ready():
			buf += channel.recv(1024)
		if fwrite == "yes":
			file_out =open(filename, 'a')
			file_out.write(buf)
		status = channel.recv_exit_status()
		return buf
	except:
		traceback.print_exc()
		print "Not able to SSH ILO!!! Have a check on ILO Session State!!!"
	ssh.close()
	if (status != 0):
		logging.warning("Failed to run cmd:'%r' exit: %d" % (cmd, status))
	return status

def main():
	files = open("testbeds.json")
	servers = json.load(files)
	format='%Y-%m-%d %H:%M:%S'
	conn = sqlite3.connect('test.db')
	
	for ilo in servers["dell7"]:
		results_dell7 = { "severity" : None, "date" : None, "time" : None, "description" : None }
		print " I have entered the loop"
                filename="logs/" + ilo + ".txt"
		totalcmd = 'racadm getsel -i'
		total = runRemoteCmd(ilo, totalcmd, filename, user='username',pw='password')
		total = total.replace("Total Records:", "", 1)
		total_cleaned = max(int(total.strip()) - 30,1)
		cmd = 'racadm getsel -o -s ' + str(total_cleaned)
                if (runRemoteCmd(ilo, cmd, filename, user='username',pw='password')!=0):
			pass
			print "I am inside loop and checking for second"
		with open(filename) as f:
			for line in f:
				dell7_res = line.split()
				dell7_res[4:] = [' '.join(dell7_res[4:])]
				results_dell7["date"] = dell7_res[0]
				results_dell7["time"] = dell7_res[1]
				try:
					results_dell7["severity"] = dell7_res[3]
					results_dell7["description"] = dell7_res[4]
					print "%s %s %s %s"%(results_dell7["date"], results_dell7["time"], results_dell7["severity"], results_dell7["description"])
					conn.execute("""REPLACE INTO ILO (DATE,TIME,SEVERITY,DESCRIPTION, TESTBED) VALUES(?, ?, ?, ?, ?);""", [results_dell7["date"], results_dell7["time"], results_dell7["severity"], results_dell7["description"], ilo ] )
					conn.commit()
				except:
					pass
			
		
        for ilo in servers["dell6"]:
		results_dell6 = { "severity" : None, "date" : None, "time" : None, "description" : None }
		print " I have entered the loop"
                filename="logs/" + ilo + ".txt"
		totalcmd = 'racadm getsel -i'
		total = runRemoteCmd(ilo, totalcmd, filename, user='username',pw='password')
		total = total.replace("Total Records:", "", 1)
		total_cleaned = max(int(total.strip()) - 30,1)
		cmd = 'racadm getsel -o -s ' + str(total_cleaned)
                if (runRemoteCmd(ilo, cmd, filename, user='username',pw='password')!=0):
			pass
			print "I am inside loop and checking for second"
		with open(filename) as f:
			for line in f:
				dell6_res = line.split()
				dell6_res[4:] = [' '.join(dell6_res[4:])]
				results_dell6["date"] = dell6_res[0]
				results_dell6["time"] = dell6_res[1]
				try:
					results_dell6["severity"] = dell6_res[3]
					results_dell6["description"] = dell6_res[4]
					print "%s %s %s %s"%(results_dell6["date"], results_dell6["time"], results_dell6["severity"], results_dell6["description"])
					conn.execute("""REPLACE INTO ILO (DATE,TIME,SEVERITY,DESCRIPTION, TESTBED) VALUES(?, ?, ?, ?, ?);""", [results_dell6["date"], results_dell6["time"], results_dell6["severity"], results_dell6["description"], ilo ] )
					conn.commit()
				except:
					pass

	
	for ilo in servers["hp"]:
		print " I have entered the loop"
		filename="logs/" + ilo + ".txt"
		#totalcmd = 'show /system1/log1'
		#total = runRemoteCmd(ilo, totalcmd, filename, user='username',pw='password',fwrite="no")
		#records=re.findall(r'record\w+',total)
		#for i in range(len(records)-30,len(records)):
			#cmd= 'show /system1/log1/' + records[i]
			#output=runRemoteCmd(ilo, cmd, filename, user='username',pw='password')
		cmd= 'show -a /system1/log1/'
		output=runRemoteCmd(ilo, cmd, filename, user='username',pw='password')
		patterns_list = ['severity', 'date', 'time', 'description']
		patterns = re.compile('|'.join(patterns_list))
		results = { "severity" : None, "date" : None, "time" : None, "description" : None }
		match_count = 1
		with open(filename) as f:
			for line in f:
				match = re.search(patterns, line)
				if match:
					s = match.start()
					e = match.end()

					if match_count == 1:
						results["severity"] = line[e+1:].strip()
					if match_count == 2:
						results["date"] = line[e+1:].strip()
					if match_count == 3:
						results["time"] = line[e+1:].strip()
					if match_count == 4:
						results["description"] = line[e+1:].strip()
					match_count = match_count + 1
					
					if match_count >4:
						match_count = 1
						conn.execute("""REPLACE INTO ILO (DATE,TIME,SEVERITY,DESCRIPTION, TESTBED) VALUES(?, ?, ?, ?, ?);""", [results["date"], results["time"], results["severity"], results["description"], ilo ] )
						conn.commit()

				else:
					pass
	conn.close()
		
			
		
			
			
			
if __name__ == '__main__':
	conn = sqlite3.connect('test.db')
	print "Opened database successfully";
	conn.execute('''CREATE TABLE IF NOT EXISTS ILO 
       (
       DATE            TEXT,
       TIME            TEXT,
       SEVERITY        TEXT,
       DESCRIPTION     VARCHAR,
       TESTBED         VARCHAR,
        PRIMARY KEY (DATE, TIME, SEVERITY, DESCRIPTION, TESTBED) );''')
	print "Creating table if not exists";
	print "Deleting the log directory"
	os.system("rm -rf logs")
	os.system("mkdir logs")
	main()
