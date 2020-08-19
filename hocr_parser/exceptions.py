class EncodingError(Exception):
    pass


class EmptyDocumentException(Exception):
    pass


class MalformedOCRException(Exception):
    pass


class MissingRequiredMetaField(UserWarning):
    pass
