# coding: utf-8
"""Utils to handle Paramiko's IO operations.
"""

import time

from paramiko.channel import ChannelFile
from paramiko.common import io_sleep


class BufferTimeoutWrapper(object):
    """Wrapper for Paramiko's ChannelStdinFile subclasses with timeout for read operations"""

    def __init__(self, wrapped, timeout=0):
        if not isinstance(wrapped, ChannelFile):
            raise ValueError("Expecting paramiko.channel.ChannelFile instance")
        self.timeout = timeout
        self._wrapped = wrapped

    def read(self, size=None):
        expiry_time = time.time() + self.timeout

        while not self._wrapped.channel.eof_received:
            if time.time() < expiry_time:
                time.sleep(io_sleep)
            else:
                self._wrapped.channel.close()
                break

        return self._wrapped.read(size=size)

    def __getattr__(self, item):
        return getattr(self._wrapped, item)


class BufferTimeoutHandler(object):
    """Context manager handling Paramiko's SFTP channel, which occasionally hangs
       on read operations, while working with exotic server implementations"""

    def __init__(self, fp, timeout=None):
        self.fp = fp
        self.timeout = timeout

    def __enter__(self):
        if self.timeout is not None:
            return BufferTimeoutWrapper(self.fp, self.timeout)
        else:
            return self.fp

    def __exit__(self, exc_type, exc_value, traceback):
        pass
