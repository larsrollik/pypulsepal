import numpy as np


def volts_to_bytes(volt=None, dac_bitMax=None):
    return np.ceil(((volt + 10) / float(20)) * dac_bitMax)


def encode_message(*message_parts, encoding=None):
    message = [np.array(part, dtype=encoding).tobytes() for part in message_parts]
    out = b"".join(message)
    return out
