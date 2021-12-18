import logging
from mock import patch
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
            '--git',
            'https://github.com/OSInside/cloud-builder-packages.git',
            '--package',
            'projects/Corbos/xsnow',
            '--branch',
            'develop',
            '--outdir',
            'obs_out'
        ]

    @patch('sys.exit')
    @patch('os.path.isdir')
    @patch('os.path.exists')
    @patch('pathlib.Path.mkdir')
    @patch('corbos_scm.corbos_scm.Command')
    def test_debian_source_not_found(
        self, mock_Command, mock_pathlib_mkdir, mock_os_path_exists,
        mock_os_path_isdir, mock_sys_exit
    ):
        mock_os_path_exists.return_value = False
        mock_os_path_isdir.return_value = False
        with self._caplog.at_level(logging.ERROR):
            main()
            assert format('CSCMDebianSourceNotFound') in self._caplog.text
            mock_pathlib_mkdir.assert_called_once_with(
                parents=True, exist_ok=True
            )
