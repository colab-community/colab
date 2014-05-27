.. -*- coding: utf-8 -*-

.. highlight:: rest

.. _colab_software:

Colab
=====

Install git and clone colab

.. code-block::

    sudo yum install git -y
    cd /opt
    sudo git clone https://github.com/colab-community/colab.git

Install colab requirements

.. code-block::

    sudo pip2.7 install mimeparse
    sudo pip2.7 install -r /opt/colab/requirements.txt

Create the local_settings file in colab folder

.. code-block::

    sudo cp /opt/colab/src/colab/local_settings-dev.py /opt/colab/src/colab/local_settings.py

And edit it inserting browser id in the end of file

.. code-block::

    sudo vim /opt/colab/src/colab/local_settings.py

.. code-block::

    BROWSERID_AUDIENCES = [SITE_URL, SITE_URL.replace('https', 'http')]

.. code-block::

    [ESC]:wq!

Create the database for colab, remind that the user colab was created at the postgresql section

.. code-block::

    sudo -u postgres psql

.. code-block::

    CREATE DATABASE "colab" WITH OWNER "colab" ENCODING 'UTF8' LC_COLLATE='en_US.UTF-8' LC_CTYPE='en_US.UTF-8' TEMPLATE=template0;
    \q

Edit pg_hba.conf to grant the permissions

.. code-block::

    vim /var/lib/pgsql/9.3/data/pg_hba.conf

Set the right permission to colab user on colab database

.. code-block::

    # TYPE  DATABASE        USER            ADDRESS                 METHOD

    # "local" is for Unix domain socket connections only
    local   all             postgres                                     peer
    local   trac_colab             colab                                     md5
    local   colab             colab                                     md5
    local   all             git                                     trust
    # IPv4 local connections:
    host    all             postgres             127.0.0.1/32            ident
    host    trac_colab             colab             127.0.0.1/32            md5
    host    colab             colab             127.0.0.1/32            md5
    host    all             git             127.0.0.1/32            trust
    # IPv6 local connections:
    host    all             postgres             ::1/128                 ident
    host    trac_colab             colab             ::1/128                 md5
    host    colab             colab             ::1/128                 md5
    host    all             git             ::1/128                 trust

.. code-block::

    [ESC]:wq!

Restart postgresql

.. code-block::

    service postgresql-9.3 restart


Build the solr schema.xml

.. code-block::

    cd /opt/colab/src
    sudo su
    python2.7 manage.py build_solr_schema > /usr/share/solr/example/solr/collection1/conf/schema.xml
    exit

Edit the schema to change the ``stopwords_en.txt`` to ``lang/stopwords_en.txt``

.. code-block::

    sudo vim /usr/share/solr/example/solr/collection1/conf/schema.xml

.. code-block::

    [ESC]:%s/stopwords_en.txt/lang\/stopwords_en.txt
    [ESC]:wq!


Syncronize and migrate the colab's database

.. code-block::

    cd /opt/colab/src
    python2.7 manage.py syncdb
    python2.7 manage.py migrate

Start Solr in a terminal, and then, in other terminal, update colab index

.. code-block::

        cd /opt/colab/src
        python2.7 manage.py update_index

Now you can close this terminal, and stop solr with ``Ctrl+C``

Import mailman e-mails

.. code-block::

    sudo python2.7 /opt/colab/src/manage.py import_emails

*NOTE:*

    To run Colab: python2.7 /opt/colab/src/manage.py runserver . To access colab go in: `http://localhost:8000 <http://localhost:8000>`_

