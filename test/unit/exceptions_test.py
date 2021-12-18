from mock import (
    Mock, patch
)
from pytest import (
    raises, fixture
)
import logging
from corbos_scm.exceptions import (
    CSCMError,
    exception_handler
)


class TestExceptions:
    @fixture(autouse=True)
    def inject_fixtures(self, caplog):
        self._caplog = caplog

    @patch('sys.exit')
    def test_exception_handler_known_error(self, mock_sys_exit):
        func = Mock()

        func.side_effect = CSCMError('issue')
        wrapper = exception_handler(func)
        with self._caplog.at_level(logging.ERROR):
            wrapper()
            assert format('issue') in self._caplog.text
            mock_sys_exit.assert_called_once_with(1)

    @patch('sys.exit')
    def test_exception_handler_keyboard_interrupt(self, mock_sys_exit):
        func = Mock()

        func.side_effect = KeyboardInterrupt
        wrapper = exception_handler(func)
        with self._caplog.at_level(logging.ERROR):
            wrapper()
            assert format('Exit on keyboard interrupt') in self._caplog.text
            mock_sys_exit.assert_called_once_with(1)

    @patch('sys.exit')
    def test_exception_handler_system_exit(self, mock_sys_exit):
        func = Mock()

        func.side_effect = SystemExit
        wrapper = exception_handler(func)
        wrapper()
        assert mock_sys_exit.called

    def test_exception_handler_unexpected_error(self):
        func = Mock()

        func.side_effect = Exception
        wrapper = exception_handler(func)
        with raises(Exception):
            with self._caplog.at_level(logging.ERROR):
                wrapper()
                assert format('Unexpected error:') in self._caplog.text
