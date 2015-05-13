zabbix-ems
==========

Zabbix Extended Monitoring Scripts (and templates)

Check our Trello board for development progress: https://trello.com/b/uCcdHHwj/zabbix-extended-monitoring-scripts

Install on EL5
--------------
* Install Python 2.6

* Install setuptools
	
	`ftp://ftp.pbone.net/mirror/ftp.pramberger.at/systems/linux/contrib/rhel5/i386/python26-setuptools-0.7.4-1.el5.pp.noarch.rpm`

* Install pip
	
	`curl https://raw.github.com/pypa/pip/master/contrib/get-pip.py && python26 get-pip.py`

* Install commandr
	
	`pip install commandr`

* Install enum34
	
	`pip install enum34`

* Install zems rpm

Install on EL6
--------------
* Install epel repository

* Install setuptools
	
	`yum install python-setuptools`

* Install pip
	
	`yum install python-pip`

* Install commandr
	
	`pip install commandr`

* Install enum34
	
	`pip install enum34`

* Install zems rpm
