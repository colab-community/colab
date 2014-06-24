.. -*- coding: utf-8 -*-

.. highlight:: rest

.. _colab_software:

Redmine
=====

Install Epel

.. code-block::

  rpm -Uvh http://fedora.uib.no/epel/6/x86_64/epel-release-6-8.noarch.rpm 


Install Requirements
.. code-block::

    sudo yum -y install zlib-devel curl-devel openssl-devel httpd-devel apr-devel apr-util-devel 
    subversion  git postgresql-devel 


Install Postgresql

.. code-block::

  sudo yum localinstall http://yum.postgresql.org/9.3/redhat/rhel-6-x86_64/pgdg-centos93-9.3-1.noarch.rpm -y
  sudo yum install postgresql93 postgresql93-devel postgresql93-libs postgresql93-server -y


Restarting Postgresql

.. code-block::

  /etc/init.d/postgresql-9.3 initdb
  sudo /etc/init.d/postgresql-9.3 restart

Change Postgres password

.. code-block::

  sudo -u postgres psql template1
  >>ALTER USER postgres with encrypted password 'postgres';

Configuring

.. code-block::

    sudo vi /var/lib/pgsql/9.3/data/pg_hba.conf
  
    change: 
    # listen_addresses = 'localhost'
    to:
      listen_addresses = 'localhost'

Restarting Postgresql

.. code-block::
  
  sudo /etc/init.d/postgresql-9.3 restart


Install Gems Requirements
  
.. code-block::

  sudo yum install gcc gcc-c++.x86_64 make automake autoconf curl-devel openssl-devel
       zlib-devel httpd-devel apr-devel apr-util-devel sqlite-devel ruby-rdoc ruby-devel
  
  sudo yum install rubygems libxslt-devel libxml2-devel.x86_64


Upgrading to Gem 1.4.2

.. code-block::
  
  wget http://production.cf.rubygems.org/rubygems/rubygems-1.4.2.tgz
  tar zxvf rubygems-1.4.2.tgz
  cd rubygems-1.4.2
  ruby setup.rb
  gem -v


Install  ImageMagick

.. code-block::

  sudo yum install php-pear gcc ImageMagick ImageMagick-devel ImageMagick-perl

Install Gem Bundle 

.. code-block::
    
  sudo gem install bundle --no-ri --no-rdoc

Install NGINX
  
..  code-block::

  cd /tmp
  wget http://nginx.org/packages/centos/6/noarch/RPMS/nginx-release-centos-6-0.el6.ngx.noarch.rpm
  sudo rpm -ivh nginx-release-centos-6-0.el6.ngx.noarch.rpm
  sudo yum install nginx -y
  sudo chkconfig nginx on

Install redmine 2.5.1

.. code-block::
  
  svn co http://svn.redmine.org/redmine/branches/2.5-stable redmine
  mv redmine-2.5 redmine
  sudo mkdir -p tmp/pdf public/plugin_assets


Install Gem requirements

.. code-block::

  sudo chown -R colab:colab redmine
  cd /opt/redmine
  bundle install --without mysql sqlite


Configuring postgresql

.. code-block::

  sudo -u postgres psql

  >>CREATE ROLE redmine LOGIN ENCRYPTED PASSWORD 'redmine' NOINHERIT VALID UNTIL 'infinity';
  >>CREATE DATABASE redmine WITH ENCODING='UTF8' OWNER=redmine; 
  >>\q


Installing Gems

.. code-block::

  sudo gem install pg -v '0.17.1' --no-ri --no-rdoc 
  sudo gem install unicorn --no-ri --no-rdoc
  sudo gem uninstall rake -v '10.3.2'


Configuring database.yml in Redmine Folder

.. code-block::
  
  mv database.yml.example database.yml
  vim database.yml

  #----------------------
  
  production:
  adapter: postgresql
  database: redmine
  host: 10.18.0.10
  username: redmine
  password: redmine
  encoding: utf8

  #----------------------


Populating Redmine

.. code-block::

  rake generate_secret_token
  RAILS_ENV=production rake db:migrate
  RAILS_ENV=production rake redmine:load_default_data 
  escolher pt-BR


Running Redimine to test if is work

.. code-block::
  
  sudo rails s -e production -d 



Configuring Unicorn

.. code-block::

  cd /opt/redmine
  mkdir pids   
  vim config/unicorn.rb

  #------------------------------------
  # Set the working application directory
  # working_directory "/path/to/your/app"
  working_directory "/opt/redmine"
  
  # Unicorn PID file location
  # pid "/path/to/pids/unicorn.pid"
  pid "/opt/redmine/pids/unicorn.pid"
  
  # Path to logs
  # stderr_path "/path/to/log/unicorn.log"
  # stdout_path "/path/to/log/unicorn.log"
  stderr_path "/opt/redmine/log/unicorn.log"
  stdout_path "/opt/redmine/log/unicorn.log"
  
  # Unicorn socket
  #listen "/tmp/unicorn.redmine.sock"
  listen "/tmp/unicorn.redmine.sock"
  
  # Number of processes
  # worker_processes 4
  worker_processes 2
  
  # Time-out
  timeout 30

  #-------------------------------------
  
  
  
Editing ROUTES

.. code-block::

  vim /opt/redmine/config/route.rb

  #-------------------------------

  Redmine::Utils::relative_url_root = "/redmine"

  RedmineApp::Application.routes.draw do
  scope Redmine::Utils::relative_url_root do
    root :to => 'welcome#index', :as => 'home'

  ...
  ...
  end
  end

  #---------------------------------

  Adding simbol link:
  
  ln -s /opt/redmine/public /opt/redmine/public/redmine

Restarting  Postgresql
  
.. code-block::
    sudo /etc/init.d/postgresql-9.3 restart

Running Redmine Using unicorn

.. code-block::
  
  unicorn_rails -c /opt/redmine/config/unicorn.rb -D -E production 



Install Plugin to Use remote_user

.. code-block::
  
  cd /opt/redmine/plugins

  git clone https://github.com/tdvsdv/single_auth.git

Editing remote_user 

.. code-block::
  
  Make login in redmine using :
    user: admin
    passwod: admin
    
    go to in plugins
    go to configurations in single_auth
    edit REMOTE_USER to HTTP_REMOTE_USER
