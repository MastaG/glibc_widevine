%define glibcsrcdir glibc-2.26.9000-1139-g64f63cb458
%define glibcversion 2.26.9000
%define glibcrelease 43%{?dist}
# Pre-release tarballs are pulled in from git using a command that is
# effectively:
#
# git archive HEAD --format=tar --prefix=$(git describe --match 'glibc-*')/ \
#	> $(git describe --match 'glibc-*').tar
# gzip -9 $(git describe --match 'glibc-*').tar
#
# glibc_release_url is only defined when we have a release tarball.
%{lua: if string.match(rpm.expand("%glibcsrcdir"), "^glibc%-[0-9.]+$") then
  rpm.define("glibc_release_url https://ftp.gnu.org/gnu/glibc/") end}
##############################################################################
# We support hte following options:
# --with/--without,
# * testsuite - Running the testsuite.
# * benchtests - Running and building benchmark subpackage.
# * bootstrap - Bootstrapping the package.
# * werror - Build with -Werror
# * docs - Build with documentation and the required dependencies.
# * valgrind - Run smoke tests with valgrind to verify dynamic loader.
#
# You must always run the testsuite for production builds.
# Default: Always run the testsuite.
%bcond_without testsuite
# Default: Always build the benchtests.
%bcond_without benchtests
# Default: Not bootstrapping.
%bcond_with bootstrap
# Default: Enable using -Werror
%bcond_without werror
# Default: Always build documentation.
%bcond_without docs
# Default: Always run valgrind tests
%bcond_without valgrind

# Run a valgrind smoke test to ensure that the release is compatible and
# doesn't any new feature that might cause valgrind to abort.
%if %{with valgrind}
%ifarch s390 ppc64 ppc64p7 %{mips}
# There is no valgrind support for 31-bit s390, nor for MIPS.
# The valgrind test does not work on ppc64, ppc64p7 (bug 1273103).
%undefine with_valgrind
%endif
%endif
%if %{with bootstrap}
# Disable benchtests, -Werror, docs, and valgrind if we're bootstrapping
%undefine with_benchtests
%undefine with_werror
%undefine with_docs
%undefine with_valgrind
%endif
##############################################################################
# Auxiliary arches are those arches that can be built in addition
# to the core supported arches. You either install an auxarch or
# you install the base arch, not both. You would do this in order
# to provide a more optimized version of the package for your arch.
%define auxarches athlon alphaev6
##############################################################################
# We support only 64-bit POWER with the following runtimes:
# 64-bit BE:
# - Power 620 / 970 ISA (default runtime, compatile with POWER4 and newer)
#	- Provided for the large number of PowerPC G5 users.
#	- IFUNC support provides optimized core routines for POWER6,
#	  POWER7, and POWER8 transparently (if not using specific runtimes
#	  below)
# - POWER6 (has power6x symlink to power6, enabled via AT_PLATFORM)
#	- Legacy for old systems. Should be deprecated at some point soon.
# - POWER7 (enabled via AT_PLATFORM)
#	- Existing deployments.
# - POWER8 (enabled via AT_PLATFORM)
#	- Latest generation.
# 64-bit LE:
# - POWER8 LE (default)
#	- Latest generation.
#
# No 32-bit POWER support is provided.
#
# There are currently no plans for POWER9 enablement, but as hardware and
# upstream support become available this will be reviewed.
#
%ifarch ppc64
# Build the additional runtimes for 64-bit BE POWER.
%define buildpower6 0
%define buildpower7 1
%define buildpower8 1
%else
# No additional runtimes for ppc64le or ppc64p7, just the default.
%define buildpower6 0
%define buildpower7 0
%define buildpower8 0
%endif

##############################################################################
# Any architecture/kernel combination that supports running 32-bit and 64-bit
# code in userspace is considered a biarch arch.
%define biarcharches %{ix86} x86_64 %{power64} s390 s390x
##############################################################################
# If the debug information is split into two packages, the core debuginfo
# pacakge and the common debuginfo package then the arch should be listed
# here. If the arch is not listed here then a single core debuginfo package
# will be created for the architecture.
%define debuginfocommonarches %{biarcharches} alpha alphaev6
##############################################################################
# %%package glibc - The GNU C Library (glibc) core package.
##############################################################################
Summary: The GNU libc libraries
Name: glibc
Version: %{glibcversion}
Release: %{glibcrelease}
# GPLv2+ is used in a bunch of programs, LGPLv2+ is used for libraries.
# Things that are linked directly into dynamically linked programs
# and shared libraries (e.g. crt files, lib*_nonshared.a) have an additional
# exception which allows linking it into any kind of programs or shared
# libraries without restrictions.
License: LGPLv2+ and LGPLv2+ with exceptions and GPLv2+
URL: http://www.gnu.org/software/glibc/
Source0: %{?glibc_release_url}%{glibcsrcdir}.tar.gz
Source1: build-locale-archive.c
Source2: glibc_post_upgrade.c
Source4: nscd.conf
Source7: nsswitch.conf
Source8: power6emul.c
Source9: bench.mk
Source10: glibc-bench-compare
# A copt of localedata/SUPPORTED in the Source0 tarball.  The
# SUPPORTED file is used below to generate the list of locale
# packages.  See the language_list macro definition.
Source11: SUPPORTED

##############################################################################
# Start of glibc patches
##############################################################################
# 0000-0999 for patches which are unlikely to ever go upstream or which
# have not been analyzed to see if they ought to go upstream yet.
#
# 1000-2000 for patches that are already upstream.
#
# 2000-3000 for patches that are awaiting upstream approval
#
# Yes, I realize this means some gratutious changes as patches to from
# one bucket to another, but I find this scheme makes it easier to track
# the upstream divergence and patches needing approval.
#
# Note that we can still apply the patches in any order we see fit, so
# the changes from one bucket to another won't necessarily result in needing
# to twiddle the patch because of dependencies on prior patches and the like.


##############################################################################
#
# Patches that are unlikely to go upstream or not yet analyzed.
#
##############################################################################

# Configuration twiddle, not sure there's a good case to get upstream to
# change this.
Patch0001: glibc-fedora-nscd.patch

# All these were from the glibc-fedora.patch mega-patch and need another
# round of reviewing.  Ideally they'll either be submitted upstream or
# dropped.
Patch0012: glibc-fedora-linux-tcsetattr.patch
Patch0014: glibc-fedora-nptl-linklibc.patch
Patch0015: glibc-fedora-localedef.patch
Patch0019: glibc-fedora-nis-rh188246.patch
Patch0020: glibc-fedora-manual-dircategory.patch
Patch0024: glibc-fedora-locarchive.patch
Patch0025: glibc-fedora-streams-rh436349.patch
Patch0028: glibc-fedora-localedata-rh61908.patch
Patch0031: glibc-fedora-__libc_multiple_libcs.patch
Patch32: glibc-rpcgen.patch

# Allow applications to call pthread_atfork without libpthread.so.
Patch0046: glibc-rh1013801.patch

Patch0047: glibc-nscd-sysconfig.patch

# confstr _CS_PATH should only return /usr/bin on Fedora since /bin is just a
# symlink to it.
Patch0053: glibc-cs-path.patch

# Add C.UTF-8 locale into /usr/lib/locale/
Patch0059: glibc-c-utf8-locale.patch

##############################################################################
#
# Patches from upstream
#
##############################################################################

##############################################################################
#
# Patches submitted, but not yet approved upstream.
#
##############################################################################
#
# Each should be associated with a BZ.
# Obviously we're not there right now, but that's the goal
#

# http://sourceware.org/ml/libc-alpha/2012-12/msg00103.html
Patch2007: glibc-rh697421.patch

Patch2013: glibc-rh741105.patch

# Upstream BZ 14247
Patch2023: glibc-rh827510.patch

# Upstream BZ 14185
Patch2027: glibc-rh819430.patch

Patch2031: glibc-rh1070416.patch

Patch2037: glibc-rh1315108.patch
Patch2040: glibc-rh1452750-allocate_once.patch
Patch2041: glibc-rh1452750-libidn2.patch

##############################################################################
# End of glibc patches.
##############################################################################

##############################################################################
# Continued list of core "glibc" package information:
##############################################################################
Obsoletes: glibc-profile < 2.4
Provides: ldconfig

# The dynamic linker supports DT_GNU_HASH
Provides: rtld(GNU_HASH)
Requires: glibc-common = %{version}-%{release}

Requires(pre): basesystem

# This is for building auxiliary programs like memusage, nscd
# For initial glibc bootstraps it can be commented out
%if %{without bootstrap}
BuildRequires: gd-devel libpng-devel zlib-devel
%endif
%if %{with docs}
# Removing texinfo will cause check-safety.sh test to fail because it seems to
# trigger documentation generation based on dependencies.  We need to fix this
# upstream in some way that doesn't depend on generating docs to validate the
# texinfo.  I expect it's simply the wrong dependency for that target.
BuildRequires: texinfo >= 5.0
%endif
%if %{without bootstrap}
BuildRequires: libselinux-devel >= 1.33.4-3
%endif
BuildRequires: audit-libs-devel >= 1.1.3, sed >= 3.95, libcap-devel, gettext
# We need procps-ng (/bin/ps), util-linux (/bin/kill), and gawk (/bin/awk),
# but it is more flexible to require the actual programs and let rpm infer
# the packages. However, until bug 1259054 is widely fixed we avoid the
# following:
# BuildRequires: /bin/ps, /bin/kill, /bin/awk
# And use instead (which should be reverted some time in the future):
BuildRequires: procps-ng, util-linux, gawk
BuildRequires: systemtap-sdt-devel

%if %{with valgrind}
# Require valgrind for smoke testing the dynamic loader to make sure we
# have not broken valgrind.
BuildRequires: valgrind
%endif

# We use systemd rpm macros for nscd
BuildRequires: systemd

# We use python for the microbenchmarks and locale data regeneration from
# unicode sources (carried out manually). We choose python3 explicitly
# because it supports both use cases.
BuildRequires: python3

# This GCC version is needed for -fstack-clash-protection support.
BuildRequires: gcc >= 7.2.1-6
%define enablekernel 3.2
Conflicts: kernel < %{enablekernel}
%define target %{_target_cpu}-redhat-linux
%ifarch %{arm}
%define target %{_target_cpu}-redhat-linuxeabi
%endif
%ifarch %{power64}
%ifarch ppc64le
%define target ppc64le-redhat-linux
%else
%define target ppc64-redhat-linux
%endif
%endif

# GNU make 4.0 introduced the -O option.
BuildRequires: make >= 4.0

# The intl subsystem generates a parser using bison.
BuildRequires: bison >= 2.7

BuildRequires: binutils >= 2.25
# Earlier releases have broken support for IRELATIVE relocations
Conflicts: prelink < 0.4.2

%if 0%{?_enable_debug_packages}
BuildRequires: elfutils >= 0.72
BuildRequires: rpm >= 4.2-0.56
%endif

%if %{without bootstrap}
%if %{with testsuite}
# The testsuite builds static C++ binaries that require a C++ compiler,
# static C++ runtime from libstdc++-static, and lastly static glibc.
BuildRequires: gcc-c++
BuildRequires: libstdc++-static
# A configure check tests for the ability to create static C++ binaries
# before glibc is built and therefore we need a glibc-static for that
# check to pass even if we aren't going to use any of those objects to
# build the tests.
BuildRequires: glibc-static

# libidn2 (but not libidn2-devel) is needed for testing AI_IDN/NI_IDN.
BuildRequires: libidn2
%endif
%endif

# Filter out all GLIBC_PRIVATE symbols since they are internal to
# the package and should not be examined by any other tool.
%global __filter_GLIBC_PRIVATE 1

# For language packs we have glibc require a virtual dependency
# "glibc-langpack" wich gives us at least one installed langpack.
# If no langpack providing 'glibc-langpack' was installed you'd
# get all of them, and that would make the transition from a
# system without langpacks smoother (you'd get all the locales
# installed). You would then trim that list, and the trimmed list
# is preserved. One problem is you can't have "no" locales installed,
# in that case we offer a "glibc-minimal-langpack" sub-pakcage for
# this purpose.
Requires: glibc-langpack = %{version}-%{release}
Suggests: glibc-all-langpacks = %{version}-%{release}

%description
The glibc package contains standard libraries which are used by
multiple programs on the system. In order to save disk space and
memory, as well as to make upgrading easier, common system code is
kept in one place and shared between programs. This particular package
contains the most important sets of shared libraries: the standard C
library and the standard math library. Without these two libraries, a
Linux system will not function.

######################################################################
# libcrypt subpackage
######################################################################

%package -n libcrypt
Summary: Password hashing library
Requires: %{name}%{_isa} = %{version}-%{release}
Provides: libcrypt%{_isa}
Obsoletes: libcrypt-nss < 2.26.9000-33

%description -n libcrypt
This package provides the crypt function, which implements password
hashing.

%post -n libcrypt
/sbin/ldconfig

%postun -n libcrypt
/sbin/ldconfig

######################################################################
# libnsl subpackage
######################################################################

%package -n libnsl
Summary: Legacy support library for NIS
Requires: %{name}%{_isa} = %{version}-%{release}

%description -n libnsl
This package provides the legacy version of libnsl library, for
accessing NIS services.

This library is provided for backwards compatibility only;
applications should use libnsl2 instead to gain IPv6 support.

%post -n libnsl
/sbin/ldconfig

%postun -n libnsl
/sbin/ldconfig

######################################################################
# rpcgen subpackage
######################################################################

%package rpcgen
Summary: rpcgen compiler for Sun RPC protocol descriptions (glibc variant)
Provides: rpcgen
Provides: /usr/bin/rpcgen

%description rpcgen
This package provides the rpcgen program, for compiled .x protocol
description files into C source code.

##############################################################################
# glibc "devel" sub-package
##############################################################################
%package devel
Summary: Object files for development using standard C libraries.
Requires(pre): /sbin/install-info
Requires(pre): %{name}-headers
Requires: %{name}-headers = %{version}-%{release}
Requires: %{name} = %{version}-%{release}
Requires: libgcc%{_isa}
Requires: libcrypt%{_isa}

%description devel
The glibc-devel package contains the object files necessary
for developing programs which use the standard C libraries (which are
used by nearly all programs).  If you are developing programs which
will use the standard C libraries, your system needs to have these
standard object files available in order to create the
executables.

Install glibc-devel if you are going to develop programs which will
use the standard C libraries.

##############################################################################
# glibc "static" sub-package
##############################################################################
%package static
Summary: C library static libraries for -static linking.
Requires: %{name}-devel = %{version}-%{release}

%description static
The glibc-static package contains the C library static libraries
for -static linking.  You don't need these, unless you link statically,
which is highly discouraged.

##############################################################################
# glibc "headers" sub-package
# - The headers package includes all common headers that are shared amongst
#   the multilib builds. It was created to reduce the download size, and
#   thus avoid downloading one header package per multilib. The package is
#   identical both in content and file list, any difference is an error.
#   Files like gnu/stubs.h which have gnu/stubs-32.h (i686) and gnu/stubs-64.h
#   are included in glibc-headers, but the -32 and -64 files are in their
#   respective i686 and x86_64 devel packages.
##############################################################################
%package headers
Summary: Header files for development using standard C libraries.
Provides: %{name}-headers(%{_target_cpu})
Requires(pre): kernel-headers
Requires: kernel-headers >= 2.2.1, %{name} = %{version}-%{release}
BuildRequires: kernel-headers >= 3.2

%description headers
The glibc-headers package contains the header files necessary
for developing programs which use the standard C libraries (which are
used by nearly all programs).  If you are developing programs which
will use the standard C libraries, your system needs to have these
standard header files available in order to create the
executables.

Install glibc-headers if you are going to develop programs which will
use the standard C libraries.

##############################################################################
# glibc "common" sub-package
##############################################################################
%package common
Summary: Common binaries and locale data for glibc
Requires: %{name} = %{version}-%{release}
Requires: tzdata >= 2003a

%description common
The glibc-common package includes common binaries for the GNU libc
libraries, as well as national language (locale) support.

%package locale-source
Summary: The sources for the locales
Requires: %{name} = %{version}-%{release}
Requires: %{name}-common = %{version}-%{release}

%description locale-source
The sources for all locales provided in the language packs.
If you are building custom locales you will most likely use
these sources as the basis for your new locale.

%{lua:
-- Array of languages (ISO-639 codes).
local languages = {}
-- Dictionary from language codes (as in the languages array) to arrays
-- of regions.
local supplements = {}
do
   -- Parse the SUPPORTED file.  Eliminate duplicates.
   local lang_region_seen = {}
   for line in io.lines(rpm.expand("%{SOURCE11}")) do
      -- Match lines which contain a language (eo) or language/region
      -- (en_US) strings.
      local lang_region = string.match(line, "^([a-z][^/@.]+)")
      if lang_region ~= nil then
	 if lang_region_seen[lang_region] == nil then
	    lang_region_seen[lang_region] = true

	    -- Split language/region pair.
	    local lang, region = string.match(lang_region, "^(.+)_(.+)")
	    if lang == nil then
	       -- Region is missing, use only the language.
	       lang = lang_region
	    end
	    local suppl = supplements[lang]
	    if suppl == nil then
	       suppl = {}
	       supplements[lang] = suppl
	       -- New language not seen before.
	       languages[#languages + 1] = lang
	    end
	    if region ~= nil then
	       -- New region because of the check against
	       -- lang_region_seen above.
	       suppl[#suppl + 1] = region
	    end
	 end
      end
   end
   -- Sort for determinism.
   table.sort(languages)
   for _, supples in pairs(supplements) do
      table.sort(supplements)
   end
end

-- Compute the Supplements: list for a language, based on the regions.
local function compute_supplements(lang)
   result = "langpacks-" .. lang
   regions = supplements[lang]
   if regions ~= nil then
      for i = 1, #regions do
	 result = result .. " or langpacks-" .. lang .. "_" .. regions[i]
      end
   end
   return result
end

-- Emit the definition of a language pack package.
local function lang_package(lang)
   local suppl = compute_supplements(lang)
   print(rpm.expand([[

%package langpack-]]..lang..[[

Summary: Locale data for ]]..lang..[[

Provides: glibc-langpack = %{version}-%{release}
Requires: %{name} = %{version}-%{release}
Requires: %{name}-common = %{version}-%{release}
Supplements: (glibc and (]]..suppl..[[))
%description langpack-]]..lang..[[

The glibc-langpack-]]..lang..[[ package includes the basic information required
to support the ]]..lang..[[ language in your applications.
%ifnarch %{auxarches}
%files -f langpack-]]..lang..[[.filelist langpack-]]..lang..[[

%defattr(-,root,root)
%endif
]]))
end

for i = 1, #languages do
   lang_package(languages[i])
end
}

# The glibc-all-langpacks provides the virtual glibc-langpack,
# and thus satisfies glibc's requirement for installed locales.
# Users can add one more other langauge packs and then eventually
# uninstall all-langpacks to save space.
%package all-langpacks
Summary: All language packs for %{name}.
Requires: %{name} = %{version}-%{release}
Requires: %{name}-common = %{version}-%{release}
Provides: %{name}-langpack = %{version}-%{release}
%description all-langpacks

# No %files, this is an empty pacakge. The C/POSIX and
# C.UTF-8 files are already installed by glibc. We create
# minimal-langpack because the virtual provide of
# glibc-langpack needs at least one package installed
# to satisfy it. Given that no-locales installed is a valid
# use case we support it here with this package.
%package minimal-langpack
Summary: Minimal language packs for %{name}.
Provides: glibc-langpack = %{version}-%{release}
Requires: %{name} = %{version}-%{release}
Requires: %{name}-common = %{version}-%{release}
%description minimal-langpack
This is a Meta package that is used to install minimal language packs.
This package ensures you can use C, POSIX, or C.UTF-8 locales, but
nothing else. It is designed for assembling a minimal system.
%ifnarch %{auxarches}
%files minimal-langpack
%endif

##############################################################################
# glibc "nscd" sub-package
##############################################################################
%package -n nscd
Summary: A Name Service Caching Daemon (nscd).
Requires: %{name} = %{version}-%{release}
%if %{without bootstrap}
Requires: libselinux >= 1.17.10-1
%endif
Requires: audit-libs >= 1.1.3
Requires(pre): /usr/sbin/useradd, coreutils
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd, /usr/sbin/userdel

%description -n nscd
The nscd daemon caches name service lookups and can improve
performance with LDAP, and may help with DNS as well.

##############################################################################
# Subpackages for NSS modules except nss_files, nss_dns
##############################################################################

%package -n nss_db
Summary: Name Service Switch (NSS) module using hash-indexed files
Requires: %{name}%{_isa} = %{version}-%{release}

%description -n nss_db
The nss_db Name Service Switch module uses hash-indexed files in /var/db
to speed up user, group, service, host name, and other NSS-based lookups.

%package -n nss_hesiod
Summary: Name Service Switch (NSS) module using Hesiod
Requires: %{name}%{_isa} = %{version}-%{release}

%description -n nss_hesiod
The nss_hesiod Name Service Switch module uses the Domain Name System
(DNS) as a source for user, group, and service information, following
the Hesiod convention of Project Athena.

%package nss-devel
Summary: Development files for directly linking NSS service modules
Requires: nss_db%{_isa} = %{version}-%{release}
Requires: nss_hesiod%{_isa} = %{version}-%{release}

%description nss-devel
The glibc-nss-devel package contains the object files necessary to
compile applications and libraries which directly link against NSS
modules supplied by glibc.

This is a rare and special use case; regular development has to use
the glibc-devel package instead.

##############################################################################
# glibc "utils" sub-package
##############################################################################
%package utils
Summary: Development utilities from GNU C library
Requires: %{name} = %{version}-%{release}

%description utils
The glibc-utils package contains memusage, a memory usage profiler,
mtrace, a memory leak tracer and xtrace, a function call tracer
which can be helpful during program debugging.

If unsure if you need this, don't install this package.

##############################################################################
# glibc core "debuginfo" sub-package
##############################################################################
%if 0%{?_enable_debug_packages}
%define debug_package %{nil}
%define __debug_install_post %{nil}
%global __debug_package 1
# Disable thew new features that glibc packages don't use.
%undefine _debugsource_packages
%undefine _debuginfo_subpackages
%undefine _unique_debug_names
%undefine _unique_debug_srcs

%package debuginfo
Summary: Debug information for package %{name}
AutoReqProv: no
%ifarch %{debuginfocommonarches}
Requires: glibc-debuginfo-common = %{version}-%{release}
%else
%ifarch %{ix86} %{sparc}
Obsoletes: glibc-debuginfo-common
%endif
%endif

%description debuginfo
This package provides debug information for package %{name}.
Debug information is useful when developing applications that use this
package or when debugging this package.

This package also contains static standard C libraries with
debugging information.  You need this only if you want to step into
C library routines during debugging programs statically linked against
one or more of the standard C libraries.
To use this debugging information, you need to link binaries
with -static -L%{_prefix}/lib/debug%{_libdir} compiler options.

##############################################################################
# glibc common "debuginfo-common" sub-package
##############################################################################
%ifarch %{debuginfocommonarches}

%package debuginfo-common
Summary: Debug information for package %{name}
AutoReqProv: no

%description debuginfo-common
This package provides debug information for package %{name}.
Debug information is useful when developing applications that use this
package or when debugging this package.

%endif # %{debuginfocommonarches}
%endif # 0%{?_enable_debug_packages}

%if %{with benchtests}
%package benchtests
Summary: Benchmarking binaries and scripts for %{name}
%description benchtests
This package provides built benchmark binaries and scripts to run
microbenchmark tests on the system.
%endif

##############################################################################
# Prepare for the build.
##############################################################################
%prep
%setup -q -n %{glibcsrcdir}

# Patch order matters.
%patch0001 -p1
%patch2007 -p1
%patch0012 -p1
%patch2013 -p1
%patch0014 -p1
%patch0015 -p1
%patch0019 -p1
%patch0020 -p1
%patch2023 -p1
%patch0024 -p1
%patch0025 -p1
%patch2027 -p1
%patch0028 -p1
%patch0031 -p1
%patch32 -p1
%patch0046 -p1
%patch2031 -p1
%patch0047 -p1
%patch0053 -p1
%patch0059 -p1
%patch2037 -p1
%patch2040 -p1
%patch2041 -p1

##############################################################################
# %%prep - Additional prep required...
##############################################################################
# Make benchmark scripts executable
chmod +x benchtests/scripts/*.py scripts/pylint

# Remove all files generated from patching.
find . -type f -size 0 -o -name "*.orig" -exec rm -f {} \;

# Ensure timestamps on configure files are current to prevent
# regenerating them.
touch `find . -name configure`

# Ensure *-kw.h files are current to prevent regenerating them.
touch locale/programs/*-kw.h

# Verify that our copy of localedata/SUPPORTED matches the glibc
# version.
#
# The separate file copy is used by the language_list macro above.
# Patches or new upstream versions may change the list of locales,
# which changes the set of langpacks we need to build.  Verify the
# differences then update the copy of SUPPORTED.  This approach has
# two purposes: (a) avoid spurious changes to the set of langpacks,
# and (b) the language_list macro can use a fully patched-up version
# of the localedata/SUPPORTED file.
diff -u %{SOURCE11} localedata/SUPPORTED

##############################################################################
# Build glibc...
##############################################################################
%build
# Log system information
uname -a
LD_SHOW_AUXV=1 /bin/true
cat /proc/cpuinfo
cat /proc/meminfo
df

# We build using the native system compilers.
GCC=gcc
GXX=g++

##############################################################################
# %%build - x86 options.
##############################################################################
# On x86 we build for the specific target cpu rpm is using.
%ifarch %{ix86}
BuildFlags="-march=%{_target_cpu} -mtune=generic"
%endif
# We don't support building for i386. The generic i386 architecture lacks the
# atomic primitives required for NPTL support. However, when a user asks to
# build for i386 we interpret that as "for whatever works on x86" and we
# select i686. Thus we treat i386 as an alias for i686.
%ifarch i386 i686
BuildFlags="-march=i686 -mtune=generic"
%endif
%ifarch i486 i586
BuildFlags="$BuildFlags -mno-tls-direct-seg-refs"
%endif
%ifarch x86_64
BuildFlags="-mtune=generic"
%endif

##############################################################################
# %%build - s390 options.
##############################################################################
# The default is to tune for z13 (newer hardware), but build for zEC12.
%ifarch s390x
BuildFlags="-march=zEC12 -mtune=z13"
%endif
%ifarch s390
BuildFlags="-march=zEC12 -mtune=z13"
GCC="$GCC -m31"
GXX="$GXX -m31"
%endif

##############################################################################
# %%build - SPARC options.
##############################################################################
%ifarch sparc
BuildFlags="-fcall-used-g6"
GCC="$GCC -m32"
GXX="$GXX -m32"
%endif
%ifarch sparcv9
BuildFlags="-mcpu=ultrasparc -fcall-used-g6"
GCC="$GCC -m32"
GXX="$GXX -m32"
%endif
%ifarch sparcv9v
BuildFlags="-mcpu=niagara -fcall-used-g6"
GCC="$GCC -m32"
GXX="$GXX -m32"
%endif
%ifarch sparc64
BuildFlags="-mcpu=ultrasparc -mvis -fcall-used-g6"
GCC="$GCC -m64"
GXX="$GXX -m64"
%endif
%ifarch sparc64v
BuildFlags="-mcpu=niagara -mvis -fcall-used-g6"
GCC="$GCC -m64"
GXX="$GXX -m64"
%endif

##############################################################################
# %%build - POWER options.
##############################################################################
%ifarch %{power64}
BuildFlags=""
GCC="$GCC -m64"
GXX="$GXX -m64"
%ifarch ppc64p7
GCC="$GCC -mcpu=power7 -mtune=power7"
GXX="$GXX -mcpu=power7 -mtune=power7"
core_with_options="--with-cpu=power7"
%endif
%ifarch ppc64le
GCC="$GCC -mcpu=power8 -mtune=power8"
GXX="$GXX -mcpu=power8 -mtune=power8"
core_with_options="--with-cpu=power8"
%endif
%endif

##############################################################################
# %%build - MIPS options.
##############################################################################
%ifarch mips mipsel
BuildFlags="-march=mips32r2 -mfpxx"
%endif
%ifarch mips64 mips64el
# Without -mrelax-pic-calls ld.so segfaults when built with -O3
BuildFlags="-march=mips64r2 -mabi=64 -mrelax-pic-calls"
%endif

##############################################################################
# %%build - Generic options.
##############################################################################
EnableKernel="--enable-kernel=%{enablekernel}"
# Save the used compiler and options into the file "Gcc" for use later
# by %%install.
echo "$GCC" > Gcc

##############################################################################
# build()
#	Build glibc in `build-%{target}$1', passing the rest of the arguments
#	as CFLAGS to the build (not the same as configure CFLAGS). Several
#	global values are used to determine build flags, kernel version,
#	system tap support, etc.
##############################################################################
build()
{
	builddir=build-%{target}${1:+-$1}
	${1+shift}
	rm -rf $builddir
	mkdir $builddir
	pushd $builddir
	build_CFLAGS="$BuildFlags -g -O2 $*"
%ifnarch %{arm}
	build_CFLAGS="$build_CFLAGS -fstack-clash-protection"
%endif
	# Some configure checks can spuriously fail for some architectures if
	# unwind info is present
	configure_CFLAGS="$build_CFLAGS -fno-asynchronous-unwind-tables"
	../configure CC="$GCC" CXX="$GXX" CFLAGS="$configure_CFLAGS" \
		--prefix=%{_prefix} \
		--with-headers=%{_prefix}/include $EnableKernel \
		--enable-bind-now \
		--build=%{target} \
		--enable-stack-protector=strong \
%ifarch %{ix86} aarch64
		--enable-static-pie \
%endif
		--enable-tunables \
		--enable-systemtap \
		${core_with_options} \
%ifarch %{ix86}
		--disable-multi-arch \
%endif
%if %{without werror}
		--disable-werror \
%endif
		--disable-profile \
%if %{with bootstrap}
		--without-selinux \
%endif
		--disable-nss-crypt ||
		{ cat config.log; false; }

	make %{?_smp_mflags} -O -r CFLAGS="$build_CFLAGS"
	popd
}

##############################################################################
# Build glibc for the default set of options.
##############################################################################
build

##############################################################################
# Build glibc for power6:
# If we support building a power6 alternate runtime then built glibc again for
# power6.
# XXX: We build in a sub-shell for no apparent reason.
##############################################################################
%if %{buildpower6}
(
	platform=`LD_SHOW_AUXV=1 /bin/true | sed -n 's/^AT_PLATFORM:[[:blank:]]*//p'`
	if [ "$platform" != power6 ]; then
		mkdir -p power6emul/{lib,lib64}
		$GCC -shared -O2 -fpic -o power6emul/%{_lib}/power6emul.so %{SOURCE8} -Wl,-z,initfirst
%ifarch ppc64
		gcc -shared -nostdlib -O2 -fpic -m32 -o power6emul/lib/power6emul.so -xc - < /dev/null
%endif
		export LD_PRELOAD=`pwd`/power6emul/\$LIB/power6emul.so
	fi
	GCC="$GCC -mcpu=power6"
	GXX="$GXX -mcpu=power6"
	core_with_options="--with-cpu=power6"
	build power6
)
%endif # %{buildpower6}

%if %{buildpower7}
(
  GCC="$GCC -mcpu=power7 -mtune=power7"
  GXX="$GXX -mcpu=power7 -mtune=power7"
  core_with_options="--with-cpu=power7"
  build power7
)
%endif

%if %{buildpower8}
(
  GCC="$GCC -mcpu=power8 -mtune=power8"
  GXX="$GXX -mcpu=power8 -mtune=power8"
  core_with_options="--with-cpu=power8"
  build power8
)
%endif

##############################################################################
# Build the glibc post-upgrade program:
# We only build one of these with the default set of options. This program
# must be able to run on all hardware for the lowest common denomintor since
# we only build it once.
##############################################################################
pushd build-%{target}
$GCC -static -L. -Os -g %{SOURCE2} \
	-o glibc_post_upgrade.%{_target_cpu} \
	'-DLIBTLS="/%{_lib}/tls/"' \
	'-DGCONV_MODULES_DIR="%{_libdir}/gconv"' \
	'-DLD_SO_CONF="/etc/ld.so.conf"' \
	'-DICONVCONFIG="%{_sbindir}/iconvconfig.%{_target_cpu}"'
popd

##############################################################################
# Install glibc...
##############################################################################
%install

# Remove existing file lists.
find . -type f -name '*.filelist' -exec rm -rf {} \;

# Ensure the permissions of errlist.c do not change.  When the file is
# regenerated the Makefile sets the permissions to 444. We set it to 644
# to match what comes out of git. The tarball of the git archive won't have
# correct permissions because git doesn't track all of the permissions
# accurately (see git-cache-meta if you need that). We also set it to 644 to
# match pre-existing rpms. We do this *after* the build because the build
# might regenerate the file and set the permissions to 444.
chmod 644 sysdeps/gnu/errlist.c

# Reload compiler and build options that were used during %%build.
GCC=`cat Gcc`

# Build and install.
make -j1 install_root=$RPM_BUILD_ROOT install -C build-%{target}

# If we are not building an auxiliary arch then install all of the supported
# locales.
%ifnarch %{auxarches}
pushd build-%{target}
make %{?_smp_mflags} -O install_root=$RPM_BUILD_ROOT \
	install-locales -C ../localedata objdir=`pwd`
popd
%endif

# install_different:
#	Install all core libraries into DESTDIR/SUBDIR. Either the file is
#	installed as a copy or a symlink to the default install (if it is the
#	same). The path SUBDIR_UP is the prefix used to go from
#	DESTDIR/SUBDIR to the default installed libraries e.g.
#	ln -s SUBDIR_UP/foo.so DESTDIR/SUBDIR/foo.so.
#	When you call this function it is expected that you are in the root
#	of the build directory, and that the default build directory is:
#	"../build-%{target}" (relatively).
#	The primary use of this function is to install alternate runtimes
#	into the build directory and avoid duplicating this code for each
#	runtime.
install_different()
{
	local lib libbase libbaseso dlib
	local destdir="$1"
	local subdir="$2"
	local subdir_up="$3"
	local libdestdir="$destdir/$subdir"
	# All three arguments must be non-zero paths.
	if ! [ "$destdir" \
	       -a "$subdir" \
	       -a "$subdir_up" ]; then
		echo "One of the arguments to install_different was emtpy."
		exit 1
	fi
	# Create the destination directory and the multilib directory.
	mkdir -p "$destdir"
	mkdir -p "$libdestdir"
	# Walk all of the libraries we installed...
	for lib in libc math/libm nptl/libpthread rt/librt nptl_db/libthread_db
	do
		libbase=${lib#*/}
		# Take care that `libbaseso' has a * that needs expanding so
		# take care with quoting.
		libbaseso=$(basename $RPM_BUILD_ROOT/%{_lib}/${libbase}-*.so)
		# Only install if different from default build library.
		if cmp -s ${lib}.so ../build-%{target}/${lib}.so; then
			ln -sf "$subdir_up"/$libbaseso $libdestdir/$libbaseso
		else
			cp -a ${lib}.so $libdestdir/$libbaseso
		fi
		dlib=$libdestdir/$(basename $RPM_BUILD_ROOT/%{_lib}/${libbase}.so.*)
		ln -sf $libbaseso $dlib
	done
}

##############################################################################
# Install the power6 build files.
##############################################################################
%if %{buildpower6}
%define power6_subdir power6
%define power6_subdir_up ..
%define power6_legacy power6x
%define power6_legacy_up ..
pushd build-%{target}-power6
destdir=$RPM_BUILD_ROOT/%{_lib}
install_different "$destdir" "%{power6_subdir}" "%{power6_subdir_up}"
# Make a legacy /usr/lib[64]/power6x directory that is a symlink to the
# power6 runtime.
# XXX: When can we remove this? What is the history behind this?
mkdir -p ${destdir}/%{power6_legacy}
pushd ${destdir}/%{power6_legacy}
ln -sf %{power6_legacy_up}/%{power6_subdir}/*.so .
cp -a %{power6_legacy_up}/%{power6_subdir}/*.so.* .
popd
popd
%endif # %{buildpower6}

%if %{buildpower7}
%define power7_subdir power7
%define power7_subdir_up ..
pushd build-%{target}-power7
destdir=$RPM_BUILD_ROOT/%{_lib}
install_different "$destdir" "%{power7_subdir}" "%{power7_subdir_up}"
popd
%endif

%if %{buildpower8}
%define power8_subdir power8
%define power8_subdir_up ..
pushd build-%{target}-power8
destdir=$RPM_BUILD_ROOT/%{_lib}
install_different "$destdir" "%{power8_subdir}" "%{power8_subdir_up}"
popd
%endif

##############################################################################
# Remove the files we don't want to distribute
##############################################################################

# Remove the libNoVersion files.
# XXX: This looks like a bug in glibc that accidentally installed these
#      wrong files. We probably don't need this today.
rm -f $RPM_BUILD_ROOT%{_libdir}/libNoVersion*
rm -f $RPM_BUILD_ROOT/%{_lib}/libNoVersion*

# Remove the old nss modules.
rm -f ${RPM_BUILD_ROOT}/%{_lib}/libnss1-*
rm -f ${RPM_BUILD_ROOT}/%{_lib}/libnss-*.so.1

# This statically linked binary is no longer necessary in a world where
# the default Fedora install uses an initramfs, and further we have rpm-ostree
# which captures the whole userspace FS tree.
# Further, see https://github.com/projectatomic/rpm-ostree/pull/1173#issuecomment-355014583
rm -f ${RPM_BUILD_ROOT}/{usr/,}sbin/sln

##############################################################################
# Install info files
##############################################################################

%if %{with docs}
# Move the info files if glibc installed them into the wrong location.
if [ -d $RPM_BUILD_ROOT%{_prefix}/info -a "%{_infodir}" != "%{_prefix}/info" ]; then
  mkdir -p $RPM_BUILD_ROOT%{_infodir}
  mv -f $RPM_BUILD_ROOT%{_prefix}/info/* $RPM_BUILD_ROOT%{_infodir}
  rm -rf $RPM_BUILD_ROOT%{_prefix}/info
fi

# Compress all of the info files.
gzip -9nvf $RPM_BUILD_ROOT%{_infodir}/libc*

%else
rm -f $RPM_BUILD_ROOT%{_infodir}/dir
rm -f $RPM_BUILD_ROOT%{_infodir}/libc.info*
%endif

##############################################################################
# Create locale sub-package file lists
##############################################################################

%ifnarch %{auxarches}
olddir=`pwd`
pushd ${RPM_BUILD_ROOT}%{_prefix}/lib/locale
rm -f locale-archive
# Intentionally we do not pass --alias-file=, aliases will be added
# by build-locale-archive.
$olddir/build-%{target}/elf/ld.so \
        --library-path $olddir/build-%{target}/ \
        $olddir/build-%{target}/locale/localedef \
        --prefix ${RPM_BUILD_ROOT} --add-to-archive \
        *_*
# Setup the locale-archive template for use by glibc-all-langpacks.
mv locale-archive{,.tmpl}
# Create the file lists for the language specific sub-packages:
for i in eo *_*
do
    lang=${i%%_*}
    if [ ! -e langpack-${lang}.filelist ]; then
        echo "%dir %{_prefix}/lib/locale" >> langpack-${lang}.filelist
    fi
    echo "%dir  %{_prefix}/lib/locale/$i" >> langpack-${lang}.filelist
    echo "%{_prefix}/lib/locale/$i/*" >> langpack-${lang}.filelist
done
popd
pushd ${RPM_BUILD_ROOT}%{_prefix}/share/locale
for i in */LC_MESSAGES/libc.mo
do
    locale=${i%%%%/*}
    lang=${locale%%%%_*}
    echo "%lang($lang) %{_prefix}/share/locale/${i}" \
         >> ${RPM_BUILD_ROOT}%{_prefix}/lib/locale/langpack-${lang}.filelist
done
popd
mv  ${RPM_BUILD_ROOT}%{_prefix}/lib/locale/*.filelist .
%endif

##############################################################################
# Install configuration files for services
##############################################################################

install -p -m 644 %{SOURCE7} $RPM_BUILD_ROOT/etc/nsswitch.conf

%ifnarch %{auxarches}
# This is for ncsd - in glibc 2.2
install -m 644 nscd/nscd.conf $RPM_BUILD_ROOT/etc
mkdir -p $RPM_BUILD_ROOT%{_tmpfilesdir}
install -m 644 %{SOURCE4} %{buildroot}%{_tmpfilesdir}
mkdir -p $RPM_BUILD_ROOT/lib/systemd/system
install -m 644 nscd/nscd.service nscd/nscd.socket $RPM_BUILD_ROOT/lib/systemd/system
%endif

# Include ld.so.conf
echo 'include ld.so.conf.d/*.conf' > $RPM_BUILD_ROOT/etc/ld.so.conf
truncate -s 0 $RPM_BUILD_ROOT/etc/ld.so.cache
chmod 644 $RPM_BUILD_ROOT/etc/ld.so.conf
mkdir -p $RPM_BUILD_ROOT/etc/ld.so.conf.d
%ifnarch %{auxarches}
mkdir -p $RPM_BUILD_ROOT/etc/sysconfig
truncate -s 0 $RPM_BUILD_ROOT/etc/sysconfig/nscd
truncate -s 0 $RPM_BUILD_ROOT/etc/gai.conf
%endif

# Include %{_libdir}/gconv/gconv-modules.cache
truncate -s 0 $RPM_BUILD_ROOT%{_libdir}/gconv/gconv-modules.cache
chmod 644 $RPM_BUILD_ROOT%{_libdir}/gconv/gconv-modules.cache

##############################################################################
# Misc...
##############################################################################

# Install the upgrade program
install -m 700 build-%{target}/glibc_post_upgrade.%{_target_cpu} \
  $RPM_BUILD_ROOT%{_prefix}/sbin/glibc_post_upgrade.%{_target_cpu}

# Strip all of the installed object files.
strip -g $RPM_BUILD_ROOT%{_libdir}/*.o

# XXX: Ugly hack for buggy rpm. What bug? BZ? Is this fixed?
ln -f ${RPM_BUILD_ROOT}%{_sbindir}/iconvconfig{,.%{_target_cpu}}

##############################################################################
# Install debug copies of unstripped static libraries
# - This step must be last in order to capture any additional static
#   archives we might have added.
##############################################################################

# If we are building a debug package then copy all of the static archives
# into the debug directory to keep them as unstripped copies.
%if 0%{?_enable_debug_packages}
mkdir -p $RPM_BUILD_ROOT%{_prefix}/lib/debug%{_libdir}
cp -a $RPM_BUILD_ROOT%{_libdir}/*.a \
	$RPM_BUILD_ROOT%{_prefix}/lib/debug%{_libdir}/
rm -f $RPM_BUILD_ROOT%{_prefix}/lib/debug%{_libdir}/*_p.a
%endif

##############################################################################
# Build the file lists used for describing the package and subpackages.
##############################################################################
# There are several main file lists (and many more for
# the langpack sub-packages (langpack-${lang}.filelist)):
# * rpm.fileslist
#	- Master file list. Eventually, after removing files from this list
#	  we are left with the list of files for the glibc package.
# * common.filelist
#	- Contains the list of flies for the common subpackage.
# * utils.filelist
#	- Contains the list of files for the utils subpackage.
# * rpcgen.filelist
#	- Contains the list of files for the rpcgen subpackage.
# * nscd.filelist
#	- Contains the list of files for the nscd subpackage.
# * devel.filelist
#	- Contains the list of files for the devel subpackage.
# * headers.filelist
#	- Contains the list of files for the headers subpackage.
# * static.filelist
#	- Contains the list of files for the static subpackage.
# * libcrypt.filelist
#       - Contains the list of files for the libcrypt subpackage
# * libnsl.filelist
#       - Contains the list of files for the libnsl subpackage
# * nss_db.filelist, nss_hesiod.filelist
#       - File lists for nss_* NSS module subpackages.
# * nss-devel.filelist
#       - File list with the .so symbolic links for NSS packages.
# * debuginfo.filelist
#	- Contains the list of files for the glibc debuginfo package.
# * debuginfocommon.filelist
#	- Contains the list of files for the glibc common debuginfo package.
#

{
  find $RPM_BUILD_ROOT \( -type f -o -type l \) \
       \( \
	 -name etc -printf "%%%%config " -o \
	 -name gconv-modules \
	 -printf "%%%%verify(not md5 size mtime) %%%%config(noreplace) " -o \
	 -name gconv-modules.cache \
	 -printf "%%%%verify(not md5 size mtime) " \
	 , \
	 ! -path "*/lib/debug/*" -printf "/%%P\n" \)
  # Print all directories with a %%dir prefix.  We omit the info directory and
  # all directories in (and including) /usr/share/locale.
  find $RPM_BUILD_ROOT -type d \
       \( -path '*%{_prefix}/share/locale' -prune -o \
       \( -path '*%{_prefix}/share/*' \
%if %{with docs}
	! -path '*%{_infodir}' -o \
%endif
	  -path "*%{_prefix}/include/*" \
       \) -printf "%%%%dir /%%P\n" \)
} | {

  # primary filelist

  # Also remove the *.mo entries.  We will add them to the
  # language specific sub-packages.
  # libnss_ files go into subpackages related to NSS modules.
  # and .*/share/i18n/charmaps/.*), they go into the sub-package
  # "locale-source":
  sed -e '\,.*/share/locale/\([^/_]\+\).*/LC_MESSAGES/.*\.mo,d' \
      -e '\,.*/share/i18n/locales/.*,d' \
      -e '\,.*/share/i18n/charmaps/.*,d' \
      -e '\,/etc/\(localtime\|nsswitch.conf\|ld\.so\.conf\|ld\.so\.cache\|default\|rpc\|gai\.conf\),d' \
      -e '\,/%{_lib}/lib\(pcprofile\|memusage\)\.so,d' \
      -e '\,bin/\(memusage\|mtrace\|xtrace\|pcprofiledump\|rpcgen\),d'
} | sort > rpm.filelist

touch common.filelist

mkdir -p $RPM_BUILD_ROOT%{_libdir}
mv -f $RPM_BUILD_ROOT/%{_lib}/lib{pcprofile,memusage}.so $RPM_BUILD_ROOT%{_libdir}

# The xtrace and memusage scripts have hard-coded paths that need to be
# translated to a correct set of paths using the $LIB token which is
# dynamically translated by ld.so as the default lib directory.
for i in $RPM_BUILD_ROOT%{_prefix}/bin/{xtrace,memusage}; do
%if %{with bootstrap}
  test -w $i || continue
%endif
  sed -e 's~=/%{_lib}/libpcprofile.so~=%{_libdir}/libpcprofile.so~' \
      -e 's~=/%{_lib}/libmemusage.so~=%{_libdir}/libmemusage.so~' \
      -e 's~='\''/\\\$LIB/libpcprofile.so~='\''%{_prefix}/\\$LIB/libpcprofile.so~' \
      -e 's~='\''/\\\$LIB/libmemusage.so~='\''%{_prefix}/\\$LIB/libmemusage.so~' \
      -i $i
done

%if %{with docs}
# Put the info files into the devel file list.
grep '%{_infodir}' < rpm.filelist | grep -v '%{_infodir}/dir' > devel.filelist
%endif

# The glibc-headers package includes only common files which are identical
# across all multilib packages. We must keep gnu/stubs.h and gnu/lib-names.h
# in the glibc-headers package, but the -32, -64, -64-v1, and -64-v2 versions
# go into the development packages.
grep '%{_prefix}/include/gnu/stubs-.*\.h$' < rpm.filelist >> devel.filelist || :
grep '%{_prefix}/include/gnu/lib-names-.*\.h$' < rpm.filelist >> devel.filelist || :
# Put the include files into headers file list.
grep '%{_prefix}/include' < rpm.filelist \
  | egrep -v '%{_prefix}/include/gnu/stubs-.*\.h$' \
  | egrep -v '%{_prefix}/include/gnu/lib-names-.*\.h$' \
  > headers.filelist

# Remove partial (lib*_p.a) static libraries, include files, and info files from
# the core glibc package.
sed -i -e '\|%{_libdir}/lib.*_p.a|d' \
       -e '\|%{_prefix}/include|d' \
       -e '\|%{_infodir}|d' \
	rpm.filelist

# Put some static files into the devel package.
grep '%{_libdir}/lib.*\.a' < rpm.filelist \
  | grep '/lib\(\(c\|pthread\|nldbl\|mvec\)_nonshared\|g\|ieee\|mcheck\)\.a$' \
  >> devel.filelist

# Put the rest of the static files into the static package.
grep '%{_libdir}/lib.*\.a' < rpm.filelist \
  | grep -v '/lib\(\(c\|pthread\|nldbl\|mvec\)_nonshared\|g\|ieee\|mcheck\)\.a$' \
  > static.filelist

# Put all of the object files and *.so (not the versioned ones) into the
# devel package.
grep '%{_libdir}/.*\.o' < rpm.filelist >> devel.filelist
grep '%{_libdir}/lib.*\.so' < rpm.filelist >> devel.filelist

# Remove all of the static, object, unversioned DSOs, and nscd from the core
# glibc package.
sed -i -e '\|%{_libdir}/lib.*\.a|d' \
       -e '\|%{_libdir}/.*\.o|d' \
       -e '\|%{_libdir}/lib.*\.so|d' \
       -e '\|nscd|d' rpm.filelist

# All of the bin and certain sbin files go into the common package.
# We explicitly exclude certain sbin files that need to go into
# the core glibc package for use during upgrades.
grep '%{_prefix}/bin' < rpm.filelist >> common.filelist
grep '%{_prefix}/sbin/[^gi]' < rpm.filelist >> common.filelist
# All of the files under share go into the common package since
# they should be multilib-independent.
grep '%{_prefix}/share' < rpm.filelist | \
  grep -v -e '%{_prefix}/share/zoneinfo' -e '%%dir %{prefix}/share' \
       >> common.filelist

# Remove the bin, locale, some sbin, and share from the
# core glibc package. We cheat a bit and use the slightly dangerous
# /usr/sbin/[^gi] to match the inverse of the search that put the
# files into common.filelist. It's dangerous in that additional files
# that start with g, or i would get put into common.filelist and
# rpm.filelist.
sed -i -e '\|%{_prefix}/bin|d' \
       -e '\|%{_prefix}/lib/locale|d' \
       -e '\|%{_prefix}/sbin/[^gi]|d' \
       -e '\|%{_prefix}/share|d' rpm.filelist

# Add the binary to build locales to the common subpackage.
echo '%{_prefix}/sbin/build-locale-archive' >> common.filelist

# The nscd binary must go into the nscd subpackage.
echo '%{_prefix}/sbin/nscd' > nscd.filelist

# The memusage and pcprofile libraries are put back into the core
# glibc package even though they are only used by utils package
# scripts..
cat >> rpm.filelist <<EOF
%{_libdir}/libmemusage.so
%{_libdir}/libpcprofile.so
EOF

# Add the utils scripts and programs to the utils subpackage.
cat > utils.filelist <<EOF
%if %{without bootstrap}
%{_prefix}/bin/memusage
%{_prefix}/bin/memusagestat
%endif
%{_prefix}/bin/mtrace
%{_prefix}/bin/pcprofiledump
%{_prefix}/bin/xtrace
EOF

# rpcgen subpackage file list
cat > rpcgen.filelist <<EOF
%{_prefix}/bin/rpcgen
EOF

# Move the NSS-related files to the NSS subpackages.  Be careful not
# to pick up .debug files, and the -devel symbolic links.
for module in db compat hesiod files dns; do
  grep -E "/libnss_$module(\.so\.[0-9.]+|-[0-9.]+\.so)$" \
    rpm.filelist > nss_$module.filelist
done
# Symlinks go into the nss-devel package (instead of the main devel
# package).
grep '/libnss_[a-z]*\.so$' devel.filelist > nss-devel.filelist
# /var/db/Makefile goes into nss_db, remove the other files from
# the main and devel file list.
sed -i -e '\,/libnss_.*\.so[0-9.]*$,d' \
    -e '\,/var/db/Makefile,d' \
    rpm.filelist devel.filelist
# Restore the built-in NSS modules.
cat nss_files.filelist nss_dns.filelist nss_compat.filelist >> rpm.filelist

# Prepare the libcrypt-related file lists.
grep '/libcrypt-[0-9.]*.so$' rpm.filelist > libcrypt.filelist
test $(wc -l < libcrypt.filelist) -eq 1
sed -i -e '\,/libcrypt,d' rpm.filelist

# Prepare the libnsl-related file lists.
grep '/libnsl-[0-9.]*.so$' rpm.filelist > libnsl.filelist
test $(wc -l < libnsl.filelist) -eq 1
sed -i -e '\,/libnsl,d' rpm.filelist

# Remove the zoneinfo files
# XXX: Why isn't this don't earlier when we are removing files?
#      Won't this impact what is shipped?
rm -rf $RPM_BUILD_ROOT%{_prefix}/share/zoneinfo

# Make sure %config files have the same timestamp across multilib packages.
#
# XXX: Ideally ld.so.conf should have the timestamp of the spec file, but there
# doesn't seem to be any macro to give us that.  So we do the next best thing,
# which is to at least keep the timestamp consistent.  The choice of using
# glibc_post_upgrade.c is arbitrary.
touch -r %{SOURCE2} $RPM_BUILD_ROOT/etc/ld.so.conf
touch -r sunrpc/etc.rpc $RPM_BUILD_ROOT/etc/rpc

pushd build-%{target}
$GCC -Os -g -static -o build-locale-archive %{SOURCE1} \
	../build-%{target}/locale/locarchive.o \
	../build-%{target}/locale/md5.o \
	../build-%{target}/locale/record-status.o \
	-I. -DDATADIR=\"%{_datadir}\" -DPREFIX=\"%{_prefix}\" \
	-L../build-%{target} \
	-B../build-%{target}/csu/ -lc -lc_nonshared
install -m 700 build-locale-archive $RPM_BUILD_ROOT%{_prefix}/sbin/build-locale-archive
popd

# Lastly copy some additional documentation for the packages.
rm -rf documentation
mkdir documentation
cp crypt/README.ufc-crypt documentation/README.ufc-crypt
cp timezone/README documentation/README.timezone
cp posix/gai.conf documentation/

%ifarch s390x
# Compatibility symlink
mkdir -p $RPM_BUILD_ROOT/lib
ln -sf /%{_lib}/ld64.so.1 $RPM_BUILD_ROOT/lib/ld64.so.1
%endif

%if %{with benchtests}
# Build benchmark binaries.  Ignore the output of the benchmark runs.
pushd build-%{target}
make BENCH_DURATION=1 bench-build
popd

# Copy over benchmark binaries.
mkdir -p $RPM_BUILD_ROOT%{_prefix}/libexec/glibc-benchtests
cp $(find build-%{target}/benchtests -type f -executable) $RPM_BUILD_ROOT%{_prefix}/libexec/glibc-benchtests/

find build-%{target}/benchtests -type f -executable | while read b; do
	echo "%{_prefix}/libexec/glibc-benchtests/$(basename $b)"
done >> benchtests.filelist

# ... and the makefile.
for b in %{SOURCE9} %{SOURCE10}; do
	cp $b $RPM_BUILD_ROOT%{_prefix}/libexec/glibc-benchtests/
	echo "%{_prefix}/libexec/glibc-benchtests/$(basename $b)" >> benchtests.filelist
done

# .. and finally, the comparison scripts.
cp benchtests/scripts/benchout.schema.json $RPM_BUILD_ROOT%{_prefix}/libexec/glibc-benchtests/
cp benchtests/scripts/compare_bench.py $RPM_BUILD_ROOT%{_prefix}/libexec/glibc-benchtests/
cp benchtests/scripts/import_bench.py $RPM_BUILD_ROOT%{_prefix}/libexec/glibc-benchtests/
cp benchtests/scripts/validate_benchout.py $RPM_BUILD_ROOT%{_prefix}/libexec/glibc-benchtests/

echo "%{_prefix}/libexec/glibc-benchtests/benchout.schema.json" >> benchtests.filelist
echo "%{_prefix}/libexec/glibc-benchtests/compare_bench.py*" >> benchtests.filelist
echo "%{_prefix}/libexec/glibc-benchtests/import_bench.py*" >> benchtests.filelist
echo "%{_prefix}/libexec/glibc-benchtests/validate_benchout.py*" >> benchtests.filelist
%endif

###############################################################################
# Rebuild libpthread.a using --whole-archive to ensure all of libpthread
# is included in a static link. This prevents any problems when linking
# statically, using parts of libpthread, and other necessary parts not
# being included. Upstream has decided that this is the wrong approach to
# this problem and that the full set of dependencies should be resolved
# such that static linking works and produces the most minimally sized
# static application possible.
###############################################################################
pushd $RPM_BUILD_ROOT%{_prefix}/%{_lib}/
$GCC -r -nostdlib -o libpthread.o -Wl,--whole-archive ./libpthread.a
rm libpthread.a
ar rcs libpthread.a libpthread.o
rm libpthread.o
popd
###############################################################################

%if 0%{?_enable_debug_packages}

# The #line directives gperf generates do not give the proper
# file name relative to the build directory.
pushd locale
ln -s programs/*.gperf .
popd
pushd iconv
ln -s ../locale/programs/charmap-kw.gperf .
popd

# Print some diagnostic information in the builds about the
# getconf binaries.
# XXX: Why do we do this?
ls -l $RPM_BUILD_ROOT%{_prefix}/bin/getconf
ls -l $RPM_BUILD_ROOT%{_prefix}/libexec/getconf
eu-readelf -hS $RPM_BUILD_ROOT%{_prefix}/bin/getconf \
	$RPM_BUILD_ROOT%{_prefix}/libexec/getconf/*

find_debuginfo_args='--strict-build-id -g'
%ifarch %{debuginfocommonarches}
find_debuginfo_args="$find_debuginfo_args \
	-l common.filelist \
	-l utils.filelist \
	-l rpcgen.filelist \
	-l nscd.filelist \
	-p '.*/(sbin|libexec)/.*' \
	-o debuginfocommon.filelist \
	-l nss_db.filelist -l nss_hesiod.filelist \
	-l libcrypt.filelist -l libnsl.filelist \
	-l rpm.filelist \
%if %{with benchtests}
	-l benchtests.filelist
%endif
	"
%endif
/usr/lib/rpm/find-debuginfo.sh $find_debuginfo_args -o debuginfo.filelist

# List all of the *.a archives in the debug directory.
list_debug_archives()
{
	local dir=%{_prefix}/lib/debug%{_libdir}
	find $RPM_BUILD_ROOT$dir -name "*.a" -printf "$dir/%%P\n"
}

%ifarch %{debuginfocommonarches}

# Remove the source files from the common package debuginfo.
sed -i '\#^%{_prefix}/src/debug/#d' debuginfocommon.filelist

# Create a list of all of the source files we copied to the debug directory.
find $RPM_BUILD_ROOT%{_prefix}/src/debug \
     \( -type d -printf '%%%%dir ' \) , \
     -printf '%{_prefix}/src/debug/%%P\n' > debuginfocommon.sources

%ifarch %{biarcharches}

# Add the source files to the core debuginfo package.
cat debuginfocommon.sources >> debuginfo.filelist

%else

%ifarch %{ix86}
%define basearch i686
%endif
%ifarch sparc sparcv9
%define basearch sparc
%endif

# The auxarches get only these few source files.
auxarches_debugsources=\
'/(generic|linux|%{basearch}|nptl(_db)?)/|/%{glibcsrcdir}/build|/dl-osinfo\.h'

# Place the source files into the core debuginfo pakcage.
egrep "$auxarches_debugsources" debuginfocommon.sources >> debuginfo.filelist

# Remove the source files from the common debuginfo package.
egrep -v "$auxarches_debugsources" \
  debuginfocommon.sources >> debuginfocommon.filelist

%endif # %{biarcharches}

# Add the list of *.a archives in the debug directory to
# the common debuginfo package.
list_debug_archives >> debuginfocommon.filelist

# It happens that find-debuginfo.sh produces duplicate entries even
# though the inputs are unique. Therefore we sort and unique the
# entries in the debug file lists. This avoids the following warnings:
# ~~~
# Processing files: glibc-debuginfo-common-2.17.90-10.fc20.x86_64
# warning: File listed twice: /usr/lib/debug/usr/sbin/build-locale-archive.debug
# warning: File listed twice: /usr/lib/debug/usr/sbin/nscd.debug
# warning: File listed twice: /usr/lib/debug/usr/sbin/zdump.debug
# warning: File listed twice: /usr/lib/debug/usr/sbin/zic.debug
# ~~~
sort -u debuginfocommon.filelist > debuginfocommon2.filelist
mv debuginfocommon2.filelist debuginfocommon.filelist

%endif # %{debuginfocommonarches}

# Remove any duplicates output by a buggy find-debuginfo.sh.
sort -u debuginfo.filelist > debuginfo2.filelist
mv debuginfo2.filelist debuginfo.filelist

# Remove some common directories from the common package debuginfo so that we
# don't end up owning them.
exclude_common_dirs()
{
	exclude_dirs="%{_prefix}/src/debug"
	exclude_dirs="$exclude_dirs $(echo %{_prefix}/lib/debug{,/%{_lib},/bin,/sbin})"
	exclude_dirs="$exclude_dirs $(echo %{_prefix}/lib/debug%{_prefix}{,/%{_lib},/libexec,/bin,/sbin})"

	for d in $(echo $exclude_dirs | sed 's/ /\n/g'); do
		sed -i "\|^%%dir $d/\?$|d" $1
	done
}

%ifarch %{debuginfocommonarches}
exclude_common_dirs debuginfocommon.filelist
%endif
exclude_common_dirs debuginfo.filelist

%endif # 0%{?_enable_debug_packages}

%if %{with docs}
# Remove the `dir' info-heirarchy file which will be maintained
# by the system as it adds info files to the install.
rm -f $RPM_BUILD_ROOT%{_infodir}/dir
%endif

%ifarch %{auxarches}

# Delete files that we do not intended to ship with the auxarch.
echo Cutting down the list of unpackaged files
sed -e '/%%dir/d;/%%config/d;/%%verify/d;s/%%lang([^)]*) //;s#^/*##' \
	common.filelist devel.filelist static.filelist headers.filelist \
	utils.filelist nscd.filelist \
%ifarch %{debuginfocommonarches}
	debuginfocommon.filelist \
%endif
	| (cd $RPM_BUILD_ROOT; xargs --no-run-if-empty rm -f 2> /dev/null || :)

%else

mkdir -p $RPM_BUILD_ROOT/var/{db,run}/nscd
touch $RPM_BUILD_ROOT/var/{db,run}/nscd/{passwd,group,hosts,services}
touch $RPM_BUILD_ROOT/var/run/nscd/{socket,nscd.pid}

%endif # %{auxarches}

%ifnarch %{auxarches}
truncate -s 0 $RPM_BUILD_ROOT/%{_prefix}/lib/locale/locale-archive
%endif

mkdir -p $RPM_BUILD_ROOT/var/cache/ldconfig
truncate -s 0 $RPM_BUILD_ROOT/var/cache/ldconfig/aux-cache

##############################################################################
# Run the glibc testsuite
##############################################################################
%check
%if %{with testsuite}

# Run the glibc tests. If any tests fail to build we exit %check with
# an error, otherwise we print the test failure list and the failed
# test output and continue.  Write to standard error to avoid
# synchronization issues with make and shell tracing output if
# standard output and standard error are different pipes.
run_tests () {
  # This hides a test suite build failure, which should be fatal.  We
  # check "Summary of test results:" below to verify that all tests
  # were built and run.
  make %{?_smp_mflags} -O check |& tee rpmbuild.check.log >&2
  test -n tests.sum
  if ! grep -q '^Summary of test results:$' rpmbuild.check.log ; then
    echo "FAIL: test suite build of target: $(basename "$(pwd)")" >& 2
    exit 1
  fi
  set +x
  grep -v ^PASS: tests.sum > rpmbuild.tests.sum.not-passing || true
  if test -n rpmbuild.tests.sum.not-passing ; then
    echo ===================FAILED TESTS===================== >&2
    echo "Target: $(basename "$(pwd)")" >& 2
    cat rpmbuild.tests.sum.not-passing >&2
    while read failed_code failed_test ; do
      for suffix in out test-result ; do
        if test -e "$failed_test.$suffix"; then
	  echo >&2
          echo "=====$failed_code $failed_test.$suffix=====" >&2
          cat -- "$failed_test.$suffix" >&2
	  echo >&2
        fi
      done
    done <rpmbuild.tests.sum.not-passing
  fi

  # Unconditonally dump differences in the system call list.
  echo "* System call consistency checks:" >&2
  cat misc/tst-syscall-list.out >&2
  set -x
}

# Increase timeouts
export TIMEOUTFACTOR=16
parent=$$
echo ====================TESTING=========================
##############################################################################
# - Test the default runtime.
#	- Power 620 / 970 ISA for 64-bit POWER BE.
#	- POWER8 for 64-bit POWER LE.
#	- ??? for 64-bit x86_64
#	- ??? for 32-bit x86
#	- ??? for 64-bit AArch64
#	- ??? for 32-bit ARM
#	- zEC12 for 64-bit s390x
#	- ??? for 32-bit s390
##############################################################################
pushd build-%{target}
run_tests
popd

%if %{buildpower6}
echo ====================TESTING -mcpu=power6=============
##############################################################################
# - Test the 64-bit POWER6 BE runtimes.
##############################################################################
pushd build-%{target}-power6
if [ -d ../power6emul ]; then
    export LD_PRELOAD=`cd ../power6emul; pwd`/\$LIB/power6emul.so
fi
run_tests
popd
%endif

%if %{buildpower7}
echo ====================TESTING -mcpu=power7=============
##############################################################################
# - Test the 64-bit POWER7 BE runtimes.
##############################################################################
pushd build-%{target}-power7
run_tests
popd
%endif

%if %{buildpower8}
echo ====================TESTING -mcpu=power8=============
##############################################################################
# - Test the 64-bit POWER8 BE runtimes.
##############################################################################
pushd build-%{target}-power8
run_tests
popd
%endif

echo ====================TESTING END=====================
PLTCMD='/^Relocation section .*\(\.rela\?\.plt\|\.rela\.IA_64\.pltoff\)/,/^$/p'
echo ====================PLT RELOCS LD.SO================
readelf -Wr $RPM_BUILD_ROOT/%{_lib}/ld-*.so | sed -n -e "$PLTCMD"
echo ====================PLT RELOCS LIBC.SO==============
readelf -Wr $RPM_BUILD_ROOT/%{_lib}/libc-*.so | sed -n -e "$PLTCMD"
echo ====================PLT RELOCS END==================

# Finally, check if valgrind runs with the new glibc.
# We want to fail building if valgrind is not able to run with this glibc so
# that we can then coordinate with valgrind to get it fixed before we update
# glibc.
pushd build-%{target}

# Show the auxiliary vector as seen by the new library
# (even if we do not perform the valgrind test).
LD_SHOW_AUXV=1 elf/ld.so --library-path .:elf:nptl:dlfcn /bin/true

%if %{with valgrind}
elf/ld.so --library-path .:elf:nptl:dlfcn \
	/usr/bin/valgrind --error-exitcode=1 \
	elf/ld.so --library-path .:elf:nptl:dlfcn /usr/bin/true
%endif
popd

%endif # %{run_glibc_tests}


%pre -p <lua>
-- Check that the running kernel is new enough
required = '%{enablekernel}'
rel = posix.uname("%r")
if rpm.vercmp(rel, required) < 0 then
  error("FATAL: kernel too old", 0)
end

%post -p %{_prefix}/sbin/glibc_post_upgrade.%{_target_cpu}

%postun -p /sbin/ldconfig

%posttrans all-langpacks -e -p <lua>
-- If at the end of the transaction we are still installed
-- (have a template of non-zero size), then we rebuild the
-- locale cache (locale-archive) from the pre-populated
-- locale cache (locale-archive.tmpl) i.e. template.
if posix.stat("%{_prefix}/lib/locale/locale-archive.tmpl", "size") > 0 then
  pid = posix.fork()
  if pid == 0 then
    posix.exec("%{_prefix}/sbin/build-locale-archive", "--install-langs", "%%{_install_langs}")
  elseif pid > 0 then
    posix.wait(pid)
  end
end

%postun all-langpacks -p <lua>
-- In the postun we always remove the locale cache.
-- We are being uninstalled and if this is an upgrade
-- then the new packages template will be used to
-- recreate a new copy of the cache.
os.remove("%{_prefix}/lib/locale/locale-archive")

%if %{with docs}
%post devel
/sbin/install-info %{_infodir}/libc.info.gz %{_infodir}/dir > /dev/null 2>&1 || :
%endif

%pre headers
# this used to be a link and it is causing nightmares now
if [ -L %{_prefix}/include/scsi ] ; then
  rm -f %{_prefix}/include/scsi
fi

%if %{with docs}
%preun devel
if [ "$1" = 0 ]; then
  /sbin/install-info --delete %{_infodir}/libc.info.gz %{_infodir}/dir > /dev/null 2>&1 || :
fi
%endif

%post utils -p /sbin/ldconfig

%postun utils -p /sbin/ldconfig

%pre -n nscd
getent group nscd >/dev/null || /usr/sbin/groupadd -g 28 -r nscd
getent passwd nscd >/dev/null ||
  /usr/sbin/useradd -M -o -r -d / -s /sbin/nologin \
		    -c "NSCD Daemon" -u 28 -g nscd nscd

%post -n nscd
%systemd_post nscd.service

%preun -n nscd
%systemd_preun nscd.service

%postun -n nscd
if test $1 = 0; then
  /usr/sbin/userdel nscd > /dev/null 2>&1 || :
fi
%systemd_postun_with_restart nscd.service

%files -f rpm.filelist
%defattr(-,root,root)
%dir %{_prefix}/%{_lib}/audit
%if %{buildpower6}
%dir /%{_lib}/power6
%dir /%{_lib}/power6x
%endif
%if %{buildpower7}
%dir /%{_lib}/power7
%endif
%if %{buildpower8}
%dir /%{_lib}/power8
%endif
%ifarch s390x
/lib/ld64.so.1
%endif
%verify(not md5 size mtime) %config(noreplace) /etc/nsswitch.conf
%verify(not md5 size mtime) %config(noreplace) /etc/ld.so.conf
%verify(not md5 size mtime) %config(noreplace) /etc/rpc
%dir /etc/ld.so.conf.d
%dir %{_prefix}/libexec/getconf
%dir %{_libdir}/gconv
%dir %attr(0700,root,root) /var/cache/ldconfig
%attr(0600,root,root) %verify(not md5 size mtime) %ghost %config(missingok,noreplace) /var/cache/ldconfig/aux-cache
%attr(0644,root,root) %verify(not md5 size mtime) %ghost %config(missingok,noreplace) /etc/ld.so.cache
%attr(0644,root,root) %verify(not md5 size mtime) %ghost %config(missingok,noreplace) /etc/gai.conf
%doc README NEWS INSTALL elf/rtld-debugger-interface.txt
# If rpm doesn't support %license, then use %doc instead.
%{!?_licensedir:%global license %%doc}
%license COPYING COPYING.LIB LICENSES

%ifnarch %{auxarches}
%files -f common.filelist common
%defattr(-,root,root)
%dir %{_prefix}/lib/locale
%dir %{_prefix}/lib/locale/C.utf8
%{_prefix}/lib/locale/C.utf8/*
%doc documentation/README.timezone
%doc documentation/gai.conf

%files all-langpacks
%attr(0644,root,root) %verify(not md5 size mtime) %{_prefix}/lib/locale/locale-archive.tmpl
%attr(0644,root,root) %verify(not md5 size mtime mode) %ghost %config(missingok,noreplace) %{_prefix}/lib/locale/locale-archive

%files locale-source
%defattr(-,root,root)
%dir %{_prefix}/share/i18n/locales
%{_prefix}/share/i18n/locales/*
%dir %{_prefix}/share/i18n/charmaps
%{_prefix}/share/i18n/charmaps/*

%files -f devel.filelist devel
%defattr(-,root,root)

%files -f static.filelist static
%defattr(-,root,root)

%files -f headers.filelist headers
%defattr(-,root,root)

%files -f utils.filelist utils
%defattr(-,root,root)

%files -f rpcgen.filelist rpcgen
%defattr(-,root,root)

%files -f nscd.filelist -n nscd
%defattr(-,root,root)
%config(noreplace) /etc/nscd.conf
%dir %attr(0755,root,root) /var/run/nscd
%dir %attr(0755,root,root) /var/db/nscd
/lib/systemd/system/nscd.service
/lib/systemd/system/nscd.socket
%{_tmpfilesdir}/nscd.conf
%attr(0644,root,root) %verify(not md5 size mtime) %ghost %config(missingok,noreplace) /var/run/nscd/nscd.pid
%attr(0666,root,root) %verify(not md5 size mtime) %ghost %config(missingok,noreplace) /var/run/nscd/socket
%attr(0600,root,root) %verify(not md5 size mtime) %ghost %config(missingok,noreplace) /var/run/nscd/passwd
%attr(0600,root,root) %verify(not md5 size mtime) %ghost %config(missingok,noreplace) /var/run/nscd/group
%attr(0600,root,root) %verify(not md5 size mtime) %ghost %config(missingok,noreplace) /var/run/nscd/hosts
%attr(0600,root,root) %verify(not md5 size mtime) %ghost %config(missingok,noreplace) /var/run/nscd/services
%attr(0600,root,root) %verify(not md5 size mtime) %ghost %config(missingok,noreplace) /var/db/nscd/passwd
%attr(0600,root,root) %verify(not md5 size mtime) %ghost %config(missingok,noreplace) /var/db/nscd/group
%attr(0600,root,root) %verify(not md5 size mtime) %ghost %config(missingok,noreplace) /var/db/nscd/hosts
%attr(0600,root,root) %verify(not md5 size mtime) %ghost %config(missingok,noreplace) /var/db/nscd/services
%ghost %config(missingok,noreplace) /etc/sysconfig/nscd
%endif

%files -f nss_db.filelist -n nss_db
/var/db/Makefile
%files -f nss_hesiod.filelist -n nss_hesiod
%doc hesiod/README.hesiod
%files -f nss-devel.filelist nss-devel

%files -f libcrypt.filelist -n libcrypt
%doc documentation/README.ufc-crypt
%ghost /%{_lib}/libcrypt.so.1

%files -f libnsl.filelist -n libnsl
/%{_lib}/libnsl.so.1

%if 0%{?_enable_debug_packages}
%files debuginfo -f debuginfo.filelist
%defattr(-,root,root)
%ifarch %{debuginfocommonarches}
%ifnarch %{auxarches}
%files debuginfo-common -f debuginfocommon.filelist
%defattr(-,root,root)
%endif
%endif
%endif

%if %{with benchtests}
%files benchtests -f benchtests.filelist
%defattr(-,root,root)
%endif

%changelog
* Fri Jan 19 2018 Florian Weimer <fweimer@redhat.com> - 2.26.9000-43
- Enable static PIE support
- Remove add-on support (already gone upstream)
- Rework test suite status reporting
- Auto-sync with upstream branch master,
  commit 64f63cb4583ecc1ba16c7253aacc192b6d088511:
- malloc: Fix integer overflows in memalign and malloc functions (swbz#22343)
- x86-64: Properly align La_x86_64_retval to VEC_SIZE (swbz#22715)
- aarch64: Update bits/hwcap.h for Linux 4.15
- Add NT_ARM_SVE to elf.h

* Wed Jan 17 2018 Florian Weimer <fweimer@redhat.com> - 2.26.9000-42
- CVE-2017-14062, CVE-2016-6261, CVE-2016-6263:
  Use libidn2 for IDNA support (#1452750)

* Mon Jan 15 2018 Florian Weimer <fweimer@redhat.com> - 2.26.9000-41
- CVE-2018-1000001: Make getcwd fail if it cannot obtain an absolute path
  (#1533837)
- elf: Synchronize DF_1_* flags with binutils (#1439328)
- Auto-sync with upstream branch master,
  commit 860b0240a5645edd6490161de3f8d1d1f2786025:
- aarch64: fix static pie enabled libc when main is in a shared library
- malloc: Ensure that the consolidated fast chunk has a sane size

* Fri Jan 12 2018 Florian Weimer <fweimer@redhat.com> - 2.26.9000-40
- libnsl: Do not install libnsl.so, libnsl.a (#1531540)
- Use unversioned Supplements: for langpacks (#1490725)
- Auto-sync with upstream branch master,
  commit 9a08a366a7e7ddffe62113a9ffe5e50605ea0924:
- hu_HU locale: Avoid double space (swbz#22657)
- math: Make default libc_feholdsetround_noex_ctx use __feholdexcept
  (swbz#22702)

* Thu Jan 11 2018 Florian Weimer <fweimer@redhat.com> - 2.26.9000-39
- nptl: Open libgcc.so with RTLD_NOW during pthread_cancel (#1527887)
- Introduce libnsl subpackage and remove NIS headers (#1531540)
- Use versioned Obsoletes: for libcrypt-nss.
- Auto-sync with upstream branch master,
  commit 08c6e95234c60a5c2f37532d1111acf084f39345:
- nptl: Add tst-minstack-cancel, tst-minstack-exit (swbz#22636)
- math: ldbl-128ibm log1pl (-qNaN) spurious "invalid" exception (swbz#22693)

* Wed Jan 10 2018 Florian Weimer <fweimer@redhat.com> - 2.26.9000-38
- nptl: Fix stack guard size accounting (#1527887)
- Remove invalid Obsoletes: on glibc-header provides
- Require python3 instead of python during builds
- Auto-sync with upstream branch master,
  commit 09085ede12fb9650f286bdcd805609ae69f80618:
- math: ldbl-128ibm lrintl/lroundl missing "invalid" exceptions (swbz#22690)
- x86-64: Add sincosf with vector FMA

* Mon Jan  8 2018 Florian Weimer <fweimer@redhat.com> - 2.26.9000-37
- Add glibc-rpcgen subpackage, until the replacement is packaged (#1531540)

* Mon Jan 08 2018 Florian Weimer <fweimer@redhat.com> - 2.26.9000-36
- Auto-sync with upstream branch master,
  commit 579396ee082565ab5f42ff166a264891223b7b82:
- nptl: Add test for callee-saved register restore in pthread_exit
- getrlimit64: fix for 32-bit configurations with default version >= 2.2
- elf: Add linux-4.15 VDSO hash for RISC-V
- elf: Add RISC-V dynamic relocations to elf.h
- powerpc: Fix error message during relocation overflow
- prlimit: Replace old_rlimit RLIM64_INFINITY with RLIM_INFINITY (swbz#22678)

* Fri Jan 05 2018 Florian Weimer <fweimer@redhat.com> - 2.26.9000-35
- Remove sln (#1531546)
- Remove Sun RPC interfaces (#1531540)
- Rebuild with newer GCC to fix pthread_exit stack unwinding issue (#1529549)
- Auto-sync with upstream branch master,
  commit f1a844ac6389ea4e111afc019323ca982b5b027d:
- CVE-2017-16997: elf: Check for empty tokens before DST expansion (#1526866)
- i386: In makecontext, align the stack before calling exit (swbz#22667)
- x86, armhfp: sync sys/ptrace.h with Linux 4.15 (swbz#22433)
- elf: check for rpath emptiness before making a copy of it
- elf: remove redundant is_path argument
- elf: remove redundant code from is_dst
- elf: remove redundant code from _dl_dst_substitute
- scandir: fix wrong assumption about errno (swbz#17804)
- Deprecate external use of libio.h and _G_config.h

* Fri Dec 22 2017 Florian Weimer <fweimer@redhat.com> - 2.26.9000-34
- Auto-sync with upstream branch master,
  commit bad7a0c81f501fbbcc79af9eaa4b8254441c4a1f:
- copy_file_range: New function to copy file data
- nptl: Consolidate pthread_{timed,try}join{_np}
- nptl: Implement pthread_self in libc.so (swbz#22635)
- math: Provide a C++ version of iseqsig (swbz#22377)
- elf: remove redundant __libc_enable_secure check from fillin_rpath
- math: Avoid signed shift overflow in pow (swbz#21309)
- x86: Add feature_1 to tcbhead_t (swbz#22563)
- x86: Update cancel_jmp_buf to match __jmp_buf_tag (swbz#22563)
- ld.so: Examine GLRO to detect inactive loader (swbz#20204)
- nscd: Fix nscd readlink argument aliasing (swbz#22446)
- elf: do not substitute dst in $LD_LIBRARY_PATH twice (swbz#22627)
- ldconfig: set LC_COLLATE to C (swbz#22505)
- math: New generic sincosf
- powerpc: st{r,p}cpy optimization for aligned strings
- CVE-2017-1000409: Count in expanded path in _dl_init_path (#1524867)
- CVE-2017-1000408: Compute correct array size in _dl_init_paths (#1524867)
- x86-64: Remove sysdeps/x86_64/fpu/s_cosf.S
- aarch64: Improve strcmp unaligned performance

* Wed Dec 13 2017 Florian Weimer <fweimer@redhat.com> - 2.26.9000-33
- Remove power6 platform directory (#1522675)

* Wed Dec 13 2017 Florian Weimer <fweimer@redhat.com> - 2.26.9000-32
- Obsolete the libcrypt-nss subpackage (#1525396)
- armhfp: Disable -fstack-clash-protection due to GCC bug (#1522678)
- ppc64: Disable power6 multilib due to GCC bug (#1522675)
- Auto-sync with upstream branch master,
  commit 243b63337c2c02f30ec3a988ecc44bc0f6ffa0ad:
- libio: Free backup area when it not required (swbz#22415)
- math: Fix nextafter and nexttoward declaration (swbz#22593)
- math: New generic cosf
- powerpc: POWER8 memcpy optimization for cached memory
- x86-64: Add sinf with FMA
- x86-64: Remove sysdeps/x86_64/fpu/s_sinf.S
- math: Fix ctanh (0 + i NaN), ctanh (0 + i Inf) (swbz#22568)
- lt_LT locale: Base collation on copy "iso14651_t1" (swbz#22524)
- math: Add _Float32 function aliases
- math: Make cacosh (0 + iNaN) return NaN + i pi/2 (swbz#22561)
- hsb_DE locale: Base collation on copy "iso14651_t1" (swbz#22515)

* Wed Dec 06 2017 Florian Weimer <fweimer@redhat.com> - 2.26.9000-31
- Add elision tunables.  Drop related configure flag.  (#1383986)
- Auto-sync with upstream branch master,
  commit 37ac8e635a29810318f6d79902102e2e96b2b5bf:
- Linux: Implement interfaces for memory protection keys
- math: Add _Float64, _Float32x function aliases
- math: Use sign as double for reduced case in sinf
- math: fix sinf(NAN)
- math: s_sinf.c: Replace floor with simple casts
- et_EE locale: Base collation on iso14651_t1 (swbz#22517)
- tr_TR locale: Base collation on iso14651_t1 (swbz#22527)
- hr_HR locale: Avoid single code points for digraphs in LC_TIME (swbz#10580)
- S390: Fix backtrace in vdso functions

* Mon Dec 04 2017 Florian Weimer <fweimer@redhat.com> - 2.26.9000-30
- Add build dependency on bison
- Auto-sync with upstream branch master,
  commit 7863a7118112fe502e8020a0db0fa74fef281f29:
- math: New generic sinf (swbz#5997)
- is_IS locale: Base collation on iso14651_t1 (swbz#22519)
- intl: Improve reproducibility by using bison (swbz#22432)
- sr_RS, bs_BA locales: make collation rules the same as for hr_HR (wbz#22534)
- hr_HR locale: various updates (swbz#10580)
- x86: Make a space in jmpbuf for shadow stack pointer
- CVE-2017-17426: malloc: Fix integer overflow in tcache (swbz#22375)
- locale: make forward accent sorting the default in collating (swbz#17750)

* Wed Nov 29 2017 Florian Weimer <fweimer@redhat.com> - 2.26.9000-29
- Enable -fstack-clash-protection (#1512531)
- Auto-sync with upstream branch master,
  commit a55430cb0e261834ce7a4e118dd9e0f2b7fb14bc:
- elf: Properly compute offsets of note descriptor and next note (swbz#22370)
- cs_CZ locale: Base collation on iso14651_t1 (swbz#22336)
- Implement the mlock2 function
- Add _Float64x function aliases
- elf: Consolidate link map sorting
- pl_PL locale: Base collation on iso14651_t1 (swbz#22469)
- nss: Export nscd hash function as __nss_hash (swbz#22459)

* Thu Nov 23 2017 Florian Weimer <fweimer@redhat.com> - 2.26.9000-28
- Auto-sync with upstream branch master,
  commit cccb6d4e87053ed63c74aee063fa84eb63ebf7b8:
- sigwait can fail with EINTR (#1516394)
- Add memfd_create function
- resolv: Fix p_secstodate overflow handling (swbz#22463)
- resolv: Obsolete p_secstodate
- Avoid use of strlen in getlogin_r (swbz#22447)
- lv_LV locale: fix collation (swbz#15537)
- S390: Add cfi information for start routines in order to stop unwinding
- aarch64: Optimized memset for falkor

* Sun Nov 19 2017 Florian Weimer <fweimer@redhat.com> - 2.26.9000-27
- Auto-sync with upstream branch master,
  commit f6e965ee94b37289f64ecd3253021541f7c214c3:
- powerpc: AT_HWCAP2 bit PPC_FEATURE2_HTM_NO_SUSPEND
- aarch64: Add HWCAP_DCPOP bit
- ttyname, ttyname_r: Don't bail prematurely (swbz#22145)
- signal: Optimize sigrelse implementation
- inet: Check length of ifname in if_nametoindex (swbz#22442)
- malloc: Account for all heaps in an arena in malloc_info (swbz#22439)
- malloc: Add missing arena lock in malloc_info (swbz#22408)
- malloc: Use __builtin_tgmath in tgmath.h with GCC 8 (swbz#21660)
- locale: Replaced unicode sequences in the ASCII printable range
- resolv: More precise checks in res_hnok, res_dnok (swbz#22409, swbz#22412)
- resolv: ns_name_pton should report trailing \ as error (swbz#22413)
- locale: mfe_MU, miq_NI, an_ES, kab_DZ, om_ET: Escape / in d_fmt (swbz#22403)

* Tue Nov 07 2017 Florian Weimer <fweimer@redhat.com> - 2.26.9000-26
- Auto-sync with upstream branch master,
  commit 6b86036452b9ac47b4ee7789a50f2f37df7ecc4f:
- CVE-2017-15804: glob: Fix buffer overflow during GLOB_TILDE unescaping
- powerpc: Use latest string function optimization for internal function calls
- math: No _Float128 support for ppc64le -mlong-double-64 (swbz#22402)
- tpi_PG locale: Fix wrong d_fmt
- aarch64: Disable lazy symbol binding of TLSDESC
- tpi_PG locale: fix syntax error (swbz#22382)
- i586: Use conditional branches in strcpy.S (swbz#22353)
- ffsl, ffsll: Declare under __USE_MISC, not just __USE_GNU
- csb_PL locale: Fix abmon/mon for March (swbz#19485)
- locale: Various yesstr/nostr/yesexpr/noexpr fixes (swbz#15260, swbz#15261)
- localedef: Add --no-warnings/--warnings option
- powerpc: Replace lxvd2x/stxvd2x with lvx/stvx in P7's memcpy/memmove
- locale: Use ASCII as much as possible in LC_MESSAGES
- Add new locale yuw_PG (swbz#20952)
- malloc: Add single-threaded path to malloc/realloc/calloc/memalloc
- i386: Replace assembly versions of e_powf with generic e_powf.c
- i386: Replace assembly versions of e_log2f with generic e_log2f.c
- x86-64: Add powf with FMA
- x86-64: Add logf with FMA
- i386: Replace assembly versions of e_logf with generic e_logf.c
- i386: Replace assembly versions of e_exp2f with generic e_exp2f.c
- x86-64: Add exp2f with FMA
- i386: Replace assembly versions of e_expf with generic e_expf.c

* Sat Oct 21 2017 Florian Weimer <fweimer@redhat.com> - 2.26.9000-25
- Auto-sync with upstream branch master,
  commit 797ba44ba27521261f94cc521f1c2ca74f650147:
- math: Add bits/floatn.h defines for more _FloatN / _FloatNx types
- posix: Fix improper assert in Linux posix_spawn (swbz#22273)
- x86-64: Use fxsave/xsave/xsavec in _dl_runtime_resolve (swbz#21265)
- CVE-2017-15670: glob: Fix one-byte overflow (#1504807)
- malloc: Add single-threaded path to _int_free
- locale: Add new locale kab_DZ (swbz#18812)
- locale: Add new locale shn_MM (swbz#13605)

* Fri Oct 20 2017 Florian Weimer <fweimer@redhat.com> - 2.26.9000-24
- Use make -O to serialize make output
- Auto-sync with upstream branch master,
  commit 63b4baa44e8d22501c433c4093aa3310f91b6aa2:
- sysconf: Fix missing definition of UIO_MAXIOV on Linux (#1504165)
- Install correct bits/long-double.h for MIPS64 (swbz#22322)
- malloc: Fix deadlock in _int_free consistency check
- x86-64: Don't set GLRO(dl_platform) to NULL (swbz#22299)
- math: Add _Float128 function aliases
- locale: Add new locale mjw_IN (swbz#13994)
- aarch64: Rewrite elf_machine_load_address using _DYNAMIC symbol
- powerpc: fix check-before-set in SET_RESTORE_ROUND
- locale: Use U+202F as thousands separators in pl_PL locale (swbz#16777)
- math: Use __f128 to define FLT128_* constants in include/float.h for old GCC
- malloc: Improve malloc initialization sequence (swbz#22159)
- malloc: Use relaxed atomics for malloc have_fastchunks
- locale: New locale ca_ES@valencia (swbz#2522)
- math: Let signbit use the builtin in C++ mode with gcc < 6.x (swbz#22296)
- locale: Place monetary symbol in el_GR, el_CY after the amount (swbz#22019)

* Tue Oct 17 2017 Florian Weimer <fweimer@redhat.com> - 2.26.9000-23
- Switch to .9000 version numbers during development

* Tue Oct 17 2017 Florian Weimer <fweimer@redhat.com> - 2.26.90-22
- Auto-sync with upstream branch master,
  commit c38a4bfd596db2be2b9c1f96715bdc833eab760a:
- malloc: Use compat_symbol_reference in libmcheck (swbz#22050)

* Mon Oct 16 2017 Florian Weimer <fweimer@redhat.com> - 2.26.90-21
- Auto-sync with upstream branch master,
  commit 596f70134a8f11967c65c1d55a94a3a2718c731d:
- Silence -O3 -Wall warning in malloc/hooks.c with GCC 7 (swbz#22052)
- locale: No warning for non-symbolic character (swbz#22295)
- locale: Allow "" int_curr_Symbol (swbz#22294)
- locale: Fix localedef exit code (swbz#22292)
- nptl: Preserve error in setxid thread broadcast in coredumps (swbz#22153)
- powerpc: Avoid putting floating point values in memory (swbz#22189)
- powerpc: Fix the carry bit on mpn_[add|sub]_n on POWER7 (swbz#22142)
- Support profiling PIE (swbz#22284)

* Wed Oct 11 2017 Florian Weimer <fweimer@redhat.com> - 2.26.90-20
- Auto-sync with upstream branch master,
  commit d8425e116cdd954fea0c04c0f406179b5daebbb3:
- nss_files performance issue in multi mode (swbz#22078)
- Ensure C99 and C11 interfaces are available for C++ (swbz#21326)

* Mon Oct 09 2017 Florian Weimer <fweimer@redhat.com> - 2.26.90-19
- Move /var/db/Makefile to nss_db (#1498900)
- Auto-sync with upstream branch master,
  commit 645ac9aaf89e3311949828546df6334322f48933:
- openpty: use TIOCGPTPEER to open slave side fd

* Fri Oct 06 2017 Carlos O'Donell <carlos@systemhalted.org> - 2.26.90-18
- Auto-sync with upstream master,
  commit 1e26d35193efbb29239c710a4c46a64708643320.
- malloc: Fix tcache leak after thread destruction (swbz#22111)
- powerpc:  Fix IFUNC for memrchr.
- aarch64: Optimized implementation of memmove for Qualcomm Falkor
- Always do locking when iterating over list of streams (swbz#15142)
- abort: Do not flush stdio streams (swbz#15436)

* Wed Oct 04 2017 Florian Weimer <fweimer@redhat.com> - 2.26.90-17
- Move nss_compat to the main glibc package (#1400538)
- Auto-sync with upstream master,
  commit 11c4f5010c58029e73e656d5df4f8f42c9b8e877:
- crypt: Use NSPR header files in addition to NSS header files (#1489339)
- math: Fix yn(n,0) without SVID wrapper (swbz#22244)
- math: Fix log2(0) and log(10) in downward rounding (swbz#22243)
- math: Add C++ versions of iscanonical for ldbl-96, ldbl-128ibm (swbz#22235)
- powerpc: Optimize memrchr for power8
- Hide various internal functions (swbz#18822)

* Sat Sep 30 2017 Florian Weimer <fweimer@redhat.com> - 2.26.90-16
- Auto-sync with upstream master,
  commit 1e2bffd05c36a9be30d7092d6593a9e9aa009ada:
- Add IBM858 charset (#1416405)
- Update kernel version in syscall-names.list to 4.13
- Add Linux 4.13 constants to bits/fcntl-linux.h
- Add fcntl sealing interfaces from Linux 3.17 to bits/fcntl-linux.h
- math: New generic powf, log2f, logf
- Fix nearbyint arithmetic moved before feholdexcept (swbz#22225)
- Mark __dso_handle as hidden (swbz#18822)
- Skip PT_DYNAMIC segment with p_filesz == 0 (swbz#22101)
- glob now matches dangling symbolic links (swbz#866, swbz#22183)
- nscd: Release read lock after resetting timeout (swbz#22161)
- Avoid __MATH_TG in C++ mode with -Os for fpclassify (swbz#22146)
- Fix dlclose/exit race (swbz#22180)
- x86: Add SSE4.1 trunc, truncf (swbz#20142)
- Fix atexit/exit race (swbz#14333)
- Use execveat syscall in fexecve (swbz#22134)
- Enable unwind info in libc-start.c and backtrace.c
- powerpc: Avoid misaligned stores in memset
- powerpc: build some IFUNC math functions for libc and libm (swbz#21745)
- Removed redundant data (LC_TIME and LC_MESSAGES) for niu_NZ (swbz#22023)
- Fix LC_TELEPHONE for az_AZ (swbz#22112)
- x86: Add MathVec_Prefer_No_AVX512 to cpu-features (swbz#21967)
- x86: Add x86_64 to x86-64 HWCAP (swbz#22093)
- Finish change from “Bengali” to “Bangla” (swbz#14925)
- posix: fix glob bugs with long login names (swbz#1062)
- posix: Fix getpwnam_r usage (swbz#1062)
- posix: accept inode 0 is a valid inode number (swbz#19971)
- Remove redundant LC_TIME data in om_KE (swbz#22100)
- Remove remaining _HAVE_STRING_ARCH_* definitions (swbz#18858)
- resolv: Fix memory leak with OOM during resolv.conf parsing (swbz#22095)
- Add miq_NI locale for Miskito (swbz#20498)
- Fix bits/math-finite.h exp10 condition (swbz#22082)

* Mon Sep 04 2017 Florian Weimer <fweimer@redhat.com> - 2.26.90-15
- Auto-sync with upstream master,
  commit b38042f51430974642616a60afbbf96fd0b98659:
- Implement tmpfile with O_TMPFILE (swbz#21530)
- Obsolete pow10 functions
- math.h: Warn about an already-defined log macro

* Fri Sep 01 2017 Florian Weimer <fweimer@redhat.com> - 2.26.90-14
- Build glibc with -O2 (following the upstream default).
- Auto-sync with upstream master,
  commit f4a6be2582b8dfe8adfa68da3dd8decf566b3983:
- malloc: Abort on heap corruption, without a backtrace (swbz#21754)
- getaddrinfo: Return EAI_NODATA for gethostbyname2_r with NO_DATA (swbz#21922)
- getaddrinfo: Fix error handling in gethosts (swbz#21915) (swbz#21922)
- Place $(elf-objpfx)sofini.os last (swbz#22051)
- Various locale fixes (swbz#15332, swbz#22044)

* Wed Aug 30 2017 Florian Weimer <fweimer@redhat.com> - 2.26.90-13
- Drop glibc-rh952799.patch, applied upstream (#952799, swbz#22025)
- Auto-sync with upstream master,
  commit 5f9409b787c5758fc277f8d1baf7478b752b775d:
- Various locale fixes (swbz#22022, swbz#22038, swbz#21951, swbz#13805,
  swbz#21971, swbz#21959)
- MIPS/o32: Fix internal_syscall5/6/7 (swbz#21956)
- AArch64: Fix procfs.h not to expose stdint.h types
- iconv_open: Fix heap corruption on gconv_init failure (swbz#22026)
- iconv: Mangle __btowc_fct even without __init_fct (swbz#22025)
- Fix bits/math-finite.h _MSUF_ expansion namespace (swbz#22028)
- Provide a C++ version of iszero that does not use __MATH_TG (swbz#21930)

* Mon Aug 28 2017 Florian Weimer <fweimer@redhat.com> - 2.26.90-12
- Auto-sync with upstream master,
  commit 2dba5ce7b8115d6a2789bf279892263621088e74.

* Fri Aug 25 2017 Florian Weimer <fweimer@redhat.com> - 2.26.90-11
- Auto-sync with upstream master,
  commit 3d7b66f66cb223e899a7ebc0f4c20f13e711c9e0:
- string/stratcliff.c: Replace int with size_t (swbz#21982)
- Fix tgmath.h handling of complex integers (swbz#21684)

* Thu Aug 24 2017 Florian Weimer <fweimer@redhat.com> - 2.26.90-10
- Use an architecture-independent system call list (#1484729)
- Drop glibc-fedora-include-bits-ldbl.patch (#1482105)

* Tue Aug 22 2017 Florian Weimer <fweimer@redhat.com> - 2.26.90-9
- Auto-sync with upstream master,
  commit 80f91666fed71fa3dd5eb5618739147cc731bc89.

* Mon Aug 21 2017 Florian Weimer <fweimer@redhat.com> - 2.26.90-8
- Auto-sync with upstream master,
  commit a8410a5fc9305c316633a5a3033f3927b759be35:
- Obsolete matherr, _LIB_VERSION, libieee.a.

* Mon Aug 21 2017 Florian Weimer <fweimer@redhat.com> - 2.26.90-7
- Auto-sync with upstream master,
  commit 4504783c0f65b7074204c6126c6255ed89d6594e.

* Mon Aug 21 2017 Florian Weimer <fweimer@redhat.com> - 2.26.90-6
- Auto-sync with upstream master,
  commit b5889d25e9bf944a89fdd7bcabf3b6c6f6bb6f7c:
- assert: Support types without operator== (int) (#1483005)

* Mon Aug 21 2017 Florian Weimer <fweimer@redhat.com> - 2.26.90-5
- Auto-sync with upstream master,
  commit 2585d7b839559e665d5723734862fbe62264b25d:
- Do not use generic selection in C++ mode
- Do not use __builtin_types_compatible_p in C++ mode (#1481205)
- x86-64: Check FMA_Usable in ifunc-mathvec-avx2.h (swbz#21966)
- Various locale fixes (swbz#21750, swbz#21960, swbz#21959, swbz#19852)
- Fix sigval namespace (swbz#21944)
- x86-64: Optimize e_expf with FMA (swbz#21912)
- Adjust glibc-rh827510.patch.

* Wed Aug 16 2017 Tomasz Kłoczko <kloczek@fedoraproject.org> - 2.26-4
- Remove 'Buildroot' tag, 'Group' tag, and '%%clean' section, and don't
  remove the buildroot in '%%install', all per Fedora Packaging Guidelines
  (#1476839)

* Wed Aug 16 2017 Florian Weimer <fweimer@redhat.com> - 2.26.90-3
- Auto-sync with upstream master,
  commit 403143e1df85dadd374f304bd891be0cd7573e3b:
- x86-64: Align L(SP_RANGE)/L(SP_INF_0) to 8 bytes (swbz#21955)
- powerpc: Add values from Linux 4.8 to <elf.h>
- S390: Add new s390 platform z14.
- Various locale fixes (swbz#14925, swbz#20008, swbz#20482, swbz#12349
  swbz#19982, swbz#20756, swbz#20756, swbz#21836, swbz#17563, swbz#16905,
  swbz#21920, swbz#21854)
- NSS: Replace exported NSS lookup functions with stubs (swbz#21962)
- i386: Do not set internal_function
- assert: Suppress pedantic warning caused by statement expression (swbz#21242)
- powerpc: Restrict xssqrtqp operands to Vector Registers (swbz#21941)
- sys/ptrace.h: remove obsolete PTRACE_SEIZE_DEVEL constant (swbz#21928)
- Remove __qaddr_t, __long_double_t
- Fix uc_* namespace (swbz#21457)
- nss: Call __resolv_context_put before early return in get*_r (swbz#21932)
- aarch64: Optimized memcpy for Qualcomm Falkor processor
- manual: Document getcontext uc_stack value on Linux (swbz#759)
- i386: Add <startup.h> (swbz#21913)
- Don't use IFUNC resolver for longjmp or system in libpthread (swbz#21041)
- Fix XPG4.2 bits/sigaction.h namespace (swbz#21899)
- x86-64: Add FMA multiarch functions to libm
- i386: Support static PIE in start.S
- Compile tst-prelink.c without PIE (swbz#21815)
- x86-64: Use _dl_runtime_resolve_opt only with AVX512F (swbz#21871)
- x86: Remove __memset_zero_constant_len_parameter (swbz#21790)

* Wed Aug 16 2017 Florian Weimer <fweimer@redhat.com> - 2.26-2
- Disable multi-arch (IFUNC string functions) on i686 (#1471427)
- Remove nosegneg 32-bit Xen PV support libraries (#1482027)
- Adjust spec file to RPM changes

* Thu Aug 03 2017 Carlos O'Donell <carlos@systemhalted.org> - 2.26-1
- Update to released glibc 2.26.
- Auto-sync with upstream master,
  commit 2aad4b04ad7b17a2e6b0e66d2cb4bc559376617b.
- getaddrinfo: Release resolver context on error in gethosts (swbz#21885)

* Wed Aug 02 2017 Fedora Release Engineering <releng@fedoraproject.org> - 2.25.90-30.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Sat Jul 29 2017 Florian Weimer <fweimer@redhat.com> - 2.25.90-30
- Auto-sync with upstream master,
  commit 5920a4a624b1f4db310d1c44997b640e2a4653e5:
- mutex: Fix robust mutex lock acquire (swbz#21778)

* Fri Jul 28 2017 Florian Weimer <fweimer@redhat.com> - 2.25.90-29
- Auto-sync with upstream master,
  commit d95fcb2df478efbf4f8537ba898374043ac4561f:
- rwlock: Fix explicit hand-over (swbz#21298)
- tunables: Use direct syscall for access (swbz#21744)
- Avoid accessing corrupted stack from __stack_chk_fail (swbz#21752)
- Remove extra semicolons in struct pthread_mutex (swbz#21804)
- grp: Fix cast-after-dereference (another big-endian group merge issue)
- S390: fix sys/ptrace.h to make it includible again after asm/ptrace.h
- Don't add stack_chk_fail_local.o to libc.a (swbz#21740)
- i386: Test memmove_chk and memset_chk only in libc.so (swbz#21741)
- Add new locales az_IR, mai_NP (swbz#14172)
- Various locale improvements

* Thu Jul 27 2017 Carlos O'Donell <codonell@redhat.com> - 2.25.90-28
- Adjust to new rpm debuginfo generation (#1475009).

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 2.25.90-27.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Wed Jul 19 2017 Florian Weimer <fweimer@redhat.com> - 2.25.90-27
- Auto-sync with upstream master,
  commit 00d7a3777369bac3d8d44152dde2bb7381984ef6:
- aarch64: Fix out of bound array access in _dl_hwcap_string

* Mon Jul 17 2017 Florian Weimer <fweimer@redhat.com> - 2.25.90-26
- Drop glibc-rh1467518.patch in favor of upstream patch (#1467518)
- Auto-sync with upstream master,
  commit 91ac3a7d8474480685632cd25f844d3154c69fdf:
- Fix pointer alignment in NSS group merge result construction (#1471985)
- Various locale fixes

* Fri Jul 14 2017 Carlos O'Donell <carlos@systemhalted.org> - 2.25.90-25
- armv7hl: Drop 32-bit ARM build fix, already in upstream master.
- s390x: Apply glibc fix again, removing PTRACE_GETREGS etc. (#1469536).
- Auto-sync with upstream master,
  commit de895ddcd7fc45caeeeb0ae312311b8bd31d82c5:
- Added Fiji Hindi language locale for Fiji (swbz#21694).
- Added yesstr/nostr for nds_DE and nds_NL (swbz#21756).
- Added yesstr and nostr for Tigrinya (swbz#21759).
- Fix LC_MESSAGES and LC_ADDRESS for anp_IN (swbz#21760).
- Added yesstr/nostr and fix yesexpr for pap_AW and pap_CW (swbz#21757).
- Added Tongan language locale for Tonga (swbz#21728).
- [ARM] Fix ld.so crash when built using Binutils 2.29.
- Added yesstr and nostr for aa_ET (swbz#21768).
- New locale for bi_VU (swbz#21767).
- Disable single thread optimization for open_memstream

* Wed Jul 12 2017 Carlos O'Donell <carlos@redhat.com> - 2.25.90-24
- Fix IFUNC crash in early startup for ppc64le static binaries (#1467518).
- Enable building with BIND_NOW on ppc64le (#1467518).
- Fix 32-bit ARM builds in presence of new binutils.

* Wed Jul 12 2017 Florian Weimer <fweimer@redhat.com> - 2.25.90-23
- malloc: Tell GCC optimizers about MAX_FAST_SIZE in _int_malloc (#1470060)
- Auto-sync with upstream master,
  commit 30200427a99e5ddac9bad08599418d44d54aa9aa:
- Add per-thread cache to malloc
- Add Samoan language locale for Samoa
- Add Awajún / Aguaruna locale for Peru
- CVE-2010-3192: Avoid backtrace from __stack_chk_fail (swbz#12189)
- Add preadv2, writev2 RWF_NOWAIT flag (swbz#21738)
- Fix abday strings for ar_JO/ar_LB/ar_SY locales (swbz#21749)
- Fix abday strings for ar_SA locale (swbz#21748, swbz#19066)
- Set data_fmt for da_DK locale (swbz#17297)
- Add yesstr and nostr for the zh_HK locale (swbz#21733)
- Fix abday strings for the ksIN@devanagari locale (swbz#21743)
- Do not include _dl_resolv_conflicts in libc.a (swbz#21742)
- Test __memmove_chk, __memset_chk only in libc.so (swbz#21741)
- Add iI and eE to  yesexpr and noexpr respectively for ts_ZA locale
- Add yesstr/nostr for kw_GB locale (swbz#21734)
- Add yesstr and nostr for the ts_ZA locale (swbz#21727)
- Fix LC_NAME for hi_IN locale (swbz#21729)
- Add yesstr and nostr for the xh_ZA locale (swbz#21724)
- Add yesstr and nostr for the zh_CN locale (swbz#21723)
- Fix full weekday names for the ks_IN@devanagari locale (swbz#21721)
- Various fixes to Arabic locales after CLDR import 

* Tue Jul 11 2017 Florian Weimer <fweimer@redhat.com> - 2.25.90-22
- Reinstantiate stack_t cleanup (#1468904)
- s390x: Restore PTRACE_GETREGS etc. to get GCC to build (#1469536)

* Sun Jul  9 2017 Florian Weimer <fweimer@redhat.com> - 2.25.90-21
- Back out stack_t cleanup (#1468904)

* Thu Jul 06 2017 Florian Weimer <fweimer@redhat.com> - 2.25.90-20
- Auto-sync with upstream master,
  commit 031e519c95c069abe4e4c7c59e2b4b67efccdee5:
- x86-64: Align the stack in __tls_get_addr (#1440287)
- Add Tok-Pisin (tpi_PG) locale.
- Add missing yesstr/nostr for Pashto locale (swbz#21711)
- Add missing yesstr/nostr for Breton locale (swbz#21706)
- Single threaded stdio optimization
- sysconf: Use conservative default for _SC_NPROCESSORS_ONLN (swbz#21542)

* Tue Jul 04 2017 Florian Weimer <fweimer@redhat.com> - 2.25.90-19
- Auto-sync with upstream master,
  commit 4446a885f3aeb3a33b95c72bae1f115bed77f0cb.

* Tue Jul 04 2017 Florian Weimer <fweimer@redhat.com> - 2.25.90-18
- Auto-sync with upstream master,
  commit 89f6307c5d270ed4f11cee373031fa9f2222f2b9.

* Tue Jul  4 2017 Florian Weimer <fweimer@redhat.com> - 2.25.90-17
- Disable building with BIND_NOW on ppc64le (#1467518)

* Mon Jul 03 2017 Florian Weimer <fweimer@redhat.com> - 2.25.90-16
- Auto-sync with upstream master,
  commit e237357a5a0559dee92261f1914d1fa2cd43a1a8:
- Support an arbitrary number of search domains in the stub resolver (#168253)
- Detect and apply /etc/resolv.conf changes in libresolv (#1374239)
- Increase malloc alignment on i386 to 16 (swbz#21120)
- Make RES_ROTATE start with a random name server (swbz#19570)
- Fix tgmath.h totalorder, totalordermag return type (swbz#21687)
- Miscellaneous sys/ucontext.h namespace fixes (swbz#21457)
- Rename struct ucontext tag (swbz#21457)
- Call exit system call directly in clone (swbz#21512)
- powerpc64le: Enable float128
- getaddrinfo: Merge IPv6 addresses and IPv4 addresses (swbz#21295)
- Avoid .symver on common symbols (swbz#21666)
- inet_pton: Reject IPv6 addresses with many leading zeros (swbz#16637)

* Fri Jun 23 2017 Florian Weimer <fweimer@redhat.com> - 2.25.90-15
- Auto-sync with upstream master,
  commit 3ec7c02cc3e922b9364dc8cfd1d4546671b91003, fixing:
- memcmp-avx2-movbe.S incorrect results for lengths 2/3 (#1464403)

* Fri Jun 23 2017 Florian Weimer <fweimer@redhat.com> - 2.25.90-14
- Auto-sync with upstream master,
  commit 12f50337ae80672c393c2317d471d097ad92c492, changing:
- localedata: fur_IT: Fix spelling of Wednesday (Miercus)
- Update to Unicode 10.0.0
- inet: __inet6_scopeid_pton should accept node-local addresses (swbz#21657)

* Fri Jun 23 2017 Florian Weimer <fweimer@redhat.com> - 2.25.90-13
- Reenable valgrind on aarch64

* Thu Jun 22 2017 Florian Weimer <fweimer@redhat.com> - 2.25.90-12
- Log auxiliary vector during build

* Thu Jun 22 2017 Florian Weimer <fweimer@redhat.com> - 2.25.90-11
- Auto-sync with upstream master,
  commit 0a47d031e44f15236bcef8aeba80e737bd013c6f.

* Thu Jun 22 2017 Florian Weimer <fweimer@redhat.com> - 2.25.90-10
- Disable valgrind on aarch64

* Wed Jun 21 2017 Florian Weimer <fweimer@redhat.com> - 2.25.90-9
- Drop historic aarch64 TLS patches
- Drop workaround for GCC PR69537
- Auto-sync with upstream master,
  commit 9649350d2ee47fae00794d57e2526aa5d67d900e.

* Wed Jun 21 2017 Florian Weimer <fweimer@redhat.com> - 2.25.90-8
- Adjust build requirements for gcc, binutils, kernel-headers.
- Auto-sync with upstream master,
  commit 43e0ac24c836eed627a75ca932eb7e64698407c6, changing:
- Remove <xlocale.h>

* Mon Jun 19 2017 Florian Weimer <fweimer@redhat.com> - 2.25.90-7
- Drop glibc-Disable-buf-NULL-in-login-tst-ptsname.c, applied upstream.
- Auto-sync with upstream master,
  commit 37e9dc814636915afb88d0779e5e897e90e7b8c0, fixing:
- CVE-2017-1000366: Avoid large allocas in the dynamic linker (#1462820)
- wait3 namespace (swbz#21625)
- S390: Sync ptrace.h with kernel (swbz#21539)
- Another x86 sys/ucontext.h namespace issue (swbz#21457)
- siginterrupt namespace (swbz#21597)
- Signal stack namespace (swbz#21584)
- Define struct rusage in sys/wait.h when required (swbz#21575)
- S390: Fix build with gcc configured with --enable-default-pie (swbz#21537)
- Update timezone code from tzcode 2017b
- nptl: Invert the mmap/mprotect logic on allocated stacks (swbz#18988)
- PowerPC64 ELFv2 PPC64_OPT_LOCALENTRY
- Make copy of <bits/std_abs.h> from GCC (swbz#21573)
- localedata: ce_RU: update weekdays from CLDR (swbz#21207)
- localedata: Remove trailing spaces (swbz#20275)
- XPG4 bsd_signal namespace (swbz#21552)
- Correct collation rules for Malayalam (swbz#19922, swbz#19919)
- waitid namespace (swbz#21561)
- Condition signal.h inclusion in sys/wait.h (swbz#21560)
- ld.so: Consolidate 2 strtouls into _dl_strtoul (swbz#21528)
- tst-timezone race (swbz#14096)
- Define SIG_HOLD for XPG4 (swbz#21538)
- struct sigaltstack namespace (swbz#21517)
- sigevent namespace (swbz#21543)
- Add shim header for bits/syscall.h (swbz#21514)
- namespace issues in sys/ucontext.h (swbz#21457)
- posix: Implement preadv2 and pwritev2
- Various float128 and tunables improvements

* Tue Jun 06 2017 Stephen Gallagher <sgallagh@redhat.com> - 2.25.90-6
- Reduce libcrypt-nss dependency to 'Suggests:'

* Wed May 31 2017 Arjun Shankar <arjun.is@lostca.se> - 2.25.90-5
- Auto-sync with upstream master,
  commit cfa9bb61cd09c40def96f042a3123ec0093c4ad0.
- Fix sys/ucontext.h namespace from signal.h etc. inclusion (swbz#21457)
- Fix sigstack namespace (swbz#21511)

* Wed May 31 2017 Arjun Shankar <arjun.is@lostca.se> - 2.25.90-4
- Disable the NULL buffer test in login/tst-ptsname.c. It leads to a build
  failure during 'make check'. A permanent solution is being discussed
  upstream.

* Tue May 23 2017 Arjun Shankar <arjun.is@lostca.se> - 2.25.90-3
- Auto-sync with upstream master,
  commit 231a59ce2c5719d2d77752c21092960e28837b4a.
- Add el_GR@euro support (swbz#20686)
- Set dl_platform and dl_hwcap from CPU features (swbz#21391)
- Use __glibc_reserved convention in mcontext, sigcontext (swbz#21457)
- Fix signal.h bsd_signal namespace (swbz#21445)
- Fix network headers stdint.h namespace (swbz#21455)
- resolv: Use RES_DFLRETRY consistently (swbz#21474)
- Condition some sys/ucontext.h contents on __USE_MISC (swbz#21457)
- Consolidate Linux read syscall (swbz#21428)
- fork: Remove bogus parent PID assertions (swbz#21386)
- Reduce value of LD_HWCAP_MASK for tst-env-setuid test case (swbz#21502)
- libio: Avoid dup already opened file descriptor (swbz#21393)

* Mon May 01 2017 Carlos O'Donell <carlos@systemhalted.org> - 2.25.90-2
- Auto-sync with upstream master,
  commit 25e39b4229fb365a605dc4c8f5d6426a77bc08a6.
- logbl for POWER7 return incorrect results (swbz#21280)
- sys/socket.h uio.h namespace (swbz#21426)
- Support POSIX_SPAWN_SETSID (swbz#21340)
- Document how to provide a malloc replacement (swbz#20424)
- Verify that all internal sockets opened with SOCK_CLOEXEC (swbz#15722)
- Use AVX2 memcpy/memset on Skylake server (swbz#21396)
- unwind-dw2-fde deadlock when using AddressSanitizer (swbz#21357)
- resolv: Reduce advertised EDNS0 buffer size to guard against
  fragmentation attacks (swbz#21361)
- mmap64 silently truncates large offset values (swbz#21270)
- _dl_map_segments does not test for __mprotect failures consistently
  (swbz#20831)

* Thu Mar 02 2017 Florian Weimer <fweimer@redhat.com> - 2.25.90-1
- Switch back to upstream master branch.
- Drop Unicode 9 patch, merged upstream.
- Auto-sync with upstream master,
  commit a10e9c4e53fc652b79abf838f7f837589d2c84db, fixing:
- Build all DSOs with BIND_NOW (#1406731)

* Wed Mar  1 2017 Jakub Hrozek <jhrozek@redhat.com> - 2.25-3
- NSS: Prefer sss service for passwd, group databases (#1427646)

* Tue Feb 28 2017 Florian Weimer <fweimer@redhat.com> - 2.25-2
- Auto-sync with upstream release/2.25/master,
  commit 93cf93e06ce123439e41d3d62790601c313134cb, fixing:
- sunrpc: Improvements for UDP client timeout handling (#1346406)
- sunrpc: Avoid use-after-free read access in clntudp_call (swbz#21115)
- Fix getting tunable values on big-endian (swbz#21109)

* Wed Feb 08 2017 Carlos O'Donell <carlos@redhat.com> - 2.25-1
- Update to final released glibc 2.25.
