#author: windpowerstake
#20.02.2022
#MIT License

import difflib
import os
import time
import datetime
import subprocess
import re
import json
from pathlib import Path


#surely things can go wrong so use at your own risk
#init threshold number of validators missing tx's
thresholdValidators=3

waitABlock=True
defaultSleepTime=8

#just an interlock in order to wait for a block before starting
while waitABlock:
	try:
		hello=subprocess.run(["junod", "status", "."], capture_output=True)
		result=re.search('latest_block_height":"(.*)","latest_block_time',str(hello))
		actualBlock=int(result.group(1))
		waitABlock=False
	except Exception as e:
		print("wrong latest block")
		#we make pause in order to avoid too much spam on us
		time.sleep(defaultSleepTime+3)

time.sleep(defaultSleepTime)
#This needs improvements by using subprocess
#init, we remove the present
#torturing IO here, I will come back to process later on, I switched to it at some point but I had problems with queries :S
os.system('rm present.txt')
os.system('junod query slashing signing-infos --height '+str(actualBlock)+' >> present.txt')
time.sleep(defaultSleepTime)

#also os, related, it is interesting to log the blocks in some subfolder
#folder is created if it does not exist
directory = "./loggedBlocks/"
if not os.path.exists(directory):
    os.makedirs(directory)

#this is an infinite loop
while True:
	#init counter of common nodes that can fail at the same time
	counter=0
	countErr=0
	ccfList=[]
	os.system('cp present.txt past.txt')
	os.system('rm present.txt')
	actualBlock=actualBlock+1
	os.system('junod query slashing signing-infos --height '+str(actualBlock)+' >> present.txt')
	hello=subprocess.run(["junod", "status", "."], capture_output=True)
	



	with open('./past.txt', 'r') as file1:
		dataPast = file1.read()
	with open('./present.txt', 'r') as file2:
		dataPresent = file2.read()

	#I use the tombstone sentence to split between validators, because it's long enough and cannot be confused :D
	#also the start of my split is the info\n, just to avoid dealing with it later on
	divideByValidators=dataPast[len("info:\n"):].split("tombstoned: false\n")
	divideByValidators1=dataPresent[len("info:\n"):].split("tombstoned: false\n")

	#Baseline is the signing info output from the last block, 6 seconds ago.
	#It would be more efficient if baseline was the present one right? omg.		
	valiList=[]
	missedListBefore=[]
	for eachVali in divideByValidators[:-1]:
		stringValidator=eachVali[len("- address: "):]
		valiList.append(stringValidator.split("\n")[0])
		missedListBefore.append(stringValidator.split("\n")[3])

	#On the fly, we go searching through the present list
	for eachVali in divideByValidators1[:-1]:
		stringValidator=eachVali[len("- address: "):]
		valiListAfter=stringValidator.split("\n")[0]
		missedListAfter=stringValidator.split("\n")[3]
		
		#Just capture an exception, maybe one validator became inactive, or maybe the command did not work this time
		try:
			#if we find the validator in the list, then we do the magic
			postProcessedMissedBefore=int(missedListBefore[valiList.index(valiListAfter)].split('"')[1])
			postProcessedMissedAfter=int(missedListAfter.split('"')[1])
			
			#we search for increases on the Missed Block Counts, not decreases
			if postProcessedMissedBefore < postProcessedMissedAfter:
				counter=counter+1
				ccfList.append(valiListAfter)
				#we inited this counter at the beginning				
				if counter>thresholdValidators:
					#result=re.search('latest_block_height":"(.*)","latest_block_time',str(hello))
					print("Block: "+str(actualBlock))
					print("Found a diff! "+valiListAfter+":"+str(postProcessedMissedBefore)+">"+str(postProcessedMissedAfter))
					print("CCF: "+str(counter))
					#you might want to have ready the logged blocks dir.
					os.system('junod query block '+str(actualBlock)+' >> ./loggedBlocks/loggedBlocks_'+str(actualBlock)+'.txt')
					#this time sleep here, it's why we can accelerate until 5 seconds wait between block at the end
					#in theory, depending on how much microseconds takes for the rest of the code we would be catching up with juno with 5 s at the end plus this
					#in theory, depending also on the rest of the code, we would be drifting down if we just decelerate to 6
					
					time.sleep(1)
					try:
						#now we saved the block in controversy, we'll capture the tx's :D
						#I want to learn better what's behid this... at the moment just logging
						with open('./loggedBlocks/loggedBlocks_'+str(actualBlock)+'.txt',"r") as blockInControversy:
							contentBlockInControversy= blockInControversy.read().splitlines(True)
						jsonInControversy=json.loads(str(contentBlockInControversy[0]))
						print("Timestamp"+str(jsonInControversy['block']['header']['time']))
						timestampThisBlock=str(jsonInControversy['block']['header']['time'])
						try:
							print("TXs: "+str(jsonInControversy['block']['data']['txs']))
							transactionsInThisBlock=str(len(jsonInControversy['block']['data']['txs']))
						except Exception as e:
							transactionsInThisBlock="0"
					except Exception as e:
						transactionsInThisBlock=""
						timestampThisBlock=""
					try:
						#get the size
						loggedBlocksTxtSize=str(Path('./loggedBlocks/loggedBlocks_'+str(actualBlock)+'.txt').stat().st_size)
					except Exception as e:
						print("fail with logblocks")
						loggedBlocksTxtSize=""
		except ValueError as e:
			print("NGMI with sleep times: "+str(defaultSleepTime)+" seconds")
			if countErr<1:
				print(valiListAfter+" not found")
			countErr=countErr+1

	# What we print here, you can log it into a file/log.
	if counter>thresholdValidators:
		print("Full list: "+str(ccfList))


	#we should write a time control algorithm, so we don't query junod too much and we pause if we are closing in too much
	if actualBlock%5==0:
		print("Actual Block: "+str(actualBlock),end=" | ")
		if actualBlock%10==0:
			try:
				hello2=subprocess.run(["junod", "status", "."], capture_output=True)
				result2=re.search('latest_block_height":"(.*)","latest_block_time',str(hello2))
				realBlock=int(result2.group(1))
				print("Real Block: "+str(realBlock))
				
				#very cheap control algo in order to avoid torturing the node more than what we are doing.
				#surely things can go wrong so use at your own risk
				if realBlock-actualBlock<25:
					defaultSleepTime=9
					print("Closing in. Decelerate 9")
				if realBlock-actualBlock<20:
					defaultSleepTime=10
					print("Closing in. Decelerate 10")
				if realBlock-actualBlock<15:
					defaultSleepTime=11
					print("Closing in and pause for "+str(defaultSleepTime)+" extra secs. Decelerate 11.")
					time.sleep(defaultSleepTime)
				if realBlock-actualBlock>70:
					print("Far away 70. Accelerate 8")
					defaultSleepTime=8
				if realBlock-actualBlock>90:
					print("Far away 90. Accelerate 7")
					defaultSleepTime=7
				if realBlock-actualBlock>150:
					print("Far away 150. Accelerate 6")
					defaultSleepTime=6
				if realBlock-actualBlock>160:
					print("Far away 160. Accelerate 5")
					defaultSleepTime=5
				if realBlock-actualBlock>170:
					print("Far away 170. Accelerate 4")
					defaultSleepTime=4
				if actualBlock>realBlock:
					defaultSleepTime=15
					print("Surpassed it! let's pause for "+str(defaultSleepTime)+" extra secs. Decelerate")
					time.sleep(defaultSleepTime)
					
			except Exception as e:
				print("wrong latest block")
				#we make pause in order to avoid too much spam on us
				time.sleep(defaultSleepTime+15)
		else:
			print("")

	time.sleep(defaultSleepTime)
	


	
