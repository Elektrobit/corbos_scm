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
import os
import shutil
import re
from pathlib import Path
from typing import NamedTuple
from tempfile import TemporaryDirectory
import docopt

from corbos_scm.version import __version__
from corbos_scm.command import Command
from corbos_scm.exceptions import (
    exception_handler,
    CSCMDebianSourceNotFound,
    CSCMDebianChangelogFormatNotDetected
)

package_type = NamedTuple(
    'package_type', [
        ('name', str),
        ('upstream_version', str),
        ('debian_revision', str),
        ('target', str)
    ]
)


@exception_handler
def main() -> None:
    args = docopt.docopt(__doc__, version=__version__)

    if not os.path.exists(args['--outdir']):
        Path(args['--outdir']).mkdir(parents=True, exist_ok=True)

    temp_git_dir = TemporaryDirectory(prefix='corbos_scm.')
    Command.run(
        ['git', 'clone', args['--git'], temp_git_dir.name]
    )
    if args['--branch']:
        Command.run(
            ['git', '-C', temp_git_dir.name, 'checkout', args['--branch']]
        )

    package_dir = os.path.join(temp_git_dir.name, args['--package'])
    debian_dir = os.path.join(package_dir, 'debian')

    if not os.path.isdir(debian_dir):
        raise CSCMDebianSourceNotFound(
            f'No debian dir in source: {debian_dir!r}'
        )

    # package_dir = '/home/ms/Project/cloud-builder-packages/projects/Corbos/xsnow'
    # debian_dir = '/home/ms/Project/cloud-builder-packages/projects/Corbos/xsnow/debian'

    package_meta = get_package_meta(debian_dir)

    create_dsc_file(
        debian_dir, args['--outdir']
    )
    create_source_tarballs(
        package_dir, package_meta, args['--outdir']
    )


def get_package_meta(debian_dir: str) -> package_type:
    with open(f'{debian_dir}/changelog') as changelog:
        latest = changelog.readline().strip()
    changelog_format = re.match(
        r'([a-zA-Z0-9_\-\.]+) \((.*)\) (.*);', latest
    )
    if changelog_format:
        debian_revision = changelog_format.group(2).split(':').pop()
        upstream_version = debian_revision.split('-')[0]
        return package_type(
            name=changelog_format.group(1),
            target=changelog_format.group(3),
            debian_revision=debian_revision,
            upstream_version=upstream_version
        )
    else:
        raise CSCMDebianChangelogFormatNotDetected(
            'Unknown format: {latest!r}'
        )


def create_dsc_file(debian_dir: str, outdir: str) -> None:
    # TODO
    # Create DSC (xsnow_3.3.2-1.dsc) file
    #    -> read contents of debian/control, some data there can be
    #       added 1:1, other data needs to be created in different
    #       format. Create shasums
    pass


def create_source_tarballs(
    package_dir: str, package: package_type, outdir: str
) -> None:
    parent_dir = os.path.dirname(package_dir)
    symlink_name = f'{parent_dir}/{package.name}-{package.upstream_version}'
    os.symlink(
        package_dir, symlink_name
    )
    shutil.move(
        f'{package_dir}/debian', parent_dir
    )
    Command.run(
        [
            'tar', '-C', parent_dir, '-h', '-cJf',
            f'{outdir}/{package.name}_{package.debian_revision}.debian.tar.xz',
            'debian'
        ]
    )
    Command.run(
        [
            'tar', '-C', parent_dir, '-h', '-czf',
            f'{outdir}/{package.name}_{package.upstream_version}.orig.tar.gz',
            f'{package.name}-{package.upstream_version}'
        ]
    )
