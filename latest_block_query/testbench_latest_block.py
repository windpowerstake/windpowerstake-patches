import os
import datetime
import time
import string
from subprocess import PIPE, Popen

blockchain="cerberusd"
#yes, this is running on a cerberus isolated instance
#in theory chain does not be to running in order to run an algorithm like this, but I have not tested it for a stopped chain

#status popen
print("same status but with Popen")
a = datetime.datetime.now()
command = blockchain + ' status 2>&1 | jq "{latest_block_height: .SyncInfo.latest_block_height}"'
outputjson=""
with Popen(command, stdout=PIPE, stderr=None, shell=True) as process:
        outputjson = process.communicate()[0].decode("utf-8")

import json

parsed_json = json.loads(outputjson)
latest_block_height = int(parsed_json['latest_block_height'])
print(latest_block_height)
b = datetime.datetime.now()
c1 = b - a
print("status query: "+str(c1))
print("")

print("give me all files containing the previous string...")
a = datetime.datetime.now()


#this is the testbench for the log_search algorithm
os.system("./log_search")


b = datetime.datetime.now()
c2 = b - a
print("status query: "+str(c2))

print("improvement: "+str(c1/c2))
