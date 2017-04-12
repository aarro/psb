"""Classes"""
import datetime

class Device(object):
    """Device info"""
    def __init__(self, name, mac):
        self.name = name
        self.mac = mac
        self.ipv4 = ""
        self.last_seen = datetime.datetime.now()
        self.online = False

    def is_active(self, secs):
        """returns a bool indicating if the Device is active"""
        active = self.last_seen + datetime.timedelta(seconds=secs) >= datetime.datetime.now()
        return active

    def seen(self, **kwargs):
        """sets online to true and updates last_seen to now()"""
        self.online = True
        self.last_seen = datetime.datetime.now()
        if 'ipv4' in kwargs:
            self.ipv4 = kwargs['ipv4']
