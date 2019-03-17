Name:       packageprofile-client
Version:	1.0.0
Release:	2%{?dist}
Summary:	Publishes the installed packages to a server

License:	Public Domain
URL:	    https://github.com/varesa/packageprofile	
BuildArch:  noarch

Requires:   python3-dnf python3-requests	

%description
Publishes the list of installed packages to a server

%install
mkdir -p %{buildroot}/etc
mkdir -p %{buildroot}/%{_bindir}
mkdir -p %{buildroot}/usr/local/lib/packageprofile/
install -p -m 644 config.template %{buildroot}/etc/packageprofile.conf
install -p -m 755 fedora.sh %{buildroot}/%{_bindir}/packageprofile-client
install -p -m 644 ../client.py %{buildroot}/usr/local/lib/packageprofile/client.py
install -p -m 644 ../packagemanager.py %{buildroot}/usr/local/lib/packageprofile/packagemanager.py

%files
%config(noreplace) /etc/packageprofile.conf
%{_bindir}/packageprofile-client
/usr/local/lib/packageprofile/

%changelog

