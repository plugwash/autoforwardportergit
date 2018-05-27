# Git based autoforwardporter.

The purpose of this tool is to assist downstreams in maintaining local changes
to Debian packages. In particular automating the merging of those local changes

"downstream" in this context can be anything from a set of packages you only use
yourself to a major derivative.

this document describes the theory of operation and the available settings. See
the file tutorial/README for a quick start guide.

## The working repo

The working repo is a repository with multiple suites in groups. The "main"
suite of each group represents what you use/ship. The "staging" suite represents
stuff that you have plan to ship but has not yet been built, passed automated
checks or whatever. The "upstream" suite represents what your upstream distro
(e.g. debian) ships.

Having a seperate staging suite is optional. If you don't have a seperate
staging suite then you can simply point the "staging suite" at your main suite.

The working repo must have uncompressed packages and sources files. It must also
use a standard pool layout.

Example reprepro configs that are suitable for use with the autoforwardporter
can be found in the tests/workingrepo/conf directory or the 
demo/workingrepo/conf directory.

If desired the autoforwardporter can generate a filter list for reprepro to
control what packages are imported into the working repo. 

## Version markers

Markers in the version number are used to identify versions locally produced by
your downstream project. These markers will normally take the form of a plus
sign, followed by the name of your prorject followed by a number. e.g. +rpi1
+ubuntu1 etc. 

Normally the marker will be placed at the end of the version number, but
sometimes this is not possible. Consider for example Debian releases a package
with version "1", you make a derived package with version "1+rpi1". Debian then
releases a new version "1+deb7u1". You cannot use "1+deb7u1+rpi1" for your new
version because "1+deb7u1+rpi1" << "1+rpi1". In this case the autoforwardporter
will use a version with the local marker in the middle, e.g. "1+rpi1+deb7u1".

Autoforwardportergit also supports a "revert marker". This is used to mark
packages where you have reverted your local changes, but still need to raise
the version number to preserve version ordering.

## pooltogit

The first stage of the process is getting your source packages into git with
a sensible history. This is the function of pooltogit.

Versions of a packages are imported in version number order and dgit is used
to import the packages. If the package has a dgit: line then the package is
simply imported using that commit.

If the package does not have a dgit tag then the history is built based on the
changelogs. The exact behaviour depends on whether the version contains a local
marker.

If there is a local marker in the version number then pooltogit strictly
insists on using the immediate parent. If the --snapshot option is specified
to pooltogit then pooltogit will attempt to use snapshotsecure to retrive
the package from snapshot.debian.org. If the immediate parent does not exist
and the user has not specified the --snapshot option or the retrieval from
snapshot.debian.org fails the import process will abort. Sometimes it will be
nessacery to manually download a dsc to the pool and re-run pooltogit.

If there is not a local version marker then pooltogit is more lax, it will
work backwards through the changelog until it finds a version that it can use
as the parent. If it doesn't find any then it will import the package with an
orphan history.

If the parent is found to be a version that is not yet imported but is in the
list of packages to import (this can happen when packages are backported, 
such that the parent has a higher version than the package being processed)
then the parent version will be pushed to the start of the list.

Pooltogit operates on a whitelist of packages. Unlike it's predecessor
dscdirtogit it is able to follow history across package name changes.

pooltogit is not normally invoked directly. Dscdirtogitdriver is used to
read configuration settings from the autoforwardportergitconfiguration and
invoke pooltogit in the appropriate directory with the appropriate arguments.

dscdirtogitdriver is invoked as

<path>/dscdirtogitdriver

Options for pooltogit can be specified by the dscdirtogitargs option in the
main section of the autoforwardportergit configuration file.

## the actual autoforwardporter

The actual autoforwardporter is conceptually simple. Take the downstream version
merge it with the new version from the upstream distro and build a source
package. Since this is dgit based these are patches-applied git trees.

The git merge will not simply succeeed. At the very least debian/changelog will
have conflicts. There are also a number of other debian related files that will
often have conflicts that can be dealt with mechanically. 

The autoforwardporter will attempt to fix up these conflicts. This process will
likely be improved and made more customisable in future versions.

Assuming the git conflicts are succesfully dealt with the focus then moves
on to the quilt series. Any fuzzy patches will be defuzzed and any packages that
cannot be applied to the upstream source will be removed from the quilt series.
dgit will then add a patch to the quilt series to make the results of applying
the quilt series the same as the files in the actual tree.

The results of the process whether successful or not will be pushed to a
"working" branch in the git repo. If there are still conflicts that could not
automatically be resolved they will be listed at the top of debian/changelog.

If the conflicts are resolved successfully then an attempt will be made to build
a source package. Optionally the autoforwardporter can build the resulting
package using sbuild and use dgit push to create dgit: tags.

The autoforwardporter is invoked as

<path>/forwardportdriver <mainsuite>

## whitelists
The git import and forward porting processes will only be performed on
whitelisted files.

The whitelist for the importer is whitelist.import, the whitelists for the
actualautoforwardporter are whitelist.<mainsuite>

The whiltelists are located in the configuratoin directory (see later).

There is a tool updateimportwhitelist which can be used to add entries
from the autoforwardporter whitelist to the 

## output and log files
output files and logs are placed in an output directory. Before trying to
perform a forward port the autoforwardporter will check for a log file. 
Therefore each package/version combination will only be tried once, if you want
to retry a package/version then simply delete the log file and re-run the
autoforwardporter.

## dependencies
dscdirtogit and autoforwardportergit require the following packages

build-essential
git
dgit 
python3
python3-debian
python3-git
moreutils (for the "sponge" untility)
rcs (for the "merge" utility)
quilt (for fixing up quilt series)
reprepro (for changestool and also reccomended for managing your working repo).
python3-bs4 (only if you intend to use snapshotsecure)

## configuration

The autoforwardporter requires configuration. To do this a configuration
directory is used. By default this is ~/.autoforwardportergit but this can be
overridden by the AFPGCONFIG environment variable.

The main configuration file is afpg.ini in the configuration directory.

The file is an "ini style" file read with python 3's config parser. There is
a main section with global settings and a setting for each suite group . The
section for each suite group is named after the "main" suite in the group.

Relative paths in the configuration file are interpreted relative to the config
directory. Absoloute paths and paths under the users homedir (starting with ~/
can also be specified.

A commented example configuration file with explanations of the settings can 
be found in the tests subdirectory.

## optional feature, sbuild
Optionally the autoforwardporter can call sbuild to build the resulting packages
so that you get binaries as well as dscs. You will need to set up sbuild so it
can be used to build source packages for your staging suite(s).

## optional feature, dgit push
Optionally the autoforwardporter can perform a dgit push to push the results
to a dgit server.

The advantage of using dgit push is that when your dscs are imported either by
your users or by dscdirtogit you will get real git history.

The downside is that you need to set up a dgit server which should be accessible
to everyone who may receive your dscs. 

Currently dgit push is "nerfed" so it uploads to the dgit repos but doesn't
actually upload to the archive. This may be made configurarable later.

## optional tool, branch pointer
Branchpointer creates branches in the git repo pointing at the version that is
in each suite.

It is invoked as 

<path>/branchpointer <mainsuite>

It uses the same whitelist as the importer.

## optional tool, pushtogithub
Pushtogithub pushes the tags produced by dscdirtogit and the branches produced
by branchpointer to github.

This tool requires some setup. 

Secondly git-credential-netrc must be copied from 
/usr/share/doc/git/contrib/credential/netrc/git-credential-netrc to /usr/bin

It uses it's own whitelist "whitelist.pushtogithub" in the configuration
directory.

It requires a netrc file with the github login settings, the location of this
file is configured in the ini file by the "netrcfile" setting. You must also
specify your github project in the "githubproject" setting.

## optional tool, snapshotsecure

snapshotsecure is a tool for retrieving source packages from snapshot.debian.org
in a reasonablly secure manner. It can optionally be called by dscdirtogit to
retrieve the source packages for the immediate parents of locally modified
versions.

Given a source package and version number, it will find out what snapshot and
suite it was in, then verify the gpg signature of the Release file in that suite
and securely validate the Source package. The source package will only be saved
to disk if it validates successfully.

By default snapshotsecure will use a list of all keys (past and present) that
are 2048 bits or stronger and have been used to sign the Debian archive.
Optionally the parameter --1024 can be passed to permit 1024 bit keys to be
used.
