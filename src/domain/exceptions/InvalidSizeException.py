from src.domain.exceptions.BadImageException import BadImageException


class InvalidSizeException(BadImageException):
    def __init__(self, message):
        super().__init__(message)
