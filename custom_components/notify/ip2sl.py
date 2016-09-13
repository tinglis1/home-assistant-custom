"""
Send ip to serial platform for notify component.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/notify.ip2sl
"""
import logging
import socket
import select
import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from homeassistant.components.notify import (
    PLATFORM_SCHEMA, BaseNotificationService)
from homeassistant.const import (
    CONF_HOST, CONF_PORT)

_LOGGER = logging.getLogger(__name__)

CONF_TIMEOUT = "timeout"
DEFAULT_TIMEOUT = 10
DEFAULT_BUFFER_SIZE = 1024
CONF_BUFFER_SIZE = "buffer_size"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_HOST): cv.string,
    vol.Required(CONF_PORT): cv.port,
    vol.Optional(CONF_TIMEOUT, default=DEFAULT_TIMEOUT): cv.positive_int,
})


def get_service(hass, config):
    """Get the IP2SL service."""

    return SendCommand(config[CONF_HOST], config[CONF_PORT], config)


class SendCommand(BaseNotificationService):
    """Implement the IP2SL service."""

    def __init__(self, host, port, config):
        """Initialize the service."""
        self._host = host
        self._port = port
        self._timeout = config.get(CONF_TIMEOUT, DEFAULT_TIMEOUT)
        self._buffersize = config.get(CONF_BUFFER_SIZE, DEFAULT_BUFFER_SIZE)

    def send_message(self, message="", **kwargs):
        """Send command to IP2SL."""
        self.send_command(message)

    def send_command(self, payload):
        payload = payload + '\r'
        _LOGGER.info("Payload: {}".format(payload))
        """Send a command to the IP2SL and return the response"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(self._timeout)
            try:
                sock.connect(
                    (self._host, self._port))
            except socket.error as err:
                _LOGGER.error(
                    "Unable to connect to {} on port {}: {}".format(
                                            self._host, self._port, err))
                return

            try:
                # sock.send(payload)
                sock.send(payload.encode())
            except socket.error as err:
                _LOGGER.error(
                    "Unable to send payload {} to {} on port {}: {}".format(
                                        payload, self._host, self._port, err))
                return

            readable, _, _ = select.select(
                [sock], [], [], self._timeout)
            if not readable:
                _LOGGER.warning(
                    "Timeout ({} second(s)) waiting for a response after "
                    "sending {} to {} on port {}.".format(
                            self._timeout, payload, self._host, self._port))
                return
            value = sock.recv(self._buffersize).decode()
            _LOGGER.info("Response: {}".format(value))
        return value
