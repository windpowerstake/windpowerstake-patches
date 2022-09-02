import os
import datetime
import time


from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
#This script is set to send e-mails throug sendgrip, please go to https://www.sendgrid.com to create an account and get more details about how to set your account.
#This file is for saving the block

blockFileLoc_huahua="./logBlock/block_huahua.txt"
blockFileLoc_evmos="./logBlock/block_evmos.txt"
hard_drive_check="./logBlock/hard_drive_space.txt"
#hard_drive_check_2="./logBlock/hard_drive_space_2.txt"


#this is an example for a node that runs evmos and chihuahua in the same machine, evmos runs on an nvme and chihuahua runs from the home folder (an SSD)

#Threshold number of missed blocks lost to send the message
#Notice that for $EVMOS you might want to get a higher threshold for your alert
numBlocklost = 160

#Threshold percentage of hard drive used to send the message
space_used = 90

#This is the text to find in the file to identify the number of missing blocks
textmissedblocks="missed_blocks_counter"

#This is the text to find the disks:
#In this case a sata drive for chihuahua and an nvme drive for evmos
textdisk1="/dev/sda2"
textdisk2="/dev/nvme0n1p1"

#This is the command in order to get the slashing signing info from Huahua
#*In your signer* (not in the RPC/aux node): Indentify the validator key (you want to monitor) with the command: --> show validator: chihuahuad tendermint show-validator --home="........"
#In this case, the algorithm works on the same monitoring node, but it can be pointed towards any address.
#check <your_user> if you have a different home for your chihuahua
stringStarter_huahua='chihuahuad query slashing signing-info \'............................\' --home="/home/<your_user>/.chihuahua" --node="http://127.0.0.1:......"'

#this is the command in order to get the slashing signing info from Evmos
#*In your signer* (not in the RPC/aux node): Indentify the validator key (you want to monitor) with the command: --> show validator: evmosd tendermint show-validator --home="........"
stringStarter_evmos='evmosd query slashing signing-info \'................................\' --home="/mnt/nvme0n1p1/.evmosd" --node="http://127.0.0.1:......."'

#This is the command to get the information from disk1
stringStarter_disk='df --output=source,pcent'

#This is the command to get the information from disk2
#stringStarter_disk2='df /dev/nvme0n1p1 --output=source,pcent'

#These are the different messages to send when we identify the different scenarios:

#Missing blocks in Huahua
message_huahua = Mail(
    from_email='xxxxxxx@gmail.com',
    to_emails='xxxxxxxx@gmail.com',
    subject='You are missing blocks in Huahua',
    html_content='Huahua is not working. You lost more than '+str(numBlocklost)+' blocks')
    
#Missing blocks in Evmos
message_evmos = Mail(
    from_email='xxxxxx@gmail.com',
    to_emails='xxxxxxxxxxx@gmail.com',
    subject='You are missing blocks in Evmos',
    html_content='Evmos is not working. You lost more than '+str(numBlocklost)+' blocks')
    
#The capacity of your main hard drive is over 90%
message_hard_drive_1 = Mail(
    from_email='xxxxxxxxxxx@gmail.com',
    to_emails='xxxxxxxxxxxxx@gmail.com',
    subject='Hard Drive 1',
    html_content='Your hard drive 1 is more than 90%')

#The capacity of your second hard drive is over 90%
message_hard_drive_2 = Mail(
    from_email='xxxxxxxxxx@gmail.com',
    to_emails='xxxxxxxxxxx@gmail.com',
    subject='Hard Drive 2',
    html_content='Your hard drive 2 is more than 90%')


#infinite loop repeated every 5 min
while True:
	#refresh and remove last query
	os.system("rm "+blockFileLoc_huahua)
	os.system("rm "+blockFileLoc_evmos)
	os.system("rm "+hard_drive_check)

	#Reset the value each time
	numBlockStr_huahua=""
	numBlockStr_evmos=""
	percentage_disk1=""
	percentage_disk2=""
	#save this new query
	os.system(stringStarter_huahua + " >> "+blockFileLoc_huahua)
	os.system(stringStarter_evmos + " >> "+blockFileLoc_evmos)
	os.system(stringStarter_disk + " >> "+hard_drive_check)


	#HUAHUA
	#Identify missing blocks in huahua:
	try:
		with open(blockFileLoc_huahua) as fp:
			for line in fp:
				if textmissedblocks in line:
					#v01_01 numBlocksStr RESULT
					numBlockStr_huahua=line.split('"')[1]
	except Exception:
			print("Something wrong trying to capture block time for huahua")
	print ("Missing blocks in Huahua: ",numBlockStr_huahua)
	

	#Check if the missing blocks identify is more than the value assigned in numBlocklost to send the mail:
	if int(numBlockStr_huahua) > numBlocklost:
		try:
			sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
			response = sg.send(message_huahua)
			print(response.status_code)
			print(response.body)
			print(response.headers)
			#After sending an email we want to wait 1h before sending the following message. We don't want to block our mail receiving the same message every 5 min.
			time.sleep(3600)
		except Exception as e:
			print(e.message_huahua)
		
	#EVMOS	
	#Identify missing blocks in evmos:
	try:
		with open(blockFileLoc_evmos) as fp:
			for line in fp:
				if textmissedblocks in line:
					#v01_01 numBlocksStr RESULT
					numBlockStr_evmos=line.split('"')[1]
	except Exception:
			print("Something wrong trying to capture block time for evmos")
	print ("Missing blocks in Evmos: ",numBlockStr_evmos)
	#Check if the missing blocks identify is more than the value assigned in numBlocklost to send the mail:
	if int(numBlockStr_evmos) > numBlocklost:
		try:
			sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
			response = sg.send(message_evmos)
			print(response.status_code)
			print(response.body)
			print(response.headers)
			#After sending an email we want to wait 1h before sending the following message. We don't want to block our mail receiving the same message every 5 min.
			time.sleep(3600)
		except Exception as e:
			print(e.message_evmos)


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
			time.sleep(3600)
		except Exception as e:
			print(e.message_hard_drive_2)		
		
		
	
	time.sleep(600)
