Corbos SCM - OBS service
========================

An Open Build Service (OBS) service to manage Debian
packages sources from a git repo. The service can be used for Debian
based package sources and utilizes the ubuntu-dev-tools

As an example, the following steps are needed to build
the `curl` package from the Ubuntu launchpad in an OBS instance.

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

The `corbos_scm` service is very simple. It uses the tooling
provided by the ubuntu-dev-tools to create the source files
such that OBS can build the package.

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
