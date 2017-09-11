%define name zems
%define release 1
#%if 0%{?el5}
#    define pythoncmd python26
#%else
#    define pythoncmd python
#%endif

Summary: ZEMS (Zabbix Extended Monitoring Scripts) is a tool to retrieve all sorts of metrics from applications and deliver it to Zabbix in a generic way.
Name: %{name}
Version: %{version}
Release: %{release}%{?dist}
Source0: %{name}-%{version}.tar.gz
License: GPL
Group: Development/Libraries
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Prefix: %{_prefix}
BuildArch: noarch

%if 0%{?el5}
Requires: python26
Requires: python26-setuptools
%else
Requires: python >= 2.6
Requires: python-setuptools
%endif

Requires: zabbix-agent
Requires: sudo
Vendor: Marijn Giesen <marijn@studio-donder.nl>
Url: https://github.com/marijngiesen/zabbix-ems

%description
ZEMS (Zabbix Extended Monitoring Scripts) is a tool to retrieve all sorts of metrics from applications and deliver it to Zabbix in a generic way.

%prep
%setup -n %{name}-%{version} -n %{name}-%{version}

%build
python setup.py build

%install
python setup.py install --single-version-externally-managed -O1 --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES

mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/%{name}/zabbix
mkdir -p $RPM_BUILD_ROOT%{_datadir}/%{name}/templates
install -m 0644 -p config/*.conf $RPM_BUILD_ROOT%{_sysconfdir}/%{name}
install -m 0644 -p config/zabbix/*.conf $RPM_BUILD_ROOT%{_sysconfdir}/%{name}/zabbix
install -m 0644 -p templates/*.xml $RPM_BUILD_ROOT%{_datadir}/%{name}/templates

%post
# Make sure Zabbix can execute zems as root
if [ -z "`cat /etc/sudoers | grep 'zabbix ALL=NOPASSWD'`" ]; then
    cat <<HERE >> /etc/sudoers
Cmnd_Alias ZABBIX_CMNDS = /usr/bin/zems
zabbix ALL=NOPASSWD: ZABBIX_CMNDS
HERE
fi
    
# Do not require a TTY for the Zabbix user
if [ -z "`cat /etc/sudoers | grep 'Defaults:zabbix !requiretty'`" ]; then
    echo 'Defaults:zabbix !requiretty' >> /etc/sudoers
fi

# We need to create the logfile, cause Zems will error out if not.
touch /var/log/zems.log
chmod 666 /var/log/zems.log

# Make zems work on EL5
if [ ! -z "`uname -r | grep el5`" ]; then
    sed -i 's/#!.*$/#!\/usr\/bin\/python26/' /usr/bin/zems
fi

%clean
rm -rf $RPM_BUILD_ROOT

%files -f INSTALLED_FILES
%dir /etc/zems
%dir /etc/zems/zabbix
%dir /usr/share/zems
%config(noreplace) /etc/zems/*.conf
%config(noreplace) /etc/zems/zabbix/*.conf
/usr/share/zems/templates/*.xml
%defattr(-,root,root)
