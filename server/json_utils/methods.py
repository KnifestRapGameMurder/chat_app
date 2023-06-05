import json

ENCODING = "ascii"


def serialize(obj) -> bytes:
    return json.dumps(obj).encode(ENCODING)


def deserialize(message: bytes):
    return json.loads(message.decode(ENCODING))
