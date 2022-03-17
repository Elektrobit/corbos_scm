Corbos SCM - OBS service
========================

An Open Build Service (OBS) service to fetch Debian
packages sources. The service can be used for Debian/Ubuntu
based packages and utilizes the ubuntu-dev-tools from
a container. Calling from a container allows to use the Ubuntu
devtools toolchain independently from the host system as long
as the host supports the podman container engine

As an example, the following steps are needed to build
the `curl` package from Debian for Ubuntu(20.10) in OBS.

1. Install `corbos_scm` service

   Install the service provided at:

   * https://build.opensuse.org/package/show/home:marcus.schaefer/python-corbos_scm

   locally and on the remote backend server of your build service

   Warning:
     **The example below can only work if the corbos_scm service
     was installed on the backend server of your build service.**

2. Create a package in OBS

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
          <param name="registry">registry.example.com</param>
          <param name="container">ubdevtools:latest</param>
          <param name="package">curl</param>
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
     the exact same way on a custom OBS server.**

   .. code:: xml

      <repository name="xUbuntu_21.04">
        <path project="Ubuntu:21.04" repository="universe"/>
        <arch>x86_64</arch>
      </repository>

Container Setup
---------------

If there is no container with ubuntu-dev-tools available, the
following KIWI description can be used to build one

.. code:: xml

   <image schemaversion="7.4" name="ubuntu-dev-tools">
     <description type="system">
       <author>Marcus Schäfer</author>
       <contact>marcus.schaefer@gmail.com</contact>
       <specification>Runtime container ubuntu dev tools</specification>
     </description>
     <preferences>
       <version>1.0.1</version>
       <packagemanager>apt</packagemanager>
       <type image="docker">
         <containerconfig name="ubdevtools"/>
       </type>
     </preferences>
     <repository type="apt-deb" alias="kiwi-next-generation" priority="1" repository_gpgcheck="false">
       <source path="obs://Virtualization:Appliances:Builder/xUbuntu_21.04"/>
     </repository>
     <repository type="apt-deb" alias="Ubuntu-Hirsute-Universe" distribution="hirsute" components="main multiverse restricted universe" repository_gpgcheck="false">
       <source path="obs://Ubuntu:21.04/universe"/>
     </repository>
     <repository type="apt-deb" alias="Ubuntu-Hirsute" distribution="hirsute" components="main multiverse restricted universe" repository_gpgcheck="false">
       <source path="obs://Ubuntu:21.04/standard"/>
     </repository>
     <packages type="image">
       <package name="ubuntu-dev-tools"/>
       <package name="mawk"/>
     </packages>
     <packages type="bootstrap"/>
   </image>

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
