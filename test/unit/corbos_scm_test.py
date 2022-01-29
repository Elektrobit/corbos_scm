from mock import (
    patch, call
)
from pytest import fixture
import sys

from corbos_scm.corbos_scm import main


class TestCorbosSCM:
    @fixture(autouse=True)
    def inject_fixtures(self, caplog):
        self._caplog = caplog

    def setup(self):
        sys.argv = [
            sys.argv[0],
            '--registry',
            'registry.example.com',
            '--container',
            'ubdevtools:latest',
            '--package',
            'curl',
            '--mirror',
            'some-mirror',
            '--distribution',
            'ubuntu',
            '--outdir',
            'obs_out'
        ]

    @patch('sys.exit')
    @patch('os.path.exists')
    @patch('corbos_scm.corbos_scm.Path')
    @patch('corbos_scm.corbos_scm.Command')
    def test_pull_and_run(
        self, mock_Command, mock_Path,
        mock_os_path_exists, mock_sys_exit
    ):
        mock_os_path_exists.return_value = False

        main()

        mock_Path.assert_called_once_with('obs_out')
        mock_Path.return_value.mkdir.assert_called_once_with(
            parents=True, exist_ok=True
        )
        assert mock_Command.run.call_args_list == [
            call(
                [
                    'podman', 'pull',
                    'registry.example.com/ubdevtools:latest'
                ]
            ),
            call(
                [
                    'podman', 'run', '-v', 'obs_out:/tmp',
                    '-ti', '--rm', 'ubdevtools:latest',
                    'bash -c "cd /tmp && pull-debian-source --download-only '
                    '--mirror some-mirror --distro ubuntu curl"'
                ]
            )
        ]
