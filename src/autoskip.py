#!/usr/bin/python
'''
autoskip.py - A YUM plugin that changes repository mirrors or
disables them using local config files.

Usage:
Place this in /usr/lib/yum-plugins and add a config file

/etc/yum/pluginconf.d/autoskip.conf:
[main]
enabled=1

Then place mirrorlists (with urls to YUM repos) 
in /etc/yum/mirrors/ with the name equal to the repo id.

A special file is /etc/yum/mirrors/disabled which contains
repo ids that always should be disabled. Wildcards (* or ?)
are allowed.

Repos for which the mirrorlist url or (if defined) baseurl is
not reachable, will also automatically be disabled (http/https only).

Description:

Autoskip will first look for a file named /etc/yum/mirrors/disabled
and disable any repo id that matches the patterns in that file

Then for each repo, autoskip will look for a file named
/etc/yum/mirrors/<repoid> and change 'mirrorlist' to this file

This helps on networks without internet access to redirect YUM to a local
mirror (ftp or http) without changing the repo definitions (as these may get
overwritten during YUM updates). If the local mirror does not respond then
YUM would still failback to the original baseurl/mirrorlist which would
not be the case if we modded the .repo files directly.

In case failovermethod is set to 'priority' this leads to the locally defined
urls to be tried first, before baseurl and the repo's mirrorlist. This avoids
errors before switching to alternative mirrors on restricted LANs.

Known issues:

- Cannot re-enable a repo with --enablerepo=<repoid> once disabled.
- FTP based repos currently not tested for reachability
- Breaks if the plugin does not load BEFORE fastestmirror.py (which is
  why I renamed it to 'autoskip'
  
Note fastestmirror.py was silently changed to use prereoposetup instead
of postreposetup causing it to fail anyway. autoskip needs to load
BEFORE fastestmirror.


This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Library General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

Author: Bart Sjerps <bart@outrun.nl>
'''

from yum.plugins import TYPE_CORE, TYPE_INTERACTIVE

import os
import urlgrabber
import fnmatch

requires_api_version = '2.3'
plugin_type = (TYPE_CORE)

# Where to look for mirror lists and the 'disabled' file
confdir = '/etc/yum/mirrors/'

# Read a config file and return an array with the containing lines

def readconfig(file):
    with open(file) as f:
        lines = f.read().splitlines()
    return lines

'''
Replace all $vars with their values in an array using yumparser.varReplace
We don't need this anymore but leave it here as it may come in handy
in the future

from yum.parser import varReplace
def replacevars(list, vars):
    replaced = []
    for url in list:
        url = varReplace(url, vars)
        replaced.append(url)
    return replaced
'''

def prereposetup_hook(conduit):
    skipped = []
    modded = []
    blocked = []
    blocklist = []

    if os.path.isfile(confdir + 'disabled'):
        blocklist = readconfig(confdir + 'disabled')

    repos = conduit.getRepos()
    for repo in repos.listEnabled():
        for pat in blocklist:
            if fnmatch.fnmatch(repo.id, pat):
                repo.enabled = False
                blocked.append(repo.id)
        if not repo.enabled:
            continue

#       No longer needed?
#       if not repo.skip_if_unavailable:
#          repo.skip_if_unavailable = True

        # Mod the mirrorlist if the local alternative exists
        if os.path.isfile(confdir + repo.id):
            repo.mirrorlist = 'file://' + confdir + repo.id
            modded.append(repo.id)

        # Get the mirrorlist url or if it's empty, the baseurl
        if repo.mirrorlist is not None:
            url = repo.mirrorlist
        elif repo.baseurl:
            url = repo.baseurl[0]

        # If the url is no http... then do nothing
        if str(url).startswith('http'):
            # Try to get the url, if it fails, disable the repo
            # also set mirrorlist and urls to file:/// so that
            # fastestmirror plugin will ignore it
            try:
                data = urlgrabber.urlread(url)
            except:
                repo.mirrorlist = 'file:///'
                repo.urls = ['file:///']
                skipped.append(repo.id)
                repo.enabled = False

    # report which repos we have messed with
    if skipped:
        conduit.info(2, "* Autoskipped: " + ", ".join(skipped))
    if modded:
        conduit.info(2, "* Automodded: " + ", ".join(modded))
    if blocked:
        conduit.info(2, "* Autoblocked: " + ", ".join(blocked))

