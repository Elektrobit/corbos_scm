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
