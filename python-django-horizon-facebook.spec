Name:		python-django-horizon-facebook
Version:	2013.1
Release:	2%{?dist}
Summary:	A facebook auth plugin for horizon and api password distribution

Group:		Development/Libraries
License:	Apache 2.0
URL:		https://github.com/trystack/horizon/commits/folsom-trystack
Source0:	%{name}-%{version}.tar.gz

BuildRequires: python2-devel 
BuildRequires: python-setuptools
Requires:	python-django-horizon

%description
Provides auth module to allow the horizon framework to use facebook as an auth method
Also provides password distribution of keystone password for api access.

%prep
%setup -q -n %{name}-%{version}


%build
%{__python} setup.py build

%install
#Facebook auth Stuff
mkdir %{buildroot}%{python_sitelib}/horizon/facebook/templates/auth/ -p
install -t %{buildroot}%{python_sitelib}/horizon/facebook/ horizon/facebook/*py*
install -t %{buildroot}%{python_sitelib}/horizon/facebook/templates/ horizon/templates/*html
install -t %{buildroot}%{python_sitelib}/horizon/facebook/templates/auth/ horizon/templates/auth/*html

#API Password Stuff
mkdir -p %{buildroot}%{_datadir}/openstack-dashboard/openstack_dashboard/dashboards/settings/apipassword/
mkdir -p %{buildroot}%{_datadir}/openstack-dashboard/openstack_dashboard/dashboards/settings/apipassword/templates/apipassword/
mkdir -p %{buildroot}%{python_sitelib}/horizon/management/commands/
mkdir -p %{buildroot}%{_sysconfdir}/cron.hourly/
install -t %{buildroot}%{_datadir}/openstack-dashboard/openstack_dashboard/dashboards/settings/apipassword/  openstack_dashboard/dashboards/settings/apipassword/*py*
install -t %{buildroot}%{_datadir}/openstack-dashboard/openstack_dashboard/dashboards/settings/apipassword/templates/apipassword  openstack_dashboard/dashboards/settings/apipassword/templates/apipassword/*html
install -t %{buildroot}%{python_sitelib}/horizon/management/commands/ horizon/management/commands/*py*
install -t %{buildroot}%{_sysconfdir}/cron.hourly/ cron/trystack-set-api-passwords

%files
%defattr(644, root, root)
%doc LICENSE
#API Password Stuff
%attr(700, root, root) /etc/cron.hourly/trystack-set-api-passwords
%{python_sitelib}/horizon/management/commands/*.py*
%{_datadir}/openstack-dashboard/openstack_dashboard/dashboards/settings/apipassword/*.py*
%{_datadir}/openstack-dashboard/openstack_dashboard/dashboards/settings/apipassword/templates/*
#Facebook auth Stuff
%{python_sitelib}/horizon/facebook/*.py*
%{python_sitelib}/horizon/facebook/templates/*.html
%{python_sitelib}/horizon/facebook/templates/auth/*.html

%changelog
* Tue Jul 16 2013 Dan Radez <dradez@redhat.com> - 2013.1-1
- Added API password managment scripts
* Tue Mar 27 2012 Dan Radez <dradez@redhat.com> - 2012.2-1
- initial packaging
