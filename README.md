# yum-plugin-autoskip
A YUM plugin that disables non-reachable YUM repositories or 
modifies them using local config files.

# Features

Autoskip changes repositories without modifying the YUM repo files:

* Skip repositories if their mirrorlist or baseurl is not reachable
  * Prevents PYCURL ERRORs on isolated networks
* Modify mirrorlist locations without changing .repo files
  * Redirect existing repositories to local mirrors so you don't have
  to create additional repo files and/or mess with the original ones
* Disable repositories if they exist based on wildcard
  * Block repos you don't want even if their repo files get overwritten
  again by YUM

# Installation

If you don't install via the RPM, then copy autoskip.py
to

_/usr/lib/yum-plugins/autoskip.py_

and add a config file _/etc/yum/pluginconf.d/autoskip.conf_:

```
[main]
enabled=1
```

# Configuration

## Redirect to local mirrors

If you want to redirect YUM to local mirrorlists, place those mirrorlists in
_/etc/yum/mirrors/_

Example: To redirect CentOS base (from CentOS-Base.repo) to a local mirror, 
create _/etc/yum/mirrors/base_:

```
http://repo.example.net/yum/centos/$release/os/$basearch
```
(assuming this is where the server will have it's YUM mirror for CentOS)

Note that this is just a mirrorlist file so you may add additional urls
for failback if the first one would be unavailable.

## Disable repos by name or wildcard

To disable repos, create _/etc/yum/mirrors/disabled_ containing the
repo ids (wildcards * and ? are accepted).
For example _/etc/yum/mirrors/disabled_:

```
ol7_UEKR5
```
Will disable the Oracle UEK kernel repo for Oracle Linux 7, UEK release 5.
_/etc/yum/mirrors/disabled_:

```
ol?_UEKR*

```
will disable all UEK kernel repos (as long as
their repoid matches the pattern).

# Description

Autoskip will look for a file named /etc/yum/mirrors/disabled and disable
all repositories defined in that file.

Then for each enabled repo, it will look for a file named
/etc/yum/mirrors/<repoid> and if exists, uses this as mirrorlist
instead of the one defined in the .repo file.

Finally, for http/https urls, it will issue a http request to
the mirrorlist url (or, if not defined, baseurl) 
and disable the repo if it cannot reach the url.

# Rationale

When installing Linux on isolated networks, YUM tends to spit out a lot
of PYCURL ERRORs and sometimes give up
(especially when using the fastestmirror plugin).

Autoskip allows one to define a local YUM mirror without
modifying .repo files such as CentOS-Base.repo - which
makes automated installs and updates on such networks a lot easier.

Even on systems that have proper http/https access, defining a
local YUM mirror may speed up updates and package installs
but configuring this by modifying .repo files through awk/sed can be 
a pain. With Autoskip you just add a mirrorlist file
with the name of the repo.

# Known issues

- Cannot re-enable a repo with --enablerepo=<repoid> once disabled.
- FTP based repos currently not tested for reachability so they may still cause failures
- Must run before the fastestmirror plugin (if enabled) to work properly
