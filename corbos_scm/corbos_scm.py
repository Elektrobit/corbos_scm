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
from corbos_scm.exceptions import exception_handler


@exception_handler
def main() -> None:
    args = docopt.docopt(__doc__, version=__version__)

    print(args)

    # 1. Find version in debian/changelog
    #    Example: "xsnow (1:3.3.2-1) unstable; urgency=low"
    #    -> xsnow-3.3.2/... (xsnow_3.3.2.orig.tar.gz)
    #    -> debian/... (xsnow_3.3.2-1.debian.tar.xz)

    # 2. Prepare source checkout into tar'able directories
    #    -> xsnow-3.3.2/
    #    -> debian/
    #    And tar them up

    # 3. Create DSC (xsnow_3.3.2-1.dsc) file
    #    -> read contents of debian/control, some data there can be
    #       added 1:1, other data needs to be created in different
    #       format. Create shasums
