# -*- coding: utf-8 -*-

import asyncio
from aiorpc.log import rootLogger

__all__ = ['Connection']
_logger = rootLogger.getChild(__name__)


class Connection:
    def __init__(self, reader, writer):
        self.reader = reader
        self.writer = writer
        self._is_closed = False

    async def sendall(self, raw_req, timeout):
        _logger.debug('sending raw_req {} to {}'.format(
            str(raw_req), self.writer.get_extra_info('peername')))
        req = raw_req + b'\r\n'
        self.writer.write(req)
        await asyncio.wait_for(self.writer.drain(), timeout)
        _logger.debug('sending {} completed'.format(str(raw_req)))

    async def recvall(self, timeout):
        _logger.debug('entered recvall')
        buffer, line = bytearray(), b''
        while not line.endswith(b'\r\n'):
            _logger.debug('receiving data, timeout: {}'.format(timeout))
            line = await asyncio.wait_for(self.reader.readline(), timeout)
            if not line:
                break
            _logger.debug('received data {}'.format(line))
            buffer.extend(line)
        _logger.debug('buffer: {}'.format(buffer))
        _logger.debug('exiting recvall')
        return buffer[:-2]

    def close(self):
        self.reader.feed_eof()
        self.writer.close()
        self._is_closed = True

    def is_closed(self):
        return self._is_closed
