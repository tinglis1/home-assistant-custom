"""
Support for switches which integrates with other components.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/switch.template/
"""
import logging
import voluptuous as vol
import homeassistant.helpers.config_validation as cv

from homeassistant.components.light import (
    ATTR_SUPPORTED_FEATURES, ENTITY_ID_FORMAT, Light, PLATFORM_SCHEMA)
from homeassistant.const import (
    ATTR_FRIENDLY_NAME, CONF_VALUE_TEMPLATE, STATE_OFF, STATE_ON,
    ATTR_ENTITY_ID, MATCH_ALL)
from homeassistant.exceptions import TemplateError
from homeassistant.helpers.entity import generate_entity_id
from homeassistant.helpers.script import Script
from homeassistant.helpers import template
from homeassistant.helpers.event import track_state_change

CONF_SWITCHES = 'switches'

# ENTITY_SWITCH = 'entity_switch'

_LOGGER = logging.getLogger(__name__)
_VALID_STATES = [STATE_ON, STATE_OFF, 'true', 'false']

SWITCH_SCHEMA = vol.Schema({
    vol.Optional(ATTR_FRIENDLY_NAME): cv.string,
    vol.Required(ATTR_ENTITY_ID, default=MATCH_ALL): cv.entity_ids
})

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_SWITCHES): vol.Schema({cv.slug: SWITCH_SCHEMA}),
})



def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the Template switch."""
    switches = []

    for device, device_config in config[CONF_SWITCHES].items():
        friendly_name = device_config.get(ATTR_FRIENDLY_NAME, device)
        entity_switch = device_config[ATTR_ENTITY_ID]

        switches.append(
            LightSwitch(
                hass,
                device,
                friendly_name,
                entity_switch)
            )
    if not switches:
        _LOGGER.error("No switches added")
        return False
    add_devices(switches)
    return True


class LightSwitch(Light):
    """Representation of a Template switch."""

    def __init__(self, hass, device_id, friendly_name, entity_switch):
        """Initialize the Template switch."""
        self.hass = hass
        self.entity_id = generate_entity_id(ENTITY_ID_FORMAT, device_id, hass=hass)
        self.entity_switch = entity_switch[0]
        self._name = friendly_name
        self._state = False

        self.update()
        
        _LOGGER.info("entity_switch: " + str(self.entity_switch))
        _LOGGER.info("entity_id: " + str(self.entity_id))
        
        def switch_state_listener(entity, old_state, new_state):
            """Called when the target device changes state."""
            self.update_ha_state(True)

        track_state_change(hass, self.entity_switch, switch_state_listener)

    @property
    def name(self):
        """Return the name of the switch."""
        return self._name

    @property
    def is_on(self):
        """Return true if device is on."""
        return self._state 

    def turn_on(self):
        """turn the switch on."""
        self.hass.states.set(self.entity_switch, STATE_ON)

    def turn_off(self):
        """turn the switch off."""
        self.hass.states.set(self.entity_switch, STATE_OFF)

    def update(self):
        """Update the state from the switch."""
        if "on" in str(self.hass.states.get(self.entity_switch)):
            self._state = True
        if "off" in str(self.hass.states.get(self.entity_switch)):
            self._state = False
            
    # @property
    # def supported_features(self):
        # """Flag supported features."""
        # return 0
        
    @property
    def should_poll(self):
        """No polling needed."""
        return False

    @property
    def available(self):
        """If switch is available."""
        return self._state is not None