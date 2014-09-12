
class colab (
  $mailman_archive_path = 'default',
  $mailman_exclude_lists = [],
  $hostnames = [],
  $solr_project_path = '',
  $mailman_ip = '127.0.0.1',
  $mailman_port = 8025
){

  require pip
  require appdeploy::deps::python
  require appdeploy::deps::essential
  require appdeploy::deps::openssl

  include nginx
  include ntp
  include security_updates
  include appdeploy::deps::lxml
  include appdeploy::deps::postgresql
  include colab::cronjobs
  include postgresql::globals
  include postgresql::server

  postgresql::server::db { 'colab':
    user     => 'colab',
    password => 'colab',
    grant    => 'all',
  }

  appdeploy::django { 'colab':
    user      => 'colab',
    directory => '/home/colab/colab/src',
    proxy_hosts => $colab::hostnames,
  }

  $package_defaults = {
    before => Pip::Install['pyOpenSSL'],
  }

  case $osfamily {

    'Redhat': {
      ensure_packages(['java-1.7.0-openjdk', 'fuse-sshfs'], $package_defaults)
    }
    'Debian': {
      ensure_packages(['openjdk-7-jre', 'sshfs'], $package_defaults)
    }
  }

  ensure_packages(['memcached'])

  # Punjab dep
  pip::install { 'Twisted': }
  pip::install { 'pyOpenSSL': }

  # XMPP connection manager
  pip::install { 'punjab':
    require => Pip::Install['Twisted', 'pyOpenSSL'],
  }

  supervisor::app { 'punjab':
    command   => 'twistd --nodaemon punjab',
    directory => '/home/colab/',
    user      => 'colab',
  }

  supervisor::app { 'solr':
    command   => 'java -jar start.jar',
    directory => $colab::solr_project_path,
    user      => 'colab',
  }

  nginx::resource::upstream { 'mailman-upstream':
    ensure  => present,
    members => ["$mailman_ip:$mailman_port"],
  }

  nginx::resource::location { 'lists':
    ensure   => present,
    vhost    => 'colab',
    location => '/lists/',
    proxy    => 'http://mailman-upstream/mailman/cgi-bin/',
  }

}
