"""Support for Dyson Pure Cool link fan."""
import logging

from .controller.const import FanMode, FanSpeed, NightMode, Oscillation
from .controller.dyson_pure_cool_link import DysonPureCoolLink
from .controller.dyson_pure_state import DysonPureCoolState
import voluptuous as vol

from homeassistant.components.fan import (
    SPEED_HIGH,
    SPEED_LOW,
    SPEED_MEDIUM,
    SUPPORT_OSCILLATE,
    SUPPORT_SET_SPEED,
    FanEntity,
)
from homeassistant.const import ATTR_ENTITY_ID
import homeassistant.helpers.config_validation as cv

from . import DYSON_DEVICES

_LOGGER = logging.getLogger(__name__)

ATTR_NIGHT_MODE = "night_mode"
ATTR_AUTO_MODE = "auto_mode"
ATTR_TIMER = "timer"
ATTR_DYSON_SPEED = "dyson_speed"
ATTR_DYSON_SPEED_LIST = "dyson_speed_list"

DYSON_DOMAIN = "dyson_fan"
DYSON_FAN_DEVICES = "dyson_fan_devices"

SERVICE_SET_NIGHT_MODE = "set_night_mode"
SERVICE_SET_AUTO_MODE = "set_auto_mode"
SERVICE_SET_TIMER = "set_timer"
SERVICE_SET_DYSON_SPEED = "set_speed"

DYSON_SET_NIGHT_MODE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTITY_ID): cv.entity_id,
        vol.Required(ATTR_NIGHT_MODE): cv.boolean,
    }
)

SET_AUTO_MODE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTITY_ID): cv.entity_id,
        vol.Required(ATTR_AUTO_MODE): cv.boolean,
    }
)

SET_TIMER_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTITY_ID): cv.entity_id,
        vol.Required(ATTR_TIMER): cv.positive_int,
    }
)

SET_DYSON_SPEED_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTITY_ID): cv.entity_id,
        vol.Required(ATTR_DYSON_SPEED): cv.positive_int,
    }
)


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the Dyson fan components."""

    if discovery_info is None:
        return

    _LOGGER.debug("Creating new Dyson fans")
    if DYSON_FAN_DEVICES not in hass.data:
        hass.data[DYSON_FAN_DEVICES] = []

    # Get Dyson Devices from parent component
    device_serials = [device.serial for device in hass.data[DYSON_FAN_DEVICES]]
    for device in hass.data[DYSON_DEVICES]:
        if device.serial not in device_serials:
            if isinstance(device, DysonPureCoolLink):
                dyson_entity = DysonPureCoolLinkDevice(hass, device)
                hass.data[DYSON_FAN_DEVICES].append(dyson_entity)

    add_entities(hass.data[DYSON_FAN_DEVICES])

    def service_handle(service):
        """Handle the Dyson services."""
        entity_id = service.data[ATTR_ENTITY_ID]
        fan_device = next(
            (fan for fan in hass.data[DYSON_FAN_DEVICES] if fan.entity_id == entity_id),
            None,
        )
        if fan_device is None:
            _LOGGER.warning("Unable to find Dyson fan device %s", str(entity_id))
            return

        if service.service == SERVICE_SET_NIGHT_MODE:
            fan_device.set_night_mode(service.data[ATTR_NIGHT_MODE])

        if service.service == SERVICE_SET_AUTO_MODE:
            fan_device.set_auto_mode(service.data[ATTR_AUTO_MODE])

        if service.service == SERVICE_SET_TIMER:
            fan_device.set_timer(service.data[ATTR_TIMER])

        if service.service == SERVICE_SET_DYSON_SPEED:
            fan_device.set_dyson_speed(service.data[ATTR_DYSON_SPEED])

    # Register dyson service(s)
    hass.services.register(
        DYSON_DOMAIN,
        SERVICE_SET_NIGHT_MODE,
        service_handle,
        schema=DYSON_SET_NIGHT_MODE_SCHEMA,
    )

    hass.services.register(
        DYSON_DOMAIN, SERVICE_SET_AUTO_MODE, service_handle, schema=SET_AUTO_MODE_SCHEMA
    )

class DysonPureCoolLinkDevice(FanEntity):
    """Representation of a Dyson fan."""

    def __init__(self, hass, device):
        """Initialize the fan."""
        _LOGGER.debug("Creating device %s", device.name)
        self.hass = hass
        self._device = device

    async def async_added_to_hass(self):
        """Call when entity is added to hass."""
        self.hass.async_add_job(self._device.add_message_listener, self.on_message)

    def on_message(self, message):
        """Call when new messages received from the fan."""

        if isinstance(message, DysonPureCoolState):
            _LOGGER.debug("Message received for fan device %s: %s", self.name, message)
            self.schedule_update_ha_state()

    @property
    def should_poll(self):
        """No polling needed."""
        return False

    @property
    def name(self):
        """Return the display name of this fan."""
        return self._device.name

    def set_speed(self, speed: str) -> None:
        """Set the speed of the fan. Never called ??."""
        _LOGGER.debug("Set fan speed to: %s", speed)

        if speed == FanSpeed.FAN_SPEED_AUTO.value:
            self._device.set_configuration(fan_mode=FanMode.AUTO)
        else:
            fan_speed = FanSpeed(f"{int(speed):04d}")
            self._device.set_configuration(fan_mode=FanMode.FAN, fan_speed=fan_speed)

    def turn_on(self, speed: str = None, **kwargs) -> None:
        """Turn on the fan."""
        _LOGGER.debug("Turn on fan %s with speed %s", self.name, speed)
        if speed:
            if speed == FanSpeed.FAN_SPEED_AUTO.value:
                self._device.set_configuration(fan_mode=FanMode.AUTO)
            else:
                fan_speed = FanSpeed(f"{int(speed):04d}")
                self._device.set_configuration(
                    fan_mode=FanMode.FAN, fan_speed=fan_speed
                )
        else:
            # Speed not set, just turn on
            self._device.set_configuration(fan_mode=FanMode.FAN)

    def turn_off(self, **kwargs) -> None:
        """Turn off the fan."""
        _LOGGER.debug("Turn off fan %s", self.name)
        self._device.set_configuration(fan_mode=FanMode.OFF)

    def oscillate(self, oscillating: bool) -> None:
        """Turn on/off oscillating."""
        _LOGGER.debug("Turn oscillation %s for device %s", oscillating, self.name)

        if oscillating:
            self._device.set_configuration(oscillation=Oscillation.OSCILLATION_ON)
        else:
            self._device.set_configuration(oscillation=Oscillation.OSCILLATION_OFF)

    @property
    def oscillating(self):
        """Return the oscillation state."""
        return self._device.state and self._device.state.oscillation == "ON"

    @property
    def is_on(self):
        """Return true if the entity is on."""
        if self._device.state:
            return self._device.state.fan_mode == "FAN"
        return False

    @property
    def speed(self) -> str:
        """Return the current speed."""
        if self._device.state:
            if self._device.state.speed == FanSpeed.FAN_SPEED_AUTO.value:
                return self._device.state.speed
            return int(self._device.state.speed)
        return None

    @property
    def current_direction(self):
        """Return direction of the fan [forward, reverse]."""
        return None

    @property
    def night_mode(self):
        """Return Night mode."""
        return self._device.state.night_mode == "ON"

    def set_night_mode(self, night_mode: bool) -> None:
        """Turn fan in night mode."""
        _LOGGER.debug("Set %s night mode %s", self.name, night_mode)
        if night_mode:
            self._device.set_configuration(night_mode=NightMode.NIGHT_MODE_ON)
        else:
            self._device.set_configuration(night_mode=NightMode.NIGHT_MODE_OFF)

    @property
    def auto_mode(self):
        """Return auto mode."""
        return self._device.state.fan_mode == "AUTO"

    def set_auto_mode(self, auto_mode: bool) -> None:
        """Turn fan in auto mode."""
        _LOGGER.debug("Set %s auto mode %s", self.name, auto_mode)
        if auto_mode:
            self._device.set_configuration(fan_mode=FanMode.AUTO)
        else:
            self._device.set_configuration(fan_mode=FanMode.FAN)

    @property
    def speed_list(self) -> list:
        """Get the list of available speeds."""
        supported_speeds = [
            FanSpeed.FAN_SPEED_AUTO.value,
            int(FanSpeed.FAN_SPEED_1.value),
            int(FanSpeed.FAN_SPEED_2.value),
            int(FanSpeed.FAN_SPEED_3.value),
            int(FanSpeed.FAN_SPEED_4.value),
            int(FanSpeed.FAN_SPEED_5.value),
            int(FanSpeed.FAN_SPEED_6.value),
            int(FanSpeed.FAN_SPEED_7.value),
            int(FanSpeed.FAN_SPEED_8.value),
            int(FanSpeed.FAN_SPEED_9.value),
            int(FanSpeed.FAN_SPEED_10.value),
        ]

        return supported_speeds

    @property
    def supported_features(self) -> int:
        """Flag supported features."""
        return SUPPORT_OSCILLATE | SUPPORT_SET_SPEED

    @property
    def device_state_attributes(self) -> dict:
        """Return optional state attributes."""
        return {ATTR_NIGHT_MODE: self.night_mode, ATTR_AUTO_MODE: self.auto_mode}