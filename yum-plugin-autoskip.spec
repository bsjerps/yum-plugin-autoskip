Name:		yum-plugin-autoskip
Summary:	YUM plugin that changes or disables repos using local config files.
Version:	1.2.0
Release:	1%{?dtap}
License:	GPLv3+
Group:		Outrun/Extras
Source0:	%{name}-%{version}.tbz2
BuildArch:	noarch
Requires:	yum >= 3.0
Provides:	yum-plugin-localmirror
Obsoletes:	yum-plugin-localmirror

# Prevent compiling .py files
%define	__python	false

%description
Autoskip changes repositories without modifying the YUM repo files.

This helps running YUM on isolated networks (no http access), or
to easily setup local YUM mirrors.

Autoskip performs 3 steps:

- Disable repositories if they exist based on wildcard
  (Block repos you don’t want)
- Modify mirrorlist locations without changing .repo files
  (Redirect existing repositories to local mirrors)
- Skip (disable) repositories if their mirrorlist or baseurl is not reachable
  (Prevents PYCURL ERRORs on isolated networks)

%prep
%setup -q -n %{name}
%install
rm -rf %{buildroot}
install -m 0755 -d %{buildroot}/usr/lib/yum-plugins
install -m 0755 -d %{buildroot}/usr/share/doc/%{name}
install -m 0755 -d %{buildroot}/usr/share/man/man5
install -m 0755 -d %{buildroot}/etc/yum/mirrors
install -m 0755 -d %{buildroot}/etc/yum/pluginconf.d

cp -p autoskip.py %{buildroot}/usr/lib/yum-plugins
cp -p autoskip.conf %{buildroot}/etc/yum/pluginconf.d
cp -p doc/* %{buildroot}/usr/share/doc/%{name}
cp -p man5/* %{buildroot}/usr/share/man/man5
touch %{buildroot}/usr/lib/yum-plugins/autoskip.py{c,o}

%files
%defattr(0644,root,root,755)
%doc /usr/share/doc/%{name}/*
/usr/share/man/man5/*
%dir /etc/yum/mirrors
%config(noreplace) /etc/yum/pluginconf.d/autoskip.conf
/usr/lib/yum-plugins/autoskip.py
%ghost /usr/lib/yum-plugins/autoskip.pyc
%ghost /usr/lib/yum-plugins/autoskip.pyo

