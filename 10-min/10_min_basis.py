import os
import datetime
import time


#infinite loop repeated every 10 minutes, quick and dirty - time series buffered snaps are also possible
while True:

	#round to the next available 10 minute interval
	tm=datetime.datetime.utcnow()
	discard = datetime.timedelta(minutes=tm.minute%10,seconds=tm.second,microseconds=tm.microsecond)
	tm -= discard
	if discard >= datetime.timedelta(minutes=5):
		tm += datetime.timedelta(minutes=10)

	#result after catching delta and rounding
	vTimestamp=str(tm.strftime('%Y-%m-%d %H:%M:%S'))+"Z"



	#print and save to history
	newSCADAln=vTimestamp+","+"var1"+","+"var2"+","+"var3"
	print(newSCADAln)
	with open("./logEnergy/history/hist_log.txt", "a") as file_object:
		file_object.write(newSCADAln+"\n")

	time.sleep(60*10)
