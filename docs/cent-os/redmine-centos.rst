.. -*- coding: utf-8 -*-

.. highlight:: rest

.. _colab_software:

Redmine
=======

[Instalar Epel]

rpm -Uvh http://fedora.uib.no/epel/6/x86_64/epel-release-6-8.noarch.rpm 

[Instalar dependencias]

sudo yum -y install zlib-devel curl-devel openssl-devel httpd-devel apr-devel apr-util-devel  subversion  git postgresql-devel 

[postgresql]

sudo yum localinstall http://yum.postgresql.org/9.3/redhat/rhel-6-x86_64/pgdg-centos93-9.3-1.noarch.rpm -y
sudo yum install postgresql93 postgresql93-devel postgresql93-libs postgresql93-server -y

#iniciando postgresql
/etc/init.d/postgresql-9.3 initdb
sudo /etc/init.d/postgresql-9.3 restart


# alterar senha de usuario
sudo -u postgres psql template1
>>ALTER USER postgres with encrypted password 'postgres';

# configurar pg_hba
sudo vi /var/lib/pgsql/9.3/data/pg_hba.conf
#   configurar pg_hba.conf para adicionar a linha:

#escudando pelo localhost
descomentar a linha no arquivo    /var/lib/pgsql/9.3/data/postgresql.conf:
listen_addresses = 'localhost'

# reiniciar banco de dados
sudo /etc/init.d/postgresql-9.3 restart


[instalar dependencias gems]

sudo yum install gcc gcc-c++.x86_64 make automake autoconf curl-devel openssl-devel zlib-devel httpd-devel apr-devel apr-util-devel sqlite-devel ruby-rdoc ruby-devel
sudo yum install rubygems libxslt-devel libxml2-devel.x86_64


[atualizar para gem 1.4.2]

wget http://production.cf.rubygems.org/rubygems/rubygems-1.4.2.tgz
tar zxvf rubygems-1.4.2.tgz
cd rubygems-1.4.2
ruby setup.rb
gem -v

[ImageMagick]

sudo yum install php-pear gcc ImageMagick ImageMagick-devel ImageMagick-perl

[instalar gem Bundle]

sudo gem install bundle --no-ri --no-rdoc

[instalar nginx]

cd /tmp
wget http://nginx.org/packages/centos/6/noarch/RPMS/nginx-release-centos-6-0.el6.ngx.noarch.rpm
sudo rpm -ivh nginx-release-centos-6-0.el6.ngx.noarch.rpm
Instale o nginx

sudo yum install nginx -y
sudo chkconfig nginx on


[instalar redmine 2.5.1]

svn co http://svn.redmine.org/redmine/branches/2.5-stable redmine
mv redmine-2.5 redmine

[instalando gems dependentes]

sudo chown -R colab:colab redmine
cd /opt/redmine
bundle install --without mysql sqlite

[Configurar banco]

sudo -u postgres psql

--> criar usuario redmine
>>CREATE ROLE redmine LOGIN ENCRYPTED PASSWORD 'redmine' NOINHERIT VALID UNTIL 'infinity';
--> criar banco redmine
>>CREATE DATABASE redmine WITH ENCODING='UTF8' OWNER=redmine; 
>>\q

sudo mkdir -p tmp/pdf public/plugin_assets

[gems]
sudo gem install pg -v '0.17.1' --no-ri --no-rdoc 
sudo gem install unicorn --no-ri --no-rdoc
sudo gem uninstall rake -v '10.3.2'

[Configurando banco de dados]
mv database.yml.example database.yml
vim database.yml

deixar descomentado apenas :

------
production:
  adapter: postgresql
  database: redmine
  host: 10.18.0.10
  username: redmine
  password: redmine
  encoding: utf8

------


[Populando Redmine]

rake generate_secret_token
RAILS_ENV=production rake db:migrate
RAILS_ENV=production rake redmine:load_default_data 
escolher pt-BR

[Verificar se redmine esta funcionando]

sudo rails s -e production -d 

[configurar Unicorn]

cd /opt/redmine
mkdir pids   
vim config/unicorn.rb

Inserir o conteudo abaixo
-----------------------------

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

-----------------------

[Configurar NGINX de sites available]

vim /etc/nginx/nginx.conf
incluir a linha:
------------------------
http {
    ....
    include /etc/nginx/sites-available/*;
    ....
}
------------------------

[Criar diretorio Sites Available]

sudo mkdir /etc/nginx/sites-available
sudo vim /etc/nginx/sites-available/redmine.conf
Colocar o conteudo abaixo:

------------------------

upstream app {
    # Path to Unicorn SOCK file, as defined previously
    server unix:/tmp/unicorn.redmine.sock fail_timeout=0;
}

server {
    listen 3004;
    server_name localhost;

    # Application root, as defined previously
    root /opt/redmine/public;

    try_files $uri/index.html $uri @app;

    location @app {
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $http_host;
        proxy_redirect off;
        proxy_pass http://app;
    }

    error_page 500 502 503 504 /500.html;
    client_max_body_size 4G;
    keepalive_timeout 10;
}  

----------------

[Reiniciando os serviços para o redmine funcionar]

sudo service nginx restart
sudo /etc/init.d/postgresql-9.3 restart

[Iniciando Unicorn Para rodar o Redmine em Produção]
unicorn_rails -c /opt/redmine/config/unicorn.rb -D -E production 
