"""Classes"""
import datetime

class Device(object):
    """Device info"""
    def __init__(self, name, mac):
        self.name = name
        self.mac = mac
        self.ipv4 = ""
        self.last_seen = datetime.datetime.now() - datetime.timedelta(days=1)
        self._online = False
        self._broadcast_state_change = False

    def is_active(self, secs):
        """returns a bool indicating if the Device is active"""
        active = self.last_seen + datetime.timedelta(seconds=secs) >= datetime.datetime.now()
        if not active:
            self._set_online(active)
        return active

    def seen(self, **kwargs):
        """updates last_seen to now() and optionally sets the ip"""
        self._set_online(True)
        self.last_seen = datetime.datetime.now()
        if 'ipv4' in kwargs:
            self.ipv4 = kwargs['ipv4']

    def get_status_message(self, **kwargs):
        """
        Gets a status message is the active status as changed.
        Once the message is generated, calling this function subsequent times will return ""
        unless the active status is changed or the optional param 'override' is True
        """
        message = ""
        if (self._broadcast_state_change or
                ('override' in kwargs and kwargs['override'])):
            self._broadcast_state_change = False
            message = self.name + " is "
            if self._online:
                message += "online!"
            else:
                message += "gone!"
        return message

    def _set_online(self, is_online):
        """sets online status"""
        if is_online != self._online:
            self._broadcast_state_change = True
            self._online = is_online
