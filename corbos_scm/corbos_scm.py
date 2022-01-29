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
"""
Usage:
    corbos_scm --package=<name> --registry=<uri> --container=<name> --outdir=<obs_out>
        [--mirror=<mirror>]
        [--distribution=<name>]
    corbos_scm -h | --help
    corbos_scm --version

Options:
    --package=<name>
        Name of package to fetch

    --mirror=<mirror>
        Preferred mirror(s)

    --distribution=<name>
        Pull from: debian, ubuntu

    --registry=<uri>
        Container registry URI

    --container=<name>
        Container name to pull. The container is expected to
        contain the Debian/Ubuntu development tools

    --outdir=<obs_out>
        Output directory to store data produced by the service.
        At the time the service is called through the OBS API
        this option is set.
"""
import os
from pathlib import Path
import docopt

from corbos_scm.version import __version__
from corbos_scm.command import Command
from corbos_scm.exceptions import (
    exception_handler
)


@exception_handler
def main() -> None:
    args = docopt.docopt(__doc__, version=__version__)

    if not os.path.exists(args['--outdir']):
        Path(args['--outdir']).mkdir(parents=True, exist_ok=True)

    Command.run(
        [
            'podman', 'pull',
            f'{args["--registry"]}/{args["--container"]}'
        ]
    )

    pull_debian_source = [
        'cd', '/tmp', '&&', 'pull-debian-source'
    ]
    if args['--mirror']:
        pull_debian_source.extend(
            ['--mirror', args['--mirror']]
        )
    if args['--distribution']:
        pull_debian_source.extend(
            ['--distro', args['--distribution']]
        )
    pull_debian_source.append(
        args['--package']
    )

    Command.run(
        [
            'podman', 'run', '-v', f'{args["--outdir"]}:/tmp',
            '-ti', '--rm', args["--container"],
            f'bash -c \"{" ".join(pull_debian_source)}\"'
        ]
    )
