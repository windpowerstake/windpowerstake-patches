import os
import datetime
import time
import string
from subprocess import PIPE, Popen

#in order for this testbench to run you need to have compiled the comparer file
#g++ log_search.cpp -o log_search
#please resolve any dependencies, e.g.: sudo apt install build-essential
#this program and log_search need to be in the .blockchain folder in order to take it as a reference, but this can be easily tweaked

blockchain="cerberusd"
#yes, this is running on a cerberus isolated instance
#in theory chain does not be to running in order to run an algorithm like this, but I have not tested it for a stopped chain
#the plan is to get it into production on other nodes later on

#status of the blockchain, we'll use popen
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
c = b - a
print("status query: "+str(c))
print("")

print("now execute the log_search, which searches the last .log file in blockstore.db and then searches for the last block registered there...")
a = datetime.datetime.now()
#this is the testbench for the log_search algorithm
os.system("./log_search")


b = datetime.datetime.now()
c = b - a
print("status query: "+str(c))
