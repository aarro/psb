"""main logic"""
import json
import os
import platform
import re
import subprocess
from time import sleep
from threading import Thread, Lock
from slackclient import SlackClient
from dotenv import load_dotenv, find_dotenv
from .classes import Device

# Load env variables
load_dotenv(find_dotenv())

# Load data
with open('devices.json') as data_file:
    DATA = json.load(data_file)

# Slack info
SLACK_TOKEN = os.environ.get("SLACK_TOKEN")
GROUP_ID = os.environ.get("SLACK_GROUP")
SLACK_CLIENT = SlackClient(SLACK_TOKEN)

# Other
LOCK = Lock()
SKIP_SLACK = os.environ.get("SKIP_SLACK") or False
MAC_REGEX = "[0-9a-f]{2}([-:])[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$"
IP_REGEX = r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}" \
           r"(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b"

def call_slack(message):
    """Sends a message to slack"""
    if not SKIP_SLACK:
        SLACK_CLIENT.api_call("chat.postMessage", channel=GROUP_ID, text=message, as_user=True)

def who_is_here(who):
    """Function that checks for device presence"""
    sleep(45) #sleep at init

    o_name = DATA[who]["name"]
    o_addr = DATA[who]["mac"]
    o_online = False

    # Loop through checking for devices and counting if they're not present
    while True:
        with LOCK:
            if STOP:
                print "Exiting Thread - " + o_name
                exit()

            # If a listed device address is present print and stream
            if o_addr in DEVICE_DICT:
                device = DEVICE_DICT[o_addr]
                if device.online:
                    if device.is_active(30): # 30 second grace period for not seeing a device
                        print device.name + ' is here (arp-scan)'
                    else: # After 30 seconds check the mac/ip directly
                        found = False
                        arping = "sudo arping -c 3 -t " + device.mac + " " + device.ipv4
                        process = subprocess.Popen(arping, stdout=subprocess.PIPE,
                                                   stderr=subprocess.PIPE, shell=True)
                        a_out, err = process.communicate()
                        if err:
                            print err
                        else:
                            a_lines = a_out.splitlines(False)
                            for a_l in a_lines:
                                ping = a_l.split(" ")
                                if len(ping) > 3:
                                    device.seen()
                                    found = True
                                    break
                            if found:
                                print device.name + ' is here (arping)'
                            else:
                                device.online = False
                                call_slack(device.name + " is gone")
                o_online = device.online

            if not o_online:
                last_seen = "never"
                if o_addr in DEVICE_DICT:
                    last_seen = DEVICE_DICT[o_addr].last_seen.strftime("%Y-%m-%d %H:%M:%S")
                print o_name + " is not here. Last seen " + last_seen
        sleep(10)

# Main thread
try:
    # Initialize a variable to trigger threads to exit when True
    STOP = False
    DEVICE_DICT = {}

    call_slack("Starting up")

    # Start the thread(s)
    for i in range(len(DATA)):
        t = Thread(target=who_is_here, args=(i,))
        t.start()

    while True:
        # mac defaults
        A_COMMAND = "arp -a"
        A_SPLIT = " "
        A_MAC_INDEX = 3
        A_IP_INDEX = 1
 
        PLATFORM = platform.system()
        # linux
        if PLATFORM == "Linux":
            A_COMMAND = "sudo arp-scan --interface=eth0 --localnet --retry=4"
            A_SPLIT = "\t"
            A_MAC_INDEX = 1
            A_IP_INDEX = 0

        OUTPUT = subprocess.check_output(A_COMMAND, shell=True)
        LINES = OUTPUT.splitlines(False)
        for l in LINES:
            conns = l.split(A_SPLIT)
            if len(conns) > 1 and re.match(MAC_REGEX, conns[A_MAC_INDEX].lower()):
                mac = conns[A_MAC_INDEX].upper()
                # mac arp-scan wraps the ip in parans
                ip_addr = re.search(IP_REGEX, conns[A_IP_INDEX]).group(0)

                # if we have a mac not already captured, see if we should
                if mac not in DEVICE_DICT:
                    for d in DATA:
                        if d["mac"] == mac:
                            DEVICE_DICT[mac] = Device(d["name"], d["mac"])
                            break

                # if mac is tracked, update the device
                if mac in DEVICE_DICT:
                    d = DEVICE_DICT[mac]
                    if not d.online:
                        call_slack(d.name + " is here")
                    DEVICE_DICT[mac].seen(ipv4=ip_addr)

        # Wait 5 seconds between arp-scans
        sleep(5)

except KeyboardInterrupt:
    # On a keyboard interrupt signal threads to exit
    STOP = True
    call_slack("Shutting down")
    sleep(30)
    exit()
