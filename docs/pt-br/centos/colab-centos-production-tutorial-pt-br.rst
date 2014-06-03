.. -*- coding: utf-8 -*-

.. highlight:: rest

.. _colab_software:

====================
Colab no Cent OS 6.5
====================

Introdução
==========

Este tutorial dará instruções para a instalação do ambiente de produção do colab no Cent OS 6.5.

.. code-block::

    Distribution      : CentOS 6.5 Minimal
    Web Server        : Nginx
    Database          : PostgreSQL
    Tools             : Trac, Solr, Mailman, Gitlab, Redmine

Pré-requisitos
--------------

- O Cent OS 6.5 deve ter passado pelo processo de atualização com o: ``sudo yum update -y``
- O usuário colab das maquinas devem estar no arquivo ``sudoers``


Termos e Expreções
------------------


Esturtura do ambiente de produção
---------------------------------


Instruções
==========

Instalação do Postgres 9.3
--------------------------

Siga todas as instruções a seguir na máquina destinada ao banco de dados Postgres

*NOTE:*

    Libere a porta xxxxxxx desta máquina para que máquina do colab possa ouvi-la

Instale o pacote postgresql

.. code-block::

    sudo yum localinstall http://yum.postgresql.org/9.3/redhat/rhel-6-x86_64/pgdg-centos93-9.3-1.noarch.rpm -y
    sudo yum install postgresql93 postgresql93-devel postgresql93-libs postgresql93-server -y

Inicie o banco de dados

.. code-block::

    sudo service postgresql-9.3 initdb

Adicione o Postgres para iniciar com o sistema

.. code-block::

    sudo chkconfig postgresql-9.3 on

Inicie o postgresql

.. code-block::

    sudo service postgresql-9.3 start

Coloque os binários do postgres na variável PATH

.. code-block::

    echo "export PATH=$PATH:/usr/pgsql-9.3/bin/" >> ~/.bashrc
    source ~/.bashrc
    sudo su
    echo "export PATH=$PATH:/usr/pgsql-9.3/bin/" >> ~/.bashrc
    source ~/.bashrc
    exit

Edite o arquivo sudoers

.. code-block::

    sudo vim /etc/sudoers

Dentro do arquivo mude a seguinte linha

.. code-block::

    Defaults    secure_path = /sbin:/bin:/usr/sbin:/usr/bin

para

.. code-block::

    Defaults    secure_path = /sbin:/bin:/usr/sbin:/usr/bin:/usr/pgsql-9.3/bin/

Salve e feche o arquivo

.. code-block::

    [ESC]:wq!

Crie todos os usuários e banco de dados necessários para o funcionamento correto do colab.

.. code-block::

    sudo -u postgres psql

.. code-block::

    CREATE USER colab SUPERUSER INHERIT CREATEDB CREATEROLE;
    ALTER USER colab PASSWORD 'colab';
    CREATE USER git;
    CREATE ROLE redmine LOGIN ENCRYPTED PASSWORD 'redmine' NOINHERIT VALID UNTIL 'infinity';

    CREATE DATABASE gitlabhq_production OWNER git;
    CREATE DATABASE "colab" WITH OWNER "colab" ENCODING 'UTF8' LC_COLLATE='en_US.UTF-8' LC_CTYPE='en_US.UTF-8' TEMPLATE=template0;
    CREATE DATABASE "trac_colab" WITH OWNER "colab" ENCODING 'UTF8' LC_COLLATE='en_US.UTF-8' LC_CTYPE='en_US.UTF-8' TEMPLATE=template0;
    CREATE DATABASE redmine WITH ENCODING='UTF8' OWNER=redmine;

    \q

Altere o pg_hba.conf para conceder as permissões corretas aos usuários

.. code-block::

    sudo vi /var/lib/pgsql/9.3/data/pg_hba.conf

As permissõe devem ser as que estão abaixo, que serão encontradas no final do arquivo, ou seja, as linhas do fim do arquivo devem ser substituidas.

.. code-block::

    # TYPE  DATABASE                        USER            ADDRESS                 METHOD

    # "local" is for Unix domain socket connections only
    local   all                             postgres                                peer
    local   redmine                         redmine                                 md5
    local   trac_colab                      colab                                   md5
    local   colab                           colab                                   md5
    local   gitlabhq_production             git                                     trust
    # IPv4 local connections:
    host    all                             postgres        127.0.0.1/32            ident
    host    redmine                         redmine         127.0.0.1/32            md5
    host    trac_colab                      colab           127.0.0.1/32            md5
    host    colab                           colab           127.0.0.1/32            md5
    host    gitlabhq_production             git             127.0.0.1/32            trust
    # IPv6 local connections:
    host    all                             postgres        ::1/128                 ident
    host    redmine                         redmine         ::1/128                 md5
    host    trac_colab                      colab           ::1/128                 md5
    host    colab                           colab           ::1/128                 md5
    host    gitlabhq_production             git             ::1/128                 trust

.. code-block::

    [ESC]:wq!

Reinicie o postgresql

.. code-block::

    sudo service postgresql-9.3 restart


Instalação do Trac 0.12
-----------------------

Siga os passo na máquina destinada ao Trac

*NOTE:*

    Libere a porta 5000 desta máquina para que máquina do colab possa ouvi-la

Instale as dependências

.. code-block::

    sudo yum install gcc python-devel python-setuptools -y

Instale o pacote python para a utilização do postgres

.. code-block::

    sudo easy_install psycopg2

Instale o Trac

.. code-block::

    sudo yum install -y trac

Inicie o Trac

.. code-block::

    sudo mkdir -p /opt/trac
    sudo trac-admin /opt/trac initenv

Em ``Project Name [My Project]>`` digite ``colab``. E em ``Database connection string [sqlite:db/trac.db]>`` coloque ``postgres://colab:colab@/trac_colab?host=localhost``

Instale o subversion

.. code-block::

    sudo yum install subversion -y

Crie uma pasta para os repositório SVN

.. code-block::

    sudo mkdir /opt/repos

Edite o arquivo de configuração do Trac

.. code-block::

    sudo vim /opt/trac/conf/trac.ini

Mude a linha

.. code-block::

    repository_dir =

para

.. code-block::

    repository_dir = /opt/repos/

Dentro da tag [trac] coloque

.. code-block::

    obey_remote_user_header = true

Insira as linhas a seguir no final do arquivo

.. code-block::

    [components]
    tracopt.versioncontrol.svn.* = enabled

.. code-block::

    [ESC]:wq!


Crie o plugin do remote user

.. code-block::

    sudo vim /opt/trac/plugins/remote-user-auth.py

Com este conteúdo dentro dele

.. code-block::

    from trac.core import *
    from trac.config import BoolOption
    from trac.web.api import IAuthenticator

    class MyRemoteUserAuthenticator(Component):

        implements(IAuthenticator)

        obey_remote_user_header = BoolOption('trac', 'obey_remote_user_header', 'false',
                   """Whether the 'Remote-User:' HTTP header is to be trusted for user logins 
                    (''since ??.??').""")

        def authenticate(self, req):
            if self.obey_remote_user_header and req.get_header('Remote-User'):
                return req.get_header('Remote-User')
            return None

.. code-block::

    [ESC]:wq!

xxxxxxxxxxxxxxxSupervisor para o Tracxxxxxxxxxxxxxx
Rode o Trac com o comando

.. code-block::

    sudo tracd --port 5000 /opt/trac

xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

Instalação do Solr 4.6.1
------------------------

Siga os passo na máquina destinada ao Solr

*NOTE:*

    Libere a porta 8983 desta máquina para que máquina do colab possa ouvi-la

Faça o download e descompacte o Solr no /tmp

.. code-block::

    cd /tmp
    sudo wget http://archive.apache.org/dist/lucene/solr/4.6.1/solr-4.6.1.tgz
    sudo tar xvzf solr-4.6.1.tgz

Instale o Solr no diretório ``/usr/share``

.. code-block::

    sudo mv solr-4.6.1 /usr/share/solr
    sudo cp /usr/share/solr/example/webapps/solr.war /usr/share/solr/example/solr/solr.war

Remova a tag ``updateLog`` no solrconfig.xml

.. code-block::

    sudo vim /usr/share/solr/example/solr/collection1/conf/solrconfig.xml

Remova as linhas do solrconfig.xml

.. code-block::

    <updateLog>
      <str name="dir">${solr.ulog.dir:}</str>
    </updateLog>

.. code-block::

    [ESC]wq!

xxxxxxxxxxxxxxxSupervisor para o Solrxxxxxxxxxxxxxx
Rode o Solr com o comando

.. code-block::

    cd /usr/share/solr/example/; sudo java -jar start.jar

Acesse em: http://localhost:8983
xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx


Instalação do Mailman 2.1
-------------------------

Siga os passo na máquina destinada ao Mailman

*NOTE:*

    Libere a porta 8025 desta máquina para que máquina do colab possa ouvi-la

Faça o download do nginx

.. code-block::

    cd /tmp
    wget http://nginx.org/packages/centos/6/noarch/RPMS/nginx-release-centos-6-0.el6.ngx.noarch.rpm
    sudo rpm -ivh nginx-release-centos-6-0.el6.ngx.noarch.rpm

Instale o nginx

.. code-block::

    sudo yum install nginx -y

Faça o nginx iniciar com o sistema

.. code-block::

    sudo chkconfig nginx on

Compile e instale o fcgiwrap

.. code-block::

    sudo yum install fcgi-devel git -y
    cd /tmp
    sudo git clone https://github.com/gnosek/fcgiwrap.git
    cd fcgiwrap
    sudo yum groupinstall "Development tools" -y
    sudo autoreconf -i
    sudo ./configure
    sudo make
    sudo make install

Instale o spawn fcgi

.. code-block::

    sudo yum install spawn-fcgi -y

Edite o arquivo de configuração do spawn-fgci

.. code-block::

    sudo vim /etc/sysconfig/spawn-fcgi

.. code-block::

    FCGI_SOCKET=/var/run/fcgiwrap.socket
    FCGI_PROGRAM=/usr/local/sbin/fcgiwrap
    FCGI_USER=apache
    FCGI_GROUP=apache
    FCGI_EXTRA_OPTIONS="-M 0770"
    OPTIONS="-u $FCGI_USER -g $FCGI_GROUP -s $FCGI_SOCKET -S $FCGI_EXTRA_OPTIONS -F 1 -P /var/run/spawn-fcgi.pid -- $FCGI_PROGRAM"

.. code-block::

    [ESC]:wq!

Instale o mailman

.. code-block::

    sudo yum install mailman -y

Instale the mail server ``postfix``

.. code-block::

    sudo yum -y install postfix

Reinicie o postfix

.. code-block::

    sudo /etc/init.d/postfix restart

Adicione o mailman para iniciar juntamente com o sistema

.. code-block::

    sudo chkconfig --levels 235 mailman on

Incie o mailman e crie o link simbólico dentro da pasta do cgi-bin

.. code-block::

    sudo /etc/init.d/mailman start
    cd /usr/lib/mailman/cgi-bin/
    sudo ln -s ./ mailman

Crie o arquivo de configuração do mailman no nginx

.. code-block::

    sudo vim /etc/nginx/conf.d/list.conf

.. code-block::

    server {
            server_name localhost;
            listen 8025;

            location /mailman/cgi-bin {
                   root /usr/lib;
                   fastcgi_split_path_info (^/mailman/cgi-bin/[^/]*)(.*)$;
                   include /etc/nginx/fastcgi_params;
                   fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
                   fastcgi_param PATH_INFO $fastcgi_path_info;
                   fastcgi_param PATH_TRANSLATED $document_root$fastcgi_path_info;
                   fastcgi_intercept_errors on;
                   fastcgi_pass unix:/var/run/fcgiwrap.socket;
            }
            location /images/mailman {
                   alias /usr/lib/mailman/icons;
            }
            location /pipermail {
                   alias /var/lib/mailman/archives/public;
                   autoindex on;
            }
    }

.. code-block::

    [ESC]:wq!

Reinicie o nginx

.. code-block::

    sudo service nginx restart

Edite o script de configuração do mailman, para consertar as urls.

.. code-block::

    sudo vim /etc/mailman/mm_cfg.py

Adicione esta linha no final do arquivo

.. code-block::

    DEFAULT_URL_PATTERN = 'https://%s/mailman/cgi-bin/'

.. code-block::

    [ESC]:wq!

Execute o commando fix_url para consertar as urls e reinicie o mailman

.. code-block::

    sudo /usr/lib/mailman/bin/withlist -l -a -r fix_url
    sudo service mailman restart

Dê as permissões corretas para o usuário nginx

.. code-block::

    sudo usermod -a -G apache nginx

Coloque o spaw-fcgi para iniciar com o sistema

.. code-block::

    sudo chkconfig --levels 235 spawn-fcgi on
    sudo /etc/init.d/spawn-fcgi start

Reinicie os serviços

.. code-block::

    sudo service mailman restart
    sudo service nginx restart

Instalação do Gitlab 6.8
------------------------

Siga os passo na máquina destinada ao Gitlab

*NOTE:*

    Libere a porta 8090 desta máquina para que máquina do colab possa ouvi-la

Adicione o repositório EPEL

.. code-block::

    sudo wget -O /etc/pki/rpm-gpg/RPM-GPG-KEY-EPEL-6 https://www.fedoraproject.org/static/0608B895.txt
    sudo rpm --import /etc/pki/rpm-gpg/RPM-GPG-KEY-EPEL-6

Adicione o repositório em PUIAS Computational

.. code-block::

    sudo rpm -Uvh https://dl.fedoraproject.org/pub/epel/6/x86_64/epel-release-6-8.noarch.rpm
    sudo wget -O /etc/yum.repos.d/PUIAS_6_computational.repo https://gitlab.com/gitlab-org/gitlab-recipes/raw/master/install/centos/PUIAS_6_computational.repo
    sudo wget -O /etc/pki/rpm-gpg/RPM-GPG-KEY-puias http://springdale.math.ias.edu/data/puias/6/x86_64/os/RPM-GPG-KEY-puias
    sudo rpm --import /etc/pki/rpm-gpg/RPM-GPG-KEY-puias

Habilite o repositório do PUIAS

.. code-block::

    sudo yum -y install yum-utils
    sudo yum-config-manager --enable epel --enable PUIAS_6_computational

Atualize os pacotes necessários e instale os que faltam

.. code-block::

    sudo yum -y update
    sudo yum -y groupinstall 'Development Tools'
    sudo yum -y install readline readline-devel ncurses-devel gdbm-devel glibc-devel tcl-devel openssl-devel curl-devel expat-devel db4-devel byacc sqlite-devel libyaml libyaml-devel libffi libffi-devel libxml2 libxml2-devel libxslt libxslt-devel libicu libicu-devel system-config-firewall-tui redis sudo wget crontabs logwatch logrotate perl-Time-HiRes

Adicione o redis para iniciar com o sistema

.. code-block::

    sudo chkconfig redis on
    sudo service redis start

Instale the mail server ``postfix``

.. code-block::

    sudo yum -y install postfix

Remova qualquer pacote git

.. code-block::

    sudo yum -y remove git

Instale o git 1.9.0 e suas dependências

.. code-block::

    sudo yum -y install zlib-devel perl-CPAN gettext curl-devel expat-devel gettext-devel openssl-devel
    sudo mkdir /tmp/git && cd /tmp/git
    sudo wget https://git-core.googlecode.com/files/git-1.9.0.tar.gz
    sudo tar xzf git-1.9.0.tar.gz
    cd git-1.9.0/
    sudo ./configure
    sudo make
    sudo make prefix=/usr/local install

Remova qualquer ruby instalado antes, e faça o download do ``ruby-2.0.0-p451``

.. code-block::

    sudo yum remove ruby -y
    mkdir /tmp/ruby && cd /tmp/ruby
    sudo curl --progress http://cache.ruby-lang.org/pub/ruby/2.0/ruby-2.0.0-p451.tar.bz2 | tar xj

Instale o ruby 2.0.0

.. code-block::

    cd ruby-2.0.0-p451
    ./configure --disable-install-rdoc
    make
    sudo make prefix=/usr/local install

Instale a gem bundler

.. code-block::

    sudo /usr/local/bin/gem install bundler --no-ri --no-rdoc

Crie o usuário ``git`` com as permissões corretas

.. code-block::

    sudo adduser --system --shell /bin/bash --comment 'GitLab' --create-home --home-dir /home/git/ git

Clone o repositório gitlab-shell

.. code-block::

    sudo su
    cd /home/git
    sudo -u git -H /usr/local/bin/git clone https://gitlab.com/gitlab-org/gitlab-shell.git
    cd gitlab-shell/
    /usr/local/bin/git reset --hard v1.9.3

Configure o host name e instale o gitlab-shell

.. code-block::

    sudo -u git -H cp config.yml.example config.yml
    sudo -u git -H /usr/local/bin/ruby ./bin/install
    restorecon -Rv /home/git/.ssh

Clone e configure o repositório ``gitlab``

.. code-block::

    cd /home/git
    sudo -u git -H /usr/local/bin/git clone https://github.com/colab-community/gitlabhq.git -b 6-8-stable gitlab
    cd /home/git/gitlab
    sudo -u git -H cp config/gitlab.yml.example config/gitlab.yml
    chown -R git {log,tmp}
    chmod -R u+rwX {log,tmp}
    sudo -u git -H mkdir /home/git/gitlab-satellites
    chmod u+rwx,g+rx,o-rwx /home/git/gitlab-satellites
    chmod -R u+rwX tmp/{pids,sockets}
    chmod -R u+rwX public/uploads
    sudo -u git -H cp config/unicorn.rb.example config/unicorn.rb
    sudo -u git -H cp config/initializers/rack_attack.rb.example config/initializers/rack_attack.rb

Mude a porta do unicorn para 8090

.. code-block::

    sudo vim /home/git/gitlab/config/unicorn.rb

Mude esta linha

.. code-block::

    listen "127.0.0.1:8080", :tcp_nopush => true

para

.. code-block::

    listen "127.0.0.1:8090", :tcp_nopush => true

No mesmo arquivo descomente a linha a seguir

.. code-block::

    ENV['RAILS_RELATIVE_URL_ROOT'] = "/gitlab"

.. code-block::

    [ESC]:wq!

Mude a URL padrão no arquivo application.rb

.. code-block::

    sudo vim /home/git/gitlab/config/application.rb

Descomentando ou adicionando a linha

.. code-block::

    config.relative_url_root = "/gitlab"

Mude a URL padrão no gitlab.yml

.. code-block::

    sudo vim /home/git/gitlab/config/gitlab.yml

Descomentando ou adicionando a linha

.. code-block::

    relative_url_root: /gitlab

Mude a URL padrão no gitlab-shell/config.yml

.. code-block::

    sudo vim /home/git/gitlab-shell/config.yml

Mudando esta linha

.. code-block::

    gitlab_url: "http://localhost/"

Para esta, mudando o IP ``127.0.0.1`` para o IP da máquina do Gitlab

.. code-block::

    gitlab_url: "http://127.0.0.1:8090/gitlab/"

Configure o git e o postgres

.. code-block::

    sudo -u git -H /usr/local/bin/git config --global user.name "GitLab"
    sudo -u git -H /usr/local/bin/git config --global user.email "gitlab@localhost"
    sudo -u git -H /usr/local/bin/git config --global core.autocrlf input
    sudo -u git cp config/database.yml.postgresql config/database.yml
    sudo -u git -H chmod o-rwx config/database.yml

xxxxxxxxxxx configurar o database do gitlab xxxxxxxxxxxxxxxxx

Configure o bundle

.. code-block::

    cd /home/git/gitlab
    sudo -u git -H /usr/local/bin/bundle config build.pg --with-pg-config=/usr/pgsql-9.3/bin/pg_config
    sudo -u git -H /usr/local/bin/bundle config build.nokogiri --use-system-libraries

Edite o arquivo sudoers para a excução dos comandos do ruby

.. code-block::

    sudo vim /etc/sudoers

Mude a linha

.. code-block::

    Defaults    secure_path = /sbin:/bin:/usr/sbin:/usr/bin

Para

.. code-block::

    Defaults    secure_path = /sbin:/bin:/usr/sbin:/usr/bin:/usr/local/bin/

.. code-block::

    [ESC]:wq!

Instale as gems que são as dependências do Gitlab.

.. code-block::

    sudo -u git -H /usr/local/bin/bundle install --deployment --without development test mysql aws
    sudo -u git -H /usr/local/bin/bundle exec rake gitlab:setup RAILS_ENV=production

Digite ``yes`` para prosseguir com a criação do banco.

Adicine o Gitlab para iniciar com o sistema

.. code-block::

    wget -O /etc/init.d/gitlab https://gitlab.com/gitlab-org/gitlab-recipes/raw/master/init/sysvinit/centos/gitlab-unicorn
    chmod +x /etc/init.d/gitlab
    chkconfig --add gitlab
    chkconfig gitlab on
    cp lib/support/logrotate/gitlab /etc/logrotate.d/gitlab
    service gitlab start

Compile os  asstes

.. code-block::

    sudo -u git -H /usr/local/bin/bundle exec rake assets:precompile RAILS_ENV=production

Mude as permissões de gurpo da pasta

    chmod g+rx /home/git/

Renicie o gitlab

.. code-block::

    sudo service gitlab restart


