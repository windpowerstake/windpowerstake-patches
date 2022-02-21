import os
import datetime
import time

#folder is created if it does not exist
dir_logs= "~/logEnergy/history/"
if not os.path.exists(dir_logs):
	os.makedirs(dir_logs)


#infinite loop repeated every 10 minutes, quick and dirty - time series buffered snaps are also possible
while True:

	#round to the next available 10 minute interval
	time_moment=datetime.datetime.utcnow()
	discard = datetime.timedelta(minutes=time_moment.minute%10,seconds=time_moment.second,microseconds=time_moment.microsecond)
	time_moment -= discard
	if discard >= datetime.timedelta(minutes=5):
		time_moment += datetime.timedelta(minutes=10)

	#result after catching delta and rounding
	variable_timestamp=str(time_moment.strftime('%Y-%m-%d %H:%M:%S'))+"Z"



	#print and save to history
	newSCADAln=variable_timestamp+","+"var_1"+","+"var_2"+","+"var_3"
	print(newSCADAln)
	with open(dir_logs+"hist_log.txt", "a") as file_object:
		file_object.write(newSCADAln+"\n")

	time.sleep(60*10)
