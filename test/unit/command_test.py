from pytest import raises
from mock import (
    patch, Mock
)

from corbos_scm.exceptions import CSCMCommandError
from corbos_scm.command import Command


class TestCommand:
    @patch('subprocess.Popen')
    def test_command_run_popen_raises(self, mock_subprocess_Popen):
        mock_subprocess_Popen.side_effect = Exception
        with raises(CSCMCommandError):
            Command.run(['ls', '-l'])

    @patch('subprocess.Popen')
    def test_command_run_exit_code_1(self, mock_subprocess_Popen):
        process = Mock()
        process.communicate.return_value = ('stdout', 'stderr')
        process.returncode = 1
        mock_subprocess_Popen.return_value = process
        with raises(CSCMCommandError):
            Command.run(['ls', '-l'])

    @patch('subprocess.Popen')
    def test_command_run_exit_code_0(self, mock_subprocess_Popen):
        process = Mock()
        process.communicate.return_value = ('stdout', 'stderr')
        process.returncode = 0
        mock_subprocess_Popen.return_value = process
        ls_cmd = Command.run(['ls', '-l'])
        assert ls_cmd.returncode == 0
        assert ls_cmd.output == 'stdout'
        assert ls_cmd.error == 'stderr'
