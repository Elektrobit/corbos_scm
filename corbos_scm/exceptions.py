# Copyright (c) 2021 Marcus Schaefer.  All rights reserved.
#
# This file is part of corbos_scm.
#
# corbos_scm is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# corbos_scm is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with corbos_scm. If not, see <http://www.gnu.org/licenses/>
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
