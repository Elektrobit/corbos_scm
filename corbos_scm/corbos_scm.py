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
"""
Usage:
    corbos_scm --git=<git_clone_source> --package=<package_path> --outdir=<obs_out>
        [--branch=<name>]
    corbos_scm -h | --help
    corbos_scm --version

Options:
    --git=<git_clone_source>
        git clone location to fetch packages sources.
        It is expected that the sources are stored in a format
        matching the EB Corbos Linux project.

    --package=<package_path>
        Path to package relative to --git root

    --branch=<name>
        Branch in git source [default: master].

    --outdir=<obs_out>
        Output directory to store data produced by the service.
        At the time the service is called through the OBS API
        this option is set.
"""
import docopt

from corbos_scm.version import __version__


def main() -> None:
    args = docopt.docopt(__doc__, version=__version__)

    print(args)
