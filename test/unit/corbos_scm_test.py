import sys

from corbos_scm.corbos_scm import main


class TestCorbosSCM:
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

    def test_main(self):
        main()
