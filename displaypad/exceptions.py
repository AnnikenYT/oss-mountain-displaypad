class DisplayPadError(Exception):
    """Base error for displaypad package."""


class TransportError(DisplayPadError):
    """Transport/USB related error."""


class DeviceNotFoundError(DisplayPadError):
    """Raised when the device cannot be located."""
