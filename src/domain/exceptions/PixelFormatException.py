from src.domain.exceptions.BadImageException import BadImageException


class PixelFormatException(BadImageException):
    def __init__(self, message):
        super().__init__(message)
