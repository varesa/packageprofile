Name:       packageprofile-client
Version:	1.0.0
Release:	4%{?dist}
Summary:	Publishes the installed packages to a server

License:	Public Domain
URL:	    https://github.com/varesa/packageprofile	
BuildArch:  noarch

%if 0%{?rhel}
Requires:   yum python-configparser python-requests	
%endif

%if 0%{?fedora}
Requires:   python3-dnf python3-requests
%endif

%description
Publishes the list of installed packages to a server

%install
mkdir -p %{buildroot}/etc
mkdir -p %{buildroot}/%{_bindir}
mkdir -p %{buildroot}/usr/local/lib/packageprofile/
install -p -m 644 config.template %{buildroot}/etc/packageprofile.conf
%if 0%{?rhel}
install -p -m 755 centos.sh %{buildroot}/%{_bindir}/packageprofile-client
%endif
%if 0%{?fedora}
install -p -m 755 fedora.sh %{buildroot}/%{_bindir}/packageprofile-client
%endif
install -p -m 644 ../client.py %{buildroot}/usr/local/lib/packageprofile/client.py
install -p -m 644 ../packagemanager.py %{buildroot}/usr/local/lib/packageprofile/packagemanager.py

%files
%config(noreplace) /etc/packageprofile.conf
%{_bindir}/packageprofile-client
/usr/local/lib/packageprofile/

%changelog

