Name:		python-django-horizon-facebook
Version:	2012.2.1
Release:	1%{?dist}
Summary:	A facebook auth plugin for horizon

Group:		Development/Libraries
License:	Apache 2.0
URL:		https://github.com/trystack/horizon/commits/folsom-trystack
Source0:	%{name}-%{version}.tar.gz

BuildRequires: python2-devel 
BuildRequires: python-setuptools
Requires:	python-django-horizon

%description
Provides auth module to allow the horizon framework to use facebook as an auth method

%prep
%setup -q -n %{name}-%{version}


%build
%{__python} setup.py build

%install
mkdir %{buildroot}%{python_sitelib}/horizon/facebook/templates/auth/ -p
install -t %{buildroot}%{python_sitelib}/horizon/facebook/ horizon/facebook/*py*
install -t %{buildroot}%{python_sitelib}/horizon/facebook/templates/ horizon/templates/*html
install -t %{buildroot}%{python_sitelib}/horizon/facebook/templates/auth/ horizon/templates/auth/*html

%files
%defattr(644, root, root, -)
%doc LICENSE
%{python_sitelib}/horizon/facebook/*.py*
%{python_sitelib}/horizon/facebook/templates/*.html
%{python_sitelib}/horizon/facebook/templates/auth/*.html

%changelog
* Thu Mar 27 2013 Dan Radez <dradez@redhat.com> - 2012.2-1
- initial packaging
