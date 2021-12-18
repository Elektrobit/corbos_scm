buildroot = /
docdir = /usr/share/doc/packages
python_version = 3
python_lookup_name = python$(python_version)
python = $(shell which $(python_lookup_name))

LC = LC_MESSAGES

version := $(shell \
    $(python) -c \
    'from corbos_scm.version import __version__; print(__version__)'\
)

install_package_docs:
	install -d -m 755 ${buildroot}${docdir}/python-corbos_scm
	install -m 644 LICENSE \
		${buildroot}${docdir}/python-corbos_scm/LICENSE
	install -m 644 README.rst \
		${buildroot}${docdir}/python-corbos_scm/README

install:
	# obs service
	install -d -m 755 ${buildroot}usr/lib/obs/service
	mv ${buildroot}usr/bin/corbos_scm \
		${buildroot}usr/lib/obs/service
	install -m 644 corbos_scm/corbos_scm.service \
		${buildroot}usr/lib/obs/service

tox:
	tox "-n 5"

git_attributes:
	# the following is required to update the $Format:%H$ git attribute
	# for details on when this target is called see setup.py
	git archive HEAD corbos_scm/version.py | tar -x

clean_git_attributes:
	# cleanup version.py to origin state
	# for details on when this target is called see setup.py
	git checkout corbos_scm/version.py

build: clean tox
	# create setup.py variant for rpm build.
	# delete module versions from setup.py for building an rpm
	# the dependencies to the python module rpm packages is
	# managed in the spec file
	sed -ie "s@>=[0-9.]*'@'@g" setup.py
	# build the sdist source tarball
	$(python) setup.py sdist
	# restore original setup.py backed up from sed
	mv setup.pye setup.py
	# provide rpm source tarball
	mv dist/corbos_scm-${version}.tar.gz dist/python-corbos_scm.tar.gz
	# update rpm changelog using reference file
	helper/update_changelog.py --since package/python-corbos_scm.changes > \
		dist/python-corbos_scm.changes
	helper/update_changelog.py --file package/python-corbos_scm.changes >> \
		dist/python-corbos_scm.changes
	# update package version in spec file
	cat package/python-corbos_scm-spec-template | \
		sed -e s'@%%VERSION@${version}@' > dist/python-corbos_scm.spec
	# provide rpm rpmlintrc
	cp package/python-corbos_scm-rpmlintrc dist

pypi: clean tox
	$(python) setup.py sdist upload

clean: clean_git_attributes
	$(python) setup.py clean
	rm -rf doc/build
	rm -rf doc/dist
