import logging
import io
from mock import (
    patch, MagicMock, call, Mock
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
            '--git',
            'https://git.launchpad.net/ubuntu/+source/curl',
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

    @patch('sys.exit')
    @patch('os.path.isdir')
    @patch('os.path.exists')
    @patch('pathlib.Path.mkdir')
    @patch('corbos_scm.corbos_scm.Command')
    def test_get_package_meta_no_match(
        self, mock_Command, mock_pathlib_mkdir, mock_os_path_exists,
        mock_os_path_isdir, mock_sys_exit
    ):
        mock_os_path_exists.return_value = True
        mock_os_path_isdir.return_value = True
        with patch('builtins.open', create=True) as mock_open:
            mock_open.return_value = MagicMock(spec=io.IOBase)
            file_handle = mock_open.return_value.__enter__.return_value
            file_handle.readline.return_value = \
                'xsnow 42 unstable; urgency=low'
            with self._caplog.at_level(logging.ERROR):
                main()
                assert format(
                    'CSCMDebianChangelogFormatNotDetected'
                ) in self._caplog.text

    @patch('sys.exit')
    @patch('yaml.safe_load')
    @patch('os.symlink')
    @patch('shutil.move')
    @patch('os.path.isdir')
    @patch('os.path.exists')
    @patch('pathlib.Path.mkdir')
    @patch('corbos_scm.corbos_scm.TemporaryDirectory')
    @patch('corbos_scm.corbos_scm.Command')
    @patch('os.path.getsize')
    def test_source_data_creation(
        self, mock_os_path_getsize, mock_Command,
        mock_TemporaryDirectory, mock_pathlib_mkdir,
        mock_os_path_exists, mock_os_path_isdir, mock_shutil_move,
        mock_os_symlink, mock_yaml_safe_load, mock_sys_exit
    ):
        read_return_tar_chunks = [b'', b'', b'', b'', b'', b'', b'data']

        def read_return(*args, **kwargs):
            if args:
                return read_return_tar_chunks.pop()
            else:
                return 'Package: foo\nPackage: bar'

        mock_os_path_getsize.return_value = 0
        tempdir = Mock()
        tempdir.name = 'tmpdir'
        mock_TemporaryDirectory.return_value = tempdir
        mock_os_path_exists.return_value = True
        mock_os_path_isdir.return_value = True
        mock_yaml_safe_load.return_value = {
            'Source': 'curl',
            'Architecture': 'any',
            'Maintainer': 'user@example.org',
            'Build-Depends': 'a, b, c',
            'Section': 'section',
            'Priority': 'priority'
        }
        with patch('builtins.open', create=True) as mock_open:
            mock_open.return_value = MagicMock(spec=io.IOBase)
            file_handle = mock_open.return_value.__enter__.return_value
            file_handle.readline.return_value = \
                'curl (1:3.3.2-1) unstable; urgency=low'
            file_handle.read.side_effect = read_return
            main()
        mock_os_symlink.assert_called_once_with(
            'tmpdir/corbos',
            'tmpdir/curl-3.3.2'
        )
        mock_shutil_move.assert_called_once_with(
            'tmpdir/corbos/debian',
            'tmpdir'
        )
        assert mock_Command.run.call_args_list == [
            call(
                [
                    'git', 'clone',
                    'https://git.launchpad.net/ubuntu/+source/curl',
                    'tmpdir/corbos'
                ]
            ),
            call(
                [
                    'rm', '-rf', 'tmpdir/corbos/.git'
                ]
            ),
            call(
                [
                    'git', '-C', 'tmpdir/corbos', 'checkout', 'develop'
                ]
            ),
            call(
                [
                    'tar', '-C', 'tmpdir',
                    '-h', '-cJf', 'obs_out/curl_3.3.2-1.debian.tar.xz',
                    'debian'
                ]
            ),
            call(
                [
                    'tar', '-C', 'tmpdir',
                    '-h', '-czf', 'obs_out/curl_3.3.2.orig.tar.gz',
                    'curl-3.3.2'
                ]
            )
        ]
        assert file_handle.write.call_args_list == [
            call('Architecture: any\n'),
            call('Binary: foo,bar\n'),
            call('Build-Depends: a, b, c\n'),
            call('Format: 3.0 (quilt)\n'),
            call('Maintainer: user@example.org\n'),
            call('Package-List:\n'),
            call(' foo deb section priority arch=any\n'),
            call(' bar deb section priority arch=any\n'),
            call('Source: curl\n'),
            call('Testsuite: autopkgtest\n'),
            call('Version: 1:3.3.2-1\n'),
            call('Checksums-Sha1:\n'),
            call(
                ' da39a3ee5e6b4b0d3255bfef95601890afd80709 0 '
                'curl_3.3.2.orig.tar.gz\n'
            ),
            call(
                ' da39a3ee5e6b4b0d3255bfef95601890afd80709 0 '
                'curl_3.3.2-1.debian.tar.xz\n'
            ),
            call('Checksums-Sha256:\n'),
            call(
                ' 3a6eb0790f39ac87c94f3856b2dd2c5d110e68116022'
                '61a9a923d3bb23adc8b7 0 curl_3.3.2.orig.tar.gz\n'
            ),
            call(
                ' e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b'
                '934ca495991b7852b855 0 curl_3.3.2-1.debian.tar.xz\n'
            ),
            call('Files:\n'),
            call(
                ' d41d8cd98f00b204e9800998ecf8427e 0 '
                'curl_3.3.2.orig.tar.gz\n'
            ),
            call(
                ' d41d8cd98f00b204e9800998ecf8427e 0 '
                'curl_3.3.2-1.debian.tar.xz\n'
            )
        ]
