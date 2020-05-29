"""Support for Dyson Pure Cool Link devices."""
import logging

import voluptuous as vol

from .controller.dyson_pure_cool_link import DysonPureCoolLink
from .controller.utils import hash_password


from homeassistant.const import CONF_NAME, CONF_PASSWORD, CONF_IP_ADDRESS, CONF_PORT, CONF_TYPE, CONF_TIMEOUT
from homeassistant.helpers import discovery
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

CONF_LANGUAGE = "language"
CONF_RETRY = "retry"
CONF_SERIAL = "serial"

DEFAULT_PORT = 1883
DEFAULT_TYPE = 475 # Usually one of 455, 465, 475
DEFAULT_TIMEOUT = 5
DEFAULT_RETRY = 10
DEFAULT_NAME = "Dyson Fan"
DYSON_DEVICES = "dyson_devices"
DYSON_PLATFORMS = ["sensor", "fan"]

DOMAIN = "dyson_fan"

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_PASSWORD): cv.string,
                vol.Required(CONF_SERIAL): cv.string,
                vol.Required(CONF_IP_ADDRESS): cv.string,
                vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.positive_int,
                vol.Optional(CONF_TYPE, default=DEFAULT_TYPE): cv.string,
                vol.Optional(CONF_TIMEOUT, default=DEFAULT_TIMEOUT): cv.positive_int,
                vol.Optional(CONF_RETRY, default=DEFAULT_RETRY): cv.positive_int,
                vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)


def setup(hass, config):
    """Set up the Dyson parent component."""
    _LOGGER.info("Creating new Dyson component")

    if DYSON_DEVICES not in hass.data:
        hass.data[DYSON_DEVICES] = []

    timeout = config[DOMAIN].get(CONF_TIMEOUT)
    retry = config[DOMAIN].get(CONF_RETRY)
    password = config[DOMAIN].get(CONF_PASSWORD)
    serial = config[DOMAIN].get(CONF_SERIAL)
    ip = config[DOMAIN].get(CONF_IP_ADDRESS)
    name = config[DOMAIN].get(CONF_NAME)
    fan_type = config[DOMAIN].get(CONF_TYPE)

    device_details = {
        "Serial": serial,
        "Name": name,
        "LocalCredentials": password,
        "ProductType": fan_type
    }

    dyson_device = DysonPureCoolLink(device_details)
    _LOGGER.info(
        "Trying to connect to device %s with timeout=%i and retry=%i and ip=%s",
        dyson_device.serial,
        timeout,
        retry,
        ip
    )

    connected = dyson_device.connect(ip)
    if connected:
        _LOGGER.info("Connected to device %s", dyson_device.serial)
        hass.data[DYSON_DEVICES].append(dyson_device)
    else:
        _LOGGER.warning("Unable to connect to device %s", dyson_device.serial)

    # Start fan/sensors components
    if hass.data[DYSON_DEVICES]:
        _LOGGER.debug("Starting sensor/fan components")
        for platform in DYSON_PLATFORMS:
            discovery.load_platform(hass, platform, DOMAIN, {}, config)

    return True
