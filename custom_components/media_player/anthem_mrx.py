"""
Support for interface with a Anthem MRX Receiver.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/media_player/
"""
import logging
import socket
import select
import time
import re

import voluptuous as vol

from homeassistant.helpers import template
from homeassistant.components.media_player import ( 
    SUPPORT_TURN_OFF, SUPPORT_VOLUME_MUTE, SUPPORT_VOLUME_SET, SUPPORT_SELECT_SOURCE,
    SUPPORT_VOLUME_STEP, MediaPlayerDevice, PLATFORM_SCHEMA)
from homeassistant.const import (
    CONF_HOST, CONF_NAME, STATE_OFF, STATE_ON, STATE_UNKNOWN, CONF_PORT)
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

DEFAULT_NAME = 'Anthem MRX'
DEFAULT_PORT = 4999
DEFAULT_MRXZONE = 1
CONF_PORT = "port"
CONF_MRXZONE = "mrxzone"
CONF_MINVOL = "minvol"
CONF_MAXVOL = "maxvol"
DEFAULT_MINVOL = -60
DEFAULT_MAXVOL = -30
CONF_TIMEOUT = "timeout"
CONF_BUFFER_SIZE = "buffer_size"
DEFAULT_TIMEOUT = 10
DEFAULT_BUFFER_SIZE = 1024
CONF_PAYLOAD = "payload"

# attributes
ATTR_LASTUPDATETIME = 'LastUpdateTime'
ATTR_LASTUPDATETIMESTR = 'LastUpdateTimeStr'
ATTR_RESPONSE = 'RawResponse'

SUPPORT_ANTHEMMRX = SUPPORT_SELECT_SOURCE | SUPPORT_VOLUME_STEP | \
    SUPPORT_VOLUME_SET | SUPPORT_VOLUME_MUTE | \
    SUPPORT_TURN_OFF

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_HOST): cv.string,
    vol.Required(CONF_PORT, default=DEFAULT_PORT): cv.port,
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
})

def setup_platform(hass, config, add_devices, discovery_info=None):

    add_devices([AnthemMrx(hass, config)])
    return True

class AnthemMrx(MediaPlayerDevice):

    def __init__(self, hass, config):

        MRX_SOURCE_NUM = ['1', '2', '3', '4', '5', '6', '7', '8', '9', 'c', 'd', 'e']
        MRX_SOURCE_NAME = ['BDP', 'CD', 'TV', 'SAT', 'GAME', 'AUX', 'MEDIA', 'AM/FM', 'iPod', 'current main zone source', 'USB', 'Internet Radio']
        # self._MRX_SOURCE_NUM = MRX_SOURCE_NUM
        # self._MRX_SOURCE_NAME = MRX_SOURCE_NAME
        
        
        self._name = config.get(CONF_NAME)
        self._muted = None
        self._volume = 0
        self._state = STATE_UNKNOWN
        self._response = None
        self._lastupdatetime = None
        self._selected_source = ''
        self._source_name_to_number = dict(zip(MRX_SOURCE_NAME, MRX_SOURCE_NUM))
        self._source_number_to_name = dict(zip(MRX_SOURCE_NUM, MRX_SOURCE_NAME))
        self._config = {
            CONF_NAME: config.get(CONF_NAME),
            CONF_HOST: config[CONF_HOST],
            CONF_PORT: config[CONF_PORT],
            CONF_MRXZONE: config.get(CONF_MRXZONE, DEFAULT_MRXZONE),
            CONF_MINVOL: config.get(CONF_MINVOL, DEFAULT_MINVOL),
            CONF_MAXVOL: config.get(CONF_MAXVOL, DEFAULT_MAXVOL),
            CONF_TIMEOUT: config.get(CONF_TIMEOUT, DEFAULT_TIMEOUT),
            CONF_BUFFER_SIZE: config.get(
                CONF_BUFFER_SIZE, DEFAULT_BUFFER_SIZE),
        }
        self.update()

    def update(self):
        CONF_PAYLOAD = "P" + str(self._config[CONF_MRXZONE]) + "?\r\n"
        response = self.send_command(CONF_PAYLOAD)    
        self._response = response
        # self._state = response
        
        
        try:
            # check for the power off default messages for zone 1 and zone 2
            if bool(re.search("Main.Off",response)) and self._config[CONF_MRXZONE] == 1:
              self._state = STATE_OFF
              return
            if bool(re.search("Zone2.Off",response)) and self._config[CONF_MRXZONE] == 2:
              self._state = STATE_OFF
              return

            # regex the response
            responseObj = re.match(r'P(.)S(.)V(.*)M(.)D(.)', response)
            #check if the correct zone has been returned
            if int(responseObj.group(1)) != self._config[CONF_MRXZONE]:
              return
            
            self._volume = max(min((int(responseObj.group(3)) + (0 - self._config[CONF_MINVOL])) / (self._config[CONF_MAXVOL] - self._config[CONF_MINVOL]),1),0)
            
            # check if it is muted
            if int(responseObj.group(4)) == 0:
              self._muted = False
            else:
              self._muted = True
            
            self._selected_source = self._source_number_to_name.get(responseObj.group(2))
            _LOGGER.info("SourceNum: " + responseObj.group(2) + " SourceName: " + self._selected_source)
           
            # if the try is pass then make the state on
            self._state = STATE_ON
        except (socket.timeout, TimeoutError, OSError):
            self._state = STATE_OFF
         
    def send_command(self, payload):
        _LOGGER.info("Payload: " + payload)
        """Send a command to the AnthemMRX and return the response"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(self._config[CONF_TIMEOUT])
            try:
                sock.connect(
                    (self._config[CONF_HOST], self._config[CONF_PORT]))
            except socket.error as err:
                _LOGGER.error(
                    "Unable to connect to %s on port %s: %s",
                    self._config[CONF_HOST], self._config[CONF_PORT], err)
                return

            try:
                sock.send(payload.encode())
            except socket.error as err:
                _LOGGER.error(
                    "Unable to send payload %r to %s on port %s: %s",
                    payload, self._config[CONF_HOST],
                    self._config[CONF_PORT], err)
                return

            readable, _, _ = select.select(
                [sock], [], [], self._config[CONF_TIMEOUT])
            if not readable:
                _LOGGER.warning(
                    "Timeout (%s second(s)) waiting for a response after "
                    "sending %r to %s on port %s.",
                    self._config[CONF_TIMEOUT], payload,
                    self._config[CONF_HOST], self._config[CONF_PORT])
                return
            self._lastupdatetime = time.time()
            value = sock.recv(self._config[CONF_BUFFER_SIZE]).decode()
            _LOGGER.info("Response: " + value)
        return value
            
    # @property
    # def state_attributes(self):
        # """ returns the atrributes of the sensor """
        # return {
            # ATTR_LASTUPDATETIME : self._lastupdatetime,
            # ATTR_LASTUPDATETIMESTR : template.timestamp_local(float(self._lastupdatetime)),
            # ATTR_RESPONSE: self._response,
        # }          


    @property
    def source(self):
        """Return the current input source."""
        return self._selected_source

    @property
    def source_list(self):
        """List of available input sources."""
        return list(self._source_name_to_number.keys())
        # return list(self._MRX_SOURCE_NUM)

    def select_source(self, source):
        """Select input source."""
        _LOGGER.info("Select Source: " + self._source_name_to_number.get(source))
        CONF_PAYLOAD = "P" + str(self._config[CONF_MRXZONE]) + "S" + self._source_name_to_number.get(source) + "\n"
        # CONF_PAYLOAD = "P" + str(self._config[CONF_MRXZONE]) + "S" + source + "\n"
        self.send_command(CONF_PAYLOAD)
        
    @property
    def name(self):
        """Return the name of the device."""
        return self._name

    @property
    def state(self):
        """Return the state of the device."""
        return self._state

    @property
    def volume_level(self):
        """Volume level of the media player (0..1)."""
        return self._volume

    @property
    def is_volume_muted(self):
        """Boolean if volume is currently muted."""
        return self._muted

    @property
    def supported_media_commands(self):
        """Flag of media commands that are supported."""
        return SUPPORT_ANTHEMMRX

    def turn_off(self):
        """Turn off media player."""
        CONF_PAYLOAD = "P" + str(self._config[CONF_MRXZONE]) + "P0\n"
        self.send_command(CONF_PAYLOAD)
        
    def turn_on(self):
        """Turn off media player."""
        CONF_PAYLOAD = "P" + str(self._config[CONF_MRXZONE]) + "P1\n"
        self.send_command(CONF_PAYLOAD)
        self.send_command(CONF_PAYLOAD)

    def volume_up(self):
        """Volume up the media player."""
        CONF_PAYLOAD = "P" + str(self._config[CONF_MRXZONE]) + "VU\n"
        self.send_command(CONF_PAYLOAD) 


    def volume_down(self):
        """Volume down media player."""
        CONF_PAYLOAD = "P" + str(self._config[CONF_MRXZONE]) + "VD\n"
        self.send_command(CONF_PAYLOAD) 

    def mute_volume(self, mute):
        """Send mute command."""
        CONF_PAYLOAD = "P" + str(self._config[CONF_MRXZONE]) + "MT\n"
        self.send_command(CONF_PAYLOAD) 

    def set_volume_level(self, volume):
        """Set volume level, range 0..1."""
        
        CONF_PAYLOAD = "P" + str(self._config[CONF_MRXZONE]) + "V-" + str(-1 * int(((self._config[CONF_MAXVOL] - self._config[CONF_MINVOL]) * volume) - (0 - self._config[CONF_MINVOL]))) + "\n"
        self.send_command(CONF_PAYLOAD) 
