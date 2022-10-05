import os
import datetime
import time
import random
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
#This script is set to send e-mails throug sendgrip, please go to https://www.sendgrid.com to create an account and get more details about how to set your account.

#File to keep the result of the missing blocks
blockFileLoc="./logBlock/block.txt"

#File to keep the result of the current space
hard_drive_check="./logBlock/hard_drive_space.txt"


#Mail variables:
from_mail = "xxxxxxx@xxxxxx.com"
to_emails="xxxxxx@xxxxxx.com"

#this is an example for a node that runs evmos and chihuahua in the same machine, evmos runs on an nvme and chihuahua runs from the home folder (an SSD)

#Threshold number of missed blocks lost to send the message
#Notice that for $EVMOS you might want to get a higher threshold for your alert
numBlocklost = 160

#Chains to check the missing blocks:
Chain=""
chain_huahua = "chihuahuad"
chain_cerberus = "cerberusd"
chain_juno = "junod"
chain_evmos = "evmosd"

all_chains = [chain_huahua, chain_cerberus, chain_juno, chain_evmos]

#Nodes manually extracted from https://cosmos.directory/
#This can be automatized and randomized, so we don't hit always the same
#As per our contribution, we're searching to put more RPC's when we receive more hardware
#huahua
# as xxxxxxx, use your pubkey
huahua_base = 'chihuahuad query slashing signing-info \'{"@type":"/cosmos.crypto.ed25519.PubKey","key":"xxxxxxxxxxxxxxxxxxxxxxxx="}\' --node="'

# as xxxxxxx, use your own node, if you are running local (and on a node), you can do tcp://127.0.0.1:26656 with the defaults
huahua_node_1 ="tcp://xxxxxxxxxxxxxxxxx"
huahua_node_2 ="https://chihuahua-rpc.polkachu.com:443"
huahua_node_3 ="https://rpc.chihuahua.wtf:443"

#cerberus
cerberus_base = 'cerberusd query slashing signing-info \'{"@type":"/cosmos.crypto.ed25519.PubKey","key":"xxxxxxxxxxxxxxxxxxxxxxxxx"}\'  --node="'


# as xxxxxxx, use your own node, if you are running local (and on a node), you can do tcp://127.0.0.1:26656 with the defaults
cerberus_node_1 ="tcp://xxxxxxxxxxxxxxxxxxxxx"
cerberus_node_2 ="https://cerberus-rpc.polkachu.com:443"
cerberus_node_3 ="https://rpc-cerberus.ecostake.com:443"


#juno
juno_base = 'junod query slashing signing-info \'{"@type":"/cosmos.crypto.ed25519.PubKey","key":"xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"}\'  --node="'


# as xxxxxxx, use your own node, if you are running local (and on a node), you can do tcp://127.0.0.1:26656 with the defaults
juno_node_1 ="tcp://xxxxxxxxxxxxxxxxxxxxx"
juno_node_2 ="https://rpc-juno.ecostake.com:443"
juno_node_3 ="https://rpc-juno.itastakers.com:443"

#evmos
evmos_base = 'evmosd query slashing signing-info \'{"@type":"/cosmos.crypto.ed25519.PubKey","key":"xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"}\' --node="'


# as xxxxxxx, use your own node, if you are running local (and on a node), you can do tcp://127.0.0.1:26656 with the defaults
evmos_node_1 ="tcp://xxxxxxxxxxxxxxxxxxxxx"
evmos_node_2 ="https://rpc.evmos.interbloc.org:443"
evmos_node_3 ="https://rpc.evmos.bh.rocks:443"

#Add all the nodes that you want to check. Remember add the base + node
nodes_to_check= [huahua_base+huahua_node_1+'"',huahua_base+huahua_node_2+'"',huahua_base+huahua_node_3+'"',cerberus_base+cerberus_node_1+'"',cerberus_base+cerberus_node_2+'"',cerberus_base+cerberus_node_3+'"',juno_base+juno_node_1+'"',juno_base+juno_node_2+'"',juno_base+juno_node_3+'"',evmos_base+evmos_node_1+'"',evmos_base+evmos_node_2+'"',evmos_base+evmos_node_3+'"']

#Number of blocks lost to send the message
numBlocklost = 80

#Percentage of space used in the hard drive to send the message
space_used = 90

#This is the text to find in the file to identify the number of missing blocks
textmissedblocks="missed_blocks_counter"

#This is the text to find the disks:
#In this case a sata drive for chihuahua and an nvme drive for evmos
textdisk1="/dev/sda2"
textdisk2="/dev/nvme0n1p1"


#This is the command to get the information from disk1
stringStarter_disk='df --output=source,pcent'
 
#The capacity of your main hard drive is over 90%
message_hard_drive_1 = Mail(
    from_email=from_mail,
    to_emails=to_emails,
    subject='Hard Drive 1',
    html_content='Your hard drive 1 is more than 90%')

#The capacity of your second hard drive is over 90%
message_hard_drive_2 = Mail(
    from_email=from_mail,
    to_emails=to_emails,
    subject='Hard Drive 2',
    html_content='Your hard drive 2 is more than 90%')


#infinite loop repeated every 5 min
while True:
	#refresh and remove last query
	os.system("rm "+hard_drive_check)
	
	#Reset variables
	percentage_disk1=""
	percentage_disk2=""

	Chain=""
	numBlockStr=""
	numBlockStr_huahua=[]
	numBlockStr_cerberus=[]
	numBlockStr_juno=[]
	numBlockStr_evmos=[]
	
	#save this new query to check disk space
	os.system(stringStarter_disk + " >> "+hard_drive_check)
	
	#Loop to check the missing blocks 
	for x in nodes_to_check:
		#Identify the block chain
		chain=x.partition(' ')[0]
		
		#Clean the variables before picking the following value
		os.system("rm "+blockFileLoc)
		os.system(x + " >> "+blockFileLoc)
		try:
			with open(blockFileLoc) as fp:
				for line in fp:
					if textmissedblocks in line:
						#Save the variable in the corresponding variable
						if chain == chain_huahua:
							#v01_01 numBlocksStr RESULT
							numBlockStr_huahua.append(int(line.split('"')[1]))
						if chain == chain_cerberus:
							#v01_01 numBlocksStr RESULT
							numBlockStr_cerberus.append(int(line.split('"')[1]))
						if chain == chain_juno:
							#v01_01 numBlocksStr RESULT
							numBlockStr_juno.append(int(line.split('"')[1]))
						if chain == chain_evmos:
							#v01_01 numBlocksStr RESULT
							numBlockStr_evmos.append(int(line.split('"')[1]))
		except Exception:
			print("Something wrong trying to capture block time for " + chain + " node1")

	#Readings from the nodes
	print ("Missing blocks: " ,numBlockStr_huahua)
	print ("Missing blocks: " ,numBlockStr_cerberus)
	print ("Missing blocks: " ,numBlockStr_juno)
	print ("Missing blocks: " ,numBlockStr_evmos)	
		
	#Loop to randomly query one of the values from previous reading and send an e-mail if the number is bigger than the one defined. We need to do this query less heavy, as there will be discarded results from query.
	#Would be useful to rather integrating them into the randomization:
	for x in all_chains:
		if x == chain_huahua and numBlockStr_huahua:
			numBlockStr=random.choice(numBlockStr_huahua)
		if x == chain_cerberus and numBlockStr_cerberus:
			numBlockStr=random.choice(numBlockStr_cerberus)
		if x == chain_juno and numBlockStr_juno:
			numBlockStr=random.choice(numBlockStr_juno)
		if x == chain_evmos and numBlockStr_evmos:
			numBlockStr=random.choice(numBlockStr_evmos)
		else:
			print("Chain not assigned")



		print ("Missing blocks in " + x + " to compare: ",numBlockStr)
		
		
		message_block_fail = Mail(
		    from_email=from_mail,
		    to_emails=to_emails,
		    subject='You are missing blocks in ' + x + '.',
		    html_content='The chain ' + x + ' is not working. You lost ' + str(numBlockStr) + ' blocks')
		

		#Check if the value with the number of missing records is really a number to avoid an error:
		if isinstance(numBlockStr, int):
			#Check if the missing blocks identify is more than the value assigned in numBlocklost to send the mail:
			if numBlockStr > numBlocklost:
				print("error enviar mail")
				try:
					sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
					response = sg.send(message_block_fail)
					print(response.status_code)
					print(response.body)
					print(response.headers)
					#After sending an email we want to wait 1h before sending the following message. We don't want to block our mail receiving the same message every 5 min.
					#As this is a general pause, check out your other stuff (just if coincidentality is a factor)
					time.sleep(3600)
				except Exception as e:
					print(e.message_block_fail)
		else:
			print("The node is not working")
	


	#Disk1	
	#Check the percentage of the Disk1:
	try:
		with open(hard_drive_check) as fp:
			for line in fp:
				if textdisk1 in line:
					#Get the percentage of the specific disk
					percentage_disk1=line.split(textdisk1)[1].replace(" ", "").replace("%", "")
	except Exception:
			print("Something wrong trying to get the space in Disk 1")
	print ("Percentage used in Disk1: ",percentage_disk1)
	#Check if the missing blocks identify is more than the value assigned in space_used to send the mail:
	if int(percentage_disk1) > space_used:
		try:
			sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
			response = sg.send(message_hard_drive_1)
			print(response.status_code)
			print(response.body)
			print(response.headers)
			#After sending an email we want to wait 1h before sending the following message. We don't want to block our mail receiving the same message every 5 min.
			#As this is a general pause, check out your other stuff (just if coincidentality is a factor)
			time.sleep(3600)
		except Exception as e:
			print(e.message_hard_drive_1)		
		

	#Disk2	
	#Check the percentage of the Disk1:
	try:
		with open(hard_drive_check) as fp:
			for line in fp:
				if textdisk2 in line:
					#Get the percentage of the specific disk
					percentage_disk2=line.split(textdisk2)[1].replace(" ", "").replace("%", "")
	except Exception:
			print("Something wrong trying to get the space in Disk 2")
	print ("Percentage used in Disk2: ",percentage_disk2)
	#Check if the missing blocks identify is more than the value assigned in space_used to send the mail:
	if int(percentage_disk1) > space_used:
		try:
			sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
			response = sg.send(message_hard_drive_2)
			print(response.status_code)
			print(response.body)
			print(response.headers)
			#After sending an email we want to wait 1h before sending the following message. We don't want to block our mail receiving the same message every 5 min.
			#As this is a general pause, check out your other stuff (just if coincidentality is a factor)
			time.sleep(3600)
		except Exception as e:
			print(e.message_hard_drive_2)		
		
		
	
	time.sleep(300)
