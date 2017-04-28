"""Classes"""
import datetime

class Device(object):
    """Device info"""
    def __init__(self, name, mac):
        self.name = name
        self.mac = mac
        self.ipv4 = ""
        self.last_seen = datetime.datetime.now() - datetime.timedelta(days=1)
        self.running_arping = False
        self._online = False
        self._broadcast_state_change = False
        self._last_message = ""

    def is_active(self, secs):
        """Returns a bool indicating if the Device has been active in the last sec seconds"""
        active = self.last_seen + datetime.timedelta(seconds=secs) >= datetime.datetime.now()
        return active

    def seen(self, **kwargs):
        """
        Updates last_seen to now(), which changes the status to Online
        Optionally sets the ip
        """
        self._set_online(True)
        self.last_seen = datetime.datetime.now()
        if 'ipv4' in kwargs:
            self.ipv4 = kwargs['ipv4']

    def unseen(self):
        """Updates the device status to be Offline"""
        self._set_online(False)

    def get_status(self):
        """Gets the status of the device. Statuses include Online, Offline, Arping"""
        if self.running_arping:
            return "Arping"
        else:
            if self._online:
                return "Online"
            else:
                return "Offline"

    def get_status_message(self, **kwargs):
        """
        Gets a status message is the active status as changed.
        Once the message is generated, calling this function subsequent times will return ""
        unless the active status is changed or the optional param 'override' is True
        """
        message = ""
        override = 'override' in kwargs and kwargs['override']
        if self._broadcast_state_change or override:
            self._broadcast_state_change = False
            message = self.name + " is "
            if self._online:
                message += "online!"
            else:
                message += "gone!"

            # if the message is the same as the last time someone asked, don't send it
            if self._last_message == message and not override:
                message = ""
            else:
                self._last_message = message

        return message

    def _set_online(self, is_online):
        """sets online status"""
        if is_online != self._online:
            self._broadcast_state_change = True
            self._online = is_online
