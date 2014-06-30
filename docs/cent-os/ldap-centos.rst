.. -*- coding: utf-8 -*-

.. highlight:: rest

.. _colab_software:

LDAP 2.4
========

*NOTE:*

    Source Tutorial: `http://wiki.openiam.com/pages/viewpage.action?pageId=7635198 <http://wiki.openiam.com/pages/viewpage.action?pageId=7635198>`_

Install openldap client and server

.. code-block::

    sudo yum install openldap-servers openldap-clients -y
    sudo yum install sssd perl-LDAP.noarch -y

Copy the database sample configuration file

.. code-block::

    sudo cp /usr/share/openldap-servers/DB_CONFIG.example /var/lib/ldap/DB_CONFIG

Change the permissions to ``/var/lib/ldap`` and copy the file ``slapd.d``

.. code-block::

    sudo chown -R ldap:ldap /var/lib/ldap
    cd /etc/openldap
    sudo mv slapd.d slapd.d.original

Generate the password, using the password ``ldapcolab``

.. code-block::

    sudo slappasswd

This will generated a key like that ``{SSHA}aCnD3GgAJiDryZY0PNxVwdPXyUz45lzd``, but it is not this key. The generated key you should copy for later use. Start LDAP server and put it to start with the system.

.. code-block::

    sudo service slapd start
    sudo chkconfig slapd on

Copy the ``ldap.conf`` file.

.. code-block::

    sudo mv ldap.conf ldap.conf.original
    sudo cp ldap.conf.original ldap.conf

Create the ``slapd.conf``

.. code-block::

    sudo vim /etc/openldap/slapd.conf

Insert the text above in the file, and change the ``rootpw`` to the ssh key generated above.

.. code-block::

    #
    # See slapd.conf(5) for details on configuration options.
    # This file should NOT be world readable.
    #
    include     /etc/openldap/schema/core.schema
    include     /etc/openldap/schema/cosine.schema
    include     /etc/openldap/schema/inetorgperson.schema
    include     /etc/openldap/schema/nis.schema

    # Added for policy
    include     /etc/openldap/schema/ppolicy.schema

    # Allow LDAPv2 client connections.  This is NOT the default.
    allow bind_v2

    # Do not enable referrals until AFTER you have a working directory
    # service AND an understanding of referrals.
    #referral   ldap://root.openldap.org

    pidfile     /var/run/openldap/slapd.pid
    argsfile    /var/run/openldap/slapd.args

    # Load dynamic backend modules:
    # modulepath    /usr/lib64/openldap

    # Modules available in openldap-servers-overlays RPM package
    # Module syncprov.la is now statically linked with slapd and there
    # is no need to load it here
    # moduleload accesslog.la
    # moduleload auditlog.la
    # moduleload denyop.la
    # moduleload dyngroup.la
    # moduleload dynlist.la
    # moduleload lastmod.la
    # moduleload pcache.la

    moduleload ppolicy.la

    # moduleload refint.la
    # moduleload retcode.la
    # moduleload rwm.la
    # moduleload smbk5pwd.la
    # moduleload translucent.la
    # moduleload unique.la
    # moduleload valsort.la

    # modules available in openldap-servers-sql RPM package:
    # moduleload back_sql.la

    # The next three lines allow use of TLS for encrypting connections using a
    # dummy test certificate which you can generate by changing to
    # /etc/pki/tls/certs, running "make slapd.pem", and fixing permissions on
    # slapd.pem so that the ldap user or group can read it.  Your client software
    # may balk at self-signed certificates, however.
    # TLSCACertificateFile /etc/pki/tls/certs/ca-bundle.crt
    # TLSCertificateFile /etc/pki/tls/certs/slapd.pem
    # TLSCertificateKeyFile /etc/pki/tls/certs/slapd.pem

    # Sample security restrictions
    #   Require integrity protection (prevent hijacking)
    #   Require 112-bit (3DES or better) encryption for updates
    #   Require 63-bit encryption for simple bind
    # security ssf=1 update_ssf=112 simple_bind=64

    # Sample access control policy:
    #   Root DSE: allow anyone to read it
    #   Subschema (sub)entry DSE: allow anyone to read it
    #   Other DSEs:
    #       Allow self write access
    #       Allow authenticated users read access
    #       Allow anonymous users to authenticate
    #   Directives needed to implement policy:
    # access to dn.base="" by * read
    # access to dn.base="cn=Subschema" by * read
    # access to *
    #   by self write
    #   by users read
    #   by anonymous auth
    #
    # if no access controls are present, the default policy
    # allows anyone and everyone to read anything but restricts
    # updates to rootdn.  (e.g., "access to * by * read")
    #
    # rootdn can always read and write EVERYTHING!

    #######################################################################
    # ldbm and/or bdb database definitions
    #######################################################################

    database    bdb
    suffix      "dc=colab,dc=com"
    rootdn      "cn=admin,dc=colab,dc=com"
    rootpw      {SSHA}...

    # PPolicy Configuration
    overlay ppolicy
    ppolicy_default "cn=default,ou=policies,dc=colab,dc=com"
    ppolicy_use_lockout
    ppolicy_hash_cleartext



    # The database directory MUST exist prior to running slapd AND
    # should only be accessible by the slapd and slap tools.
    # Mode 700 recommended.
    directory   /var/lib/ldap

    # Indices to maintain for this database
    index objectClass                       eq,pres
    index ou,cn,mail,surname,givenname      eq,pres,sub
    index uidNumber,gidNumber,loginShell    eq,pres
    index uid,memberUid                     eq,pres,sub
    index nisMapName,nisMapEntry            eq,pres,sub

.. code-block::

    [ESC]:wq!

Create the ``ppolicy.ldif`` file

.. code-block::

    sudo vim /etc/openldap/ppolicy.ldif

Insert the content below

.. code-block::

    dn: ou = policies,dc=colab,dc=com
    objectClass: organizationalUnit
    objectClass: top
    ou: policies

    # default, policies, example.com
    dn: cn=default,ou=policies,dc=colab,dc=com
    objectClass: top
    objectClass: pwdPolicy
    objectClass: person
    cn: default
    sn: dummy value
    pwdAttribute: userPassword
    pwdMaxAge: 7516800
    pwdExpireWarning: 14482463
    pwdMinLength: 2
    pwdMaxFailure: 10
    pwdLockout: TRUE
    pwdLockoutDuration: 60
    pwdMustChange: FALSE
    pwdAllowUserChange: FALSE
    pwdSafeModify: FALSE

.. code-block::

    [ESC]:wq!

Start the LDAP server.

.. code-block::

    sudo service slapd start

*NOTE:*

    To test connection: ldapsearch -h localhost -D "cn=admin,dc=colab,dc=com" -w ldapcolab -b "dc=colab,dc=com" -s sub "objectclass=*"   . Should not return invalid credential or could not connect.

Create a ``base.ldif``

.. code-block::

    mkdir /tmp/ldap
    cd /tmp/ldap
    sudo vim base.ldif

Insert the text below

.. code-block::

    dn: dc=colab,dc=com
    objectClass: dcObject
    objectClass: organization
    dc: colab
    o: Colab
    description: Colab

    dn: cn=admin,dc=colab,dc=com
    objectClass: organizationalRole
    cn: Admin
    description: System Manager

    dn: ou=users,dc=colab,dc=com
    objectClass: organizationalUnit
    ou: users

    dn: ou=oldusers,dc=colab,dc=com
    objectClass: organizationalUnit
    ou: oldusers

.. code-block::

    [ESC]:wq!

To generate the LDAP schema add the base.ldif

.. code-block::

    ldapadd -x -D "cn=Manager,dc=openiamdemo,dc=com" -w ldapcolab -f base.ldif

*NOTE:*

    You can purge LDAP data by erasing the files in folder /var/lib/ldap/, just keep the file DB_CONFIG

Configure Gitlab LDAP
=====================

To enable LDAP on Gitlab you should edit the gilab.yml configuration file as root

.. code-block::

    sudo su
    vim config/gitlab.yml

Set the following option like the information below. You should change localhost to the LDAP machine IP

.. code-block::

  ldap:
    enabled: true
    host: 'localhost'
    base: 'dc=colab,dc=com'
    port: 389
    uid: 'uid'
    method: 'plain'
    bind_dn: 'cn=admin,dc=colab,dc=com'
    password: 'ldapcolab'
    allow_username_or_email_login: true

.. code-block::

    [ESC]:wq!

Restart Gitlab service

.. code-block::

    sudo service gitlab restart

