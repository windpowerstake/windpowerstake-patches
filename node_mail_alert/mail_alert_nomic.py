import os
import datetime
import time
import random
import pycurl
import re
from io import BytesIO


directorylog="./logBlock/"
# Check whether the specified path exists or not
isExist = os.path.exists(directorylog)
if not isExist:
   # Create a new directory because it does not exist
   os.makedirs(directorylog)
   print("The new directory is created!")

#File to keep the status of nomic validators
blockFileLoc_nomic=directorylog+"nomic_page.txt"

#Identifies the start and end lines which contains the information with the validators
start_line = 'precommits_bit_array'
end_line = '"votes_bit_array":'

#nomic validator to check if it is active
#this is an example containing windpowerstake nomic_base ID
nomic_base = '6E6D95D314E8'

#Nodes to check the status of the validator
#it's assummed all nodes are healthy
#Nodes from https://cosmos.directory/
nomic_node_1 ="https://rpc-nomic.carbonzero.zone/dump_consensus_state?"
nomic_node_2 ="https://nomic-rpc.polkachu.com/dump_consensus_state?"
nomic_node_3 ="http://138.197.71.46:26657/dump_consensus_state?"

#Add the nodes to an array
nomic_nodes_to_check= [nomic_node_1,nomic_node_3,nomic_node_3]

while True:
	#Nomic: Array to keep the status of validator: 1 active, 0 Inactive
	nomic_status=[]
	
	#Nomic: Variable with the number of checks before deciding if the validator is active or not
	Number_of_checks = 3

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
		        	    		# end line being votes bit array, interrupts reading the file, and ensures at least one line with our vote is there (or not)
		        	    		if end_line in line.strip().lower():
		        	        		break

			#Insert the content into a string the indentify how many times the validator appears:
			get_body_check = "".join(mylines)
		
			#Inserts the result into the array
			nomic_status.append(int(get_body_check.count(nomic_base)))
			
			
			#Sleep six seconds between one check and another check, just in case, liveliness alone does not need bizantine checks :_)
			time.sleep(6)
		
		#Reduce the variable for the loop
		Number_of_checks -=1
	
		#Wait 30 seconds before doing round 2
		time.sleep(30)
	
	print ("Status of validator in Nomic: " ,nomic_status)
	


	
	#if the validator was identified at least once, we understand it is active:
	if 1 in nomic_status:
		print("Active validator in Nomic")
	else:
		print("Validator not active in Nomic. Sending mail:")
		#commands to send mail, sendgrid, or google particular application, etc..

	#wait 20 minutes between check and check
	time.sleep(1200)
