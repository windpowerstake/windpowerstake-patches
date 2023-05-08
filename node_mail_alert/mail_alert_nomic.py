import os
import datetime
import time
import random
import pycurl
import re
from io import BytesIO

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
#This script is set to send e-mails throug sendgrip, please go to https://www.sendgrid.com to create an account and get more details about how to set your account.

#Mail variables:
from_mail = "whateveryourmailis@gmail.com"
to_emails1="destinationmail1@gmail.com"

SENDGRID_API_KEY='this is your sendgrid api key'


#File to keep the status of nomic validators
# please build the dir yourself <your_user>/alert_mails/logBlock/nomic_page.txt
directorylog="/home/<your_user>/alert_mails/logBlock/"
# Check whether the specified path exists or not
isExist = os.path.exists(directorylog)
if not isExist:
	# Create a new directory because it does not exist
	os.makedirs(directorylog)
	print("The new directory is created!")

blockFileLoc_nomic=directorylog+"nomic_page.txt"

#Identifies the start and end lines which contains the information with the validators
start_line = 'precommits_bit_array'
end_line = '"votes_bit_array":'

#nomic validator to check if it is active
# this is windpowerstake keybase when dumping consensus stake, search your own for the test
nomic_base = '6E6D95D314E8'

#Nodes to check the status of the validator
#this are examples, please also mix with your own
nomic_node_1 ="https://rpc.nomic.interbloc.org/dump_consensus_state?"
nomic_node_2 ="https://nomic-rpc.polkachu.com/dump_consensus_state?"
nomic_node_3 ="http://138.197.71.46:26657/dump_consensus_state?"

#Add the nodes to an array
nomic_nodes_to_check= [nomic_node_1,nomic_node_3,nomic_node_3]

#Nodes extracted from https://cosmos.directory/

while True:
	#Nomic: Array to keep the status of validator: 1 active, 0 Inactive
	nomic_status=[]
	
	#Nomic: Variable with the number of checks before deciding if the validator is active or not
	Number_of_checks = 2

	while Number_of_checks > 0:


		#Create a loop to check twice if the validator is active in the following 30 seconds

		#Loop to identify if the validator is active in all the nodes defined above.
		for x in nomic_nodes_to_check:

			#Reads the content of the html 
			b_obj = BytesIO()
			crl = pycurl.Curl()
			crl.setopt(crl.URL, x)
			# To write bytes using charset utf 8 encoding
			crl.setopt(crl.WRITEDATA, b_obj) 
			# Start transfer 
			crl.perform() 
			# End curl session 
			crl.close() 
			# Get the content stored in the BytesIO object (in byte characters) 
			get_body = b_obj.getvalue() 
			get_body_text = get_body.decode('utf8','strict')
			#get_body_cut = re.search('precommits_bit_array(.*)"votes_bit_array":', get_body_text)

			#Inserts the content of the html into a file
			f = open(blockFileLoc_nomic,"w+")
			f.writelines(get_body_text)
			f.close()


			#Read the file and keep only the content between the lines defined as start_line and end_line
			mylines = []
			flag = False
			with open(blockFileLoc_nomic, 'rt', encoding='utf-8') as myfile:
				for line in myfile:
		        		if start_line in line.strip().lower():
		        	    		flag = not flag
		        		if flag:
		        	    		mylines.append(line)
		        	    		if end_line in line.strip().lower():
		        	        		break

			#Insert the content into a string the indentify how many times the validator appears:
			get_body_check = "".join(mylines)
		
			#Inserts the result into the array
			nomic_status.append(int(get_body_check.count(nomic_base)))
		
		#Reduce the variable for the loop
		Number_of_checks -=1
	
		#Wait 30 seconds to check the status of nodes again
		time.sleep(30)
	
	print ("Status of validator in Nomic: " ,nomic_status)
	
	
	
	#Alert mail to the first person
	message_block_fail1 = Mail(
	    from_email=from_mail,
	    to_emails=to_emails1,
	    subject='Nomic is not working',
	    html_content='The chain Nomic is not working. Your node seems to be stopped.')

	    
	#OK mail to the first person
	message_block_ok1 = Mail(
	    from_email=from_mail,
	    to_emails=to_emails1,
	    subject='Nomic is working',
	    html_content='The chain Nomic is working.')

	

	
	#if the validator was identified at least once, we understand it is active:
	if 1 in nomic_status:
		print("Active validator in Nomic")
		
		
		print("Validator is active in Nomic. No sending mail:")

#		try:
#			sg = SendGridAPIClient(api_key = SENDGRID_API_KEY)
#			response = sg.send(message_block_ok1)
#			print(response.status_code)
#			print(response.body)
#			print(response.headers)
			#After sending an email we want to wait 2h before sending the following message. We don't want to block our mail receiving the same message every 5 min.
#			time.sleep(10)
#		except Exception as e:
#			print(e.message_block_ok1)

		

		
	else:
		print("Validator not active in Nomic. Sending mail:")

		try:
			sg = SendGridAPIClient(api_key = SENDGRID_API_KEY)
			response = sg.send(message_block_fail1)
			print(response.status_code)
			print(response.body)
			print(response.headers)
			#After sending an email we want to wait 2h before sending the following message. We don't want to block our mail receiving the same message every 5 min.
			time.sleep(10)
		except Exception as e:
			print(e.message_block_fail1)


	time.sleep(21600)
