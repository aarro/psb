"""
bot
"""
import json
import os
import platform
import re
import subprocess
from time import sleep
from slackclient import SlackClient
from .classes import Device

MAC_REGEX = "[0-9a-f]{2}([-:])[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$"
IP_REGEX = r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}" \
           r"(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b"

class PSBot(object):
    """The bot"""
    def __init__(self):
        self.os_type = platform.system()
        self.devices = {}
        self.skip_slack = os.environ.get("SKIP_SLACK") or False
        # slack info
        self.slack_token = os.environ.get("SLACK_TOKEN")
        self.group_id = os.environ.get("SLACK_GROUP")
        self.slack_client = SlackClient(self.slack_token)
        # load whitelist
        with open('devices.json') as data_file:
            self._data = json.load(data_file)

    def _call_slack(self, message):
        """Sends a message to slack"""
        if message:
            print message
            if not self.skip_slack:
                self.slack_client.api_call("chat.postMessage",
                                           channel=self.group_id, text=message, as_user=True)

    def start(self):
        """kick off the bot"""
        self._call_slack("Starting up")
        while True:
            self._run_arp()
            self._check_device_activity()
            sleep(1)

    def stop(self):
        """stop the bot"""
        self._call_slack("Shutting down")

    def _check_add_device(self, mac):
        """if we have a mac not already captured, see if we should"""
        if mac not in self.devices:
            for device in self._data:
                if device["mac"] == mac:
                    self.devices[mac] = Device(device["name"], device["mac"])
                    break

    def _check_device_activity(self):
        """loops through all devices to check active state and notify accordingly"""
        for key in self.devices:
            dev = self.devices[key]
            if dev.is_active(300): #active in the last 5min
                pass
            else:
                pass
                # do this on a new thread? new process?
                # arping = "sudo arping -c 3 -t " + dev.mac + " " + dev.ipv4

            message = dev.get_status_message()
            self._call_slack(message)

    def _run_arp(self):
        """run arp scan based on os"""
        # mac defaults
        command = "arp -a"
        split = " "
        mac_index = 3
        ip_index = 1

        # linux
        if self.os_type == "Linux":
            command = "sudo arp-scan --interface=eth0 --localnet --retry=4"
            split = "\t"
            mac_index = 1
            ip_index = 0

        output = subprocess.check_output(command, shell=True)
        lines = output.splitlines(False)
        for line in lines:
            conns = line.split(split)
            if len(conns) > 1 and re.match(MAC_REGEX, conns[mac_index].lower()):
                mac = conns[mac_index].upper()
                self._check_add_device(mac)

                # if mac is tracked, update the device
                if mac in self.devices:
                    # mac arp-scan wraps the ip in parans
                    ip_addr = re.search(IP_REGEX, conns[ip_index]).group(0)
                    self.devices[mac].seen(ipv4=ip_addr)
