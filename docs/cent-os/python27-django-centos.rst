.. -*- coding: utf-8 -*-

.. highlight:: rest

.. _colab_software:

Python 2.7
==========

Install the devel tools to build specific python 2.7 modules

.. code-block::

    sudo yum groupinstall "Development tools" -y
    sudo yum install zlib-devel bzip2-devel openssl-devel ncurses-devel libxslt-devel -y

Download and compile Python 2.7

.. code-block::

    cd /tmp
    sudo wget --no-check-certificate https://www.python.org/ftp/python/2.7.6/Python-2.7.6.tar.xz
    sudo tar xf Python-2.7.6.tar.xz
    cd Python-2.7.6
    sudo ./configure --prefix=/usr/local
    sudo make
    
Install python 2.7 as an alternative python, because cent os uses python 2.6 in the system.
    
.. code-block::

    sudo make altinstall

Update the PATH variable to execute python as root.

.. code-block::

    sudo su
    echo "export PATH=$PATH:/usr/local/bin/" >> ~/.bashrc
    source ~/.bashrc
    exit

Install the easy_install for python 2.7

.. code-block::

    cd /tmp
    sudo wget https://bitbucket.org/pypa/setuptools/raw/bootstrap/ez_setup.py
    sudo /usr/local/bin/python2.7 ez_setup.py
    
Instal pip 2.7

.. code-block::

    sudo /usr/local/bin/easy_install-2.7 pip

Install additional packages to python.

.. code-block::

    sudo yum remove libevent -y
    sudo yum install mercurial libevent-devel python-devel -y

Edit sudores file to let ``python2.7`` execute in sudo mode. 

*NOTE:*

    The path ``/usr/bin:/usr/pgsql-9.3/bin/`` will be only in this file if you installed postgresql before, if you didn't just remove it from those lines.

.. code-block::

    sudo vim /etc/sudoers

Change the line

.. code-block::

    Defaults    secure_path = /sbin:/bin:/usr/sbin:/usr/bin:/usr/pgsql-9.3/bin/
    
To

.. code-block::

    Defaults    secure_path = /sbin:/bin:/usr/sbin:/usr/bin:/usr/pgsql-9.3/bin/:/usr/local/bin/
    
.. code-block::

    [ESC]:wq!
    
Django 1.6
==========

Install django and uwsgi

.. code-block::

    sudo pip2.7 install django
    sudo pip2.7 install uwsgi

