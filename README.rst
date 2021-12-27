Corbos SCM - OBS service
========================

An Open Build Service (OBS) service to manage packages
sources as they are used by the ElektroBit (EB) Corbos
Linux system.

The service can generally be used for Debian based package
sources if the following conditions applies:

1. The sources are organized in a git repo
2. The referenced source path contains a directory named: `debian`
3. The rest of the referenced sources with the `debian`
   directory excluded is expected to provide the upstream sources.

Package source provider that matches the above criteria can be
found in e.g Ubuntu's launchpad or on Debian's salsa. As an example,
the following steps are needed to build the `curl` package from the
Ubuntu launchpad in an OBS instance.

1. Install `corbos_scm` service

   Install the service provided at:

   * https://build.opensuse.org/package/show/home:marcus.schaefer/python-corbos_scm

   locally and on the remote backend server of your build service

   Warning:
     **The example below can only work if the corbos_scm service
     was installed on the backend server of your build service.**

2. Create a package in your OBS instance

   .. code:: bash

      osc mkpac curl

3. Create the `_service` file and add it

   .. code:: bash

      cd curl
      touch _service
      osc add _service

4. Add the following contents to the `_service` file

   .. code:: xml

      <services>
        <service name="corbos_scm">
          <param name="git">https://git.launchpad.net/ubuntu/+source/curl</param>
        </service>
      </services>

5. Commit the service setup

   .. code:: bash

      osc ci

6. Add Ubuntu repository to allow dependency resolving and
   the package build

   .. code:: bash

      osc meta -e prj

   Add a repo definition which allows to resolve the required
   build dependencies. The following is just an example matching
   repos as they exist in the public build service provided by
   SUSE.

   Note:
     **Be aware that the following repo definiton just serves
     as an example and will most likely not be available in
     the exact same way on your custom OBS server.**

   .. code:: xml

      <repository name="xUbuntu_20.10">
        <path project="Ubuntu:20.10" repository="universe"/>
        <arch>x86_64</arch>
      </repository>


Behind the Scenes
-----------------

The `corbos_scm` service is very simple. It looks up all relevant
information from data inside of the `debian` directory and
creates the `.dsc` file. Next it creates the debian tarball
from the `debian` directory and the source tarball from
everyting but the `debian` directory. The result files are
committed as data to the OBS backend and allows OBS to build
debian packages using the native debian toolchain.

On the local system the service can be tested with:

.. code:: bash

   osc service localrun

This call creates the mentioned data locally. For the service to
be effective on the remote backend of OBS, it's required to install
it there. This is because obs creates a command call from the
information provided in the `_service` file and issues that command
on its remote backend.

Along with the most simple `_service` file the following
optional parameters exists:

.. code:: xml

   <param name="package">path/to/package</param>

This setting allows to specify a path to the package sources in
the git. By default this path is set to `.` which is the directory
of the git checkout. However if the git is organized differently
a path spec to point to the source might be needed.

.. code:: xml

   <param name="branch">branch_name</param>

This setting specifies the git branch to use. By default no branch
specification is used, which leads to the branch that is configured
to be the default on the remote side of the git server.
