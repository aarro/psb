"""misc utils"""
import subprocess

def arping(mac, ipv4):
    """run arping against a mac and ipv4"""
    found = False
    command = "sudo arping -c 3 -t " + mac + " " + ipv4
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
        lines = output.splitlines(False)
        for line in lines:
            ping = line.split(" ")
            if len(ping) > 3:
                found = True
                break
    except subprocess.CalledProcessError:
        pass # timeout

    return (mac, found)
