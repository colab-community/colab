Create SVN and repositories
======

Make sure trac is running

Create new repository, changing repository_name to the project name

.. code-block::

  svnadmin create /home/colab/repository_name

Access trac-admin interface

.. code-block::

  trac-admin /opt/trac/

Add repository, changing ALIAS to the name of the repository

.. code-block::

  repository add ALIAS /home/colab/repository_name

quit

Add users permission to the repository

.. code-block::

  vim /home/colab/repository_name/conf/svnserve.conf

Uncomment the following lines

.. code-block::

  anon-access = none
  auth-access = write

Create the users

.. code-block::

  vim /home/colab/repository_name/conf/passwd

Add users and passwords in the following pattern

.. code-block::

  username = password

Import Repository to SVN

.. code-block::

  svn import /home/colab/repository_name file:////home/colab/repository_name -m ""

  