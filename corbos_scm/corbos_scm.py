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
    corbos_scm -h | --help
    corbos_scm --version

Options:
    --package=<name>
        Name of package to fetch

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
from tempfile import TemporaryDirectory
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
        'cd', '/mnt', '&&', 'apt', 'update', '&&',
        'apt', 'source', args['--package'], '&&',
        'find', '-maxdepth', '1', '-type', 'd', '-not', '-path', '.', '|',
        'xargs', 'rm', '-rf'
    ]

    # Create a safe symlink with regards to the volume
    # name limitations of podman. For sharing a directory
    # some characters are not allowed, e.g ":". In OBS
    # the colon is used as project separator. Because of
    # that it happens very easily that the --outdir path
    # created by OBS at call time of the service contains
    # colons and prevents this directory name from being
    # eligible to be shared via --volume with podman.
    # The recommended workaround from the podman team is
    # to create a temporary symlink which is what is
    # done next
    save_volume_dir = TemporaryDirectory()
    save_volume_file = os.sep.join(
        [save_volume_dir.name, 'volume']
    )

    os.symlink(args["--outdir"], save_volume_file)

    Command.run(
        [
            'podman', 'run', '--volume', f'{save_volume_file}:/mnt',
            '-ti', '--rm', args["--container"], 'bash', '-c',
            ' '.join(pull_debian_source)
        ]
    )
