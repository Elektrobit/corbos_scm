# Copyright (c) 2021 Marcus Schäfer
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
import sys
import logging
from functools import wraps
from typing import Callable

log = logging.getLogger('corbos_scm')


def exception_handler(func: Callable) -> Callable:
    """
    Decorator method to add exception handling
    Methods marked with this decorator are called under
    control of the cloud builder exceptions

    :param Callable func: Function pointer

    :return: func, wrapped with exception handling

    :rtype: Callable
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except CSCMError as issue:
            # known exception, log information and exit
            log.error(f'{type(issue).__name__}: {issue}')
            sys.exit(1)
        except KeyboardInterrupt:
            log.error('Exit on keyboard interrupt')
            sys.exit(1)
        except SystemExit as issue:
            # user exception, program aborted by user
            sys.exit(issue)
        except Exception:
            # exception we did no expect, show python backtrace
            log.error('Unexpected error:')
            raise
    return wrapper


class CSCMError(Exception):
    """
    Base class to handle all known exceptions

    Specific exceptions are implemented as sub classes of CBError
    """
    def __init__(self, message) -> None:
        """
        Store exception message

        :param str message: Exception message text
        """
        self.message = message

    def __str__(self) -> str:
        """
        Return representation of exception message

        :return: A message

        :rtype: str
        """
        return format(self.message)


class CSCMCommandError(CSCMError):
    """
    Exception raised if popen call failed and or command
    execution was not successful
    """
