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
        Branch in git source.

    --outdir=<obs_out>
        Output directory to store data produced by the service.
        At the time the service is called through the OBS API
        this option is set.
"""
import os
import yaml
import shutil
import re
from pathlib import Path
from typing import (
    NamedTuple, Dict, Union, List
)
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
        ('epoch', str),
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

    clone_target = temp_git_dir.name
    checkout_subdir_name = 'corbos'
    if args['--package'] == '.':
        # if no dedicated directory exists for the package
        # we need to name one for the clone target. This is
        # needed to allow the tar process to work
        clone_target = os.path.join(clone_target, checkout_subdir_name)
        args['--package'] = checkout_subdir_name

    Command.run(
        ['git', 'clone', args['--git'], clone_target]
    )
    Command.run(
        ['rm', '-rf', f'{clone_target}/.git']
    )

    if args['--branch']:
        Command.run(
            ['git', '-C', clone_target, 'checkout', args['--branch']]
        )

    package_dir = os.path.join(temp_git_dir.name, args['--package'])
    debian_dir = os.path.join(package_dir, 'debian')

    if not os.path.isdir(debian_dir):
        raise CSCMDebianSourceNotFound(
            f'No debian dir in source: {debian_dir!r}'
        )

    package_meta = get_package_meta(debian_dir)

    dsc_file = create_dsc_file(
        debian_dir, package_meta, args['--outdir']
    )

    create_source_tarballs(
        package_dir, package_meta, dsc_file, args['--outdir']
    )


def get_package_meta(debian_dir: str) -> package_type:
    with open(f'{debian_dir}/changelog') as changelog:
        latest = changelog.readline().strip()
    changelog_format = re.match(
        r'([a-zA-Z0-9_\-\.]+) \((.*)\) (.*);', latest
    )
    if changelog_format:
        debian_epoch = '0'
        debian_revision_and_epoch = changelog_format.group(2).split(':')
        debian_revision = debian_revision_and_epoch.pop()
        if debian_revision_and_epoch:
            debian_epoch = debian_revision_and_epoch[0]
        debian_revision = changelog_format.group(2).split(':').pop()
        upstream_version = debian_revision.split('-')[0]
        return package_type(
            name=changelog_format.group(1),
            target=changelog_format.group(3),
            epoch=debian_epoch,
            debian_revision=debian_revision,
            upstream_version=upstream_version
        )
    else:
        raise CSCMDebianChangelogFormatNotDetected(
            'Unknown format: {latest!r}'
        )


def create_dsc_file(
    debian_dir: str, package: package_type, outdir: str
) -> str:
    dsc_file_name = os.path.join(
        outdir, f'{package.name}_{package.debian_revision}.dsc'
    )
    dsc_data: Dict[str, Union[str, List]] = {
        'Format': '3.0 (quilt)',
        'Version': f'{package.epoch}:{package.debian_revision}',
        'Testsuite': 'autopkgtest'
    }
    with open(f'{debian_dir}/control') as control:
        # treat the control file input as a yaml syntax.
        # This is not quite accurate but did not cause
        # issues for the standard values of the control_keys
        # list so far.
        control_dict = yaml.safe_load(control)
        control_keys = [
            'Source',
            'Architecture',
            'Maintainer',
            'Build-Depends',
            'Standards-Version',
            'Homepage',
            'Vcs-Browser',
            'Vcs-Git'
        ]
        for control_key in control_keys:
            if control_key in control_dict:
                dsc_data[control_key] = control_dict[control_key]

    package_list = []
    binary_list = []
    with open(f'{debian_dir}/control') as control:
        control_lines = control.read().split(os.linesep)
        for control_line in control_lines:
            if control_line.startswith('Package:'):
                package_name = control_line.split(':')[1].strip()
                binary_list.append(package_name)
                package_list.append(
                    '{0} {1} {2} {3} arch={4}'.format(
                        package_name,
                        'deb',
                        control_dict.get('Section') or 'none',
                        control_dict.get('Priority') or 'optional',
                        control_dict.get('Architecture') or 'any'
                    )
                )
    dsc_data['Binary'] = ','.join(binary_list)
    dsc_data['Package-List'] = package_list

    with open(dsc_file_name, 'w') as dsc:
        for key in sorted(dsc_data.keys()):
            if key == 'Package-List':
                dsc.write('{0}:{1}'.format(key, os.linesep))
                for package_name in dsc_data[key]:
                    dsc.write(' {0}{1}'.format(package_name, os.linesep))
            else:
                dsc.write('{0}: {1}{2}'.format(key, dsc_data[key], os.linesep))
    return dsc_file_name


def create_source_tarballs(
    package_dir: str, package: package_type, dsc_file: str, outdir: str
) -> None:
    parent_dir = os.path.dirname(package_dir)
    symlink_name = f'{parent_dir}/{package.name}-{package.upstream_version}'
    os.symlink(
        package_dir, symlink_name
    )
    shutil.move(
        f'{package_dir}/debian', parent_dir
    )
    debian_tar_file_name = \
        f'{outdir}/{package.name}_{package.debian_revision}.debian.tar.xz'
    Command.run(
        [
            'tar', '-C', parent_dir, '-h', '-cJf', debian_tar_file_name,
            'debian'
        ]
    )
    source_tar_file_name = \
        f'{outdir}/{package.name}_{package.upstream_version}.orig.tar.gz'
    Command.run(
        [
            'tar', '-C', parent_dir, '-h', '-czf', source_tar_file_name,
            f'{package.name}-{package.upstream_version}'
        ]
    )
    # TODO: create Checksums-Sha1: Checksums-Sha256: Files:
