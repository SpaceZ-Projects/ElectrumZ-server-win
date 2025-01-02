

'''Base class of servers'''

import asyncio
import os
import platform
import re
import signal
import sys
import time
from contextlib import suppress
from functools import partial
from typing import TYPE_CHECKING

from aiorpcx import spawn

from electrumz.lib.util import class_logger

if TYPE_CHECKING:
    from electrumz.server.env import Env


class ServerBase:
    '''Base class server implementation.

    Derived classes are expected to:

    - set PYTHON_MIN_VERSION and SUPPRESS_MESSAGE_REGEX as appropriate
    - implement the serve() coroutine, called from the run() method.
      Upon return the event loop runs until the shutdown signal is received.
    '''
    SUPPRESS_MESSAGE_REGEX = re.compile('SSL handshake|Fatal read error on|'
                                        'SSL error in data received|'
                                        'socket.send() raised exception')
    SUPPRESS_TASK_REGEX = re.compile('accept_connection2')
    PYTHON_MIN_VERSION = (3, 7)

    def __init__(self, env: 'Env'):
        '''Save the environment, perform basic sanity checks, and set the
        event loop policy.
        '''
        # First asyncio operation must be to set the event loop policy
        # as this replaces the event loop
        asyncio.set_event_loop_policy(env.loop_policy)

        self.logger = class_logger(__name__, self.__class__.__name__)
        version_str = ' '.join(sys.version.splitlines())
        self.logger.info(f'Python version: {version_str}')
        self.env = env
        self.start_time = 0

        # Sanity checks
        if sys.version_info < self.PYTHON_MIN_VERSION:
            mvs = '.'.join(str(part) for part in self.PYTHON_MIN_VERSION)
            raise RuntimeError(f'Python version >= {mvs} is required')

        if platform.system() == 'Windows':
            pass
        elif os.geteuid() == 0 and not env.allow_root:
            raise RuntimeError('RUNNING AS ROOT IS STRONGLY DISCOURAGED!\n'
                               'You shoud create an unprivileged user account '
                               'and use that.\n'
                               'To continue as root anyway, restart with '
                               'environment variable ALLOW_ROOT non-empty')

    async def serve(self, shutdown_event: asyncio.Event):
        '''Override to provide the main server functionality.
        Run as a task that will be cancelled to request shutdown.

        Setting the event also shuts down the server.
        '''

    def on_exception(self, loop, context):
        '''Suppress spurious messages it appears we cannot control.'''
        message = context.get('message')
        if message and self.SUPPRESS_MESSAGE_REGEX.match(message):
            return
        if self.SUPPRESS_TASK_REGEX.match(repr(context.get('task'))):
            return
        loop.default_exception_handler(context)

    async def run(self):
        '''Run the server application:

        - record start time
        - install SIGINT and SIGTERM handlers to trigger shutdown_event
        - set loop's exception handler to suppress unwanted messages
        - run the event loop until serve() completes
        '''
        def on_signal(signame):
            shutdown_event.set()
            self.logger.warning(f'received {signame} signal, initiating shutdown')

        async def serve():
            try:
                await self.serve(self._shutdown_event)
            finally:
                self._shutdown_event.set()

        self.start_time = time.time()
        loop = asyncio.get_event_loop()
        self._shutdown_event = asyncio.Event()

        if platform.system() != 'Windows':
            # No signals on Windows
            for signame in ('SIGINT', 'SIGTERM'):
                loop.add_signal_handler(getattr(signal, signame),
                                        partial(on_signal, signame))
        loop.set_exception_handler(self.on_exception)

        # Start serving and wait for shutdown, log receipt of the event
        self._server_task = await spawn(serve, daemon=True)
        try:
            await self._shutdown_event.wait()
        except KeyboardInterrupt:
            self.logger.warning('received keyboard interrupt, initiating shutdown')

        self.logger.info('shutting down')

        self._server_task.cancel()
        try:
            with suppress(asyncio.CancelledError):
                await self._server_task
        finally:
            self.logger.info('shutdown complete')

    
    def stop(self):
        '''Stop the server gracefully. This will cancel the server task and set the shutdown event.'''
        if self._server_task:
            self.logger.info('Stopping server...')
            self._shutdown_event.set()  # Trigger shutdown event

            # Cancel the server task
            self._server_task.cancel()

            try:
                with suppress(asyncio.CancelledError):
                    asyncio.create_task(self._server_task)
            finally:
                self.logger.info('Server stopped.')
