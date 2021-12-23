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
import os
import subprocess
from typing import (
    NamedTuple, List, Dict
)
from corbos_scm.exceptions import CSCMCommandError

command_type = NamedTuple(
    'command_type', [
        ('output', str),
        ('error', str),
        ('returncode', int)
    ]
)


class Command:
    """
    Simple command invocation interface
    """
    @staticmethod
    def run(
        command: List, custom_env: Dict[str, str] = None,
        raise_on_error: bool = True
    ) -> command_type:
        """
        Execute a program and block the caller.

        :param list command: command and arguments
        :param list custom_env: custom os.environ
        :param bool raise_on_error:
            if true, raise exception if command did not succeed
            ecode != 0

        :return:
            A command_type

        :rtype: NamedTuple
        """
        environment = custom_env if custom_env else os.environ
        try:
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=environment
            )
        except Exception as issue:
            raise CSCMCommandError(
                f'{issue!r}'
            )
        output, error = process.communicate()
        if process.returncode != 0 and raise_on_error:
            raise CSCMCommandError(
                f'stderr: {error!r}, stdout: {output!r}'
            )
        return command_type(
            output=format(output),
            error=format(error),
            returncode=process.returncode
        )
