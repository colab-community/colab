.. -*- coding: utf-8 -*-

.. highlight:: rest

.. _colab_software:

Nginx 1.6
=========

Download the nginx

.. code-block::

    cd /tmp
    wget http://nginx.org/packages/centos/6/noarch/RPMS/nginx-release-centos-6-0.el6.ngx.noarch.rpm
    sudo rpm -ivh nginx-release-centos-6-0.el6.ngx.noarch.rpm

Install nginx

.. code-block::

    sudo yum install nginx -y

Start nginx with the system

.. code-block::

    sudo chkconfig nginx on

