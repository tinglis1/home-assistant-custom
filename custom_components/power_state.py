
import logging
from homeassistant.helpers.event import track_state_change
from homeassistant.const import STATE_ON, STATE_OFF, STATE_HOME, STATE_NOT_HOME, MATCH_ALL

_LOGGER = logging.getLogger(__name__)

DOMAIN = 'power'
DEPENDENCIES = []

def setup(hass, config=None):
    """Setup the Power component. """
    _LOGGER.info("The 'current_power_mwh' component is ready!")
    def state_changed(entity_id, old_state, new_state):
        if new_state is None:
            return
        if 'current_power_mwh' in new_state.attributes:
            hass.states.set('sensor.%s_power' % new_state.object_id,
                            float(new_state.attributes['current_power_mwh'])/1000,
                            {
                                'friendly_name': "%s Power" % new_state.attributes['friendly_name'],
                                'unit_of_measurement': 'W',
                                'icon': 'mdi:power-socket'
                            })

    track_state_change(hass, MATCH_ALL, state_changed)

    return True