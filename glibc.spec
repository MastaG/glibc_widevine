%define glibcdate 20070918T1931
%define glibcname glibc
%define glibcsrcdir glibc-20070918T1931
%define glibc_release_tarballs 0
%define glibcversion 2.6.90
%define glibcrelease 14
%define run_glibc_tests 1
%define auxarches i586 i686 athlon sparcv9v sparc64v alphaev6
%define xenarches i686 athlon
%ifarch %{xenarches}
%define buildxen 1
%define xenpackage 0
%else
%define buildxen 0
%define xenpackage 0
%endif
%ifarch ppc ppc64
%define buildpower6 1
%else
%define buildpower6 0
%endif
%define rtkaioarches %{ix86} x86_64 ia64 ppc ppc64 s390 s390x
%define debuginfocommonarches %{ix86} alpha alphaev6 sparc sparcv9 sparcv9v sparc64 sparc64v
%define _unpackaged_files_terminate_build 0
Summary: The GNU libc libraries.
Name: glibc
Version: %{glibcversion}
Release: %{glibcrelease}
# GPLv2+ is used in a bunch of programs, LGPLv2+ is used for libraries.
# Things that are linked directly into dynamically linked programs
# and shared libraries (e.g. crt files, lib*_nonshared.a) have an additional
# exception which allows linking it into any kind of programs or shared
# libraries without restrictions.
License: LGPLv2+ and LGPLv2+ with exceptions and GPLv2+
Group: System Environment/Libraries
Source0: %{glibcsrcdir}.tar.bz2
%if %{glibc_release_tarballs}
Source1: %(echo %{glibcsrcdir} | sed s/glibc-/glibc-linuxthreads-/).tar.bz2
Source2: %(echo %{glibcsrcdir} | sed s/glibc-/glibc-libidn-/).tar.bz2
%define glibc_release_unpack -a1 -a2
%endif
Source3: %{glibcname}-fedora-%{glibcdate}.tar.bz2
Patch0: %{glibcname}-fedora.patch
Patch1: %{name}-ia64-lib64.patch
Buildroot: %{_tmppath}/glibc-%{PACKAGE_VERSION}-root
Obsoletes: zoneinfo, libc-static, libc-devel, libc-profile, libc-headers,
Obsoletes: gencat, locale, ldconfig, locale-ja, glibc-profile
Provides: ldconfig
# The dynamic linker supports DT_GNU_HASH
Provides: rtld(GNU_HASH)
Autoreq: false
Requires: glibc-common = %{version}-%{release}
%ifarch sparc
Obsoletes: libc
%endif
# Require libgcc in case some program calls pthread_cancel in its %%post
Prereq: basesystem, libgcc
# This is for building auxiliary programs like memusage, nscd
# For initial glibc bootstraps it can be commented out
BuildPreReq: gd-devel libpng-devel zlib-devel texinfo, libselinux-devel >= 1.33.4-3
BuildPreReq: audit-libs-devel >= 1.1.3, sed >= 3.95, libcap-devel, gettext
BuildPreReq: /bin/ps, /bin/kill, /bin/awk
# This is to ensure that __frame_state_for is exported by glibc
# will be compatible with egcs 1.x.y
BuildPreReq: gcc >= 3.2
Conflicts: rpm <= 4.0-0.65
Conflicts: glibc-devel < 2.2.3
Conflicts: gcc4 <= 4.0.0-0.6
%ifarch x86_64 %{ix86}
# Need gdb that understands DW_CFA_val_expression
Conflicts: gdb < 6.3.0.0-1.111
%endif
# Earlier shadow-utils packages had too restrictive permissions on
# /etc/default
Conflicts: shadow-utils < 2:4.0.3-20
Conflicts: nscd < 2.3.3-52
Conflicts: kernel < 2.6.9
%define enablekernel 2.6.9
%ifarch i386
%define nptl_target_cpu i486
%else
%define nptl_target_cpu %{_target_cpu}
%endif
# Need AS_NEEDED directive
# Need --hash-style=* support
BuildRequires: binutils >= 2.17.50.0.2-5
BuildRequires: gcc >= 3.2.1-5
%ifarch ppc s390 s390x
BuildRequires: gcc >= 4.1.0-0.17
%endif
%if "%{_enable_debug_packages}" == "1"
BuildPreReq: elfutils >= 0.72
BuildPreReq: rpm >= 4.2-0.56
%endif
%define __find_provides %{_builddir}/%{glibcsrcdir}/find_provides.sh
%define _filter_GLIBC_PRIVATE 1

%description
The glibc package contains standard libraries which are used by
multiple programs on the system. In order to save disk space and
memory, as well as to make upgrading easier, common system code is
kept in one place and shared between programs. This particular package
contains the most important sets of shared libraries: the standard C
library and the standard math library. Without these two libraries, a
Linux system will not function.

%if %{xenpackage}
%package xen
Summary: The GNU libc libraries (optimized for running under Xen)
Group: System Environment/Libraries
Requires: glibc = %{version}-%{release}, glibc-utils = %{version}-%{release}

%description xen
The standard glibc package is optimized for native kernels and does not
perform as well under the Xen hypervisor.  This package provides alternative
library binaries that will be selected instead when running under Xen.

Install glibc-xen if you might run your system under the Xen hypervisor.
%endif

%package devel
Summary: Object files for development using standard C libraries.
Group: Development/Libraries
Conflicts: texinfo < 3.11
# Need AS_NEEDED directive
Conflicts: binutils < 2.15.94.0.2-1
Prereq: /sbin/install-info
Obsoletes: libc-debug, libc-headers, libc-devel, linuxthreads-devel
Obsoletes: glibc-debug, nptl-devel
Prereq: %{name}-headers
Requires: %{name}-headers = %{version}-%{release}, %{name} = %{version}-%{release}
%ifarch %{ix86}
# Earlier gcc's had atexit reference in crtendS.o, which does not
# work with this glibc where atexit is in libc_nonshared.a
Conflicts: gcc < 2.96-79
%endif
Autoreq: true

%description devel
The glibc-devel package contains the object files necessary
for developing programs which use the standard C libraries (which are
used by nearly all programs).  If you are developing programs which
will use the standard C libraries, your system needs to have these
standard object files available in order to create the
executables.

Install glibc-devel if you are going to develop programs which will
use the standard C libraries.

%package headers
Summary: Header files for development using standard C libraries.
Group: Development/Libraries
Provides: %{name}-headers(%{_target_cpu})
%ifarch x86_64
# If both -m32 and -m64 is to be supported on AMD64, x86_64 glibc-headers
# have to be installed, not i386 ones.
Obsoletes: %{name}-headers(i386)
%endif
Obsoletes: libc-debug, libc-headers, libc-devel
Prereq: kernel-headers
Requires: kernel-headers >= 2.2.1, %{name} = %{version}-%{release}
BuildRequires: kernel-headers >= 2.6.22
Autoreq: true

%description headers
The glibc-headers package contains the header files necessary
for developing programs which use the standard C libraries (which are
used by nearly all programs).  If you are developing programs which
will use the standard C libraries, your system needs to have these
standard header files available in order to create the
executables.

Install glibc-headers if you are going to develop programs which will
use the standard C libraries.

%package common
Summary: Common binaries and locale data for glibc
Conflicts: %{name} < %{version}
Conflicts: %{name} > %{version}
Autoreq: false
Requires: tzdata >= 2003a
Group: System Environment/Base

%description common
The glibc-common package includes common binaries for the GNU libc
libraries, as well as national language (locale) support.

%package -n nscd
Summary: A Name Service Caching Daemon (nscd).
Group: System Environment/Daemons
Conflicts: kernel < 2.2.0
Requires: libselinux >= 1.17.10-1, audit-libs >= 1.1.3
Conflicts: selinux-policy-targeted < 1.17.30-2.2
Prereq: /sbin/chkconfig, /usr/sbin/useradd, /usr/sbin/userdel, sh-utils
Autoreq: true

%description -n nscd
Nscd caches name service lookups and can dramatically improve
performance with NIS+, and may help with DNS as well.

%package utils
Summary: Development utilities from GNU C library
Group: Development/Tools
Requires: glibc = %{version}-%{release}

%description utils
The glibc-utils package contains memusage, a memory usage profiler,
mtrace, a memory leak tracer and xtrace, a function call tracer
which can be helpful during program debugging.

If unsure if you need this, don't install this package.

%if "%{_enable_debug_packages}" == "1"
%define debug_package %{nil}

%package debuginfo
Summary: Debug information for package %{name}
Group: Development/Debug
AutoReqProv: no
%ifarch %{debuginfocommonarches}
Requires: glibc-debuginfo-common = %{version}-%{release}
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
with -static -L%{_prefix}/lib/debug%{_prefix}/%{_lib} compiler options.

%ifarch %{debuginfocommonarches}

%package debuginfo-common
Summary: Debug information for package %{name}
Group: Development/Debug
AutoReqProv: no

%description debuginfo-common
This package provides debug information for package %{name}.
Debug information is useful when developing applications that use this
package or when debugging this package.

%endif
%endif

%prep
%setup -q -n %{glibcsrcdir} %{glibc_release_unpack} -a3
%patch0 -E -p1
%ifarch ia64
%if "%{_lib}" == "lib64"
%patch1 -p1
%endif
%endif

# A lot of programs still misuse memcpy when they have to use
# memmove. The memcpy implementation below is not tolerant at
# all.
rm -f sysdeps/alpha/alphaev6/memcpy.S

find . -type f -size 0 -o -name "*.orig" -exec rm -f {} \;
cat > find_provides.sh <<EOF
#!/bin/sh
/usr/lib/rpm/find-provides | grep -v GLIBC_PRIVATE
exit 0
EOF
chmod +x find_provides.sh
touch `find . -name configure`
touch locale/programs/*-kw.h

%build
GCC=gcc
GXX=g++
%ifarch %{ix86}
BuildFlags="-march=%{nptl_target_cpu} -mtune=generic"
%endif
%ifarch i686
BuildFlags="-march=i686 -mtune=generic"
%endif
%ifarch i386
BuildFlags="$BuildFlags -mno-tls-direct-seg-refs"
%endif
%ifarch x86_64
BuildFlags="-mtune=generic"
%endif
%ifarch alphaev6
BuildFlags="-mcpu=ev6"
%endif
%ifarch sparc
BuildFlags="-fcall-used-g6"
GCC="gcc -m32"
GXX="g++ -m32"
%endif
%ifarch sparcv9
BuildFlags="-mcpu=ultrasparc -fcall-used-g6"
GCC="gcc -m32"
GXX="g++ -m32"
%endif
%ifarch sparcv9v
BuildFlags="-mcpu=niagara -fcall-used-g6"
GCC="gcc -m32"
GXX="g++ -m32"
%endif
%ifarch sparc64
BuildFlags="-mcpu=ultrasparc -mvis -fcall-used-g6"
GCC="gcc -m64"
GXX="g++ -m64"
%endif
%ifarch sparc64v
BuildFlags="-mcpu=niagara -mvis -fcall-used-g6"
GCC="gcc -m64"
GXX="g++ -m64"
%endif
%ifarch ppc64
BuildFlags="-mno-minimal-toc"
GCC="gcc -m64"
GXX="g++ -m64"
%endif

BuildFlags="$BuildFlags -DNDEBUG=1 -fasynchronous-unwind-tables"
EnableKernel="--enable-kernel=%{enablekernel}"
echo "$GCC" > Gcc
AddOns=`echo */configure | sed -e 's!/configure!!g;s!\(linuxthreads\|nptl\|rtkaio\|powerpc-cpu\)\( \|$\)!!g;s! \+$!!;s! !,!g;s!^!,!;/^,\*$/d'`
%ifarch %{rtkaioarches}
AddOns=,rtkaio$AddOns
%endif

build_nptl()
{
builddir=build-%{nptl_target_cpu}-$1
shift
rm -rf $builddir
mkdir $builddir ; cd $builddir
build_CFLAGS="$BuildFlags -g -O3 $*"
CC="$GCC" CXX="$GXX" CFLAGS="$build_CFLAGS" ../configure --prefix=%{_prefix} \
	--enable-add-ons=nptl$AddOns --without-cvs $EnableKernel \
	--with-headers=%{_prefix}/include --enable-bind-now \
	--with-tls --with-__thread --build %{nptl_target_cpu}-redhat-linux \
	--host %{nptl_target_cpu}-redhat-linux \
	--disable-profile
make %{?_smp_mflags} -r CFLAGS="$build_CFLAGS" PARALLELMFLAGS=-s

cd ..
}

build_nptl linuxnptl

%if %{buildxen}
build_nptl linuxnptl-nosegneg -mno-tls-direct-seg-refs
%endif

%if %{buildpower6}
(
platform=`LD_SHOW_AUXV=1 /bin/true | sed -n 's/^AT_PLATFORM:[[:blank:]]*//p'`
if [ "$platform" != power6 ]; then
  mkdir -p power6emul/{lib,lib64}
  $GCC -shared -O2 -fpic -o power6emul/%{_lib}/power6emul.so fedora/power6emul.c -Wl,-z,initfirst
%ifarch ppc
  echo '' | gcc -shared -nostdlib -O2 -fpic -m64 -o power6emul/lib64/power6emul.so -xc -
%endif
%ifarch ppc64
  echo '' | gcc -shared -nostdlib -O2 -fpic -m32 -o power6emul/lib/power6emul.so -xc -
%endif
  export LD_PRELOAD=`pwd`/power6emul/\$LIB/power6emul.so
fi
AddOns="$AddOns --with-cpu=power6"
GCC="$GCC -mcpu=power6"
GXX="$GXX -mcpu=power6"
build_nptl linuxnptl-power6
)
%endif

cd build-%{nptl_target_cpu}-linuxnptl
$GCC -static -L. -Os ../fedora/glibc_post_upgrade.c -o glibc_post_upgrade.%{_target_cpu} \
    -DNO_SIZE_OPTIMIZATION \
%ifarch i386
    -DARCH_386 \
%endif
    '-DLIBTLS="/%{_lib}/tls/"' \
    '-DGCONV_MODULES_DIR="%{_prefix}/%{_lib}/gconv"' \
    '-DLD_SO_CONF="/etc/ld.so.conf"' \
    '-DICONVCONFIG="%{_sbindir}/iconvconfig.%{_target_cpu}"'
cd ..

%install
GCC=`cat Gcc`

rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT
make -j1 install_root=$RPM_BUILD_ROOT install -C build-%{nptl_target_cpu}-linuxnptl PARALLELMFLAGS=-s
%ifnarch %{auxarches}
cd build-%{nptl_target_cpu}-linuxnptl && \
    make %{?_smp_mflags} install_root=$RPM_BUILD_ROOT install-locales -C ../localedata objdir=`pwd` && \
    cd ..
%endif

librtso=`basename $RPM_BUILD_ROOT/%{_lib}/librt.so.*`

%ifarch %{rtkaioarches}
rm -f $RPM_BUILD_ROOT{,%{_prefix}}/%{_lib}/librtkaio.so*
rm -f $RPM_BUILD_ROOT%{_prefix}/%{_lib}/librt.so.*
mkdir -p $RPM_BUILD_ROOT/%{_lib}/rtkaio
mv $RPM_BUILD_ROOT/%{_lib}/librtkaio-*.so $RPM_BUILD_ROOT/%{_lib}/rtkaio/
rm -f $RPM_BUILD_ROOT/%{_lib}/$librtso
ln -sf `basename $RPM_BUILD_ROOT/%{_lib}/librt-*.so` $RPM_BUILD_ROOT/%{_lib}/$librtso
ln -sf `basename $RPM_BUILD_ROOT/%{_lib}/rtkaio/librtkaio-*.so` $RPM_BUILD_ROOT/%{_lib}/rtkaio/$librtso
%endif

%if %{buildxen}
%define nosegneg_subdir_base i686
%define nosegneg_subdir i686/nosegneg
cd build-%{nptl_target_cpu}-linuxnptl-nosegneg
SubDir=%{nosegneg_subdir}
mkdir -p $RPM_BUILD_ROOT/%{_lib}/$SubDir/
cp -a libc.so $RPM_BUILD_ROOT/%{_lib}/$SubDir/`basename $RPM_BUILD_ROOT/%{_lib}/libc-*.so`
ln -sf `basename $RPM_BUILD_ROOT/%{_lib}/libc-*.so` $RPM_BUILD_ROOT/%{_lib}/$SubDir/`basename $RPM_BUILD_ROOT/%{_lib}/libc.so.*`
cp -a math/libm.so $RPM_BUILD_ROOT/%{_lib}/$SubDir/`basename $RPM_BUILD_ROOT/%{_lib}/libm-*.so`
ln -sf `basename $RPM_BUILD_ROOT/%{_lib}/libm-*.so` $RPM_BUILD_ROOT/%{_lib}/$SubDir/`basename $RPM_BUILD_ROOT/%{_lib}/libm.so.*`
cp -a nptl/libpthread.so $RPM_BUILD_ROOT/%{_lib}/$SubDir/libpthread-%{version}.so
pushd $RPM_BUILD_ROOT/%{_lib}/$SubDir
ln -sf libpthread-*.so `basename $RPM_BUILD_ROOT/%{_lib}/libpthread.so.*`
popd
cp -a rt/librt.so $RPM_BUILD_ROOT/%{_lib}/$SubDir/`basename $RPM_BUILD_ROOT/%{_lib}/librt-*.so`
ln -sf `basename $RPM_BUILD_ROOT/%{_lib}/librt-*.so` $RPM_BUILD_ROOT/%{_lib}/$SubDir/$librtso
cp -a nptl_db/libthread_db.so $RPM_BUILD_ROOT/%{_lib}/$SubDir/`basename $RPM_BUILD_ROOT/%{_lib}/libthread_db-*.so`
ln -sf `basename $RPM_BUILD_ROOT/%{_lib}/libthread_db-*.so` $RPM_BUILD_ROOT/%{_lib}/$SubDir/`basename $RPM_BUILD_ROOT/%{_lib}/libthread_db.so.*`
%ifarch %{rtkaioarches}
mkdir -p $RPM_BUILD_ROOT/%{_lib}/rtkaio/$SubDir
cp -a rtkaio/librtkaio.so $RPM_BUILD_ROOT/%{_lib}/rtkaio/$SubDir/`basename $RPM_BUILD_ROOT/%{_lib}/librt-*.so | sed s/librt-/librtkaio-/`
ln -sf `basename $RPM_BUILD_ROOT/%{_lib}/rtkaio/$SubDir/librtkaio-*.so` $RPM_BUILD_ROOT/%{_lib}/rtkaio/$SubDir/$librtso
%endif
cd ..
%endif

%if %{buildpower6}
cd build-%{nptl_target_cpu}-linuxnptl-power6
mkdir -p $RPM_BUILD_ROOT/%{_lib}/power6{,x}
cp -a libc.so $RPM_BUILD_ROOT/%{_lib}/power6/`basename $RPM_BUILD_ROOT/%{_lib}/libc-*.so`
ln -sf `basename $RPM_BUILD_ROOT/%{_lib}/libc-*.so` $RPM_BUILD_ROOT/%{_lib}/power6/`basename $RPM_BUILD_ROOT/%{_lib}/libc.so.*`
cp -a math/libm.so $RPM_BUILD_ROOT/%{_lib}/power6/`basename $RPM_BUILD_ROOT/%{_lib}/libm-*.so`
ln -sf `basename $RPM_BUILD_ROOT/%{_lib}/libm-*.so` $RPM_BUILD_ROOT/%{_lib}/power6/`basename $RPM_BUILD_ROOT/%{_lib}/libm.so.*`
cp -a nptl/libpthread.so $RPM_BUILD_ROOT/%{_lib}/power6/libpthread-%{version}.so
pushd $RPM_BUILD_ROOT/%{_lib}/power6
ln -sf libpthread-*.so `basename $RPM_BUILD_ROOT/%{_lib}/libpthread.so.*`
popd
cp -a rt/librt.so $RPM_BUILD_ROOT/%{_lib}/power6/`basename $RPM_BUILD_ROOT/%{_lib}/librt-*.so`
ln -sf `basename $RPM_BUILD_ROOT/%{_lib}/librt-*.so` $RPM_BUILD_ROOT/%{_lib}/power6/$librtso
cp -a nptl_db/libthread_db.so $RPM_BUILD_ROOT/%{_lib}/power6/`basename $RPM_BUILD_ROOT/%{_lib}/libthread_db-*.so`
ln -sf `basename $RPM_BUILD_ROOT/%{_lib}/libthread_db-*.so` $RPM_BUILD_ROOT/%{_lib}/power6/`basename $RPM_BUILD_ROOT/%{_lib}/libthread_db.so.*`
pushd $RPM_BUILD_ROOT/%{_lib}/power6x
ln -sf ../power6/*.so .
cp -a ../power6/*.so.* .
popd
%ifarch %{rtkaioarches}
mkdir -p $RPM_BUILD_ROOT/%{_lib}/rtkaio/power6{,x}
cp -a rtkaio/librtkaio.so $RPM_BUILD_ROOT/%{_lib}/rtkaio/power6/`basename $RPM_BUILD_ROOT/%{_lib}/librt-*.so | sed s/librt-/librtkaio-/`
ln -sf `basename $RPM_BUILD_ROOT/%{_lib}/rtkaio/power6/librtkaio-*.so` $RPM_BUILD_ROOT/%{_lib}/rtkaio/power6/$librtso
pushd $RPM_BUILD_ROOT/%{_lib}/rtkaio/power6x
ln -sf ../power6/*.so .
cp -a ../power6/*.so.* .
popd
%endif
cd ..
%endif

# Remove the files we don't want to distribute
rm -f $RPM_BUILD_ROOT%{_prefix}/%{_lib}/libNoVersion*
rm -f $RPM_BUILD_ROOT/%{_lib}/libNoVersion*

# NPTL <bits/stdio-lock.h> is not usable outside of glibc, so include
# the generic one (#162634)
cp -a bits/stdio-lock.h $RPM_BUILD_ROOT%{_prefix}/include/bits/stdio-lock.h
# And <bits/libc-lock.h> needs sanitizing as well.
cp -a fedora/libc-lock.h $RPM_BUILD_ROOT%{_prefix}/include/bits/libc-lock.h

if [ -d $RPM_BUILD_ROOT%{_prefix}/info -a "%{_infodir}" != "%{_prefix}/info" ]; then
    mkdir -p $RPM_BUILD_ROOT%{_infodir}
    mv -f $RPM_BUILD_ROOT%{_prefix}/info/* $RPM_BUILD_ROOT%{_infodir}
    rm -rf $RPM_BUILD_ROOT%{_prefix}/info
fi

gzip -9nvf $RPM_BUILD_ROOT%{_infodir}/libc*

ln -sf libbsd-compat.a $RPM_BUILD_ROOT%{_prefix}/%{_lib}/libbsd.a

install -p -m 644 fedora/nsswitch.conf $RPM_BUILD_ROOT/etc/nsswitch.conf

mkdir -p $RPM_BUILD_ROOT/etc/default
install -p -m 644 nis/nss $RPM_BUILD_ROOT/etc/default/nss

# Take care of setuids
# -- new security review sez that this shouldn't be needed anymore
#chmod 755 $RPM_BUILD_ROOT%{_prefix}/libexec/pt_chown

# This is for ncsd - in glibc 2.2
install -m 644 nscd/nscd.conf $RPM_BUILD_ROOT/etc
mkdir -p $RPM_BUILD_ROOT/etc/rc.d/init.d
install -m 755 nscd/nscd.init $RPM_BUILD_ROOT/etc/rc.d/init.d/nscd

# Don't include ld.so.cache
rm -f $RPM_BUILD_ROOT/etc/ld.so.cache

# Include ld.so.conf
echo 'include ld.so.conf.d/*.conf' > $RPM_BUILD_ROOT/etc/ld.so.conf
> $RPM_BUILD_ROOT/etc/ld.so.cache
chmod 644 $RPM_BUILD_ROOT/etc/ld.so.conf
mkdir -p $RPM_BUILD_ROOT/etc/ld.so.conf.d
mkdir -p $RPM_BUILD_ROOT/etc/sysconfig
> $RPM_BUILD_ROOT/etc/sysconfig/nscd

# Include %{_prefix}/%{_lib}/gconv/gconv-modules.cache
> $RPM_BUILD_ROOT%{_prefix}/%{_lib}/gconv/gconv-modules.cache
chmod 644 $RPM_BUILD_ROOT%{_prefix}/%{_lib}/gconv/gconv-modules.cache

# Install the upgrade program
install -m 700 build-%{nptl_target_cpu}-linuxnptl/glibc_post_upgrade.%{_target_cpu} \
  $RPM_BUILD_ROOT/usr/sbin/glibc_post_upgrade.%{_target_cpu}

strip -g $RPM_BUILD_ROOT%{_prefix}/%{_lib}/*.o

mkdir -p $RPM_BUILD_ROOT%{_prefix}/lib/debug%{_prefix}/%{_lib}
cp -a $RPM_BUILD_ROOT%{_prefix}/%{_lib}/*.a \
  $RPM_BUILD_ROOT%{_prefix}/lib/debug%{_prefix}/%{_lib}/
rm -f $RPM_BUILD_ROOT%{_prefix}/lib/debug%{_prefix}/%{_lib}/*_p.a
# Now strip debugging info from static libraries
pushd $RPM_BUILD_ROOT%{_prefix}/%{_lib}/
for i in *.a; do
  if [ -f $i ]; then
    case "$i" in
    *_p.a) ;;
    *) strip -g -R .comment $i ;;
    esac
  fi
done
popd

# rquota.x and rquota.h are now provided by quota
rm -f $RPM_BUILD_ROOT%{_prefix}/include/rpcsvc/rquota.[hx]

# Hardlink identical locale files together
%ifnarch %{auxarches}
gcc -O2 -o build-%{nptl_target_cpu}-linuxnptl/hardlink fedora/hardlink.c
olddir=`pwd`
pushd ${RPM_BUILD_ROOT}%{_prefix}/lib/locale
rm locale-archive || :
# Intentionally we do not pass --alias-file=, aliases will be added
# by build-locale-archive.
$olddir/build-%{nptl_target_cpu}-linuxnptl/elf/ld.so \
  --library-path $olddir/build-%{nptl_target_cpu}-linuxnptl/ \
  $olddir/build-%{nptl_target_cpu}-linuxnptl/locale/localedef \
    --prefix ${RPM_BUILD_ROOT} --add-to-archive \
    *_*
rm -rf *_*
mv locale-archive{,.tmpl}
popd
#build-%{nptl_target_cpu}-linuxnptl/hardlink -vc $RPM_BUILD_ROOT%{_prefix}/lib/locale
%endif

rm -f ${RPM_BUILD_ROOT}/%{_lib}/libnss1-*
rm -f ${RPM_BUILD_ROOT}/%{_lib}/libnss-*.so.1

# Ugly hack for buggy rpm
ln -f ${RPM_BUILD_ROOT}%{_sbindir}/iconvconfig{,.%{_target_cpu}}

rm -f $RPM_BUILD_ROOT/etc/gai.conf

# In F7+ this is provided by rpcbind rpm
rm -f $RPM_BUILD_ROOT%{_sbindir}/rpcinfo

# BUILD THE FILE LIST
find $RPM_BUILD_ROOT -type f -or -type l |
	sed -e 's|.*/etc|%config &|' \
	    -e 's|.*/gconv/gconv-modules$|%verify(not md5 size mtime) %config(noreplace) &|' \
	    -e 's|.*/gconv/gconv-modules.cache|%verify(not md5 size mtime) &|' \
	    -e '/lib\/debug/d' > rpm.filelist.in
for n in %{_prefix}/share %{_prefix}/include %{_prefix}/lib/locale; do
    find ${RPM_BUILD_ROOT}${n} -type d | \
	grep -v '%{_prefix}/share$' | \
	grep -v '%{_infodir}' | \
	sed "s/^/%dir /" >> rpm.filelist.in
done

# primary filelist
SHARE_LANG='s|.*/share/locale/\([^/_]\+\).*/LC_MESSAGES/.*\.mo|%lang(\1) &|'
LIB_LANG='s|.*/lib/locale/\([^/_]\+\)|%lang(\1) &|'
# rpm does not handle %lang() tagged files hardlinked together accross
# languages very well, temporarily disable
LIB_LANG=''
sed -e "s|$RPM_BUILD_ROOT||" -e "$LIB_LANG" -e "$SHARE_LANG" < rpm.filelist.in |
	grep -v '/etc/\(localtime\|nsswitch.conf\|ld.so.conf\|ld.so.cache\|default\)'  | \
	grep -v '/%{_lib}/lib\(pcprofile\|memusage\).so' | \
	grep -v 'bin/\(memusage\|mtrace\|xtrace\|pcprofiledump\)' | \
	sort > rpm.filelist

mkdir -p $RPM_BUILD_ROOT%{_prefix}/%{_lib}
mv -f $RPM_BUILD_ROOT/%{_lib}/lib{pcprofile,memusage}.so $RPM_BUILD_ROOT%{_prefix}/%{_lib}
for i in $RPM_BUILD_ROOT%{_prefix}/bin/{xtrace,memusage}; do
  cp -a $i $i.tmp
  sed -e 's~=/%{_lib}/libpcprofile.so~=%{_prefix}/%{_lib}/libpcprofile.so~' \
      -e 's~=/%{_lib}/libmemusage.so~=%{_prefix}/%{_lib}/libmemusage.so~' \
      -e 's~='\''/\\\$LIB/libpcprofile.so~='\''%{_prefix}/\\$LIB/libpcprofile.so~' \
      -e 's~='\''/\\\$LIB/libmemusage.so~='\''%{_prefix}/\\$LIB/libmemusage.so~' \
    $i.tmp > $i
  chmod 755 $i; rm -f $i.tmp
done

grep '%{_infodir}' < rpm.filelist | grep -v '%{_infodir}/dir' > devel.filelist
grep '%{_prefix}/include/gnu/stubs-[32164]\+\.h' < rpm.filelist >> devel.filelist || :

grep '%{_prefix}/include' < rpm.filelist |
	egrep -v '%{_prefix}/include/(linuxthreads|gnu/stubs-[32164]+\.h)' \
		> headers.filelist

mv rpm.filelist rpm.filelist.full
grep -v '%{_prefix}/%{_lib}/lib.*_p.a' rpm.filelist.full |
	egrep -v "(%{_prefix}/include)|(%{_infodir})" > rpm.filelist

grep '%{_prefix}/%{_lib}/lib.*\.a' < rpm.filelist >> devel.filelist
grep '%{_prefix}/%{_lib}/.*\.o' < rpm.filelist >> devel.filelist
grep '%{_prefix}/%{_lib}/lib.*\.so' < rpm.filelist >> devel.filelist

mv rpm.filelist rpm.filelist.full
grep -v '%{_prefix}/%{_lib}/lib.*\.a' < rpm.filelist.full |
	grep -v '%{_prefix}/%{_lib}/.*\.o' |
	grep -v '%{_prefix}/%{_lib}/lib.*\.so'|
	grep -v '%{_prefix}/%{_lib}/linuxthreads' |
	grep -v 'nscd' > rpm.filelist

grep '%{_prefix}/bin' < rpm.filelist >> common.filelist
#grep '%{_prefix}/lib/locale' < rpm.filelist | grep -v /locale-archive.tmpl >> common.filelist
grep '%{_prefix}/libexec/pt_chown' < rpm.filelist >> common.filelist
grep '%{_prefix}/sbin/[^gi]' < rpm.filelist >> common.filelist
grep '%{_prefix}/share' < rpm.filelist \
  | grep -v '%{_prefix}/share/zoneinfo' >> common.filelist

mv rpm.filelist rpm.filelist.full
grep -v '%{_prefix}/bin' < rpm.filelist.full |
	grep -v '%{_prefix}/lib/locale' |
	grep -v '%{_prefix}/libexec/pt_chown' |
	grep -v '%{_prefix}/sbin/[^gi]' |
	grep -v '%{_prefix}/share' > rpm.filelist

> nosegneg.filelist
%if %{xenpackage}
grep '/%{_lib}/%{nosegneg_subdir}' < rpm.filelist >> nosegneg.filelist
mv rpm.filelist rpm.filelist.full
grep -v '/%{_lib}/%{nosegneg_subdir}' < rpm.filelist.full > rpm.filelist
%endif

echo '%{_prefix}/sbin/build-locale-archive' >> common.filelist
echo '%{_prefix}/sbin/tzdata-update' >> common.filelist
echo '%{_prefix}/sbin/nscd' > nscd.filelist

cat > utils.filelist <<EOF
%{_prefix}/%{_lib}/libmemusage.so
%{_prefix}/%{_lib}/libpcprofile.so
%{_prefix}/bin/memusage
%{_prefix}/bin/memusagestat
%{_prefix}/bin/mtrace
%{_prefix}/bin/pcprofiledump
%{_prefix}/bin/xtrace
EOF

# /etc/localtime
rm -f $RPM_BUILD_ROOT/etc/localtime
cp -f $RPM_BUILD_ROOT%{_prefix}/share/zoneinfo/US/Eastern $RPM_BUILD_ROOT/etc/localtime
#ln -sf ..%{_prefix}/share/zoneinfo/US/Eastern $RPM_BUILD_ROOT/etc/localtime

rm -rf $RPM_BUILD_ROOT%{_prefix}/share/zoneinfo

# Make sure %config files have the same timestamp
touch -r fedora/glibc.spec.in $RPM_BUILD_ROOT/etc/ld.so.conf
touch -r timezone/northamerica $RPM_BUILD_ROOT/etc/localtime
touch -r sunrpc/etc.rpc $RPM_BUILD_ROOT/etc/rpc

cd fedora
$GCC -Os -static -o build-locale-archive build-locale-archive.c \
  ../build-%{nptl_target_cpu}-linuxnptl/locale/locarchive.o \
  ../build-%{nptl_target_cpu}-linuxnptl/locale/md5.o \
  -DDATADIR=\"%{_datadir}\" -DPREFIX=\"%{_prefix}\" \
  -L../build-%{nptl_target_cpu}-linuxnptl
install -m 700 build-locale-archive $RPM_BUILD_ROOT/usr/sbin/build-locale-archive
$GCC -Os -static -o tzdata-update tzdata-update.c \
  -L../build-%{nptl_target_cpu}-linuxnptl
install -m 700 tzdata-update $RPM_BUILD_ROOT/usr/sbin/tzdata-update
cd ..

# the last bit: more documentation
rm -rf documentation
mkdir documentation
cp crypt/README.ufc-crypt documentation/README.ufc-crypt
cp timezone/README documentation/README.timezone
cp ChangeLog{,.15,.16} documentation
bzip2 -9 documentation/ChangeLog*
cp posix/gai.conf documentation/

%ifarch s390x
# Compatibility symlink
mkdir -p $RPM_BUILD_ROOT/lib
ln -sf /%{_lib}/ld64.so.1 $RPM_BUILD_ROOT/lib/ld64.so.1
%endif
%ifarch ia64
%if "%{_lib}" == "lib64"
# Compatibility symlink
mkdir -p $RPM_BUILD_ROOT/lib
ln -sf /%{_lib}/ld-linux-ia64.so.2 $RPM_BUILD_ROOT/lib/ld-linux-ia64.so.2
%endif
%endif

%if %{run_glibc_tests}

# Increase timeouts
export TIMEOUTFACTOR=16
parent=$$
echo ====================TESTING=========================
cd build-%{nptl_target_cpu}-linuxnptl
( make %{?_smp_mflags} -k check PARALLELMFLAGS=-s 2>&1
  sleep 10s
  teepid="`ps -eo ppid,pid,command | awk '($1 == '${parent}' && $3 ~ /^tee/) { print $2 }'`"
  [ -n "$teepid" ] && kill $teepid
) | tee check.log || :
cd ..
%if %{buildxen}
echo ====================TESTING -mno-tls-direct-seg-refs=============
cd build-%{nptl_target_cpu}-linuxnptl-nosegneg
( make -j$numprocs -k check PARALLELMFLAGS=-s 2>&1
  sleep 10s
  teepid="`ps -eo ppid,pid,command | awk '($1 == '${parent}' && $3 ~ /^tee/) { print $2 }'`"
  [ -n "$teepid" ] && kill $teepid
) | tee check.log || :
cd ..
%endif
%if %{buildpower6}
echo ====================TESTING -mcpu=power6=============
cd build-%{nptl_target_cpu}-linuxnptl-power6
( if [ -d ../power6emul ]; then
    export LD_PRELOAD=`cd ../power6emul; pwd`/\$LIB/power6emul.so
  fi
  make -j$numprocs -k check PARALLELMFLAGS=-s 2>&1
  sleep 10s
  teepid="`ps -eo ppid,pid,command | awk '($1 == '${parent}' && $3 ~ /^tee/) { print $2 }'`"
  [ -n "$teepid" ] && kill $teepid
) | tee check.log || :
cd ..
%endif
echo ====================TESTING DETAILS=================
for i in `sed -n 's|^.*\*\*\* \[\([^]]*\.out\)\].*$|\1|p' build-*-linux*/check.log`; do
  echo =====$i=====
  cat $i || :
  echo ============
done
echo ====================TESTING END=====================
PLTCMD='/^Relocation section .*\(\.rela\?\.plt\|\.rela\.IA_64\.pltoff\)/,/^$/p'
echo ====================PLT RELOCS LD.SO================
readelf -Wr $RPM_BUILD_ROOT/%{_lib}/ld-*.so | sed -n -e "$PLTCMD"
echo ====================PLT RELOCS LIBC.SO==============
readelf -Wr $RPM_BUILD_ROOT/%{_lib}/libc-*.so | sed -n -e "$PLTCMD"
echo ====================PLT RELOCS END==================

%endif

%if "%{_enable_debug_packages}" == "1"

# The #line directives gperf generates do not give the proper
# file name relative to the build directory.
(cd locale; ln -s programs/*.gperf .)
(cd iconv; ln -s ../locale/programs/charmap-kw.gperf .)

ls -l $RPM_BUILD_ROOT/usr/bin/getconf
ls -l $RPM_BUILD_ROOT/usr/libexec/getconf
eu-readelf -hS $RPM_BUILD_ROOT/usr/bin/getconf $RPM_BUILD_ROOT/usr/libexec/getconf/*

find_debuginfo_args='--strict-build-id -g'
%ifarch %{debuginfocommonarches}
find_debuginfo_args="$find_debuginfo_args \
  -l common.filelist -l utils.filelist -l nscd.filelist \
  -o debuginfocommon.filelist \
  -l rpm.filelist -l nosegneg.filelist \
"
%endif
/usr/lib/rpm/find-debuginfo.sh $find_debuginfo_args -o debuginfo.filelist

list_debug_archives()
{
  local dir=%{_prefix}/lib/debug%{_prefix}/%{_lib}
  (cd $RPM_BUILD_ROOT; ls ${dir#/}/*.a) | sed 's,^,/,'
}

%ifarch %{debuginfocommonarches}

%ifarch %{ix86}
%define basearch i386
%endif
%ifarch alpha alphaev6
%define basearch alpha
%endif
%ifarch sparc sparcv9
%define basearch sparc
%endif

sed -i '\#^%{_prefix}/src/debug/#d' debuginfocommon.filelist
(cd $RPM_BUILD_ROOT%{_prefix}/src; find debug -type d) |
sed 's#^#%dir %{_prefix}/src/#' > debuginfocommon.sources
(cd $RPM_BUILD_ROOT%{_prefix}/src; find debug ! -type d) |
sed 's#^#%{_prefix}/src/#' >> debuginfocommon.sources

# auxarches get only these few source files
auxarches_debugsources=\
'/(generic|linux|%{basearch}|nptl(_db)?)/|/%{glibcsrcdir}/build|/dl-osinfo\.h'

egrep "$auxarches_debugsources" debuginfocommon.sources >> debuginfo.filelist

egrep -v "$auxarches_debugsources" \
      debuginfocommon.sources >> debuginfocommon.filelist
%ifarch %{auxarches}
%else
# non-aux arches when there is a debuginfo-common
# all the sources go into debuginfo-common
#cat debuginfocommon.sources >> debuginfocommon.filelist
%endif

list_debug_archives >> debuginfocommon.filelist

%else

list_debug_archives >> debuginfo.filelist

%endif

%endif

rm -f $RPM_BUILD_ROOT%{_infodir}/dir

%ifarch %{auxarches}

echo Cutting down the list of unpackaged files
>> debuginfocommon.filelist
sed -e '/%%dir/d;/%%config/d;/%%verify/d;s/%%lang([^)]*) //;s#^/*##' \
	  common.filelist devel.filelist headers.filelist \
    utils.filelist nscd.filelist debuginfocommon.filelist |
(cd $RPM_BUILD_ROOT; xargs --no-run-if-empty rm -f 2> /dev/null || :)

%else

mkdir -p $RPM_BUILD_ROOT/var/{db,run}/nscd
touch $RPM_BUILD_ROOT/var/{db,run}/nscd/{passwd,group,hosts,services}
touch $RPM_BUILD_ROOT/var/run/nscd/{socket,nscd.pid}
%endif

%ifnarch %{auxarches}
> $RPM_BUILD_ROOT/%{_prefix}/lib/locale/locale-archive
%endif

mkdir -p $RPM_BUILD_ROOT/var/cache/ldconfig
> $RPM_BUILD_ROOT/var/cache/ldconfig/aux-cache

%post -p /usr/sbin/glibc_post_upgrade.%{_target_cpu}

%postun -p /sbin/ldconfig

%post common -p /usr/sbin/build-locale-archive

%triggerin common -p /usr/sbin/tzdata-update -- tzdata

%post devel
/sbin/install-info %{_infodir}/libc.info.gz %{_infodir}/dir || :

%pre headers
# this used to be a link and it is causing nightmares now
if [ -L %{_prefix}/include/scsi ] ; then
    rm -f %{_prefix}/include/scsi
fi

%preun devel
if [ "$1" = 0 ]; then
    /sbin/install-info --delete %{_infodir}/libc.info.gz %{_infodir}/dir || :
fi

%post utils -p /sbin/ldconfig

%postun utils -p /sbin/ldconfig

%pre -n nscd
/usr/sbin/useradd -M -o -r -d / -s /sbin/nologin \
	-c "NSCD Daemon" -u 28 nscd > /dev/null 2>&1 || :

%post -n nscd
/sbin/chkconfig --add nscd

%preun -n nscd
if [ $1 = 0 ] ; then
    service nscd stop > /dev/null 2>&1
    /sbin/chkconfig --del nscd
fi

%postun -n nscd
if [ $1 = 0 ] ; then
    /usr/sbin/userdel nscd > /dev/null 2>&1 || :
fi
if [ "$1" -ge "1" ]; then
    service nscd condrestart > /dev/null 2>&1 || :
fi

%if %{xenpackage}
%post xen -p /sbin/ldconfig
%postun xen -p /sbin/ldconfig
%endif

%clean
rm -rf "$RPM_BUILD_ROOT"
rm -f *.filelist*

%files -f rpm.filelist
%defattr(-,root,root)
%ifarch %{rtkaioarches}
%dir /%{_lib}/rtkaio
%endif
%if %{buildxen} && !%{xenpackage}
%dir /%{_lib}/%{nosegneg_subdir_base}
%dir /%{_lib}/%{nosegneg_subdir}
%ifarch %{rtkaioarches}
%dir /%{_lib}/rtkaio/%{nosegneg_subdir_base}
%dir /%{_lib}/rtkaio/%{nosegneg_subdir}
%endif
%endif
%if %{buildpower6}
%dir /%{_lib}/power6
%dir /%{_lib}/power6x
%ifarch %{rtkaioarches}
%dir /%{_lib}/rtkaio/power6
%dir /%{_lib}/rtkaio/power6x
%endif
%endif
%ifarch s390x
%dir /lib
/lib/ld64.so.1
%endif
%ifarch ia64
%if "%{_lib}" == "lib64"
%dir /lib
/lib/ld-linux-ia64.so.2
%endif
%endif
%verify(not md5 size mtime) %config(noreplace) /etc/localtime
%verify(not md5 size mtime) %config(noreplace) /etc/nsswitch.conf
%verify(not md5 size mtime) %config(noreplace) /etc/ld.so.conf
%dir /etc/ld.so.conf.d
%dir %{_prefix}/libexec/getconf
%dir %{_prefix}/%{_lib}/gconv
%dir %attr(0700,root,root) /var/cache/ldconfig
%attr(0600,root,root) %verify(not md5 size mtime) %ghost %config(missingok,noreplace) /var/cache/ldconfig/aux-cache
%attr(0644,root,root) %verify(not md5 size mtime) %ghost %config(missingok,noreplace) /etc/ld.so.cache
%doc README NEWS INSTALL FAQ BUGS NOTES PROJECTS CONFORMANCE
%doc COPYING COPYING.LIB README.libm LICENSES
%doc hesiod/README.hesiod

%if %{xenpackage}
%files -f nosegneg.filelist xen
%defattr(-,root,root)
%dir /%{_lib}/%{nosegneg_subdir_base}
%dir /%{_lib}/%{nosegneg_subdir}
%endif

%ifnarch %{auxarches}
%files -f common.filelist common
%defattr(-,root,root)
%dir %{_prefix}/lib/locale
%attr(0644,root,root) %verify(not md5 size mtime) %{_prefix}/lib/locale/locale-archive.tmpl
%attr(0644,root,root) %verify(not md5 size mtime mode) %ghost %config(missingok,noreplace) %{_prefix}/lib/locale/locale-archive
%dir %attr(755,root,root) /etc/default
%verify(not md5 size mtime) %config(noreplace) /etc/default/nss
%doc documentation/*

%files -f devel.filelist devel
%defattr(-,root,root)

%files -f headers.filelist headers
%defattr(-,root,root)

%files -f utils.filelist utils
%defattr(-,root,root)

%files -f nscd.filelist -n nscd
%defattr(-,root,root)
%config(noreplace) /etc/nscd.conf
%config /etc/rc.d/init.d/nscd
%dir %attr(0755,root,root) /var/run/nscd
%dir %attr(0755,root,root) /var/db/nscd
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

%if "%{_enable_debug_packages}" == "1"
%files debuginfo -f debuginfo.filelist
%defattr(-,root,root)
%ifarch %{debuginfocommonarches}
%ifnarch %{auxarches}
%files debuginfo-common -f debuginfocommon.filelist
%defattr(-,root,root)
%endif
%endif
%endif

%changelog
* Tue Sep 18 2007 Jakub Jelinek <jakub@redhat.com> 2.6.90-14
- -D_FORTIFY_SOURCE{,=2} support for C++
- fortification of fread{,_unlocked}
- support *scanf m allocation modifier (%ms, %mls, %mc, ...)
- in -std=c99 or -D_XOPEN_SOURCE=600 mode don't recognize
  %as, %aS and %a[ as a GNU extension for *scanf
- fix splice, vmsplice, tee return value, make them cancellation
  points
- mq_open checking
- use inline function rather than function-like macro
  for open{,at}{,64} checking
- IFA_F_OPTIMISTIC handling in getaddrinfo (#259681)
- fix an ABBA deadlock in ld.so (#284171)
- remove sparc{32,64} unwind info from _start and clone

* Mon Aug 27 2007 Jakub Jelinek <jakub@redhat.com> 2.6.90-13
- fix personality on x86_64/ppc/ppc64 (#256281)

* Sat Aug 25 2007 Jakub Jelinek <jakub@redhat.com> 2.6.90-12
- readd x86_64 gettimeofday stuff, initialize it earlier
- nis_list fix (#254115)
- workaround for bugs in ia64 silly /emul/ia32-linux hack (#253961)
- misc fixes (BZ#3924, BZ#4566, BZ#4582, BZ#4588, BZ#4726, BZ#4946,
  BZ#4905, BZ#4814, BZ#4925, BZ#4936, BZ#4896, BZ#4937, BZ#3842,
  BZ#4554, BZ#4557, BZ#4938)

* Fri Aug 17 2007 Jakub Jelinek <jakub@redhat.com> 2.6.90-11
- remove __strtold_internal and __wcstold_internal from ppc*/s390*/sparc*
  *-ldbl.h headers
- temporarily backout x86_64 gettimeofday.S changes (#252453)
- some further sparc, sparc64 and alpha fixes

* Wed Aug 15 2007 Jakub Jelinek <jakub@redhat.com> 2.6.90-10
- don't open /etc/ld.so.{cache,preload} with O_NOATIME (#252146)
- s390{,x}, alpha and sparc fixes
- sparcv9 is no longer an aux arch, as we expect
  to not build sparc.rpm glibc any longer, only sparcv9.rpm,
  sparc64.rpm and new two aux arches sparcv9v.rpm and sparc64v.rpm

* Tue Aug 14 2007 Jakub Jelinek <jakub@redhat.com> 2.6.90-9
- private futex even for mutexes and condvars
- some further O_CLOEXEC changes
- use vDSO on x86_64 if available
- ia64 build fixes (#251983)

* Fri Aug 10 2007 Roland McGrath <roland@redhat.com> 2.6.90-8
- update to trunk
  - fix missing strtold_l export on ppc64

* Thu Aug  9 2007 Roland McGrath <roland@redhat.com> 2.6.90-6
- update to trunk
  - fix local PLT regressions
- spec file revamp for new find-debuginfo.sh

* Sun Aug  5 2007 Jakub Jelinek <jakub@redhat.com> 2.6.90-4
- fix librt.so and librtkaio.so on ppc32, so that it is not using
  bss PLT

* Sat Aug  4 2007 Jakub Jelinek <jakub@redhat.com> 2.6.90-3
- fix open{,at}{,64} macro for -pedantic (#250897)
- add transliteration for l with stroke (#250492)
- fix strtod ("-0", NULL)
- update License tag

* Wed Aug  1 2007 Jakub Jelinek <jakub@redhat.com> 2.6.90-2
- make aux-cache purely optional performance optimization in ldconfig,
  don't issue any errors if it can't be created (#250430)
- remove override_headers hack, BuildRequire >= 2.6.22 kernel-headers
  and rely on its content

* Tue Jul 31 2007 Jakub Jelinek <jakub@redhat.com> 2.6.90-1
- update to trunk
  - private futex optimizations
  - open{,at}{,64} argument checking
- ldconfig speedups

* Sun Jul  8 2007 Jakub Jelinek <jakub@redhat.com> 2.6-4
- filter <built-in> pseudo-files from debuginfo source lists (#245714)
- fix sscanf when errno is EINTR before the call (BZ#4745)
- save/restore errno around reading /etc/default/nss (BZ#4702)
- fix LD_HWCAP_MASK handling
- disable workaround for #210748, instead backport
  ld.so locking fixes from the trunk (#235026)
- new x86_64 memcpy
- don't write uninitialized padding bytes to nscd socket
- fix dl{,v}sym, dl_iterate_phdr and dlopen if some library is
  mapped into ld.so's inter-segment hole on x86_64 (#245035, #244545)
- fix LD_AUDIT=a:b program (#180432)
- don't crash on pseudo-zero long double values passed to
  *printf on i?86/x86_64/ia64 (BZ#4586)
- fix *printf %La and strtold with some hexadecimal floating point
  constants on ppc/ppc64
- fix nextafterl on ppc/ppc64
- fix sem_timedwait on i?86 and x86_64

* Thu May 24 2007 Jakub Jelinek <jakub@redhat.com> 2.6-3
- don't use %%config(missingok) for locale-archive.tmpl,
  instead of removing it altogether truncate it to zero
  size (#240697)
- add a workaround for #210748

* Mon May 21 2007 Jakub Jelinek <jakub@redhat.com> 2.6-2
- restore malloc_set_state backwards compatibility (#239344)
- fix epoll_pwait (BZ#4525)
- fix printf with unknown format spec or positional arguments
  and large width and/or precision (BZ#4514)
- robust mutexes fix (BZ#4512)

* Tue May 15 2007 Roland McGrath <roland@redhat.com> 2.6-1
- glibc 2.6 release

* Fri May 11 2007 Jakub Jelinek <jakub@redhat.com> 2.5.90-24
- utimensat, futimens and lutimes support

* Thu May 10 2007 Jakub Jelinek <jakub@redhat.com> 2.5.90-23
- use madvise MADV_DONTNEED in malloc
- fix ia64 feraiseexcept
- fix s390{,x} feholdexcept (BZ#3427)
- ppc fenv fixes
- make fdatasync a cancellation point (BZ#4465)
- fix *printf for huge precisions with wide char code and multi-byte
  strings
- fix dladdr (#232224, BZ#4131)

* Fri May  4 2007 Jakub Jelinek <jakub@redhat.com> 2.5.90-22
- add transliteration for <U2044> (BZ#3213)
- fix *scanf with %f on hexadecimal floats without exponent (BZ#4342)
- fix *printf with very large precisions for %s (#238406, BZ#4438)
- fix inet_ntop size checking for AF_INET (BZ#4439)
- for *printf %e avoid 1.000e-00, for exponent 0 always use + sign (#238431)
- fix a regression introduced in #223467 changes
- gethostby*_r alignment fixes (BZ#4381)
- fix ifaddrs error handling

* Mon Apr 16 2007 Jakub Jelinek <jakub@redhat.com> 2.5.90-21
- don't include individual locale files in glibc-common,
  rather include prepared locale-archive template and let
  build-locale-archive create locale-archive from the template
  and any user supplied /usr/lib/locale/*_* directories,
  then unlink the locale-archive template - this should save
  > 80MB of glibc-common occupied disk space
- fix _XOPEN_VERSION (BZ#4364)
- fix printf with %g and values tiny bit smaller than 1.e-4 (#235864,
  BZ#4362)
- fix NIS+ __nisfind_server (#235229)

* Sat Mar 31 2007 Jakub Jelinek <jakub@redhat.com> 2.5.90-20
- assorted NIS+ speedups (#223467)
- fix HAVE_LIBCAP configure detection (#178934)
- remove %{_prefix}/sbin/rpcinfo from glibc-common (#228894)
- nexttoward*/nextafter* fixes (BZ#3306)
- feholdexcept/feupdateenv fixes (BZ#3427)
- speed up fnmatch with two or more * in the pattern

* Sat Mar 17 2007 Jakub Jelinek <jakub@redhat.com> 2.5.90-19
- fix power6 libm compat symbols on ppc32 (#232633)
- fix child refcntr in NPTL fork (#230198)
- fix ifaddrs with many net devices on > 4KB page size arches (#230151)
- fix pthread_mutex_timedlock on x86_64 (#228103)
- various fixes (BZ#3919, BZ#4101, BZ#4130, BZ#4181, BZ#4069, BZ#3458)

* Wed Feb 21 2007 Jakub Jelinek <jakub@redhat.com> 2.5.90-18
- fix nftw with FTW_CHDIR on / (BZ#4076)
- nscd fixes (BZ#4074)
- fix fmod{,f,l} on i?86 (BZ#3325)
- support localized digits for fp values in *scanf (BZ#2211)
- namespaces fixes (BZ#2633)
- fix euidaccess (BZ#3842)
- glob fixes (BZ#3996)
- assorted locale data fixes (BZ#1430, BZ#672, BZ#58, BZ#3156,
  BZ#2692, BZ#2648, BZ#3363, BZ#3334, BZ#3326, BZ#3322, BZ#3995,
  BZ#3885, BZ#3884, BZ#3851)

* Sun Feb 11 2007 Jakub Jelinek <jakub@redhat.com> 2.5.90-17
- RFC2671 support in resolver (#205842)
- fix strptime (BZ#3944)
- fix regcomp with REG_NEWLINE (BZ#3957)
- fix pthread_mutex_timedlock on x86_64 (#228103)

* Fri Feb  2 2007 Jakub Jelinek <jakub@redhat.com> 2.5.90-16
- add strerror_l
- fix application crashes when doing NSS lookups through nscd
  mmapped databases and nscd decides to start garbage collection
  during the lookups (#219145, #225315)
- fix %0lld printing of 0LL on 32-bit architectures (BZ#3902)
- ignore errors from install-info in glibc-devel scriptlets
  (#223691)

* Wed Jan 17 2007 Jakub Jelinek <jakub@redhat.com> 2.5.90-15
- fix NIS getservbyname when proto is NULL
- fix nss_compat +group handling (#220658)
- cache services in nscd
- fix double free in fts_close (#222089)
- fix vfork+execvp memory leak (#221187)
- soft-fp fixes (BZ#2749)
- further strtod fixes (BZ#3855)
- make sure pthread_kill doesn't return EINVAL even if
  the target thread exits in between pthread_kill ESRCH check
  and the actual tgkill syscall (#220420)
- fix ABBA deadlock possibility in ld.so scope locking code

* Tue Dec 19 2006 Jakub Jelinek <jakub@redhat.com> 2.5.90-14
- fix {j,m}rand48{,_r} on 64-bit arches (BZ#3747)
- handle power6x AT_PLATFORM (#216970)
- fix a race condition in getXXbyYY_r (#219145)
- fix tst-pselect testcase

* Thu Dec 14 2006 Jakub Jelinek <jakub@redhat.com> 2.5.90-13
- fix setcontext on ppc32 (#219107)
- fix wide stdio after setvbuf (#217064, BZ#2337)
- handle relatime mount option in statvfs
- revert i?86/x86_64 clone CFI temporarily

* Sun Dec 10 2006 Jakub Jelinek <jakub@redhat.com> 2.5.90-12
- fix hasmntopt (#218802)
- fix setusershell and getusershell (#218782)
- strtod fixes (BZ#3664, BZ#3673, BZ#3674)
- fix memusage with realloc (x, 0)

* Tue Dec  5 2006 Jakub Jelinek <jakub@redhat.com> 2.5.90-11
- allow suid apps to setenv NIS_PATH and influence through that
  nis_list and nis_lookup (#209155)
- fix ttyname and ttyname_r with invalid file descriptor (#218276)
- cs_CZ LC_TIME fixes (#218438)
- fix build with 2.6.19+ headers (#217723)

* Fri Dec  1 2006 Jakub Jelinek <jakub@redhat.com> 2.5.90-10
- fix x86-64 restore_rt unwind info

* Thu Nov 30 2006 Jakub Jelinek <jakub@redhat.com> 2.5.90-9
- fix last svc_run change (#217850)
- on ppc64 build __libc_start_main without unwind info,
  as it breaks MD_FROB_UPDATE_CONTEXT (#217729, #217775; in the
  future that could be fixable just by providing .cfi_undefined r2
  in __libc_start_main instead)
- add unwind info for x86-64 restore_rt signal return landing pad
  (#217087)
- add power6x subdir to /%{_lib}/ and /%{_lib}/rtkaio/,
  link all libs from ../power6/* into them

* Tue Nov 28 2006 Jakub Jelinek <jakub@redhat.com> 2.5.90-8
- fix svc_run (#216834, BZ#3559)
- add -fasynchronous-unwind-tables to CFLAGS (#216518)
- make sure there is consistent timestamp for /etc/ld.so.conf,
  /etc/localtime and /etc/rpc between multilib glibc rpms

* Mon Nov 20 2006 Jakub Jelinek <jakub@redhat.com> 2.5.90-7
- handle IPv6 addresses in /etc/hosts that are mappable to
  IPv4 addresses in IPv4 host lookups (#215283)
- fix :include: /etc/alias handling (#215572)
- handle new tzdata format to cope with year > 2037 transitions
  on 64-bit architectures

* Fri Nov 10 2006 Jakub Jelinek <jakub@redhat.com> 2.5.90-6
- fix strxfrm fix
- fix i?86 floor and ceil inlines (BZ#3451)

* Thu Nov  9 2006 Jakub Jelinek <jakub@redhat.com> 2.5.90-5
- fix sysconf (_SC_LEVEL{2,3}_CACHE_SIZE) on Intel Core Duo
  CPUs
- fix libthread_db.so on TLS_DTV_AT_TP architectures
- fix --inhibit-rpath (#214569)
- fix _r_debug content when prelinked ld.so executes
  a program as its argument
- fix strxfrm
- powerpc-cpu add-on updates

* Fri Nov  3 2006 Jakub Jelinek <jakub@redhat.com> 2.5.90-4
- fix atexit backwards compatibility (#213388)
- add mai_IN locale (#213415)
- remove bogus %{_libdir}/librt.so.1 symlink (#213555)
- fix memusage (#213656)
- change libc.info category (#209493)

* Sun Oct 29 2006 Jakub Jelinek <jakub@redhat.com> 2.5.90-3
- fix suid/sgid binaries on i?86/x86_64 (#212723)

* Fri Oct 27 2006 Jakub Jelinek <jakub@redhat.com> 2.5.90-2
- fix ia64 build
- don't call _dl_close outside of dl_load_lock critical section
  if dlopen failed (BZ#3426)
- add rtld scope locking (#211133)

* Wed Oct 25 2006 Jakub Jelinek <jakub@redhat.com> 2.5.90-1
- fix i?86 6 argument syscalls (e.g. splice)
- fix rtld minimal realloc (BZ#3352)
- fix RFC3484 getaddrinfo sorting according to rules 4 and 7 (BZ#3369)
- fix xdrmem_setpos (#211452)
- bump __GLIBC_MINOR__
- increase PTHREAD_STACK_MIN on ppc{,64} to 128K to allow
  64K pagesize kernels (#209877)
- speed up initgroups on NIS+ (#208203)

* Mon Oct  2 2006 Jakub Jelinek <jakub@redhat.com> 2.5-2
- fix nscd database growing (#207928)
- bypass prelinking when LD_DYNAMIC_WEAK=1 is in the environment

* Fri Sep 29 2006 Jakub Jelinek <jakub@redhat.com> 2.5-1
- glibc 2.5 release

* Wed Sep 27 2006 Jakub Jelinek <jakub@redhat.com> 2.4.90-36
- rebuilt with gcc-4.1.1-26 to fix unwind info

* Mon Sep 25 2006 Jakub Jelinek <jakub@redhat.com> 2.4.90-35
- fix glob with large number of matches (BZ#3253)
- fix fchownat on kernels that don't support that syscall (BZ#3252)
- fix lrintl on s390{,64}

* Sat Sep 23 2006 Jakub Jelinek <jakub@redhat.com> 2.4.90-34
- fix ppc{32,64} longjmp (BZ#3225)
- fix user visible spelling errors (BZ#3137)
- fix l{,l}rint{,f,l} around zero (BZ#2592)
- avoid stack trampoline in s390{,x} makecontext

* Tue Sep 15 2006 Jakub Jelinek <jakub@redhat.com> 2.4.90-33
- fix dlclose (#206639)
- don't load platform optimized libraries if kernel doesn't set
  AT_PLATFORM
- fix ppc{32,64} libSegFault.so
- use -mtune=generic even for glibc-devel.i386 (#206437)
- fix /%{_lib}/librt.so.1 symlink

* Fri Sep 15 2006 Jakub Jelinek <jakub@redhat.com> 2.4.90-32
- on ppc* use just AT_PLATFORM and altivec AT_HWCAP bit for library selection
- fix lrintl and lroundl on ppc{,64}
- use hidden visibility on fstatat{,64} and mknodat in libc_nonshared.a

* Sun Sep 10 2006 Jakub Jelinek <jakub@redhat.com> 2.4.90-31
- fix pthread_cond_{,timed}wait cancellation (BZ#3123)
- fix lrint on ppc32 (BZ#3155)
- fix malloc allocating more than half of address space (BZ#2775)
- fix mktime on 32-bit arches a few years after 2038 (BZ#2821)

* Thu Sep  7 2006 Jakub Jelinek <jakub@redhat.com> 2.4.90-30
- add librtkaio, to use it add /%{lib}/rtkaio to your
  LD_LIBRARY_PATH or /etc/ld.so.conf
- fix or_IN February name (#204730)
- fix pthread_create called from cancellation handlers (BZ#3124)
- fix regex case insensitive searches with characters where upper
  and lower case multibyte representations have different length
  (e.g. I and dotless i, #202991)

* Tue Sep  5 2006 Jakub Jelinek <jakub@redhat.com> 2.4.90-29
- randomize resolver query ids before use instead after use (#205113)
- fix resolver symver checking with DT_GNU_HASH (#204909)
- put .hash section in glibc libraries at the end of RO segment
  when .gnu.hash is present

* Thu Aug 31 2006 Jakub Jelinek <jakub@redhat.com> 2.4.90-28
- another malloc doubly linked list corruption problem fix (#204653)

* Thu Aug 31 2006 Jakub Jelinek <jakub@redhat.com> 2.4.90-27
- allow $LIB and $PLATFORM in dlopen parameters even in suid/sgid (#204399)
- handle $LIB/$PLATFORM in LD_LIBRARY_PATH
- fix splice prototype (#204530)

* Mon Aug 28 2006 Jakub Jelinek <jakub@redhat.com> 2.4.90-26
- real fix for the doubly linked list corruption problem
- try harder in realloc to allocate memory (BZ#2684)
- fix getnameinfo error reporting (#204122)
- make localedef more robust on invalid input (#203728)

* Fri Aug 25 2006 Jakub Jelinek <jakub@redhat.com> 2.4.90-25
- temporarily back out code to limit number of unsorted block
  sort iterations (#203735, #204027)
- handle PLT symbols in dladdr properly (BZ#2683)
- avoid malloc infinite looping for allocations larger than
  the system can allocate (#203915)

* Tue Aug 22 2006 Jakub Jelinek <jakub@redhat.com> 2.4.90-23
- malloc fixes, especially for 32-bit arches (#202309)
- further *_IN locale fixes (#200230)
- fix get{serv,rpc}ent{,_r} if NIS map is empty (#203237)
- fix /usr/bin/iconv (#203400)

* Fri Aug 18 2006 Jakub Jelinek <jakub@redhat.com> 2.4.90-22
- rebuilt with latest binutils to pick up 64K -z commonpagesize
  on ppc/ppc64 (#203001)

* Tue Aug 15 2006 Jakub Jelinek <jakub@redhat.com> 2.4.90-21
- if some test gets stuck, kill the tee process after make check
  finishes
- build with -mtune=generic on i686 and x86_64

* Tue Aug 15 2006 Jakub Jelinek <jakub@redhat.com> 2.4.90-20
- PTHREAD_PRIO_PROTECT support
- fix errno if nice() fails (#201826)

* Thu Aug 10 2006 Jakub Jelinek <jakub@redhat.com> 2.4.90-19
- adaptive malloc brk/mmap threshold
- fix fchownat to use kernel syscall (if available) on many arches (#201870)
- only define O_DIRECT with -D_GNU_SOURCE on ia64 to match all
  other arches (#201748)

* Mon Aug  7 2006 Jakub Jelinek <jakub@redhat.com> 2.4.90-18
- NIS+ fixes
- fix memusage and xtrace scripts (#200736)
- redirect /sbin/service sshd condrestart std{out,err} to /dev/null
  when executed from glibc_post_upgrade

* Wed Aug  2 2006 Jakub Jelinek <jakub@redhat.com> 2.4.90-17
- typo fix for the dladdr patch
- build i?86 glibc with -mno-tls-direct-seg-refs (#200469)

* Wed Aug  2 2006 Jakub Jelinek <jakub@redhat.com> 2.4.90-16
- fix dladdr on binaries/libraries with only DT_GNU_HASH and no
  DT_HASH (#200635)
- fix early timeout of initgroups data in nscd (#173019)
- add am/pm display to es_PE and es_NI locales (#167101)
- fix nss_compat failures when nis/nis+ unavailable (#192072)

* Mon Jul 31 2006 Roland McGrath <roland@redhat.com> 2.4.90-15
- fix missing destructor calls in dlclose (#197932)
- enable transliteration support in all locales (#196713)
- disallow RTLD_GLOBAL flag for dlmopen in secondary namespaces (#197462)
- PI mutex support

* Tue Jul 10 2006 Jakub Jelinek <jakub@redhat.com> 2.4.90-13
- DT_GNU_HASH support

* Fri Jun 30 2006 Jakub Jelinek <jakub@redhat.com> 2.4.90-12
- buildrequire gettext
- enable fstatat64/newfstatat syscalls even on ppc*/s390*/ia64 (#196494)
- fix out of memory behavior in gettext (#194321)
- fix regex on multi-byte non-UTF-8 charsets (#193873)
- minor NIS+ fixes (#190803)
- don't use cancellable calls in posix_spawn* and only set{u,g}id
  current thread if requested (#193631)

* Wed May 31 2006 Jakub Jelinek <jakub@redhat.com> 2.4.90-11
- don't exit from nscd -i <database> before the database is
  actually invalidated, add locking to prune_cache (#191464)
- build glibc-devel.i386 static libraries with
  -mno-tls-direct-seg-refs -DNO_TLS_DIRECT_SEG_REFS
- RFC3542 support (advanced API for IPv6; #191001, BZ##2693)

* Wed May 24 2006 Jakub Jelinek <jakub@redhat.com> 2.4.90-10
- on i686 make glibc owner of /lib/i686 directory (#192597)
- search parent NIS+ domains (#190803)

* Sun May 21 2006 Jakub Jelinek <jakub@redhat.com> 2.4.90-9
- update from CVS
  - big NIS+ changes

* Fri May 19 2006 Jakub Jelinek <jakub@redhat.com> 2.4.90-8
- update from CVS
  - fix nss_compat when SETENT_BATCH_READ=TRUE is in /etc/default/nss
  - fix RFC3484 precedence table for site-local and ULA addresses (#188364)
  - fix a sunrpc memory leak

* Thu May 11 2006 Jakub Jelinek <jakub@redhat.com> 2.4.90-7
- update from CVS
  - fix tcgetattr (#177965)
  - fix <sys/queue.h> (#191264)

* Fri May  5 2006 Jakub Jelinek <jakub@redhat.com> 2.4.90-6
- update from CVS
- rebuilt using fixed rpm

* Fri May  5 2006 Jakub Jelinek <jakub@redhat.com> 2.4.90-5
- update from CVS
  - some NIS+ fixes
  - allow overriding rfc3484 address sorting tables for getaddrinfo
    through /etc/gai.conf (sample config file included in %%doc directory)

* Mon May  1 2006 Jakub Jelinek <jakub@redhat.com> 2.4.90-4
- update from CVS
  - SETENT_BATCH_READ /etc/default/nss option for speeding up
    some usages of NIS+ (#188246)
  - move debug state change notification (#179208)
  - fix ldd script if one of the dynamic linkers is not installed (#190259)

* Thu Apr 27 2006 Jakub Jelinek <jakub@redhat.com> 2.4.90-3
- update from CVS
  - fix a typo in nscd.conf (#190085)
  - fix handling of SIGHUP in nscd when some caches are disabled (#189978)
  - make nscd paranoia mode working with non-root server-user (#189779)

* Wed Apr 26 2006 Jakub Jelinek <jakub@redhat.com> 2.4.90-2
- update from CVS
  - fix getaddrinfo (#190002)
  - add auto-propagate nscd.conf options (#177154)
  - fix nscd auditing (#169148)

* Tue Apr 25 2006 Jakub Jelinek <jakub@redhat.com> 2.4.90-1
- update from CVS

* Mon Apr 24 2006 Jakub Jelinek <jakub@redhat.com> 2.4-6
- update from CVS
  - NIS+ fixes
  - don't segfault on too large argp key values (#189545)
  - getaddrinfo fixes for RFC3484 (#188364)

* Tue Mar 28 2006 Jakub Jelinek <jakub@redhat.com> 2.4-5
- update from CVS
  - pshared robust mutex support
  - fix btowc and bwtoc in C++ (#186410)
  - fix NIS+ (#186592)
  - don't declare __wcsto*l_internal for non-GCC or if not -O1+ (#185667)
- don't mention nscd failures on 2.0 kernels (#185335)

* Tue Mar  7 2006 Roland McGrath <roland@redhat.com> 2.4-4
- back up %%{ix86} gdb conflicts to < 6.3.0.0-1.111

* Tue Mar  7 2006 Jakub Jelinek <jakub@redhat.com> 2.4-3
- really fix rintl on ppc64

* Tue Mar  7 2006 Jakub Jelinek <jakub@redhat.com> 2.4-2
- accurate unwind info for lowlevellock.h stubs on %%{ix86}
- fix ppc/ppc64 ceill, floorl, rintl, roundl and truncl (BZ#2423)

* Mon Mar  6 2006 Jakub Jelinek <jakub@redhat.com> 2.4-1
- update from CVS
  - glibc 2.4 release

* Mon Mar  6 2006 Jakub Jelinek <jakub@redhat.com> 2.3.91-2
- update from CVS
  - fix sYSMALLOc for MALLOC_ALIGNMENT > 2 * SIZE_SZ (#183895)
  - revert ppc32 malloc alignment patch, it breaks malloc_set_state
    and needs some further thoughts and time (#183894)
- provide accurate unwind info for lowlevellock.h stubs on x86_64

* Thu Mar  2 2006 Jakub Jelinek <jakub@redhat.com> 2.3.91-1
- update from CVS
  - fixes for various arches
- ensure malloc returns pointers aligned to at least
  MIN (2 * sizeof (size_t), __alignof__ (long double))
  (only on ppc32 this has not been the case lately with addition
   of 128-bit long double, #182742)

* Wed Mar  1 2006 Jakub Jelinek <jakub@redhat.com> 2.3.90-39
- update from CVS

* Fri Feb 17 2006 Jakub Jelinek <jakub@redhat.com> 2.3.90-38
- update from CVS
  - robust mutexes rewrite

* Mon Feb 13 2006 Jakub Jelinek <jakub@redhat.com> 2.3.90-37
- update from CVS
  - *at fixes
  - unshare syscall wrapper

* Sat Feb  4 2006 Jakub Jelinek <jakub@redhat.com> 2.3.90-36
- update from CVS
  - fix frequency setting for ITIMER_PROF (#179938, BZ#2268)
  - fix powerpc inline fegetround ()
  - fix nptl_db (#179946)

* Fri Feb  3 2006 Jakub Jelinek <jakub@redhat.com> 2.3.90-35
- update from CVS
  - handle futimesat (fd, NULL, tvp) as futimes (fd, tvp)
- fix <stdlib.h> q{e,f,g}cvt{,_r} for -mlong-double-64

* Thu Feb  2 2006 Jakub Jelinek <jakub@redhat.com> 2.3.90-34
- fix <math.h> with C++ and -mlong-double-64 (#179742)
- add nexttowardl redirect for -mlong-double-64

* Thu Feb  2 2006 Jakub Jelinek <jakub@redhat.com> 2.3.90-33
- update from CVS
  - long double support fixes

* Wed Feb  1 2006 Jakub Jelinek <jakub@redhat.com> 2.3.90-32
- update from CVS
  - 128-bit long double fixes for ppc{,64}, s390{,x} and sparc{,v9},
    alpha 128-bit long double support
- add inotify syscall numbers to the override <asm/unistd.h> headers
  (#179366)

* Mon Jan 30 2006 Jakub Jelinek <jakub@redhat.com> 2.3.90-31
- update from CVS
  - 128-bit long double on ppc, ppc64, s390, s390x and sparc{,v9}
- add some new syscall numbers to the override <asm/unistd.h>
  headers

* Mon Jan  9 2006 Jakub Jelinek <jakub@redhat.com> 2.3.90-30
- update from CVS
  - <pthread.h> initializer fixes for -std=c{8,9}9 on 32-bit
    arches
- avoid writable .rodata (#177121)

* Fri Jan  6 2006 Jakub Jelinek <jakub@redhat.com> 2.3.90-29
- update from CVS
  - make pthread_mutex_t an unnamed union again, as it affects
    libstdc++ ABI mangling

* Fri Jan  6 2006 Jakub Jelinek <jakub@redhat.com> 2.3.90-28
- update from CVS
  - make aio_suspend interruptible by signals (#171968)

* Fri Jan  6 2006 Jakub Jelinek <jakub@redhat.com> 2.3.90-27
- only rely on d_type in 32-bit getdents on s390 for 2.6.11+

* Wed Jan  4 2006 Jakub Jelinek <jakub@redhat.com> 2.3.90-26
- update from CVS
  - for newly linked lio_listio* callers, send per request
    notifications (#170116)
  - fixup nscd -S option removal changes (#176860)
  - remove nonnull attribute from ctermid (#176753)
  - fix PTHREAD_*_INITIALIZER{,_NP} on 64-bit arches
  - SPARC NPTL support for pre-v9 CPUs
- drop support for 2.4.xx and < 2.6.9 kernels

* Mon Jan  2 2006 Jakub Jelinek <jakub@redhat.com> 2.3.90-25
- update from CVS
  - s390{,x} and sparc{,64} pointer mangling fixes
- install a sanitized LinuxThreads <bits/libc-lock.h>

* Mon Jan  2 2006 Jakub Jelinek <jakub@redhat.com> 2.3.90-24
- update from CVS
  - nscd audit changes (#174422)
  - ppc{32,64} vDSO support and ppc32 hp-timing

* Tue Dec 27 2005 Jakub Jelinek <jakub@redhat.com> 2.3.90-23
- update from CVS
  - robust mutexes
- fix transliteration segfaults (#176573, #176583)
- ignore prelink temporaries in ldconfig (#176570)

* Wed Dec 21 2005 Jakub Jelinek <jakub@redhat.com> 2.3.90-22
- update from CVS
  - minor fts fixes
- revert broken _Pragma () workaround
- fix ldconfig on bi-arch architectures (#176316)

* Tue Dec 20 2005 Jakub Jelinek <jakub@redhat.com> 2.3.90-21
- update from CVS
  - fix pointer (de)mangling in gconv_cache.c

* Tue Dec 20 2005 Jakub Jelinek <jakub@redhat.com> 2.3.90-20
- update from CVS
  - time ((void *) 1) should segfault, not return -EFAULT (#174856, BZ#1952)
  - fix errlist generation
- update ulps for GCC 4.1 on IA-64

* Mon Dec 19 2005 Jakub Jelinek <jakub@redhat.com> 2.3.90-19
- update from CVS
  - sysdeps/generic reorg
  - setjmp/longjmp jump pointer mangling
- rebuilt with GCC 4.1-RH prerelease, worked around broken _Pragma ()
  handling in it
- remove glibc-profile subpackage
- use non-PLT calls for malloc/free/realloc/memalign invocations in
  mtrace and mcheck hooks (#175261)
- setjmp/longjmp jump pointer mangling on ppc{,64}/ia64/s390{,x}

* Sat Nov 19 2005 Jakub Jelinek <jakub@redhat.com> 2.3.90-18
- update from CVS
  - change <sys/stat.h> for broken apps that #define const /**/,
    handle non-GCC compilers
  - fix ppc{32,64} strncmp (BZ#1877, #173643, IT#83510)
  - provide shmatt_t typedef in ia64 <sys/shm.h (#173680)
  - support 2nd arg to futimesat being NULL (#173581)

* Wed Nov 16 2005 Jakub Jelinek <jakub@redhat.com> 2.3.90-17
- update from CVS
  - fix <sys/stat.h> in C++
  - {fstat,fchown,rename,unlink}at fixes
  - epoll_wait is now a cancellation point

* Tue Nov 15 2005 Jakub Jelinek <jakub@redhat.com> 2.3.90-16
- update from CVS
- make sure waitid syscall is used on ppc*/s390*

* Thu Oct 20 2005 Jakub Jelinek <jakub@redhat.com> 2.3.90-15
- update from CVS
  - be permissive in %n check because of kernel bug #165351 (#171240)
  - don't misalign stack in pthread_once on x86_64 (#170786, IT#81521)
  - many locale fixes

* Mon Oct 10 2005 Jakub Jelinek <jakub@redhat.com> 2.3.90-14
- update from CVS
  - fix malloc bug after fork introduced in the last update
  - fix getent hosts IP for IPv4 IPs (#169831)

* Mon Oct  3 2005 Jakub Jelinek <jakub@redhat.com> 2.3.90-13
- update from CVS
  - fix setuid etc. hangs if some thread exits during the call (#167766)
  - fix innetgr memory leak (#169051)
  - support > 2GB nscd log files (#168851)
  - too many other changes to list here
- include errno in nscd message if audit_open failed (#169148)

* Mon Sep 12 2005 Jakub Jelinek <jakub@redhat.com> 2.3.90-12
- update from CVS
  - netgrp handling fixes (#167728)
  - fix memory leak in setlocale (BZ#1318)
  - fix hwcaps computation
  - several regex portability improvements (#167019)
  - hypotf fix
  - fix *printf return code if underlying write fails (BZ#1146)
  - PPC64 dl{,v}sym fixes for new ABI .opd symbols
- fix calloc with MALLOC_PERTURB_ in environment on 64-bit architectures
  (#166719)
- source /etc/sysconfig/nscd (if it exists) in /etc/rc.d/init.d/nscd
  (#167083)
- add %%triggerin for tzdata to glibc-common, so that tzdata updates
  update /etc/localtime and /var/spool/postfix/etc/localtime if they
  exist (#167787)

* Mon Aug 29 2005 Jakub Jelinek <jakub@redhat.com> 2.3.90-11
- FUTEX_WAKE_OP support to speed up pthread_cond_signal

* Wed Aug 24 2005 Jakub Jelinek <jakub@redhat.com> 2.3.90-10
- update from CVS
  - fix growing of nscd persistent database (BZ#1204)
  - fix _FORTIFY_SOURCE mbstowcs and wcstombs if destination size
    is known at compile time, but length argument is not

* Mon Aug 22 2005 Jakub Jelinek <jakub@redhat.com> 2.3.90-9
- update from CVS
  - fix resolving over TCP (#161181, #165802)
  - on ia64 don't abort on unhandled math function exception codes
    (#165693)

* Mon Aug  8 2005 Jakub Jelinek <jakub@redhat.com> 2.3.90-8
- update from CVS
  - nscd persistent database verifier (#164001)
  - cleanup _FORTIFY_SOURCE bits/*.h headers (#165000)
  - handle EINTR in sigwait properly
- make sure poor man's stack guard randomization keeps first
  byte 0 even on big-endian 32-bit arches
- fix {elf,nptl}/tst-stackguard1
- obsolete linuxthreads-devel in glibc-devel

* Fri Jul 29 2005 Jakub Jelinek <jakub@redhat.com> 2.3.90-7
- update from CVS
- do some poor man's stack guard randomization even without
  the costly --enable-stackguard-randomization
- rebuilt with new GCC to make it use -msecure-plt on PPC32

* Mon Jul 25 2005 Jakub Jelinek <jakub@redhat.com> 2.3.90-6
- update from CVS
  - fix execvp if PATH is not in environment and the call is going
    to fail (BZ#1125)
  - another bits/wchar2.h fix (#163990)

* Fri Jul 22 2005 Jakub Jelinek <jakub@redhat.com> 2.3.90-5
- update from CVS
  - fix stubs.h generation
- don't use _G_va_list in bits/wchar2.h

* Fri Jul 22 2005 Jakub Jelinek <jakub@redhat.com> 2.3.90-4
- update from CVS
  - make sure bits/wchar2.h header is installed
  - fix __getgroups_chk return type

* Thu Jul 21 2005 Jakub Jelinek <jakub@redhat.com> 2.3.90-3
- update from CVS
  - make sure nscd cmsg buffers aren't misaligned, handle EINTR from
    poll when contacting nscd more gracefully
  - remove malloc attribute from posix_memalign
  - correctly size nscd buffer for grpcache key (#163538)
  - fix atan2f
  - fix error memory leaks
  - some more _FORTIFY_SOURCE protection

* Fri Jul  8 2005 Jakub Jelinek <jakub@redhat.com> 2.3.90-2
- update from CVS
  - ia64 stack protector support
  - handle DNS referral results as server errors (#162625)
  - ctan{,h}{,f,l} fixes (#160759)
  - pass argc, argv and envp also to executable's *ni_array
    functions (BZ#974)
  - add ellipsis to clone prototype (#161593)
  - fix glibc-profile (#162601)
  - nss_compat fixes
- use sysdeps/generic version of <bits/stdio-lock.h> in installed
  headers instead of NPTL version (#162634)

* Mon Jun 27 2005 Jakub Jelinek <jakub@redhat.com> 2.3.90-1
- update from CVS
  - stack protector support
  - fix xdr_{,u_}{longlong_t,hyper} on 64-bit arches (#161583)
- enable @GLIBC_2.4 symbols
- remove linuxthreads

* Mon Jun 20 2005 Jakub Jelinek <jakub@redhat.com> 2.3.5-11
- update from CVS
  - PPC32 -msecure-plt support
  - support classes keyword in /etc/hesiod.conf (#150350)
  - add RLIMIT_NICE and RLIMIT_RTPRIO to <sys/resources.h> (#157049)
  - decrease number of .plt relocations in libc.so
  - use -laudit in nscd (#159217)
  - handle big amounts of networking interfaces in getifaddrs/if_nameindex
    (#159399)
  - fix pa_IN locale's am_pm (#158715, BZ#622)
  - fix debugging of PIEs

* Mon May 30 2005 Jakub Jelinek <jakub@redhat.com> 2.3.5-10
- fix LD_ASSUME_KERNEL (since 2.3.5-8 GLRO(dl_osversion)
  has been always overwritten with the version of currently
  running kernel)
- remove linuxthreads man pages other than those covered in
  3p section, as 3p man pages are far better quality and describe
  POSIX behaviour that NPTL implements (#159084)

* Tue May 24 2005 Jakub Jelinek <jakub@redhat.com> 2.3.5-9
- update from CVS
  - increase bindresvport's LOWPORT to 512, apparently some
    broken daemons don't think 0 .. 511 ports are reserved

* Mon May 23 2005 Jakub Jelinek <jakub@redhat.com> 2.3.5-8
- update from CVS
  - fix kernel version check in ld.so
- fix sendfile{,64} prototypes (BZ#961)
- try more ports in bindresvport if all 600..1023 are
  used, don't use priviledged ports when talking to portmap
  (#141773)

* Fri May 20 2005 Jakub Jelinek <jakub@redhat.com> 2.3.5-7
- update from CVS
  - make regexec thread safe (BZ#934)
- fix statically linked programs on i?86, x86_64, s390* and
  sparc* (#158027)
- fix IBM939 iconv module (BZ#955)

* Wed May  4 2005 Jakub Jelinek <jakub@redhat.com> 2.3.5-6
- update from CVS
  - fix cancellation on i?86
  - add call frame information to i?86 assembly

* Tue May  3 2005 Jakub Jelinek <jakub@redhat.com> 2.3.5-5
- update from CVS
  - add some more UTF-8 locales (#156115)
- clean up /lib64/tls instead of /lib/tls on x86-64, s390x and
  ppc64 in glibc_post_upgrade (#156656)
- fix posix_fallocate{,64} (#156289)

* Thu Apr 28 2005 Jakub Jelinek <jakub@redhat.com> 2.3.5-4
- update from CVS
  - fix nscd cache pruning (#150748)

* Wed Apr 27 2005 Jakub Jelinek <jakub@redhat.com> 2.3.5-3
- update from CVS
  - fix linuxthreads clocks
- put xen libs into the glibc-2*.i686 package instead of a separate one
- fix librt.so symlink in linuxthreads-devel
- do not include linuxthreads-devel on %{auxarches},
  just on the base architectures

* Wed Apr 27 2005 Jakub Jelinek <jakub@redhat.com> 2.3.5-2
- update from CVS
  - with MALLOC_CHECK_=N N>0 (#153003)
  - fix recursive dlclose (#154641)
  - handle %z in strptime (#154804)
  - automatically append /%{_lib}/obsolete/linuxthreads/
    to standard library search path if LD_ASSUME_KERNEL=N N <= 2.4.19
    or for glibc 2.0 binaries (or broken ones that don't use errno/h_errno
    properly).  Warning: all those will stop working when LinuxThreads
    is finally nuked, which is not very far away
  - remove nonnull attribute from acct prototype (BZ#877)
  - kernel CPU clocks support
  - fix *scanf in locales with multi-byte decimal point

* Wed Apr 27 2005 Roland McGrath <roland@redhat.com>
- glibc-xen subpackage for i686

* Fri Apr 15 2005 Roland McGrath <roland@redhat.com> 2.3.5-1
- update from CVS
  - fix execvp regression (BZ#851)
  - ia64 libm updates
  - sparc updates
  - fix initstate{,_r}/strfry (#154504)
  - grok PT_NOTE in vDSO for kernel version and extra hwcap dirs,
    support "hwcap" keyword in ld.so.conf files

* Tue Apr  4 2005 Jakub Jelinek <jakub@redhat.com> 2.3.4-21
- update from CVS
  - fix xdr_rmtcall_args on 64-bit arches (#151686)
- fix <pthread.h> and <bits/libc-lock.h> with -std=c89 -fexceptions (#153774)

* Mon Apr  4 2005 Jakub Jelinek <jakub@redhat.com> 2.3.4-20
- move LinuxThreads libraries to /%{_lib}/obsolete/linuxthreads/
  and NPTL libraries to /%{_lib}.  To run a program against LinuxThreads,
  LD_ASSUME_KERNEL=2.4.xx LD_LIBRARY_PATH=/%{_lib}/obsolete/linuxthreads/
  is now needed
- bzip2 ChangeLog* files instead of gzipping them

* Sat Apr  2 2005 Jakub Jelinek <jakub@redhat.com> 2.3.4-19
- update from CVS
  - fix nextafterl and several other libm routines on ia64
  - fix initgroups (BZ#661)
- kill nptl-devel subpackage, add linuxthreads-devel,
  compile and link by default against NPTL and only with
  -I/usr/include/linuxthreads -L/usr/%{_lib}/linuxthreads
  against LinuxThreads
- package /usr/lib/debug/%{_lib}/tls/i{5,6}86 symlinks in
  i386 glibc-debuginfo
- limit number of ChangeLog* files in glibc-common %%doc
  to last 2.5 years of changes only to save space

* Fri Mar 25 2005 Jakub Jelinek <jakub@redhat.com> 2.3.4-18
- fix build on 64-bit arches with new GCC

* Thu Mar 24 2005 Jakub Jelinek <jakub@redhat.com> 2.3.4-17
- update from CVS
  - fix LD_AUDIT in LinuxThreads ld.so
  - fix calloc with M_PERTURB
  - fix error handling in pthread_create with PTHREAD_EXPLICIT_SCHED
    on ppc*/ia64/alpha/mips (BZ#801)
  - fix a typo in WINDOWS-31J charmap (#151739)
  - fix NIS ypprot_err (#151469)

* Sun Mar 20 2005 Jakub Jelinek <jakub@redhat.com> 2.3.4-16
- fix pread with -D_FILE_OFFSET_BITS=64 (#151573)

* Sat Mar 19 2005 Jakub Jelinek <jakub@redhat.com> 2.3.4-15
- update from CVS
  - better fix for the dlclose bug (#145810, #150414)
  - fix regex crash on case insensitive search in zh_CN locale
    (#151215)
  - fix malloc_trim (BZ#779)
  - with -D_FORTIFY_SOURCE=*, avoid defining read and a bunch of others
    as function-like macros, there are too many broken programs
    out there
- add %%dir %{_prefix}/%{_lib}/gconv to glibc's file list (#151372)

* Sun Mar  6 2005 Roland McGrath <roland@redhat.com> 2.3.4-14
- fix bits/socket2.h macro typos

* Sat Mar  5 2005 Jakub Jelinek <jakub@redhat.com> 2.3.4-12
- fix tst-chk{2,3}
- fix up AS_NEEDED directive in /usr/%{_lib}/libc.so
- BuildReq binutils >= 2.15.94.0.2-1 for AS_NEEDED, in
  glibc-devel Conflict with binutils < 2.15.94.0.2-1

* Thu Mar  3 2005 Jakub Jelinek <jakub@redhat.com> 2.3.4-11
- update from CVS
  - fix execvp (#149290)
  - fix dlclose (#145810)
  - clear padding in gconv-modules.cache (#146614, BZ#776)
- rebuilt with GCC4
- changed __GLIBC_MINOR__ for now back to 3
- back out the newly added GLIBC_2.4 *_chk routines, instead
  do the checking in macros

* Sat Feb 12 2005 Jakub Jelinek <jakub@redhat.com> 2.3.4-10
- hopefully fix interaction with prelink (#147655)

* Fri Feb 11 2005 Jakub Jelinek <jakub@redhat.com> 2.3.4-9
- update from CVS
  - bi-arch <gnu/stubs.h> (BZ#715)

* Fri Feb 11 2005 Jakub Jelinek <jakub@redhat.com> 2.3.4-8
- update from CVS
  - bi-arch <gnu/lib-names.h> (BZ#632)
  - fix libdl on s390 and maybe other platforms
  - fix initstate{,_r} (BZ#710)
  - fix <gnu/stubs.h> generation (BZ#157)
- define CMSPAR in bits/termios.h (#147533)

* Tue Feb  8 2005 Jakub Jelinek <jakub@redhat.com> 2.3.4-7
- update from CVS
  - fix TLS handling in linuxthreads

* Tue Feb  8 2005 Jakub Jelinek <jakub@redhat.com> 2.3.4-6
- update from CVS
  - ld.so auditing
  - fix segfault if chrooted app attempts to dlopen a library
    and no standard library directory exists at all (#147067, #144303)
  - fix initgroups when nscd is running, but has group caching disabled
    (#146588)
  - fix pthread_key_{create,destroy} in LinuxThreads when pthread_create
    has not been called yet (#146710)
  - fix ppc64 swapcontext and setcontext (#146736, BZ#700)
  - service nscd cosmetic fixes (#146776)
  - fix IA-32 and x86-64 stack alignment in DSO constructors (#145689)
  - fix zdump -v segfaults on x86-64 (#146210)
  - avoid calling sigaction (SIGPIPE, ...) inside syslog (#146021, IT#56686)
  - fix errno values for futimes (BZ#633)
  - unconditionally include <features.h> in malloc.h (BZ#650)
  - change regex \B handling to match old GNU regex as well as perl/grep's dfa
    (from empty string inside of word to empty string not at a word boundary,
     BZ#693)
  - slightly optimize i686 TLS accesses, use direct TLS %gs access in sem_*
    and allow building -mno-tls-direct-seg-refs glibc that is free of direct TLS
    %gs access with negative offsets
  - fix addseverity
  - fix fmemopen
  - fix rewinddir
  - increase svc{tcp,unix}_create listen backlog

* Thu Jan  6 2005 Jakub Jelinek <jakub@redhat.com> 2.3.4-5
- update from CVS
  - add some warn_unused_result marking
  - make ftruncate available even for just -D_POSIX_C_SOURCE=200112L
    (BZ#640)

* Thu Jan  6 2005 Jakub Jelinek <jakub@redhat.com> 2.3.4-4
- update from CVS
  - fix IA-32 stack alignment for LinuxThreads thread functions
    and functions passed to clone(2) directly
  - fix ecvt{,_r} on denormals (#143279)
  - fix __tls_get_addr typo
  - fix rounding in IA-64 alarm (#143710)
  - don't reinitialize __environ in __libc_start_main, so that
    effects of setenv/putenv done in DSO initializers are preserved
    (#144037, IT#57403)
  - fix fmemopen
  - fix vDSO l_map_end and l_text_end values
  - IA64 libm update (#142494)
- fix ppc rint/ceil etc. (BZ#602)

* Tue Dec 21 2004 Jakub Jelinek <jakub@redhat.com> 2.3.4-3
- rebuilt

* Mon Dec 20 2004 Jakub Jelinek <jakub@redhat.com> 2.3.4-2
- work around rpm bug some more, this time by copying
  iconvconfig to iconvconfig.%%{_target_cpu}.

* Mon Dec 20 2004 Jakub Jelinek <jakub@redhat.com> 2.3.4-1
- update from CVS
  - glibc 2.3.4 release
  - add -o and --nostdlib options to iconvconfig
- if /sbin/ldconfig doesn't exist when running
  glibc_post_upgrade.%%{_target_cpu}, just don't attempt to run it.
  This can happen during first install of bi-arch glibc and the
  other arch glibc's %post wil run /sbin/ldconfig (#143326)
- use -o and --nostdlib options to create all needed
  gconv-modules.cache files on bi-arch setups

* Sun Dec 19 2004 Jakub Jelinek <jakub@redhat.com> 2.3.3-99
- rebuilt

* Sat Dec 18 2004 Jakub Jelinek <jakub@redhat.com> 2.3.3-98
- add .%%{_target_cpu} to glibc_post_upgrade, only run telinit u
  if /sbin/init is the same ELF class and machine as
  glibc_post_upgrade.%%{_target_cpu} and similarly with
  condrestarting sshd (#143046)

* Fri Dec 17 2004 Jakub Jelinek <jakub@redhat.com> 2.3.3-97
- update from CVS
  - fix ppc64 getcontext and swapcontext (BZ#610)
  - sparc/sparc64 fixes

* Wed Dec 15 2004 Jakub Jelinek <jakub@redhat.com> 2.3.3-96
- update from CVS
  - fix i686 __USE_STRING_INLINES strncat
  - make sure ppc/ppc64 maintain correct stack alignment
    across clone

* Wed Dec 15 2004 Jakub Jelinek <jakub@redhat.com> 2.3.3-95
- export nis_domain_of_r from libnsl.so again which was
  unintentionally lost

* Wed Dec 15 2004 Jakub Jelinek <jakub@redhat.com> 2.3.3-93
- update from CVS
  - ppc/ppc64 clone without CLONE_THREAD getpid () adjustement
  - fix MALLOC_CHECK_={1,2,3} for non-contiguous main arena
    (BZ#457)
  - fix sysconf (_POSIX_V6_*) for other ABI environments in
    bi-arch setups
- s390/s390x clone without CLONE_THREAD getpid () adjustement

* Tue Dec 14 2004 Jakub Jelinek <jakub@redhat.com> 2.3.3-92
- update from CVS
- fix %{_prefix}/libexec/getconf filenames generation

* Tue Dec 14 2004 Jakub Jelinek <jakub@redhat.com> 2.3.3-91
- update from CVS
  - double buffer size in getXXbyYY or getXXent on ERANGE
    instead of adding BUFLEN (#142617)
  - avoid busy loop in malloc if another thread is doing fork
    (#142214)
  - some more realloc corruption checks
  - fix getconf _POSIX_V6_WIDTH_RESTRICTED_ENVS output,
    tweak %{_prefix}/libexec/getconf/ filenames

* Fri Dec 10 2004 Jakub Jelinek <jakub@redhat.com> 2.3.3-90
- update from CVS
  - regex speedups
  - use | cat in ldd if running under bash3+ to allow running
    it on binaries that are not through SELinux allowed to access
    console or tty
- add __NR_waitid defines for alpha and ia64

* Wed Dec  8 2004 Jakub Jelinek <jakub@redhat.com> 2.3.3-89
- update from CVS
  - fix clone2 on ia64
  - avoid tst-timer5 failing with linuxthreads implementation
- if __libc_enable_secure, disallow mode != normal
- change ldd script to imply -r when -u is used, properly
  propagate return value and handle suid binaries

* Tue Dec  7 2004 Jakub Jelinek <jakub@redhat.com> 2.3.3-88
- update from CVS
  - disregard LD_SHOW_AUXV and LD_DYNAMIC_WEAK if __libc_enable_secure
  - disregard LD_DEBUG if __libc_enable_secure in normal mode
    if /suid-debug doesn't exist
  - fix fseekpos after ungetc
  - avoid reading bytes before start of buffers in regex's
    check_dst_limits_calc_pos_1 (#142060)
  - make getpid () working with clone/clone2 without CLONE_THREAD
    (so far on i386/x86_64/ia64 only)
- move %{_prefix}/libexec/getconf/* to glibc from glibc-common
- make %{_prefix}/libexec/getconf directory owned by glibc package

* Fri Dec  3 2004 Jakub Jelinek <jakub@redhat.com> 2.3.3-87
- update from CVS
  - build libpthread_nonshared.a objects with -fPIC on s390/s390x
  - fix mktime with < 0 or > 59 tm_sec on entry
  - remove nonnull attribute for realpath
  - add $(make-target-directory) for errlist-compat.c rule
    (hopefully fix #141404)
- add testcase for ungetc bug
- define _POSIX_{,THREAD_}CPUTIME to 0 on all Linux arches

* Tue Nov 30 2004 Jakub Jelinek <jakub@redhat.com> 2.3.3-86
- update from CVS
  - some posix_opt.h fixes
- fix strtold use of unitialized memory (#141000)
- some more bugfixes for bugs detected by valgrind
- rebuilt with GCC >= 3.4.3-5 to avoid packed stack layout
  on s390{,x} (#139678)

* Fri Nov 26 2004 Jakub Jelinek <jakub@redhat.com> 2.3.3-85
- update from CVS
  - support -v specification in getconf
  - fix sysconf (_SC_LFS64_CFLAGS) etc.
  - avoid thread stack aliasing issues on EM64T (#140803)
- move %{_prefix}/include/nptl headers from nptl-devel
  to glibc-headers, so that even NPTL specific programs
  can be built bi-arch without problems

* Wed Nov 24 2004 Jakub Jelinek <jakub@redhat.com> 2.3.3-84
- update from CVS
  - fix memory leak in getaddrinfo if using nscd (#139559)
  - handle large lines in /etc/hosts and /etc/networks
    (#140378)
  - add nonnull attributes to selected dirent.h and dlfcn.h
    functions

* Sun Nov 21 2004 Jakub Jelinek <jakub@redhat.com> 2.3.3-83
- update from CVS
  - add deprecated and/or nonnull attribute to some signal.h
    functions
  - speed up tzset () by only using stat instead of open/fstat
    when calling tzset for the second and following time if
    /etc/localtime has not changed
- fix tgamma (BZ #552)

* Sat Nov 20 2004 Jakub Jelinek <jakub@redhat.com> 2.3.3-82
- update from CVS
  - some malloc () checking
  - libpthread.a object dependency cleanups (#115157)
  - <bits/socket.h> fix for -std=c89 -pedantic-errors (#140132)

* Fri Nov 19 2004 Jakub Jelinek <jakub@redhat.com> 2.3.3-81
- don't use chunksize in <= 2 * SIZE_SZ free () checks

* Fri Nov 19 2004 Jakub Jelinek <jakub@redhat.com> 2.3.3-80
- update from CVS
  - with -D_FORTIFY_SOURCE=2, prevent missing %N$ formats
  - for -D_FORTIFY_SOURCE=2 and %n in writable format string,
    issue special error message instead of using the buffer overflow
    detected one
  - speedup regex searching with REG_NOSUB, add RE_NO_SUB,
    speedup searching with nested subexps (BZ #544)
  - block SIGCANCEL in NPTL timer_* helper thread
- further free () checking

* Tue Nov 16 2004 Jakub Jelinek <jakub@redhat.com> 2.3.3-79
- update from CVS
- fix free () checking
- move /etc/default/nss into glibc-common (hopefully fix #132392)

* Mon Nov 15 2004 Jakub Jelinek <jakub@redhat.com> 2.3.3-78
- update from CVS
  - fix LD_DEBUG=statistics
  - issue error message before aborting in __chk_fail ()
- some more free () checking

* Fri Nov 12 2004 Jakub Jelinek <jakub@redhat.com> 2.3.3-77
- update from CVS
  - speedup regex on palindromes (BZ #429)
  - fix NPTL set{,e,re,res}[ug]id, so that even if making process
    less priviledged all threads change their credentials successfully

* Wed Nov 10 2004 Jakub Jelinek <jakub@redhat.com> 2.3.3-76
- update from CVS
  - fix regcomp crash (#138439)
  - fix ftell{,o,o64} (#137885)
  - robustification of nscd to cope with corrupt databases (#137140)
  - fix NPTL with pthread_exit immediately after pthread_create (BZ #530)
  - some regex optimizations

* Tue Nov  2 2004 Jakub Jelinek <jakub@redhat.com> 2.3.3-75
- update from CVS
  - mktime cleanups (BZ #487, #473)
  - unique comments in free(3) check error messages
- adjust some x86_64 headers for -m32 (#129712)
- object size checking support even with GCC-3.4.2-RH >= 3.4.2-8

* Wed Oct 27 2004 Jakub Jelinek <jakub@redhat.com> 2.3.3-74
- fix <netinet/udp.h> header
- fix globfree (#137176)
- fix exiting if there are dlmopened libraries in namespaces
  other than main one not closed yet
- export again _res_opcodes and __p_{class,type}_syms from
  libresolv.so that were lost in -69

* Thu Oct 21 2004 Jakub Jelinek <jakub@redhat.com> 2.3.3-73
- remove setaltroot and key{_add,_request,ctl} also from Versions
- back out _sys_errlist changes

* Thu Oct 21 2004 Jakub Jelinek <jakub@redhat.com> 2.3.3-72
- back out setaltroot and key{_add,_request,ctl} addition
- fix severe x86-64 symbol versioning regressions that breaks
  e.g. java binaries

* Wed Oct 20 2004 Jakub Jelinek <jakub@redhat.com> 2.3.3-71
- update from CVS
  - fix minor catchsegv temp file handling vulnerability
    (CAN-2004-0968, #136319)
  - add 4 new errno codes
  - setaltroot, key{_add,_request,ctl} syscalls on some arches
  - export _dl_debug_state@GLIBC_PRIVATE from ld.so again for
    gdb purpose
  - use inet_pton to decide what is address and what is hostname
    in getent (#135422)
  - change dladdr/dladdr1, so that dli_saddr is the same kind
    of value as dlsym/dlvsym return (makes difference on ia64/hppa only)
  - fix catchsegv script so that it works with both 32-bit and 64-bit
    programs on multi-arch platforms

* Tue Oct 19 2004 Jakub Jelinek <jakub@redhat.com> 2.3.3-70
- update from CVS
- require newer selinux-policy (#135978)
- add %%dir for /var/run/nscd and /var/db/nscd and %%ghost
  files in it
- conflict with gcc4 4.0.0-0.6 and earlier (needs __builtin_object_size)

* Mon Oct 18 2004 Jakub Jelinek <jakub@redhat.com> 2.3.3-69
- update from CVS
  - object size checking support (-D_FORTIFY_SOURCE={1,2})

* Thu Oct 14 2004 Jakub Jelinek <jakub@redhat.com> 2.3.3-68
- update from CVS
  - support for namespaces in the dynamic linker
  - fix dlclose (BZ #77)
  - libSegFault.so uses now backtrace() to work on IA-64, x86-64
    and s390 (#130254)

* Tue Oct 12 2004 Jakub Jelinek <jakub@redhat.com> 2.3.3-67
- update from CVS
  - use non-blocking sockets in resolver (#135234)
  - reset pd->res options on thread exit, so that threads
    reusing cached stacks get resolver state properly initialized
    (BZ #434)

* Wed Oct  6 2004 Jakub Jelinek <jakub@redhat.com> 2.3.3-66
- update from CVS
- avoid using perl in the spec file, buildrequire sed >= 3.95
  (#127671)
- export TIMEOUTFACTOR=16
- fix _JMPBUF_CFA_UNWINDS_ADJ on s390{,x}

* Tue Oct  5 2004 Jakub Jelinek <jakub@redhat.com> 2.3.3-65
- update from CVS
  - define _POSIX_THREAD_PROCESS_SHARED and _POSIX_CLOCK_SELECTION
    to -1 in LinuxThreads
  - define _POSIX_CPUTIME and _POSIX_THREAD_CPUTIME to 0
    on i?86/ia64 and make sure sysconf (_SC_{,THREAD_}CPUTIME)
    returns correct value
- if _POSIX_CLOCK_SELECTION == -1 in nscd, still try
  sysconf (_SC_CLOCK_SELECTION) and if it returns true,
  dlopen libpthread.so and dlsym pthread_condattr_setclock
- build nscd with -z relro and -z now

* Mon Oct  4 2004 Jakub Jelinek <jakub@redhat.com> 2.3.3-64
- update from CVS
  - stop using __builtin_expect in assert and assert_perror
    (#127606)
  - try to avoid too much VA fragmentation with malloc
    on flexmap layout (#118574)
  - nscd robustification
  - change valloc to use debugging hooks (#134385)
- make glibc_post_upgrade more verbose on errors (Fergal Daly,
  #125700)

* Fri Oct  1 2004 Jakub Jelinek <jakub@redhat.com> 2.3.3-63
- update from CVS
  - fix __nscd_getgrouplist
  - fix a typo in x86_64 pthread_mutex_timedwait fix

* Fri Oct  1 2004 Jakub Jelinek <jakub@redhat.com> 2.3.3-62
- update from CVS
  - fix NPTL pthread_mutex_timedwait on i386/x86_64 (BZ #417)

* Thu Sep 30 2004 Jakub Jelinek <jakub@redhat.com> 2.3.3-61
- update from CVS
  - some nscd fixes (#134193)
  - cache initgroups in nscd (#132850)
  - reread /etc/localtime in tzset () even if just mtime changed
    (#133481)
  - fix glob (#126460)
  - another get_myaddress fix

* Wed Sep 29 2004 Jakub Jelinek <jakub@redhat.com> 2.3.3-60
- update from CVS
  - fix get_myaddress (#133982)
  - remove nonnull attribute from second utime argument (#133866)
  - handle SIGSETXID the same way as SIGCANCEL in
    sigaction/pthread_kill/sigwait/sigwaitinfo etc.
  - add __extension__ to long long types in NPTL <bits/pthreadtypes.h>

* Mon Sep 27 2004 Jakub Jelinek <jakub@redhat.com> 2.3.3-59
- update from CVS
  - fix BZ #151, #362, #381, #407
  - fdim fix for +inf/+inf (BZ #376)

* Sun Sep 26 2004 Jakub Jelinek <jakub@redhat.com> 2.3.3-58
- update from CVS
  - vasprintf fix (BZ #346)
  - gettext locking (BZ #322)
- change linuxthreads useldt.h inclusion login again, the last
  one failed all linuxthreads FLOATING_STACKS tests

* Sat Sep 25 2004 Jakub Jelinek <jakub@redhat.com> 2.3.3-57
- update from CVS
  - fix setuid in LD_ASSUME_KERNEL=2.2.5 libc (#133558)
  - fix nis locking (#132204)
  - RTLD_DEEPBIND support
  - fix pthread_create bugs (BZ #401, #405)

* Wed Sep 22 2004 Roland McGrath <roland@redhat.com> 2.3.3-56
- migrated CVS to fedora-branch in sources.redhat.com glibc repository
  - source tarballs renamed
  - redhat/ moved to fedora/, some old cruft removed
- update from trunk
  - some __nonnull annotations

* Wed Sep 22 2004 Jakub Jelinek <jakub@redhat.com> 2.3.3-55
- update from CVS
  - set{re,e,res}[ug]id now affect the whole process in NPTL
  - return EAGAIN instead of ENOMEM when not enough memory
    in pthread_create

* Fri Sep 17 2004 Jakub Jelinek <jakub@redhat.com> 2.3.3-54
- update from CVS
  - nscd getaddrinfo caching

* Tue Sep 14 2004 Jakub Jelinek <jakub@redhat.com> 2.3.3-53
- restore temporarily old definition of __P()/__PMT()
  for third party apps

* Tue Sep 14 2004 Jakub Jelinek <jakub@redhat.com> 2.3.3-52
- update from CVS
  - nscd bi-arch fix
  - remove all uses of __P()/__PMT() from glibc headers
- update and reenable nscd SELinux patch
- remove libnss1* and libnss*.so.1 compatibility NSS modules
  on IA-32, SPARC and Alpha

* Fri Sep 10 2004 Jakub Jelinek <jakub@redhat.com> 2.3.3-51
- update from CVS
  - disable one of the malloc double free checks for non-contiguous
    arenas where it doesn't have to be true even for non-broken
    apps

* Thu Sep  9 2004 Jakub Jelinek <jakub@redhat.com> 2.3.3-50
- update from CVS
  - pwd/grp/host loops with nscd speed up by sharing the
    nscd cache r/o with applications
  - inexpensive double free check in free(3)
  - make NPTL pthread.h initializers usable even from C++
    (BZ #375)
- use atomic instructions even in i386 nscd on i486+ CPUs
  (conditionally)

* Sat Sep  3 2004 Jakub Jelinek <jakub@redhat.com> 2.3.3-49
- update from CVS
- fix linuxthreads tst-cancel{[45],-static}

* Fri Sep  3 2004 Jakub Jelinek <jakub@redhat.com> 2.3.3-48
- update from CVS
  - fix pthread_cond_destroy (BZ #342)
  - fix fnmatch without FNM_NOESCAPE (BZ #361)
  - fix ppc32 setcontext (BZ #357)
- add NPTL support for i386 glibc (only if run on i486 or higher CPU)
- add __NR_waitid defines for i386, x86_64 and sparc*

* Tue Aug 31 2004 Jakub Jelinek <jakub@redhat.com> 2.3.3-47
- update from CVS
  - persistent nscd caching
  - ppc64 32-bit atomicity fix
  - fix x86-64 nptl-devel headers for -m32 compilation
- %%ghost /etc/ld.so.cache (#130597)
- edit /etc/ld.so.conf in glibc_post_upgrade if
  include ld.so.conf.d/*.conf line is missing (#120588)
- ugly hacks for the IA-64 /emul braindamage (#124996, #128267)

* Sat Aug 21 2004 Jakub Jelinek <jakub@redhat.com> 2.3.3-46
- update from CVS

* Thu Aug 19 2004 Jakub Jelinek <jakub@redhat.com> 2.3.3-45
- update from CVS
  - fix nss_compat's initgroups handling (#130363)
  - fix getaddrinfo ai_canonname setting

* Thu Aug 19 2004 Jakub Jelinek <jakub@redhat.com> 2.3.3-44
- update from CVS
  - add ip6-dotint resolv.conf option, make
    no-ip6-dotint the default
- BuildPrereq libselinux-devel (#129946)
- on ppc64, build without dot symbols

* Thu Aug 12 2004 Jakub Jelinek <jakub@redhat.com> 2.3.3-43
- update from CVS
  - remove debugging printout (#129747)
  - make <sys/shm.h> usable in C++ (IT#45148)
- update RLIMIT_* constants in <bits/resource.h>, make
  <sys/resource.h> POSIX compliant (#129740)

* Wed Aug 11 2004 Jakub Jelinek <jakub@redhat.com> 2.3.3-42
- fix last tzset () fixes, disable rereading of /etc/localtime
  every time for now
- really enable SELinux support for NSCD

* Wed Aug 11 2004 Jakub Jelinek <jakub@redhat.com> 2.3.3-41
- update from CVS
  - fread_unlocked/fwrite_unlocked macro fixes (BZ #309, #316)
  - tzset () fixes (BZ #154)
- speed up pthread_rwlock_unlock on arches other than i386 and
  x86_64 (#129455)
- fix compilation with -ansi (resp. -std=c89 or -std=c99) and
  -D_XOPEN_SOURCE=[56]00 but no -D_POSIX_SOURCE* or -D_POSIX_C_SOURCE*
  (BZ #284)
- add SELinux support for NSCD

* Fri Aug  6 2004 Jakub Jelinek <jakub@redhat.com> 2.3.3-40
- update from CVS
  - change res_init to force all threads to re-initialize
    resolver before they use it next time (#125712)
  - various getaddrinfo and related fixes (BZ #295, #296)
  - fix IBM{932,943} iconv modules (#128674)
  - some nscd fixes (e.g. BZ #292)
  - RFC 3678 support (Multicast Source Filters)
- handle /lib/i686/librtkaio-* in i386 glibc_post_upgrade
  the same as /lib/i686/librt-*

* Fri Jul 23 2004 Jakub Jelinek <jakub@redhat.com> 2.3.3-39
- update from CVS
  - conformance related changes in headers
- remove -finline-limit=2000 for GCC 3.4.x+

* Thu Jul 22 2004 Jakub Jelinek <jakub@redhat.com> 2.3.3-38
- update from CVS
  - fix res_init leaks
  - fix newlocale races
  - fix ppc64 setjmp
- fix strtold (BZ #274)

* Fri Jul 16 2004 Jakub Jelinek <jakub@redhat.com> 2.3.3-37
- update from CVS
  - allow pthread_cancel in DSO destructors run at exit time
- fix pow{f,,l} on IA-32 and powl on x86-64
- allow PIEs on IA-32 to have main in a shared library they depend on

* Mon Jul  5 2004 Jakub Jelinek <jakub@redhat.com> 2.3.3-36
- s390* .plt slot reduction
- fix pthread_rwlock_timedrdlock on x86_64

* Wed Jun 30 2004 Jakub Jelinek <jakub@redhat.com> 2.3.3-35
- tweak spec file for the libpthread-0.61.so -> libpthread-2.3.3.so
  NPTL changes

* Wed Jun 30 2004 Jakub Jelinek <jakub@redhat.com> 2.3.3-34
- update from CVS
  - if_nameindex using preferably netlink
  - printf_parsemb initialization fix
  - NPTL version is now the same as glibc version

* Mon Jun 28 2004 Jakub Jelinek <jakub@redhat.com> 2.3.3-33
- update from CVS
  - reread resolv.conf for nscd --invalidate=hosts
  - fix F_GETLK/F_SETLK/F_SETLKW constants on x86_64 for
    -m32 -D_FILE_OFFSET_BITS=64 compilations
  - avoid calling non-existing fcntl64 syscall on ppc64

* Mon Jun 14 2004 Jakub Jelinek <jakub@redhat.com> 2.3.3-32
- update from CVS
  - FUTEX_CMP_REQUEUE support (fix pthread_cond_* deadlocks)
  - fix backtrace in statically linked programs
- rebuilt with GCC 3.4, adjusted ulps and i386 <bits/string.h>

* Fri May 28 2004 Jakub Jelinek <jakub@redhat.com> 2.3.3-31
- update from CVS
- <bits/string2.h> and <bits/mathinline.h> changes for GCC 3.{2,4,5}+
- make c_stubs buildable even with GCC 3.2.x (#123042)

* Fri May 21 2004 Jakub Jelinek <jakub@redhat.com> 2.3.3-30
- fix pthread_cond_wait on architectures other than IA-32 and
  x86_64

* Thu May 20 2004 Jakub Jelinek <jakub@redhat.com> 2.3.3-29
- use lib64 instead of lib on ia64 if %%{_lib} is defined to lib64

* Wed May 19 2004 Jakub Jelinek <jakub@redhat.com> 2.3.3-28
- update from CVS
  - FUTEX_REQUEUE fixes (#115349)
  - SPARC GCC 3.4 build fix
  - fix handling of undefined TLS symbols on IA32 (RELA only),
    SPARC and SH
  - regex translate fix
  - speed up sprintf
  - x86_64 makecontext alignment fix
  - make POSIX sigpause the default sigpause, unless BSD sigpause
    requested

* Tue May 11 2004 Jakub Jelinek <jakub@redhat.com> 2.3.3-27
- remove /lib64/tls/librtkaio-2.3.[23].so in glibc_post_upgrade
  on x86-64, s390x and ppc64 instead of /lib/tls/librtkaio-2.3.[23].so
- build mq_{send,receive} with -fexceptions

* Fri May  7 2004 Jakub Jelinek <jakub@redhat.com> 2.3.3-26
- update from CVS
  - fix <tgmath.h>
  - fix memory leaks in nis, getifaddrs, etc. caused by incorrect
    use of realloc
- remove /lib/{tls,i686}/librtkaio-2.3.[23].so in glibc_post_upgrade
  and rerun ldconfig if needed, otherwise after glibc upgrade librt.so.1
  might be a stale symlink

* Wed May  5 2004 Jakub Jelinek <jakub@redhat.com> 2.3.3-25
- update from CVS
- disable FUTEX_REQUEUE (work around #115349)
- mq for sparc/sparc64/ia64

* Tue May  4 2004 Jakub Jelinek <jakub@redhat.com> 2.3.3-24
- update from CVS
  - define S_ISSOCK in -D_XOPEN_SOURCE=600 and S_I[FS]SOCK
    plus F_[SG]ETOWN also in -D_XOPEN_SOURCE=500 (both
    included already in XNS5)
  - reorder dlopen checks, so that dlopening ET_REL objects
    complains about != ET_DYN != ET_EXEC, not about phentsize
    (#121606)
  - fix strpbrk macro for GCC 3.4+ (BZ #130)
  - fix <sys/sysctl.h> (BZ #140)
  - sched_[gs]etaffinity documentation fix (BZ #131)
  - fix sparc64 build (BZ #139)
  - change linuxthreads back to use non-cancellable writes
    to manager pipes etc.
  - fix sem_timedwait return value in linuxthreads (BZ #133)
  - ia64 unnecessary PLT relocs removal

* Thu Apr 22 2004 Jakub Jelinek <jakub@redhat.com> 2.3.3-23
- update from CVS
  - fix *scanf
  - fix shm_unlink, sem_unlink and mq_unlink errno values
  - avoid memory leaks in error
  - execstack fixes on s390

* Mon Apr 19 2004 Jakub Jelinek <jakub@redhat.com> 2.3.3-22
- update from CVS
  - mq and timer fixes
- rebuilt with binutils >= 2.15.90.0.3-2 to fix IA-64 statically
  linked binaries
- fix linuxthreads librt.so on s390{,x}, so it is no longer DT_TEXTREL

* Sat Apr 17 2004 Jakub Jelinek <jakub@redhat.com> 2.3.3-21
- disable rtkaio
- update from CVS
  - POSIX message passing support
  - fixed SIGEV_THREAD support for POSIX timers
  - fix free on non-malloced memory in syslog
  - fix ffsl on some 64-bit arches
  - fix sched_setaffinity on x86-64, ia64
  - fix ppc64 umount
  - NETID_AUTHORITATIVE, SERVICES_AUTHORITATIVE support
  - various NIS speedups
  - fix fwrite with > 2GB sizes on 64-bit arches
  - fix pthread_getattr_np guardsize reporting in NPTL
- report PLT relocations in ld.so and libc.so during the build

* Fri Mar 25 2004 Jakub Jelinek <jakub@redhat.com> 2.3.3-20
- update from CVS
  - change NPTL PTHREAD_MUTEX_ADAPTIVE_NP mutexes to spin on SMP
  - strtol speed optimization
  - don't try to use certainly unimplemented syscalls on ppc64
- kill -debug subpackage, move the libs to glibc-debuginfo{,-common}
  into /usr/lib/debug/usr/%{_lib}/ directory
- fix c_stubs with gcc 3.4
- move all the up to 3 builds into %%build scriptlet and
  leave only installation in the %%install scriptlet

* Mon Mar 22 2004 Jakub Jelinek <jakub@redhat.com> 2.3.3-19
- update from CVS
  - affinity API changes

* Thu Mar 18 2004 Jakub Jelinek <jakub@redhat.com> 2.3.3-18
- update from CVS
  - fix ia64 iopl (#118591)
  - add support for /etc/ld.so.conf.d/*.conf
  - fix x86-64 LD_DEBUG=statistics
- fix hwcap handling when using ld.so.cache (#118518)

* Mon Mar 15 2004 Jakub Jelinek <jakub@redhat.com> 2.3.3-17
- update from CVS
  - implement non-_l function on top of _l functions

* Thu Mar 11 2004 Jakub Jelinek <jakub@redhat.com> 2.3.3-16
- update from CVS
- fix s390{,x} TLS handling

* Wed Mar 10 2004 Jakub Jelinek <jakub@redhat.com> 2.3.3-15
- update from CVS
  - special section for compatibility code
  - make getpid () work even in vfork () child
- configure with --enable-bind-now to avoid lazy binding in ld.so
  and libc.so

* Fri Mar  5 2004 Jakub Jelinek <jakub@redhat.com> 2.3.3-14
- update from CVS
  - fix iconv -c (#117021)
  - fix PIEs on sparc/sparc64
  - fix posix_fadvise on 64-bit architectures
- add locale-archive as %%ghost file (#117014)

* Mon Mar  1 2004 Jakub Jelinek <jakub@redhat.com> 2.3.3-13
- update from CVS

* Fri Feb 27 2004 Jakub Jelinek <jakub@redhat.com> 2.3.3-12
- update from CVS

* Fri Feb 27 2004 Jakub Jelinek <jakub@redhat.com> 2.3.3-11
- update from CVS
  - fix ld.so when vDSO is randomized

* Fri Feb 20 2004 Jakub Jelinek <jakub@redhat.com> 2.3.3-10
- update from CVS

* Fri Feb 20 2004 Jakub Jelinek <jakub@redhat.com> 2.3.3-9
- update from CVS

* Tue Feb 10 2004 Jakub Jelinek <jakub@redhat.com> 2.3.3-8
- update from CVS

* Tue Jan 27 2004 Jakub Jelinek <jakub@redhat.com> 2.3.3-7
- update from CVS
  - dl_iterate_phdr extension to signal number of added/removed
    libraries
- fix PT_GNU_RELRO support on ppc* with prelinking

* Fri Jan 23 2004 Jakub Jelinek <jakub@redhat.com> 2.3.3-6
- rebuilt with fixed GCC on IA-64

* Thu Jan 22 2004 Jakub Jelinek <jakub@redhat.com> 2.3.3-5
- fix PT_GNU_RELRO support

* Wed Jan 21 2004 Jakub Jelinek <jakub@redhat.com> 2.3.3-4
- update from CVS
  - some further regex speedups
  - fix re.translate handling in regex (#112869)
  - change regfree to match old regex behaviour (what is freed
    and clearing of freed pointers)
  - fix accesses to unitialized memory in regex (#113507, #113425,
    #113421)
  - PT_GNU_RELRO support

* Tue Dec 30 2003 Jakub Jelinek <jakub@redhat.com> 2.3.3-3
- update from CVS
  - fix pmap_set fd and memory leak (#112726)
- fix backreference handling in regex
- rebuilt under glibc without the above bug to fix
  libc.so linker script (#112738)

* Mon Dec 29 2003 Jakub Jelinek <jakub@redhat.com> 2.3.3-2
- update from CVS
  - faster getpid () in NPTL builds
  - fix to make pthread_setcancelstate (PTHREAD_CANCEL_DISABLE, )
    really disable cancellation (#112512)
  - more regex fixes and speedups
  - fix nextafter*/nexttoward*
  - handle 6th syscall(3) argument on AMD64
  - handle memalign/posix_memalign in mtrace
  - fix linuxthreads memory leak (#112208)
  - remove throw () from cancellation points in linuxthreads (#112602)
  - fix NPTL unregister_atfork
  - fix unwinding through alternate signal stacks

* Mon Dec  1 2003 Jakub Jelinek <jakub@redhat.com> 2.3.3-1
- update from CVS
  - 2.3.3 release
  - lots of regex fixes and speedups (#110401)
  - fix atan2
  - fix pshared condvars in NPTL
  - fix pthread_attr_destroy for attributes created with
    pthread_attr_init@GLIBC_2.0
- for the time being, include both nb_NO* and no_NO* as locales
  so that the distribution can catch up with the no_NO->nb_NO
  transition
- add BuildPrereq texinfo (#110252)

* Tue Nov 18 2003 Jakub Jelinek <jakub@redhat.com> 2.3.2-102
- update from CVS
  - fix getifaddrs (CAN-2003-0859)
  - fix ftw fd leak
  - fix linuxthreads sigaction (#108634)
  - fix glibc 2.0 stdio compatibility
  - fix uselocale (LC_GLOBAL_LOCALE)
  - speed up stdio locking in non-threaded programs on IA-32
  - try to maintain correct order of cleanups between those
    registered with __attribute__((cleanup))
    and with LinuxThreads style pthread_cleanup_push/pop (#108631)
  - fix segfault in regex (#109606)
  - fix RE_ICASE multi-byte handling in regex
  - fix pthread_exit in libpthread.a (#109790)
  - FTW_ACTIONRETVAL support
  - lots of regex fixes and speedups
  - fix ceill/floorl on AMD64

* Mon Oct 27 2003 Jakub Jelinek <jakub@redhat.com> 2.3.2-101
- update from CVS
  - fix ld.so --verify (and ldd)

* Mon Oct 27 2003 Jakub Jelinek <jakub@redhat.com> 2.3.2-100
- update from CVS
  - fix sprof (#103727)
  - avoid infinite loops in {,f}statvfs{,64} with hosed mounts file
  - prevent dlopening of executables
  - fix glob with GLOB_BRACE and without GLOB_NOESCAPE
  - fix locale printing of word values on 64-bit big-endian arches
    (#107846)
  - fix getnameinfo and getaddrinfo with reverse IPv6 lookups
    (#101261)

* Wed Oct 22 2003 Jakub Jelinek <jakub@redhat.com> 2.3.2-99
- update from CVS
  - dl_iterate_phdr in libc.a on arches other than IA-64
  - LD_DEBUG=statistics prints number of relative relocations
  - fix hwcap computation
- NPTL is now part of upstream glibc CVS
- include {st,xh,zu}_ZA{,.UTF-8} locales

* Sat Oct  4 2003 Jakub Jelinek <jakub@redhat.com> 2.3.2-98
- update from CVS
  - fix close, pause and fsync (#105348)
  - fix pthread_once on IA-32
- implement backtrace () on IA-64, handle -fomit-frame-pointer
  in AMD64 backtrace () (#90402)

* Tue Sep 30 2003 Jakub Jelinek <jakub@redhat.com> 2.3.2-97
- update from CVS
  - fix <sys/sysmacros.h> with C++ or -ansi or -pedantic C
  - fix mknod/ustat return value when given bogus device number (#105768)

* Fri Sep 26 2003 Jakub Jelinek <jakub@redhat.com> 2.3.2-96
- rebuilt

* Fri Sep 26 2003 Jakub Jelinek <jakub@redhat.com> 2.3.2-95
- fix IA-64 getcontext

* Thu Sep 25 2003 Jakub Jelinek <jakub@redhat.com> 2.3.2-94
- update from CVS
- fix syslog with non-C non-en_* locales (#61296, #104979)
- filter GLIBC_PRIVATE symbols from glibc provides
- fix NIS+

* Thu Sep 25 2003 Jakub Jelinek <jakub@redhat.com> 2.3.2-93
- update from CVS
- assume 2.4.21 kernel features on RHEL/ppc*, so that
  {make,set,get,swap}context works
- backout execstack support for RHEL
- build rtkaio on amd64 too

* Wed Sep 24 2003 Jakub Jelinek <jakub@redhat.com> 2.3.2-92
- update from CVS
  - execstack/noexecstack support
  - build nscd as PIE
- move __libc_stack_end back to @GLIBC_2.1
- build against elfutils >= 0.86 to fix stripping on s390x

* Mon Sep 22 2003 Jakub Jelinek <jakub@redhat.com> 2.3.2-91
- rebuilt

* Mon Sep 22 2003 Jakub Jelinek <jakub@redhat.com> 2.3.2-90
- update from CVS
  - NPTL locking change (#102682)
- don't jump around lock on amd64

* Thu Sep 18 2003 Jakub Jelinek <jakub@redhat.com> 2.3.2-89
- fix open_memstream/syslog (#104661)

* Thu Sep 18 2003 Jakub Jelinek <jakub@redhat.com> 2.3.2-88
- update from CVS
  - retrieve affinity in pthread_getattr_np
  - fix pthread_attr_[gs]etaffinity_np
  - handle hex and octal in wordexp

* Wed Sep 17 2003 Jakub Jelinek <jakub@redhat.com> 2.3.2-87
- update from CVS
  - truncate instead of round in utimes when utimes syscall is not available
  - don't align stack in every glibc function unnecessarily on IA-32
  - make sure threads have their stack 16 byte aligned on IA-32
  - move sched_[sg]etaffinity to GLIBC_2.3.3 symbol version (#103231)
  - fix pthread_getattr_np for the initial thread (#102683)
  - avoid linuxthreads signal race (#104368)
- ensure all gzip invocations are done with -n option

* Fri Sep 12 2003 Jakub Jelinek <jakub@redhat.com> 2.3.2-86
- update from CVS
- avoid linking in libgcc_eh.a unnecessarily
- change ssize_t back to long int on s390 -m31, unless
  gcc 2.95.x is used

* Wed Sep 10 2003 Jakub Jelinek <jakub@redhat.com> 2.3.2-85
- update from CVS
  - fix IA-64 memccpy (#104114)

* Tue Sep  9 2003 Jakub Jelinek <jakub@redhat.com> 2.3.2-84
- update from CVS
  - undo broken amd64 signal context changes

* Tue Sep  9 2003 Jakub Jelinek <jakub@redhat.com> 2.3.2-83
- update from CVS
- change *nlink_t, *ssize_t and *intptr_t types on s390 -m31 to
  {unsigned,} int
- change *u_quad_t, *quad_t, *qaddr_t, *dev_t, *ino64_t, *loff_t,
  *off64_t, *rlim64_t, *blkcnt64_t, *fsblkcnt64_t, *fsfilcnt64_t
  on 64-bit arches from {unsigned,} long long int {,*} to
  {unsigned,} long int {,*} to restore binary compatibility
  for C++ functions using these types as arguments

* Sun Sep  7 2003 Jakub Jelinek <jakub@redhat.com> 2.3.2-82
- rebuilt

* Sat Sep  6 2003 Jakub Jelinek <jakub@redhat.com> 2.3.2-81
- update from CVS
  - fix tc[gs]etattr/cf[gs]et[io]speed on ppc (#102732)
  - libio fixes

* Thu Sep  4 2003 Jakub Jelinek <jakub@redhat.com> 2.3.2-80
- update from CVS
  - fix IA-64 cancellation when mixing __attribute__((cleanup ()))
    and old-style pthread_cleanup_push cleanups

* Tue Sep  2 2003 Jakub Jelinek <jakub@redhat.com> 2.3.2-79
- updated from CVS
  - lots of cancellation fixes
  - fix posix_fadvise* on ppc32
  - TLS layout fix
  - optimize stdio cleanups (#103354)
  - sparcv9 NPTL
  - include sigset, sighold, sigrelse, sigpause and sigignore prototypes
    in signal.h even if -D_XOPEN_SOURCE_EXTENDED (#103269)
  - fix svc_getreqset on 64-bit big-endian arches
  - return ENOSYS in linuxthreads pthread_barrierattr_setpshared for
    PTHREAD_PROCESS_SHARED
  - add pthread_cond_timedwait stubs to libc.so (#102709)
- split glibc-devel into glibc-devel and glibc-headers to ensure
  amd64 /usr/include always wins on amd64/i386 bi-arch installs
- increase PTHREAD_STACK_MIN on alpha, ia64 and sparc*
- get rid of __syscall_* prototypes and stubs in sysdeps/unix/sysv/linux
- run make check also with linuxthreads (on IA-32 non-FLOATING_STACKS)
  ld.so and NPTL (on IA-32 also FLOATING_STACKS linuxthreads) libraries
  and tests

* Tue Aug 25 2003 Jakub Jelinek <jakub@redhat.com> 2.3.2-78
- include dl-osinfo.h only in glibc-debuginfo-2*.rpm, not
  in glibc-debuginfo-common*

* Mon Aug 25 2003 Jakub Jelinek <jakub@redhat.com> 2.3.2-77
- update from CVS
  - fix glibc 2.0 libio compatibility (#101385)
  - fix ldconfig with /usr/lib/lib*.so symlinks (#102853)
  - fix assert.h (#102916, #103017)
  - make ld.so.cache identical between IA-32 and AMD64 (#102887)
  - fix static linking of large IA-64 binaries (#102586)
- avoid using floating point regs in lazy binding code on ppc64 (#102763)

* Fri Aug 22 2003 Roland McGrath <roland@redhat.com> 2.3.2-76
- add td_thr_tls_get_addr changes missed in initial nptl_db rewrite

* Sun Aug 17 2003 Roland McGrath <roland@redhat.com> 2.3.2-74
- nptl_db rewrite not yet in CVS

* Thu Aug 14 2003 Jakub Jelinek <jakub@redhat.com> 2.3.2-72
- update from CVS
  - fix rtkaio aio_fsync{,64}
  - update rtkaio for !BROKEN_THREAD_SIGNALS
  - fix assert macro when used on pointers

* Wed Aug 13 2003 Jakub Jelinek <jakub@redhat.com> 2.3.2-71
- update from CVS

* Tue Aug 12 2003 Jakub Jelinek <jakub@redhat.com> 2.3.2-70
- update from CVS
- disable CLONE_STOPPED for now until it is resolved
- strip crt files
- fix libio on arches with no < GLIBC_2.2 support (#102102, #102105)
- fix glibc-debuginfo to include all nptl and nptl_db sources

* Thu Aug  7 2003 Jakub Jelinek <jakub@redhat.com> 2.3.2-69
- update from CVS
  - fix pthread_create@GLIBC_2.0 (#101767)
- __ASSUME_CLONE_STOPPED on all arches but s390* in RHEL

* Sun Aug  3 2003 Jakub Jelinek <jakub@redhat.com> 2.3.2-68
- update from CVS
  - only use CLONE_STOPPED if kernel supports it, fix setting of thread
    explicit scheduling (#101457)

* Fri Aug  1 2003 Jakub Jelinek <jakub@redhat.com> 2.3.2-67
- update from CVS
  - fix utimes and futimes if kernel doesn't support utimes syscall
  - fix s390 ssize_t type
  - fix dlerror when called before any dlopen/dlsym
  - update IA-64 bits/sigcontext.h (#101344)
  - various warning fixes
  - fix pthread.h comment typos (#101363)

* Wed Jul 30 2003 Jakub Jelinek <jakub@redhat.com> 2.3.2-66
- update from CVS
- fix dlopen of libraries using TLS IE/LE models

* Tue Jul 29 2003 Jakub Jelinek <jakub@redhat.com> 2.3.2-65
- update from CVS
  - fix timer_create
  - use __extension__ before long long typedefs in <bits/types.h> (#100718)

* Mon Jul 28 2003 Jakub Jelinek <jakub@redhat.com> 2.3.2-64
- update from CVS
  - fix wcpncpy (#99462)
  - export _res@GLIBC_2.0 even from NPTL libc.so (__res_state ()
    unlike __errno_location () or __h_errno_location () was introduced
    in glibc 2.2)
  - fix zic bug on 64-bit platforms
  - some TLS handling fixes
  - make ldconfig look into alternate ABI dirs by default (#99402)
- move %{_datadir}/zoneinfo to tzdata package, so that it can be
  errataed separately from glibc
- new add-on - rtkaio
- prereq libgcc, as glibc now relies on libgcc_s.so.1 for pthread_cancel

* Tue Jul 15 2003 Jakub Jelinek <jakub@redhat.com> 2.3.2-63
- fix thread cancellation on ppc64

* Sat Jul 12 2003 Jakub Jelinek <jakub@redhat.com> 2.3.2-62
- update from CVS
  - fix thread cancellation on ppc32, s390 and s390x

* Thu Jul 10 2003 Jakub Jelinek <jakub@redhat.com> 2.3.2-61
- update from CVS
  - build libc_nonshared.a with -fPIC instead of -fpic
- fix ppc64 PIE support
- add cfi directives to NPTL sysdep-cancel.h on ppc/ppc64/s390/s390x

* Tue Jul  8 2003 Jakub Jelinek <jakub@redhat.com> 2.3.2-60
- update from CVS

* Thu Jul  3 2003 Jakub Jelinek <jakub@redhat.com> 2.3.2-59
- update from CVS
- on IA-64 use different symbols for cancellation portion of syscall
  handlers to make gdb happier

* Thu Jun 26 2003 Jakub Jelinek <jakub@redhat.com> 2.3.2-58
- update from CVS
  - nss_compat supporting LDAP etc.

* Tue Jun 24 2003 Jakub Jelinek <jakub@redhat.com> 2.3.2-57
- update from CVS

* Thu Jun 19 2003 Jakub Jelinek <jakub@redhat.com> 2.3.2-56
- fix condvars and semaphores in ppc* NPTL
- fix test-skeleton.c reporting of timed-out tests (#91269)
- increase timeouts for tests during make check

* Wed Jun 18 2003 Jakub Jelinek <jakub@redhat.com> 2.3.2-55
- make ldconfig default to both /lib+/usr/lib and /lib64+/usr/lib64
  on bi-ABI architectures (#97557)
- disable FUTEX_REQUEUE on ppc* temporarily

* Wed Jun 18 2003 Jakub Jelinek <jakub@redhat.com> 2.3.2-54
- update from CVS
- fix glibc_post_upgrade on ppc

* Tue Jun 17 2003 Jakub Jelinek <jakub@redhat.com> 2.3.2-53
- update from CVS
- fix localedef (#90659)
- tweak linuxthreads for librt cancellation

* Mon Jun 16 2003 Jakub Jelinek <jakub@redhat.com> 2.3.2-52
- update from CVS

* Thu Jun 12 2003 Jakub Jelinek <jakub@redhat.com> 2.3.2-51
- update from CVS
- fix <gnu/stubs.h> (#97169)

* Wed Jun 11 2003 Jakub Jelinek <jakub@redhat.com> 2.3.2-50
- update from CVS

* Tue Jun 10 2003 Jakub Jelinek <jakub@redhat.com> 2.3.2-49
- update from CVS
  - fix pthread_cond_signal on IA-32 (#92080, #92253)
  - fix setegid (#91567)
- don't prelink -R libc.so on any architecture, it prohibits
  address randomization

* Fri Jun  5 2003 Jakub Jelinek <jakub@redhat.com> 2.3.2-48
- update from CVS
  - fix IA-64 NPTL build

* Thu Jun  5 2003 Jakub Jelinek <jakub@redhat.com> 2.3.2-47
- update from CVS
- PT_GNU_STACK segment in binaries/executables and .note.GNU-stack
  section in *.[oa]

* Sun Jun  1 2003 Jakub Jelinek <jakub@redhat.com> 2.3.2-46
- update from CVS
- enable NPTL on AMD64
- avoid using trampolines in localedef

* Fri May 29 2003 Jakub Jelinek <jakub@redhat.com> 2.3.2-45
- enable NPTL on IA-64

* Fri May 29 2003 Jakub Jelinek <jakub@redhat.com> 2.3.2-44
- update from CVS
- enable NPTL on s390 and s390x
- make __init_array_start etc. symbols in elf-init.oS hidden undefined

* Thu May 29 2003 Jakub Jelinek <jakub@redhat.com> 2.3.2-43
- update from CVS

* Fri May 23 2003 Jakub Jelinek <jakub@redhat.com> 2.3.2-42
- update from CVS

* Tue May 20 2003 Jakub Jelinek <jakub@redhat.com> 2.3.2-41
- update from CVS
- use NPTL libs if uname -r contains nptl substring or is >= 2.5.69
  or set_tid_address syscall is available instead of checking
  AT_SYSINFO dynamic tag

* Thu May 15 2003 Jakub Jelinek <jakub@redhat.com> 2.3.2-40
- update from CVS

* Wed May 14 2003 Jakub Jelinek <jakub@redhat.com> 2.3.2-39
- update from CVS
  - fix for prelinking of libraries with no dependencies

* Tue May 13 2003 Jakub Jelinek <jakub@redhat.com> 2.3.2-38
- update from CVS
- enable NPTL on ppc and ppc64

* Tue May  6 2003 Matt Wilson <msw@redhat.com> 2.3.2-37
- rebuild

* Sun May  4 2003 Jakub Jelinek <jakub@redhat.com> 2.3.2-36
- update from CVS

* Sat May  3 2003 Jakub Jelinek <jakub@redhat.com> 2.3.2-35
- update from CVS
  - make -jN build fixes

* Fri May  2 2003 Jakub Jelinek <jakub@redhat.com> 2.3.2-34
- update from CVS
- avoid using trampolines in iconvconfig for now

* Sat Apr 26 2003 Jakub Jelinek <jakub@redhat.com> 2.3.2-33
- update from CVS

* Fri Apr 25 2003 Jakub Jelinek <jakub@redhat.com> 2.3.2-32
- update from CVS
- more ppc TLS fixes

* Wed Apr 23 2003 Jakub Jelinek <jakub@redhat.com> 2.3.2-31
- update from CVS
  - nscd fixes
  - fix Bahrain spelling (#56298)
  - fix Ukrainian collation (#83973)
  - accept trailing spaces in /etc/ld.so.conf (#86032)
  - perror fix (#85994)
  - fix localedef (#88978)
  - fix getifaddrs (#89026)
  - fix strxfrm (#88409)
- fix ppc TLS
- fix getaddrinfo (#89448)
- don't print warning about errno, h_errno or _res if
  LD_ASSUME_KERNEL=2.4.1 or earlier

* Tue Apr 15 2003 Jakub Jelinek <jakub@redhat.com> 2.3.2-30
- update from CVS
- fix prelink on ppc32
- add TLS support on ppc32 and ppc64
- make sure on -m64 arches all helper binaries are built with this
  option

* Mon Apr 14 2003 Jakub Jelinek <jakub@redhat.com> 2.3.2-29
- update from CVS
  - fix strxfrm (#88409)
- use -m64 -mno-minimal-toc on ppc64
- conflict with kernels < 2.4.20 on ppc64 and < 2.4.0 on x86_64
- link glibc_post_upgrade against newly built libc.a

* Sun Apr 13 2003 Jakub Jelinek <jakub@redhat.com> 2.3.2-28
- update from CVS
  - fix NPTL pthread_detach and already terminated, but not yet
    joined thread (#88219)
  - fix bug-regex4 testcase (#88118)
  - reenable prelink support broken in 2.3.2-13
  - fix register_printf_function (#88052)
  - fix double free with fopen using ccs= (#88056)
  - fix potential access below $esp in {set,swap}context (#88093)
  - fix buffer underrun in gencat -H (#88099)
  - avoid using unitialized variable in tst-tgmath (#88101)
  - fix gammal (#88104)
  - fix iconv -c
  - fix xdr_string (PR libc/4999)
  - fix /usr/lib/nptl/librt.so symlink
  - avoid running NPTL cleanups twice in some cases
  - unblock __pthread_signal_cancel in linuxthreads, so that
    linuxthreads threaded programs work correctly if spawned
    from NPTL threaded programs
  - fix sysconf _SC_{NPROCESSORS_{CONF,ONLN},{,AV}PHYS_PAGES}
- remove /lib/i686 directory before running ldconfig in glibc post
  during i686 -> i386 glibc "upgrades" (#88456)

* Wed Apr  2 2003 Jakub Jelinek <jakub@redhat.com> 2.3.2-22
- update from CVS
  - add pthread_atfork to libpthread.a

* Tue Apr  1 2003 Jakub Jelinek <jakub@redhat.com> 2.3.2-21
- update from CVS
- make sure linuxthreads pthread_mutex_lock etc. is not a cancellation
  point

* Sat Mar 29 2003 Jakub Jelinek <jakub@redhat.com> 2.3.2-20
- update from CVS
- if kernel >= 2.4.1 doesn't support NPTL, fall back to
  /lib/i686 libs on i686, not stright to /lib

* Fri Mar 28 2003 Jakub Jelinek <jakub@redhat.com> 2.3.2-19
- update from CVS
  - timers fixes

* Thu Mar 27 2003 Jakub Jelinek <jakub@redhat.com> 2.3.2-18
- update from CVS
- fix NPTL pthread_cond_timedwait
- fix sysconf (_SC_MONOTONIC_CLOCK)
- use /%%{_lib}/tls instead of /lib/tls on x86-64
- add /%{_lib}/tls/librt*so* and /%{_lib}/i686/librt*so*
- display content of .out files for all make check failures

* Wed Mar 26 2003 Jakub Jelinek <jakub@redhat.com> 2.3.2-17
- update from CVS
  - kernel POSIX timers support

* Sat Mar 22 2003 Jakub Jelinek <jakub@redhat.com> 2.3.2-16
- update from CVS
  - export __fork from glibc again
- fix glibc-compat build in NPTL
- fix c_stubs
- fix some more atomic.h problems
- don't check abi in glibc-compat libs

* Fri Mar 21 2003 Jakub Jelinek <jakub@redhat.com> 2.3.2-15
- update from CVS
- build glibc-compat (for glibc 2.0 compatibility) and c_stubs add-ons
- condrestart sshd in glibc_post_upgrade so that the user can
  log in remotely and handle the rest (#86339)
- fix a typo in glibc_post_upgrade on sparc

* Tue Mar 18 2003 Jakub Jelinek <jakub@redhat.com> 2.3.2-14
- update from CVS
- change i686/athlon libc.so.6 base to 0x00e80000

* Mon Mar 17 2003 Jakub Jelinek <jakub@redhat.com> 2.3.2-13
- update from CVS
  - hopefully last fix for condvar problems

* Fri Mar 14 2003 Jakub Jelinek <jakub@redhat.com> 2.3.2-12
- fix bits/syscall.h creation on x86-64

* Thu Mar 13 2003 Jakub Jelinek <jakub@redhat.com> 2.3.2-11
- update from CVS

* Wed Mar 12 2003 Jakub Jelinek <jakub@redhat.com> 2.3.2-10
- update from CVS

* Tue Mar 11 2003 Jakub Jelinek <jakub@redhat.com> 2.3.2-9
- update from CVS
- fix glibc-debug description (#85111)
- make librt.so a symlink again, not linker script

* Tue Mar  4 2003 Jakub Jelinek <jakub@redhat.com> 2.3.2-8
- update from CVS
- remove the workarounds for broken software accessing GLIBC_PRIVATE
  symbols

* Mon Mar  3 2003 Jakub Jelinek <jakub@redhat.com> 2.3.2-7
- update from CVS

* Sun Mar  2 2003 Jakub Jelinek <jakub@redhat.com> 2.3.2-6
- fix TLS IE/LE model handling in dlopened libraries
  on TCB_AT_TP arches

* Thu Feb 25 2003 Jakub Jelinek <jakub@redhat.com> 2.3.2-5
- update from CVS

* Tue Feb 25 2003 Jakub Jelinek <jakub@redhat.com> 2.3.2-4
- update from CVS

* Mon Feb 24 2003 Jakub Jelinek <jakub@redhat.com> 2.3.2-3
- update from CVS
- only warn about errno, h_errno or _res for binaries, never
  libraries
- rebuilt with gcc-3.2.2-4 to use direct %gs TLS access insn sequences

* Sun Feb 23 2003 Jakub Jelinek <jakub@redhat.com> 2.3.2-2
- update from CVS

* Sat Feb 22 2003 Jakub Jelinek <jakub@redhat.com> 2.3.2-1
- update from CVS

* Thu Feb 20 2003 Jakub Jelinek <jakub@redhat.com> 2.3.1-51
- update from CVS

* Wed Feb 19 2003 Jakub Jelinek <jakub@redhat.com> 2.3.1-50
- update from CVS

* Wed Feb 19 2003 Jakub Jelinek <jakub@redhat.com> 2.3.1-49
- update from CVS
- remove nisplus and nis from the default nsswitch.conf (#67401, #9952)

* Tue Feb 18 2003 Jakub Jelinek <jakub@redhat.com> 2.3.1-48
- update from CVS

* Sat Feb 15 2003 Jakub Jelinek <jakub@redhat.com> 2.3.1-47
- update from CVS

* Fri Feb 14 2003 Jakub Jelinek <jakub@redhat.com> 2.3.1-46
- update from CVS
  - pthread_cond* NPTL fixes, new NPTL testcases

* Thu Feb 13 2003 Jakub Jelinek <jakub@redhat.com> 2.3.1-45
- update from CVS
- include also linuxthreads FLOATING_STACKS libs on i686 and athlon:
  LD_ASSUME_KERNEL=2.2.5 to LD_ASSUME_KERNEL=2.4.0 is non-FLOATING_STACKS lt,
  LD_ASSUME_KERNEL=2.4.1 to LD_ASSUME_KERNEL=2.4.19 is FLOATING_STACKS lt,
  later is NPTL
- enable TLS on alpha/alphaev6
- add BuildPreReq: /usr/bin/readlink

* Tue Feb 11 2003 Jakub Jelinek <jakub@redhat.com> 2.3.1-44
- update from CVS
  - pthread_once fix

* Mon Feb 10 2003 Jakub Jelinek <jakub@redhat.com> 2.3.1-43
- update from CVS
- vfork fix on s390
- rebuilt with binutils 2.13.90.0.18-5 so that accesses to errno
  don't bind locally (#83325)

* Thu Feb 06 2003 Jakub Jelinek <jakub@redhat.com> 2.3.1-42
- update from CVS
- fix pthread_create after vfork+exec in linuxthreads

* Wed Feb 05 2003 Jakub Jelinek <jakub@redhat.com> 2.3.1-41
- update from CVS

* Thu Jan 30 2003 Jakub Jelinek <jakub@redhat.com> 2.3.1-40
- update from CVS

* Wed Jan 29 2003 Jakub Jelinek <jakub@redhat.com> 2.3.1-39
- update from CVS
- enable TLS on s390{,x} and sparc{,v9}

* Fri Jan 17 2003 Jakub Jelinek <jakub@redhat.com> 2.3.1-38
- update from CVS
- initialize __environ in glibc_post_upgrade to empty array,
  so that it is not NULL
- compat symlink for s390x /lib/ld64.so.1
- enable glibc-profile on x86-64
- only include libNoVersion.so on IA-32, Alpha and Sparc 32-bit

* Thu Jan 16 2003 Jakub Jelinek <jakub@redhat.com> 2.3.1-37
- update from CVS
  - nscd fixes, *scanf fix
- fix %%nptlarches noarch build (#81909)
- IA-64 TLS fixes

* Tue Jan 14 2003 Jakub Jelinek <jakub@redhat.com> 2.3.1-36
- update from CVS
- rework -debuginfo subpackage, add -debuginfo-common
  subpackage on IA-32, Alpha and Sparc (ie. auxiliary arches)
- fix vfork in libc.a on PPC32, Alpha, Sparc
- fix libio locks in linuxthreads libc.so if libpthread.so
  is dlopened later (#81374)

* Mon Jan 13 2003 Jakub Jelinek <jakub@redhat.com> 2.3.1-35
- update from CVS
  - dlclose bugfixes
- fix NPTL libpthread.a
- fix glibc_post_upgrade on several arches

* Sat Jan 11 2003 Jakub Jelinek <jakub@redhat.com> 2.3.1-34
- update from CVS
- TLS support on IA-64

* Wed Jan  8 2003 Jakub Jelinek <jakub@redhat.com> 2.3.1-33
- fix vfork in linuxthreads (#81377, #81363)

* Tue Jan  7 2003 Jakub Jelinek <jakub@redhat.com> 2.3.1-32
- update from CVS
- don't use TLS libs if kernel doesn't set AT_SYSINFO
  (#80921, #81212)
- add ntp_adjtime on alpha (#79996)
- fix nptl_db (#81116)

* Sun Jan  5 2003 Jakub Jelinek <jakub@redhat.com> 2.3.1-31
- update from CVS
- support all architectures again

* Fri Jan  3 2003 Jakub Jelinek <jakub@redhat.com> 2.3.1-30
- fix condvar compatibility wrappers
- add ugly hack to use non-TLS libs if a binary is seen
  to have errno, h_errno or _res symbols in .dynsym

* Fri Jan  3 2003 Jakub Jelinek <jakub@redhat.com> 2.3.1-29
- update from CVS
  - fixes for new condvar

* Thu Jan  2 2003 Jakub Jelinek <jakub@redhat.com> 2.3.1-28
- new NPTL condvar implementation plus related linuxthreads
  symbol versioning updates

* Thu Jan  2 2003 Jakub Jelinek <jakub@redhat.com> 2.3.1-27
- update from CVS
- fix #include <sys/stat.h> with -D_BSD_SOURCE or without
  feature set macros
- make *sigaction, sigwait and raise the same between
  -lpthread -lc and -lc -lpthread in linuxthreads builds

* Tue Dec 31 2002 Jakub Jelinek <jakub@redhat.com> 2.3.1-26
- fix dlclose

* Sun Dec 29 2002 Jakub Jelinek <jakub@redhat.com> 2.3.1-25
- enable sysenter by default for now
- fix endless loop in ldconfig

* Sat Dec 28 2002 Jakub Jelinek <jakub@redhat.com> 2.3.1-24
- update from CVS

* Fri Dec 27 2002 Jakub Jelinek <jakub@redhat.com> 2.3.1-23
- update from CVS
  - fix ptmalloc_init after clearenv (#80370)

* Sun Dec 22 2002 Jakub Jelinek <jakub@redhat.com> 2.3.1-22
- update from CVS
- add IA-64 back
- move TLS libraries from /lib/i686 to /lib/tls

* Thu Dec 19 2002 Jakub Jelinek <jakub@redhat.com> 2.3.1-21
- system(3) fix for linuxthreads
- don't segfault in pthread_attr_init from libc.so
- add cancellation tests from nptl to linuxthreads

* Wed Dec 18 2002 Jakub Jelinek <jakub@redhat.com> 2.3.1-20
- fix up lists of exported symbols + their versions
  from the libraries

* Wed Dec 18 2002 Jakub Jelinek <jakub@redhat.com> 2.3.1-19
- fix --with-tls --enable-kernel=2.2.5 libc on IA-32

* Wed Dec 18 2002 Jakub Jelinek <jakub@redhat.com> 2.3.1-18
- update from CVS
  - fix NPTL hanging mozilla
  - initialize malloc in mALLOPt (fixes problems with squid, #79957)
  - make linuxthreads work with dl_dynamic_weak 0
  - clear dl_dynamic_weak everywhere

* Tue Dec 17 2002 Jakub Jelinek <jakub@redhat.com> 2.3.1-17
- update from CVS
  - NPTL socket fixes, flockfile/ftrylockfile/funlockfile fix
  - kill -debug sub-package, rename -debug-static to -debug
  - clear dl_dynamic_weak for NPTL

* Mon Dec 16 2002 Jakub Jelinek <jakub@redhat.com> 2.3.1-16
- fix <bits/mathinline.h> and <bits/nan.h> for C++
- automatically generate NPTL libpthread wrappers

* Mon Dec 16 2002 Jakub Jelinek <jakub@redhat.com> 2.3.1-15
- update from CVS
  - all functions which need cancellation should now be cancellable
    both in libpthread.so and libc.so
  - removed @@GLIBC_2.3.2 cancellation wrappers

* Fri Dec 13 2002 Jakub Jelinek <jakub@redhat.com> 2.3.1-14
- update from CVS
  - replace __libc_lock_needed@GOTOFF(%ebx) with
    %gs:offsetof(tcbhead_t, multiple_threads)
  - start of new NPTL cancellation wrappers

* Thu Dec 12 2002 Jakub Jelinek <jakub@redhat.com> 2.3.1-13
- update from CVS
- use inline locks in malloc

* Tue Dec 10 2002 Jakub Jelinek <jakub@redhat.com> 2.3.1-12
- update from CVS
  - support LD_ASSUME_KERNEL=2.2.5 in statically linked programs

* Mon Dec  9 2002 Jakub Jelinek <jakub@redhat.com> 2.3.1-11
- update from CVS
- rebuilt with gcc-3.2.1-2

* Fri Dec  6 2002 Jakub Jelinek <jakub@redhat.com> 2.3.1-10
- update from CVS
- non-nptl --with-tls --without-__thread FLOATING_STACKS libpthread
  should work now
- faster libc locking when using nptl
- add OUTPUT_FORMAT to linker scripts
- fix x86_64 sendfile (#79111)

* Wed Dec  4 2002 Jakub Jelinek <jakub@redhat.com> 2.3.1-9
- update from CVS
  - RUSCII support (#78906)
- for nptl builds add BuildRequires
- fix byteswap.h for non-gcc (#77689)
- add nptl-devel package

* Tue Dec  3 2002 Jakub Jelinek <jakub@redhat.com> 2.3.1-8
- update from CVS
  - make --enable-kernel=2.2.5 --with-tls --without-__thread
    ld.so load nptl and other --with-__thread libs
- disable nptl by default for now

* Wed Nov 27 2002 Jakub Jelinek <jakub@redhat.com> 2.3.1-7
- update from CVS
- restructured redhat/Makefile and spec, so that src.rpm contains
  glibc-<date>.tar.bz2, glibc-redhat-<date>.tar.bz2 and glibc-redhat.patch
- added nptl

* Fri Nov  8 2002 Jakub Jelinek <jakub@redhat.com> 2.3.1-6
- update from CVS
  - even more regex fixes
- run sed testsuite to check glibc regex

* Thu Oct 24 2002 Jakub Jelinek <jakub@redhat.com> 2.3.1-5
- fix LD_DEBUG=statistics and LD_TRACE_PRELINKING in programs
  using libpthread.so.

* Thu Oct 24 2002 Jakub Jelinek <jakub@redhat.com> 2.3.1-4
- update from CVS
  - fixed %a and %A in *printf (#75821)
  - fix re_comp memory leaking (#76594)

* Tue Oct 22 2002 Jakub Jelinek <jakub@redhat.com> 2.3.1-3
- update from CVS
  - some more regex fixes
- fix libpthread.a (#76484)
- fix locale-archive enlarging

* Fri Oct 18 2002 Jakub Jelinek <jakub@redhat.com> 2.3.1-2
- update from CVS
  - don't need to use 128K of stacks for DNS lookups
  - regex fixes
  - updated timezone data e.g. for this year's Brasil DST
    changes
  - expand ${LIB} in RPATH/RUNPATH/dlopen filenames

* Fri Oct 11 2002 Jakub Jelinek <jakub@redhat.com> 2.3.1-1
- update to 2.3.1 final
  - support really low thread stack sizes (#74073)
- tzdata update

* Wed Oct  9 2002 Jakub Jelinek <jakub@redhat.com> 2.3-2
- update from CVS
  - handle low stack limits
  - move s390x into */lib64

* Thu Oct  3 2002 Jakub Jelinek <jakub@redhat.com> 2.3-1
- update to 2.3 final
  - fix freopen on libstdc++ <= 2.96 stdin/stdout/stderr (#74800)

* Sun Sep 29 2002 Jakub Jelinek <jakub@redhat.com> 2.2.94-3
- don't prelink -r libc.so on ppc/x86-64/sparc*, it doesn't
  speed things up, because they are neither REL arches, nor
  ELF_MACHINE_REL_RELATIVE
- fix sparc64 build

* Sun Sep 29 2002 Jakub Jelinek <jakub@redhat.com> 2.2.94-2
- update from CVS

* Sat Sep 28 2002 Jakub Jelinek <jakub@redhat.com> 2.2.94-1
- update from CVS
- prelink on ppc and x86-64 too
- don't remove ppc memset
- instead of listing on which arches to remove glibc-compat
  list where it should stay

* Fri Sep  6 2002 Jakub Jelinek <jakub@redhat.com> 2.2.93-5
- fix wcsmbs functions with invalid character sets (or malloc
  failures)
- make sure __ctype_b etc. compat vars are updated even if
  they are copy relocs in the main program

* Thu Sep  5 2002 Jakub Jelinek <jakub@redhat.com> 2.2.93-4
- fix /lib/libnss1_dns.so.1 (missing __set_h_errno definition
  leading to unresolved __set_h_errno symbol)

* Wed Sep  4 2002 Jakub Jelinek <jakub@redhat.com> 2.2.93-3
- security fix - increase dns-network.c MAXPACKET to at least
  65536 to avoid buffer overrun. Likewise glibc-compat
  dns-{host,network}.c.

* Tue Sep  3 2002 Jakub Jelinek <jakub@redhat.com> 2.2.93-2
- temporarily add back __ctype_b, __ctype_tolower and __ctype_toupper to
  libc.a and export them as @@GLIBC_2.0 symbols, not @GLIBC_2.0
  from libc.so - we have still lots of .a libraries referencing
  __ctype_{b,tolower,toupper} out there...

* Tue Sep  3 2002 Jakub Jelinek <jakub@redhat.com> 2.2.93-1
- update from CVS
  - 2.2.93 release
  - use double instead of single indirection in isXXX macros
  - per-locale wcsmbs conversion state

* Sat Aug 31 2002 Jakub Jelinek <jakub@redhat.com> 2.2.92-2
- update from CVS
  - fix newlocale/duplocale/uselocale
- disable profile on x86_64 for now

* Sat Aug 31 2002 Jakub Jelinek <jakub@redhat.com> 2.2.92-1
- update from CVS
  - 2.2.92 release
  - fix gettext after uselocale
  - fix locales in statically linked threaded programs
  - fix NSS

* Thu Aug 29 2002 Jakub Jelinek <jakub@redhat.com> 2.2.91-1
- update from CVS
  - 2.2.91 release
  - fix fd leaks in locale-archive reader (#72043)
- handle EROFS in build-locale-archive gracefully (#71665)

* Wed Aug 28 2002 Jakub Jelinek <jakub@redhat.com> 2.2.90-27
- update from CVS
  - fix re_match (#72312)
- support more than 1024 threads

* Fri Aug 23 2002 Jakub Jelinek <jakub@redhat.com> 2.2.90-26
- update from CVS
  - fix i386 build

* Thu Aug 22 2002 Jakub Jelinek <jakub@redhat.com> 2.2.90-25
- update from CVS
  - fix locale-archive loading hang on some (non-primary) locales
    (#72122, #71878)
  - fix umount problems with locale-archives when /usr is a separate
    partition (#72043)
- add LICENSES file

* Fri Aug 16 2002 Jakub Jelinek <jakub@redhat.com> 2.2.90-24
- update from CVS
  - only mmap up to 2MB of locale-archive on 32-bit machines
    initially
  - fix fseek past end + fread segfault with mmaped stdio
- include <sys/debugreg.h> which is mistakenly not included
  in glibc-devel on IA-32

* Fri Aug 16 2002 Jakub Jelinek <jakub@redhat.com> 2.2.90-23
- don't return normalized locale name in setlocale when using
  locale-archive

* Thu Aug 15 2002 Jakub Jelinek <jakub@redhat.com> 2.2.90-22
- update from CVS
  - optimize for primary system locale
- localedef fixes (#71552, #67705)

* Wed Aug 14 2002 Jakub Jelinek <jakub@redhat.com> 2.2.90-21
- fix path to locale-archive in libc reader
- build locale archive at glibc-common %post time
- export __strtold_internal and __wcstold_internal on Alpha again
- workaround some localedata problems

* Tue Aug 13 2002 Jakub Jelinek <jakub@redhat.com> 2.2.90-20
- update from CVS
- patch out set_thread_area for now

* Fri Aug  9 2002 Jakub Jelinek <jakub@redhat.com> 2.2.90-19
- update from CVS
- GB18030 patch from Yu Shao
- applied Debian patch for getaddrinfo IPv4 vs. IPv6
- fix regcomp (#71039)

* Sun Aug  4 2002 Jakub Jelinek <jakub@redhat.com> 2.2.90-18
- update from CVS
- use /usr/sbin/prelink, not prelink (#70376)

* Thu Jul 25 2002 Jakub Jelinek <jakub@redhat.com> 2.2.90-17
- update from CVS

* Thu Jul 25 2002 Jakub Jelinek <jakub@redhat.com> 2.2.90-16
- update from CVS
  - ungetc fix (#69586)
  - fseek errno fix (#69589)
  - change *etrlimit prototypes for C++ (#68588)
- use --without-tls instead of --disable-tls

* Thu Jul 11 2002 Jakub Jelinek <jakub@redhat.com> 2.2.90-15
- set nscd user's shell to /sbin/nologin (#68369)
- fix glibc-compat buffer overflows (security)
- buildrequire prelink, don't build glibc's own copy of it (#67567)
- update from CVS
  - regex fix (#67734)
  - fix unused warnings (#67706)
  - fix freopen with mmap stdio (#67552)
  - fix realloc (#68499)

* Tue Jun 25 2002 Bill Nottingham <notting@redhat.com> 2.2.90-14
- update from CVS
  - fix argp on long words
  - update atime in libio

* Sat Jun 22 2002 Jakub Jelinek <jakub@redhat.com> 2.2.90-13
- update from CVS
  - a thread race fix
  - fix readdir on invalid dirp

* Wed Jun 19 2002 Jakub Jelinek <jakub@redhat.com> 2.2.90-12
- update from CVS
  - don't use __thread in headers
- fix system(3) in threaded apps
- update prelink, so that it is possible to prelink -u libc.so.6.1
  on Alpha

* Fri Jun  7 2002 Jakub Jelinek <jakub@redhat.com> 2.2.90-11
- update from CVS
  - fix __moddi3 (#65612, #65695)
  - fix ether_line (#64427)
- fix setvbuf with mmap stdio (#65864)
- --disable-tls for now, waiting for kernel
- avoid duplication of __divtf3 etc. on IA-64
- make sure get*ent_r and _IO_wfile_jumps are exported (#62278)

* Tue May 21 2002 Jakub Jelinek <jakub@redhat.com> 2.2.90-10
- update from CVS
  - fix Alpha pthread bug with gcc 3.1

* Fri Apr 19 2002 Jakub Jelinek <jakub@redhat.com> 2.2.5-35
- fix nice

* Mon Apr 15 2002 Jakub Jelinek <jakub@redhat.com> 2.2.5-34
- add relocation dependencies even for weak symbols (#63422)
- stricter check_fds check for suid/sgid binaries
- run make check at %%install time

* Sat Apr 13 2002 Jakub Jelinek <jakub@redhat.com> 2.2.5-33
- handle Dec 31 1969 in mktime for timezones west of GMT (#63369)
- back out do-lookup.h change (#63261, #63305)
- use "memory" clobber instead all the fancy stuff in i386/i686/bits/string.h
  since lots of compilers break on it
- fix sparc build with gcc 3.1
- fix spec file for athlon

* Tue Apr  9 2002 Jakub Jelinek <jakub@redhat.com> 2.2.5-32
- fix debugging of threaded apps (#62804)
- fix DST for Estonia (#61494)
- document that pthread_mutexattr_?etkind_np are deprecated
  and pthread_mutexattr_?ettype should be used instead in man
  pages (#61485)
- fix libSegFault.so undefined externals

* Fri Apr  5 2002 Jakub Jelinek <jakub@redhat.com> 2.2.5-31
- temporarily disable prelinking ld.so, as some statically linked
  binaries linked against debugging versions of old glibcs die on it
  (#62352)
- fix <semaphore.h> for -std=c99 (#62516)
- fix ether_ntohost segfault (#62397)
- remove in glibc_post_upgrade on i386 all /lib/i686/libc-*.so,
  /lib/i686/libm-*.so and /lib/i686/libpthread-*.so, not just current
  version (#61633)
- prelink -r on alpha too

* Thu Mar 28 2002 Jakub Jelinek <jakub@redhat.com> 2.2.5-30
- update GB18030 iconv module (Yu Shao)

* Tue Mar 26 2002 Jakub Jelinek <jakub@redhat.com> 2.2.5-29
- features.h fix

* Tue Mar 26 2002 Jakub Jelinek <jakub@redhat.com> 2.2.5-28
- update from CVS
  - fix nscd with huge groups
  - fix nis to not close fds it shouldn't
- rebuilt against newer glibc-kernheaders to use the correct
  PATH_MAX
- handle .athlon.rpm glibc the same way as .i686.rpm
- add a couple of .ISO-8859-15 locales (#61922)
- readd temporarily currencies which were superceeded by Euro
  into the list of accepted currencies by localedef to make
  standard conformance testsuites happy
- temporarily moved __libc_waitpid back to make Sun JDK happy
- use old malloc code
- prelink i686/athlon ld.so and prelink -r i686/athlon libc.so

* Thu Mar 14 2002 Jakub Jelinek <jakub@redhat.com> 2.2.5-27
- update from CVS
  - fix DST handling for southern hemisphere (#60747)
  - fix daylight setting for tzset (#59951)
  - fix ftime (#60350)
  - fix nice return value
  - fix a malloc segfault
- temporarily moved __libc_wait, __libc_fork and __libc_stack_end
  back to what they used to be exported at
- censorship (#60758)

* Thu Feb 28 2002 Jakub Jelinek <jakub@redhat.com> 2.2.5-26
- update from CVS
- use __attribute__((visibility(...))) if supported, use _rtld_local
  for ld.so only objects
- provide libc's own __{,u}{div,mod}di3

* Wed Feb 27 2002 Jakub Jelinek <jakub@redhat.com> 2.2.5-25
- switch back to 2.2.5, mmap stdio needs work

* Mon Feb 25 2002 Jakub Jelinek <jakub@redhat.com> 2.2.90-8
- fix two other mmap stdio bugs (#60228)

* Thu Feb 21 2002 Jakub Jelinek <jakub@redhat.com> 2.2.90-7
- fix yet another mmap stdio bug (#60145)

* Tue Feb 19 2002 Jakub Jelinek <jakub@redhat.com> 2.2.90-6
- fix mmap stdio bug (seen on ld as File truncated error, #60043)
- apply Andreas Schwab's fix for pthread sigwait
- remove /lib/i686/ libraries in glibc_post_upgrade when
  performing i386 glibc install

* Thu Feb 14 2002 Jakub Jelinek <jakub@redhat.com> 2.2.90-5
- update to CVS
- added glibc-utils subpackage
- disable autoreq in glibc-debug
- readd %%lang() to locale files

* Fri Feb  7 2002 Jakub Jelinek <jakub@redhat.com> 2.2.90-4
- update to CVS
- move glibc private symbols to GLIBC_PRIVATE symbol version

* Wed Jan  9 2002 Jakub Jelinek <jakub@redhat.com> 2.2.90-3
- fix a sqrt bug on alpha which caused SHN_UNDEF $__full_ieee754_sqrt..ng
  symbol in libm

* Tue Jan  8 2002 Jakub Jelinek <jakub@redhat.com> 2.2.90-2
- add debug-static package

* Mon Dec 31 2001 Jakub Jelinek <jakub@redhat.com> 2.2.90-1
- update from CVS
- remove -D__USE_STRING_INLINES
- add debug subpackage to trim glibc and glibc-devel size

* Wed Oct  3 2001 Jakub Jelinek <jakub@redhat.com> 2.2.4-19
- fix strsep

* Fri Sep 28 2001 Jakub Jelinek <jakub@redhat.com> 2.2.4-18
- fix a ld.so bug with duplicate searchlists in l_scope
- fix erfcl(-inf)
- turn /usr/lib/librt.so into linker script

* Wed Sep 26 2001 Jakub Jelinek <jakub@redhat.com> 2.2.4-17
- fix a ld.so lookup bug after lots of dlopen calls
- fix CMSG_DATA for non-gcc non-ISOC99 compilers (#53984)
- prelinking support for Sparc64

* Fri Sep 21 2001 Jakub Jelinek <jakub@redhat.com> 2.2.4-16
- update from CVS to fix DT_SYMBOLIC
- prelinking support for Alpha and Sparc

* Tue Sep 18 2001 Jakub Jelinek <jakub@redhat.com> 2.2.4-15
- update from CVS
  - linuxthreads now retries if -1/EINTR is returned from
    reading or writing to thread manager pipe (#43742)
- use DT_FILTER in librt.so (#53394)
  - update glibc prelink patch so that it handles filters
- fix timer_* with SIGEV_NONE (#53494)
- make glibc_post_upgrade work on PPC (patch from Franz Sirl)

* Mon Sep 10 2001 Jakub Jelinek <jakub@redhat.com> 2.2.4-14
- fix build on sparc32
- 2.2.4-13 build for some reason missed some locales
  on alpha/ia64

* Mon Sep  3 2001 Jakub Jelinek <jakub@redhat.com> 2.2.4-13
- fix iconvconfig

* Mon Sep  3 2001 Jakub Jelinek <jakub@redhat.com> 2.2.4-12
- add fam to /etc/rpc (#52863)
- fix <inttypes.h> for C++ (#52960)
- fix perror

* Mon Aug 27 2001 Jakub Jelinek <jakub@redhat.com> 2.2.4-11
- fix strnlen(x, -1)

* Mon Aug 27 2001 Jakub Jelinek <jakub@redhat.com> 2.2.4-10
- doh, <bits/libc-lock.h> should only define __libc_rwlock_t
  if __USE_UNIX98.

* Mon Aug 27 2001 Jakub Jelinek <jakub@redhat.com> 2.2.4-9
- fix bits/libc-lock.h so that gcc can compile
- fix s390 build

* Fri Aug 24 2001 Jakub Jelinek <jakub@redhat.com> 2.2.4-8
- kill stale library symlinks in ldconfig (#52350)
- fix inttypes.h for G++ < 3.0
- use DT_REL*COUNT

* Wed Aug 22 2001 Jakub Jelinek <jakub@redhat.com> 2.2.4-7
- fix strnlen on IA-64 (#50077)

* Thu Aug 16 2001 Jakub Jelinek <jakub@redhat.com> 2.2.4-6
- glibc 2.2.4 final
- fix -lpthread -static (#51672)

* Fri Aug 10 2001 Jakub Jelinek <jakub@redhat.com> 2.2.4-5
- doh, include libio/tst-swscanf.c

* Fri Aug 10 2001 Jakub Jelinek <jakub@redhat.com> 2.2.4-4
- don't crash on catclose(-1)
- fix wscanf %[] handling
- fix return value from swprintf
- handle year + %U/%W week + week day in strptime

* Thu Aug  9 2001 Jakub Jelinek <jakub@redhat.com> 2.2.4-3
- update from CVS to
  - fix strcoll (#50548)
  - fix seekdir (#51132)
  - fix memusage (#50606)
- don't make gconv-modules.cache %%config file, just don't verify
  its content.

* Mon Aug  6 2001 Jakub Jelinek <jakub@redhat.com>
- fix strtod and *scanf (#50723, #50724)

* Sat Aug  4 2001 Jakub Jelinek <jakub@redhat.com>
- update from CVS
  - fix iconv cache handling
- glibc should not own %{_infodir}, %{_mandir} nor %{_mandir}/man3 (#50673)
- add gconv-modules.cache as emtpy config file (#50699)
- only run iconvconfig if /usr is mounted read-write (#50667)

* Wed Jul 25 2001 Jakub Jelinek <jakub@redhat.com>
- move iconvconfig from glibc-common into glibc subpackage,
  call it from glibc_post_upgrade instead of common's post.

* Tue Jul 24 2001 Jakub Jelinek <jakub@redhat.com>
- turn off debugging printouts in iconvconfig

* Tue Jul 24 2001 Jakub Jelinek <jakub@redhat.com>
- update from CVS
  - fix IA-32 makecontext
  - make fflush(0) thread-safe (#46446)

* Mon Jul 23 2001 Jakub Jelinek <jakub@redhat.com>
- adjust prelinking DT_* and SHT_* values in elf.h
- update from CVS
  - iconv cache
  - make iconv work in SUID/SGID programs (#34611)

* Fri Jul 20 2001 Jakub Jelinek <jakub@redhat.com>
- update from CVS
  - kill non-pic code in libm.so
  - fix getdate
  - fix some locales (#49402)
- rebuilt with binutils-2.11.90.0.8-5 to place .interp section
  properly in libBrokenLocale.so, libNoVersion.so and libanl.so
- add floating stacks on IA-64, Alpha, Sparc (#49308)

* Mon Jul 16 2001 Jakub Jelinek <jakub@redhat.com>
- make /lib/i686 directory owned by glibc*.i686.rpm

* Mon Jul  9 2001 Jakub Jelinek <jakub@redhat.com>
- remove rquota.[hx] headers which are now provided by quota (#47141)
- add prelinking patch

* Thu Jul  5 2001 Jakub Jelinek <jakub@redhat.com>
- require sh-utils for nscd

* Mon Jun 25 2001 Jakub Jelinek <jakub@redhat.com>
- update from CVS (#43681, #43350, #44663, #45685)
- fix ro_RO bug (#44644)

* Wed Jun  6 2001 Jakub Jelinek <jakub@redhat.com>
- fix a bunch of math bugs (#43210, #43345, #43346, #43347, #43348, #43355)
- make rpc headers -ansi compilable (#42390)
- remove alphaev6 optimized memcpy, since there are still far too many
  broken apps which call memcpy where they should call memmove
- update from CVS to (among other things):
  - fix tanhl bug (#43352)

* Tue May 22 2001 Jakub Jelinek <jakub@redhat.com>
- fix #include <signal.h> with -D_XOPEN_SOURCE=500 on ia64 (#35968)
- fix a dlclose reldeps handling bug
- some more profiling fixes
- fix tgmath.h

* Thu May 17 2001 Jakub Jelinek <jakub@redhat.com>
- make ldconfig more quiet
- fix LD_PROFILE on i686 (#41030)

* Wed May 16 2001 Jakub Jelinek <jakub@redhat.com>
- fix the hardlink program, so that it really catches all files with
  identical content
- add a s390x clone fix

* Wed May 16 2001 Jakub Jelinek <jakub@redhat.com>
- fix rpc for non-threaded apps using svc_fdset and similar variables (#40409)
- fix nss compatibility DSO versions for alphaev6
- add a hardlink program instead of the shell 3x for plus cmp -s/link
  which takes a lot of time during build
- rework BuildPreReq and Conflicts with gcc, so that
  it applies only where it has to

* Fri May 11 2001 Jakub Jelinek <jakub@redhat.com>
- fix locale name of ja_JP in UTF-8 (#39783)
- fix re_search_2 (#40244)
- fix memusage script (#39138, #39823)
- fix dlsym(RTLD_NEXT, ) from main program (#39803)
- fix xtrace script (#39609)
- make glibc conflict with glibc-devel 2.2.2 and below (to make sure
  libc_nonshared.a has atexit)
- fix getconf LFS_CFLAGS on 64bitters
- recompile with gcc-2.96-84 or above to fix binary compatibility problem
  with __frame_state_for function (#37933)

* Fri Apr 27 2001 Jakub Jelinek <jakub@redhat.com>
- glibc 2.2.3 release
  - fix strcoll (#36539)
- add BuildPreReqs (#36378)

* Wed Apr 25 2001 Jakub Jelinek <jakub@redhat.com>
- update from CVS

* Fri Apr 20 2001 Jakub Jelinek <jakub@redhat.com>
- update from CVS
  - fix sparc64, ia64
  - fix some locale syntax errors (#35982)

* Wed Apr 18 2001 Jakub Jelinek <jakub@redhat.com>
- update from CVS

* Wed Apr 11 2001 Jakub Jelinek <jakub@redhat.com>
- update from CVS

* Fri Apr  6 2001 Jakub Jelinek <jakub@redhat.com>
- support even 2.4.0 kernels on ia64, sparc64 and s390x
- include UTF-8 locales
- make gconv-modules %%config(noreplace)

* Fri Mar 23 2001 Jakub Jelinek <jakub@redhat.com>
- back out sunrpc changes

* Wed Mar 21 2001 Jakub Jelinek <jakub@redhat.com>
- update from CVS
  - fix ia64 build
  - fix pthread_getattr_np

* Fri Mar 16 2001 Jakub Jelinek <jakub@redhat.com>
- update from CVS
  - run atexit() registered functions at dlclose time if they are in shared
    libraries (#28625)
  - add pthread_getattr_np API to make JVM folks happy

* Wed Mar 14 2001 Jakub Jelinek <jakub@redhat.com>
- require 2.4.1 instead of 2.4.0 on platforms where it required 2.4 kernel
- fix ldd behaviour on unresolved symbols
- remove nonsensical ldconfig warning, update osversion for the most
  recent library with the same soname in the same directory instead (#31703)
- apply selected patches from CVS
- s390x spec file changes from Florian La Roche

* Wed Mar  7 2001 Jakub Jelinek <jakub@redhat.com>
- fix gencat (#30894)
- fix ldconfig changes from yesterday, fix LD_ASSUME_KERNEL handling

* Tue Mar  6 2001 Jakub Jelinek <jakub@redhat.com>
- update from CVS
- make pthread_attr_setstacksize consistent before and after pthread manager
  is started (#28194)
- pass back struct sigcontext from pthread signal wrapper (on ia32 only so
  far, #28493)
- on i686 ship both --enable-kernel 2.2.5 and 2.4.0 libc/libm/libpthread,
  make ld.so pick the right one

* Sat Feb 17 2001 Preston Brown <pbrown@redhat.com>
- glib-common doesn't require glibc, until we can figure out how to get out of dependency hell.

* Sat Feb 17 2001 Jakub Jelinek <jakub@redhat.com>
- make glibc require particular version of glibc-common
  and glibc-common prerequire glibc.

* Fri Feb 16 2001 Jakub Jelinek <jakub@redhat.com>
- glibc 2.2.2 release
  - fix regex REG_ICASE bug seen in ksymoops

* Sat Feb 10 2001 Jakub Jelinek <jakub@redhat.com>
- fix regexec leaking memory (#26864)

* Fri Feb  9 2001 Jakub Jelinek <jakub@redhat.com>
- update from CVS
  - fix ia64 build with gnupro
  - make regex 64bit clean
  - fix tgmath make check failures on alpha

* Tue Feb  6 2001 Jakub Jelinek <jakub@redhat.com>
- update again for ia64 DF_1_INITFIRST

* Fri Feb  2 2001 Jakub Jelinek <jakub@redhat.com>
- update from CVS
  - fix getaddrinfo (#25437)
  - support DF_1_INITFIRST (#25029)

* Wed Jan 24 2001 Jakub Jelinek <jakub@redhat.com>
- build all auxiliary arches with --enablekernel 2.4.0, those wanting
  to run 2.2 kernels can downgrade to the base architecture glibc.

* Sat Jan 20 2001 Jakub Jelinek <jakub@redhat.com>
- remove %%lang() flags from %%{_prefix}/lib/locale files temporarily

* Sun Jan 14 2001 Jakub Jelinek <jakub@redhat.com>
- update to 2.2.1 final
  - fix a pthread_kill_other_threads_np breakage (#23966)
  - make static binaries using dlopen work on ia64 again
- fix a typo in glibc-common group

* Wed Jan 10 2001 Bernhard Rosenkraenzer <bero@redhat.com>
- devel requires glibc = %%{version}
- noreplace /etc/nscd.conf

* Wed Jan 10 2001 Jakub Jelinek <jakub@redhat.com>
- some more security fixes:
  - don't look up LD_PRELOAD libs in cache for SUID apps
    (because that bypasses SUID bit checking on the library)
  - place output files for profiling SUID apps into /var/profile,
    use O_NOFOLLOW for them
  - add checks for $MEMUSAGE_OUTPUT and $SEGFAULT_OUTPUT_NAME
- hardlink identical locale files together
- add %%lang() tags to locale stuff
- remove ko_KR.utf8 for now, it is provided by locale-utf8 package

* Mon Jan  8 2001 Jakub Jelinek <jakub@redhat.com>
- add glibc-common subpackage
- fix alphaev6 memcpy (#22494)
- fix sys/cdefs.h (#22908)
- don't define stdin/stdout/stderr as macros for -traditional (#22913)
- work around a bug in IBM JDK (#22932, #23012)
- fix pmap_unset when network is down (#23176)
- move nscd in rc.d before netfs on shutdown
- fix $RESOLV_HOST_CONF in SUID apps (#23562)

* Fri Dec 15 2000 Jakub Jelinek <jakub@redhat.com>
- fix ftw and nftw

* Wed Dec 13 2000 Jakub Jelinek <jakub@redhat.com>
- fix fcvt (#22184)
- ldd /lib/ld-linux.so.2 is not crashing any longer again (#22197)
- fix gencat

* Mon Dec 11 2000 Jakub Jelinek <jakub@redhat.com>
- fix alpha htonl and alphaev6 stpcpy

* Sat Dec  9 2000 Jakub Jelinek <jakub@redhat.com>
- update to CVS to:
  - fix getnameinfo (#21934)
  - don't stomp on memory in rpath handling (#21544)
  - fix setlocale (#21507)
- fix libNoVersion.so.1 loading code (#21579)
- use auxarches define in spec file for auxiliary
  architectures (#21219)
- remove /usr/share directory from filelist (#21218)

* Sun Nov 19 2000 Jakub Jelinek <jakub@redhat.com>
- update to CVS to fix getaddrinfo

* Fri Nov 17 2000 Jakub Jelinek <jakub@redhat.com>
- update to CVS to fix freopen
- remove all alpha workarounds, not needed anymore

* Wed Nov 15 2000 Jakub Jelinek <jakub@redhat.com>
- fix dladdr bug on alpha/sparc32/sparc64
- fix Makefiles so that they run static tests properly

* Tue Nov 14 2000 Jakub Jelinek <jakub@redhat.com>
- update to CVS to fix ldconfig

* Thu Nov  9 2000 Jakub Jelinek <jakub@redhat.com>
- update to glibc 2.2 release

* Mon Nov  6 2000 Jakub Jelinek <jakub@redhat.com>
- update to CVS to:
  - export __sysconf@@GLIBC_2.2 (#20417)

* Fri Nov  3 2000 Jakub Jelinek <jakub@redhat.com>
- merge to 2.1.97

* Mon Oct 30 2000 Jakub Jelinek <jakub@redhat.com>
- update to CVS, including:
  - fix WORD_BIT/LONG_BIT definition in limits.h (#19088)
  - fix hesiod (#19375)
  - set LC_MESSAGES in zic/zdump for proper error message output (#19495)
  - fix LFS fcntl when used with non-LFS aware kernels (#19730)

* Thu Oct 19 2000 Jakub Jelinek <jakub@redhat.com>
- fix alpha semctl (#19199)
- update to CVS, including:
  - fix glibc headers for Compaq non-gcc compilers
  - fix locale alias handling code (#18832)
  - fix rexec on little endian machines (#18886)
- started writing changelog again

* Thu Aug 10 2000 Adrian Havill <havill@redhat.com>
- added ja ujis alias for backwards compatibility
