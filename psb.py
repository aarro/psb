"""something something linting"""
import datetime
import json
import os
import platform
import re
import subprocess
from time import sleep
from threading import Thread
from slackclient import SlackClient
from dotenv import load_dotenv, find_dotenv

# Load env variables
load_dotenv(find_dotenv())

# Load data
with open('devices.json') as data_file:
    DATA = json.load(data_file)

# Arrays for tracking state
FIRST_RUN = [1] * len(DATA)
PRESENT_SENT = [0] * len(DATA)
NOT_PRESENT_SENT = [0] * len(DATA)

# Slack info
SLACK_TOKEN = os.environ.get("SLACK_TOKEN")
GROUP_ID = os.environ.get("SLACK_GROUP")
SLACK_CLIENT = SlackClient(SLACK_TOKEN)

# Other
MAC_REGEX = "[0-9a-f]{2}([-:])[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$"

def who_is_here(who):
    """Function that checks for device presence"""
    sleep(45) #sleep at init

    o_name = DATA[who]["name"]
    o_addr = DATA[who]["mac"].lower()

    # Loop through checking for devices and counting if they're not present
    while True:
        # Exits thread if Keyboard Interrupt occurs
        if STOP:
            print "Exiting Thread - " + o_name
            exit()
        else:
            pass

        # If a listed device address is present print and stream
        if (o_addr in MAC_TIME and
                MAC_TIME[o_addr] + datetime.timedelta(minutes=4) >= datetime.datetime.now()):
            print o_name + " is here"
            if PRESENT_SENT[who] == 0:
                #notify slack
                #SLACK_CLIENT.api_call("chat.postMessage", channel=GROUP_ID,
                #                      text=o_name + " is here!", as_user=True)
                #set counters
                FIRST_RUN[who] = 0
                PRESENT_SENT[who] = 1
                NOT_PRESENT_SENT[who] = 0
        # If a listed device address is not present, print and stream
        else:
            last_seen = "never"
            if o_addr in MAC_TIME:
                last_seen = MAC_TIME[o_addr].strftime("%Y-%m-%d %H:%M:%S")
            print o_name + " is NOT here. Last seen " + last_seen
            if FIRST_RUN[who] == 0 and NOT_PRESENT_SENT[who] == 0:
                #SLACK_CLIENT.api_call("chat.postMessage", channel=GROUP_ID,
                #                      text=o_name + " is gone!", as_user=True)
                NOT_PRESENT_SENT[who] = 1
                PRESENT_SENT[who] = 0
            FIRST_RUN[who] = 0
        sleep(10)

# Main thread
try:
    # Initialize a variable to trigger threads to exit when True
    STOP = False
    MAC_TIME = {}

    #SLACK_CLIENT.api_call("chat.postMessage", channel=GROUP_ID, text='Starting up', as_user=True)

    # Start the thread(s)
    # It will start as many threads as there are values in the occupant array
    for i in range(len(DATA)):
        t = Thread(target=who_is_here, args=(i,))
        t.start()

    while True:
        # mac defaults
        A_COMMAND = "arp -a"
        A_SPLIT = " "
        A_INDEX = 3

        # arping!
        # sudo arping -i en0 -c 3 -t 1c:67:58:ee:4b:e6 192.168.1.77

        PLATFORM = platform.system()
        if PLATFORM == "Linux":
            A_COMMAND = "sudo arp-scan --interface=eth0 --localnet --retry=4"
            A_SPLIT = "\t"
            A_INDEX = 1

        OUTPUT = subprocess.check_output(A_COMMAND, shell=True)
        LINES = OUTPUT.splitlines(False)
        for l in LINES:
            conns = l.split(A_SPLIT)
            if len(conns) > 1 and re.match(MAC_REGEX, conns[A_INDEX].lower()):
                mac = conns[A_INDEX]
                MAC_TIME[mac] = datetime.datetime.now()

        # Wait 10 seconds between scans
        sleep(5)

except KeyboardInterrupt:
    # On a keyboard interrupt signal threads to exit
    STOP = True
    #SLACK_CLIENT.api_call("chat.postMessage", channel=GROUP_ID, text='Shutting down', as_user=True)
    sleep(30)
    exit()
