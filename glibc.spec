%define glibcdate 20041210T0634
%define glibcversion 2.3.3
%define glibcrelease 90
%define auxarches i586 i686 athlon sparcv9 alphaev6
%define prelinkarches noarch
%define nptlarches i386 i686 athlon x86_64 ia64 s390 s390x sparcv9 ppc ppc64
%define rtkaioarches noarch
%define withtlsarches i386 i686 athlon x86_64 ia64 s390 s390x alpha alphaev6 sparc sparcv9 ppc ppc64
%define debuginfocommonarches %{ix86} alpha alphaev6 sparc sparcv9
%define _unpackaged_files_terminate_build 0
Summary: The GNU libc libraries.
Name: glibc
Version: %{glibcversion}
Release: %{glibcrelease}
Copyright: LGPL
Group: System Environment/Libraries
%define glibcsrcdir %{name}-%{glibcdate}
Source0: %{glibcsrcdir}.tar.bz2
Source1: %{name}-fedora-%{glibcdate}.tar.bz2
Patch0: %{name}-fedora.patch
Patch1: %{name}-nptl-check.patch
Patch2: %{name}-ppc-assume.patch
Patch3: %{name}-ia64-lib64.patch
Buildroot: %{_tmppath}/glibc-%{PACKAGE_VERSION}-root
Obsoletes: zoneinfo, libc-static, libc-devel, libc-profile, libc-headers,
Obsoletes:  linuxthreads, gencat, locale, ldconfig, locale-ja
Provides: ldconfig
Autoreq: false
Requires: glibc-common = %{version}-%{release}
%ifarch sparc
Obsoletes: libc
%endif
# Require libgcc in case some program calls pthread_cancel in its %%post
Prereq: basesystem, libgcc
# This is for building auxiliary programs like memusage, nscd
# For initial glibc bootstraps it can be commented out
BuildPreReq: gd-devel libpng-devel zlib-devel texinfo, libselinux-devel >= 1.17.10-1
BuildPreReq: sed >= 3.95
%ifarch %{prelinkarches}
BuildPreReq: prelink >= 0.2.0-5
%endif
# This is to ensure that __frame_state_for is exported by glibc
# will be compatible with egcs 1.x.y
BuildPreReq: gcc >= 3.2
Conflicts: rpm <= 4.0-0.65
Conflicts: glibc-devel < 2.2.3
Conflicts: gcc4 <= 4.0.0-0.6
# Earlier shadow-utils packages had too restrictive permissions on
# /etc/default
Conflicts: shadow-utils < 2:4.0.3-20
Conflicts: nscd < 2.3.3-52
%ifarch ia64 sparc64 s390x x86_64
Conflicts: kernel < 2.4.0
%define enablekernel 2.4.0
%else
%ifarch ppc64
Conflicts: kernel < 2.4.19
%define enablekernel 2.4.19
%else
%define enablekernel 2.2.5
%ifarch i686 athlon
%define enablekernelltfs 2.4.1
%endif
%endif
%endif
%ifarch %{nptlarches}
%define enablekernelnptl 2.4.20
%ifarch i386
%define nptl_target_cpu i486
%define tls_subdir tls/i486
%else
%define nptl_target_cpu %{_target_cpu}
%define tls_subdir tls
%endif
%endif
BuildRequires: binutils >= 2.13.90.0.16-5
BuildRequires: gcc >= 3.2.1-5
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

%package devel
Summary: Object files for development using standard C libraries.
Group: Development/Libraries
Conflicts: texinfo < 3.11
Conflicts: binutils < 2.13.90.0.16-5
Prereq: /sbin/install-info
Obsoletes: libc-debug, libc-headers, libc-devel, linuxthreads-devel
Obsoletes: glibc-debug
Prereq: %{name}-headers
Requires: %{name}-headers = %{version}-%{release}, %{name} = %{version}
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
Obsoletes: libc-debug, libc-headers, libc-devel, linuxthreads-devel
Prereq: kernel-headers
Requires: kernel-headers >= 2.2.1, %{name} = %{version}
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

%package -n nptl-devel
Summary: Header files and static libraries for development using NPTL library.
Group: Development/Libraries
Requires: glibc-devel = %{version}-%{release}
Autoreq: true

%description -n nptl-devel
The nptl-devel package contains the header and object files necessary
for developing programs which use the NPTL library (and either need
NPTL specific header files or want to link against NPTL statically).

%package profile
Summary: The GNU libc libraries, including support for gprof profiling.
Group: Development/Libraries
Obsoletes: libc-profile
Autoreq: true

%description profile
The glibc-profile package includes the GNU libc libraries and support
for profiling using the gprof program.  Profiling is analyzing a
program's functions to see how much CPU time they use and determining
which functions are calling other functions during execution.  To use
gprof to profile a program, your program needs to use the GNU libc
libraries included in glibc-profile (instead of the standard GNU libc
libraries included in the glibc package).

If you are going to use the gprof program to profile a program, you'll
need to install the glibc-profile package.

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
Requires: libselinux >= 1.17.10-1
Conflicts: selinux-policy-targeted < 1.17.30-2.2
Prereq: /sbin/chkconfig, /usr/sbin/useradd, /usr/sbin/userdel, sh-utils
Autoreq: true

%description -n nscd
Nscd caches name service lookups and can dramatically improve
performance with NIS+, and may help with DNS as well. Note that you
can't use nscd with 2.0 kernels because of bugs in the kernel-side
thread support. Unfortunately, nscd happens to hit these bugs
particularly hard.

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

%description debuginfo-common
This package provides debug information for package %{name}.
Debug information is useful when developing applications that use this
package or when debugging this package.

%endif
%endif

%prep
%setup -q -n %{glibcsrcdir} -a1
%patch0 -E -p1
case "`gcc --version | head -1`" in
gcc*\ 3.[34]*)
%ifarch %{nptlarches}
%patch1 -p1
%endif
  ;;
gcc*\ 3.2.3*)
  case "`uname -r`" in *.ent*|*.EL*)
%patch2 -p1
  ;; esac ;;
esac
%ifarch ia64
%if "%{_lib}" == "lib64"
%patch3 -p1
%endif
%endif

# Hack till glibc-kernheaders get updated, argh
mkdir asm
cat > asm/unistd.h <<EOF
#ifndef _HACK_ASM_UNISTD_H
#include_next <asm/unistd.h>
%ifarch alpha
#ifndef __NR_stat64
#define __NR_stat64			425
#define __NR_lstat64			426
#define __NR_fstat64			427
#endif
#ifndef __NR_mq_open
#define __NR_mq_open			432
#define __NR_mq_unlink			433
#define __NR_mq_timedsend		434
#define __NR_mq_timedreceive		435
#define __NR_mq_notify			436
#define __NR_mq_getsetattr		437
#endif
#ifndef __NR_waitid
#define __NR_waitid			438
#endif
%endif
%ifarch %{ix86}
#ifndef __NR_mq_open
#define __NR_mq_open 		277
#define __NR_mq_unlink		(__NR_mq_open+1)
#define __NR_mq_timedsend	(__NR_mq_open+2)
#define __NR_mq_timedreceive	(__NR_mq_open+3)
#define __NR_mq_notify		(__NR_mq_open+4)
#define __NR_mq_getsetattr	(__NR_mq_open+5)
#endif
#ifndef __NR_waitid
#define __NR_waitid		284
#endif
%endif
%ifarch ia64
#ifndef __NR_timer_create
#define __NR_timer_create		1248
#define __NR_timer_settime		1249
#define __NR_timer_gettime		1250
#define __NR_timer_getoverrun		1251
#define __NR_timer_delete		1252
#define __NR_clock_settime		1253
#define __NR_clock_gettime		1254
#define __NR_clock_getres		1255
#define __NR_clock_nanosleep		1256
#endif
#ifndef __NR_mq_open
#define __NR_mq_open			1262
#define __NR_mq_unlink			1263
#define __NR_mq_timedsend		1264
#define __NR_mq_timedreceive		1265
#define __NR_mq_notify			1266
#define __NR_mq_getsetattr		1267
#endif
#ifndef __NR_waitid
#define __NR_waitid			1270
#endif
%endif
%ifarch ppc
#ifndef __NR_utimes
#define __NR_utimes		251
#endif
#ifndef __NR_statfs64
#define __NR_statfs64		252
#define __NR_fstatfs64		253
#endif
#ifndef __NR_fadvise64_64
#define __NR_fadvise64_64	254
#endif
#ifndef __NR_mq_open
#define __NR_mq_open		262
#define __NR_mq_unlink		263
#define __NR_mq_timedsend	264
#define __NR_mq_timedreceive	265
#define __NR_mq_notify		266
#define __NR_mq_getsetattr	267
#endif
%endif
%ifarch ppc64
#ifndef __NR_utimes
#define __NR_utimes		251
#endif
#ifndef __NR_mq_open
#define __NR_mq_open		262
#define __NR_mq_unlink		263
#define __NR_mq_timedsend	264
#define __NR_mq_timedreceive	265
#define __NR_mq_notify		266
#define __NR_mq_getsetattr	267
#endif
%endif
%ifarch s390
#ifndef __NR_timer_create
#define __NR_timer_create	254
#define __NR_timer_settime	(__NR_timer_create+1)
#define __NR_timer_gettime	(__NR_timer_create+2)
#define __NR_timer_getoverrun	(__NR_timer_create+3)
#define __NR_timer_delete	(__NR_timer_create+4)
#define __NR_clock_settime	(__NR_timer_create+5)
#define __NR_clock_gettime	(__NR_timer_create+6)
#define __NR_clock_getres	(__NR_timer_create+7)
#define __NR_clock_nanosleep	(__NR_timer_create+8)
#endif
#ifndef __NR_fadvise64_64
#define __NR_fadvise64_64	264
#endif
#ifndef __NR_statfs64
#define __NR_statfs64		265
#define __NR_fstatfs64		266
#endif
#ifndef __NR_mq_open
#define __NR_mq_open		271
#define __NR_mq_unlink		272
#define __NR_mq_timedsend	273
#define __NR_mq_timedreceive	274
#define __NR_mq_notify		275
#define __NR_mq_getsetattr	276
#endif
%endif
%ifarch s390x
#ifndef __NR_timer_create
#define __NR_timer_create	254
#define __NR_timer_settime	(__NR_timer_create+1)
#define __NR_timer_gettime	(__NR_timer_create+2)
#define __NR_timer_getoverrun	(__NR_timer_create+3)
#define __NR_timer_delete	(__NR_timer_create+4)
#define __NR_clock_settime	(__NR_timer_create+5)
#define __NR_clock_gettime	(__NR_timer_create+6)
#define __NR_clock_getres	(__NR_timer_create+7)
#define __NR_clock_nanosleep	(__NR_timer_create+8)
#endif
#ifndef __NR_mq_open
#define __NR_mq_open		271
#define __NR_mq_unlink		272
#define __NR_mq_timedsend	273
#define __NR_mq_timedreceive	274
#define __NR_mq_notify		275
#define __NR_mq_getsetattr	276
#endif
%endif
%ifarch sparc sparc64
#ifndef __NR_mq_open
#define __NR_mq_open		273
#define __NR_mq_unlink		274
#define __NR_mq_timedsend	275
#define __NR_mq_timedreceive	276
#define __NR_mq_notify		277
#define __NR_mq_getsetattr	278
#endif
#ifndef __NR_waitid
#define __NR_waitid		279
#endif
%endif
%ifarch x86_64
#ifndef __NR_mq_open
#define __NR_mq_open		240
#define __NR_mq_unlink		241
#define __NR_mq_timedsend	242
#define __NR_mq_timedreceive	243
#define __NR_mq_notify		244
#define __NR_mq_getsetattr	245
#endif
#ifndef __NR_waitid
#define __NR_waitid		247
#endif
%endif
#endif
EOF

%ifnarch %{ix86} alpha alphaev6 sparc sparcv9
rm -rf glibc-compat
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

%build
rm -rf build-%{_target_cpu}-linux
mkdir build-%{_target_cpu}-linux ; cd build-%{_target_cpu}-linux
GCC=gcc
%ifarch %{ix86}
BuildFlags="-march=%{_target_cpu}"
%endif
%ifarch alphaev6
BuildFlags="-mcpu=ev6"
%endif
%ifarch sparc
BuildFlags="-fcall-used-g6"
GCC="gcc -m32"
%endif
%ifarch sparcv9
BuildFlags="-mcpu=ultrasparc -fcall-used-g6"
GCC="gcc -m32"
%endif
%ifarch sparc64
BuildFlags="-mcpu=ultrasparc -mvis -fcall-used-g6"
GCC="gcc -m64"
%endif
%ifarch ppc64
BuildFlags="-mno-minimal-toc"
GCC="gcc -m64"
%endif

# If gcc supports __thread, test it even in --with-tls --without-__thread
# builds.
if echo '__thread int a;' | $GCC -xc - -S -o /dev/null 2>/dev/null; then
  sed -ie 's/0 [|][|]/1 ||/' ../elf/tst-tls10.h ../linuxthreads/tst-tls1.h
fi

BuildFlags="$BuildFlags -DNDEBUG=1"
if gcc -v 2>&1 | grep -q 'gcc version 3.[0123]'; then
  BuildFlags="$BuildFlags -finline-limit=2000"
fi
EnableKernel="--enable-kernel=%{enablekernel}"
echo "$BuildFlags" > ../BuildFlags
echo "$GCC" > ../Gcc
AddOns=`cd .. && echo */configure | sed -e 's!/configure!!g;s!\(linuxthreads\|nptl\|rtkaio\)\( \|$\)!!g;s! \+$!!;s! !,!g;s!^!,!;/^,\*$/d'`
echo "$AddOns" > ../AddOns
Pthreads=linuxthreads
%ifarch %{withtlsarches}
WithTls="--with-tls --without-__thread"
%else
WithTls="--without-tls --without-__thread"
%endif
CC="$GCC" CFLAGS="$BuildFlags -g -O3" ../configure --prefix=%{_prefix} \
	--enable-add-ons=$Pthreads$AddOns --without-cvs $EnableKernel \
	--with-headers=%{_prefix}/include --enable-bind-now \
	$WithTls --build %{_target_cpu}-redhat-linux --host %{_target_cpu}-redhat-linux
if [ -x /usr/bin/getconf ] ; then
  numprocs=$(/usr/bin/getconf _NPROCESSORS_ONLN)
  if [ $numprocs -eq 0 ]; then
    numprocs=1
  fi
else
  numprocs=1
fi
make -j$numprocs -r CFLAGS="$BuildFlags -g -O3" PARALLELMFLAGS=-s
$GCC -static -L. -Os ../fedora/glibc_post_upgrade.c -o glibc_post_upgrade \
%ifarch i386
    -DARCH_386 \
%endif
%ifarch %{nptlarches}
    '-DLIBTLS="/%{_lib}/tls/"' \
%endif
    '-DGCONV_MODULES_CACHE="%{_prefix}/%{_lib}/gconv/gconv-modules.cache"' \
    '-DLD_SO_CONF="/etc/ld.so.conf"'
cd ..

# hack
unset LD_ASSUME_KERNEL || :

%ifarch %{rtkaioarches}
AddOns=,rtkaio$AddOns
%endif

%ifarch i686 athlon
rm -rf build-%{_target_cpu}-linuxltfs
mkdir build-%{_target_cpu}-linuxltfs ; cd build-%{_target_cpu}-linuxltfs
EnableKernel="--enable-kernel=%{enablekernelltfs} --disable-profile"
Pthreads=linuxthreads
%ifarch %{withtlsarches}
WithTls="--with-tls --without-__thread"
%else
WithTls="--without-tls --without-__thread"
%endif
CC="$GCC" CFLAGS="$BuildFlags -g -O3" ../configure --prefix=%{_prefix} \
	--enable-add-ons=$Pthreads$AddOns --without-cvs $EnableKernel \
	--with-headers=%{_prefix}/include --enable-bind-now \
	$WithTls --build %{_target_cpu}-redhat-linux --host %{_target_cpu}-redhat-linux
make -j$numprocs -r CFLAGS="$BuildFlags -g -O3" PARALLELMFLAGS=-s

cd ..
%endif

%ifarch %{nptlarches}
rm -rf build-%{nptl_target_cpu}-linuxnptl
mkdir build-%{nptl_target_cpu}-linuxnptl ; cd build-%{nptl_target_cpu}-linuxnptl
EnableKernel="--enable-kernel=%{enablekernelnptl} --disable-profile"
Pthreads=nptl
WithTls="--with-tls --with-__thread"
CC="$GCC" CFLAGS="$BuildFlags -g -O3" ../configure --prefix=%{_prefix} \
	--enable-add-ons=$Pthreads$AddOns --without-cvs $EnableKernel \
	--with-headers=%{_prefix}/include --enable-bind-now \
	$WithTls --build %{nptl_target_cpu}-redhat-linux --host %{nptl_target_cpu}-redhat-linux
make -j$numprocs -r CFLAGS="$BuildFlags -g -O3" PARALLELMFLAGS=-s

cd ..
%endif

%install
# hack
unset LD_ASSUME_KERNEL || :

BuildFlags=`cat BuildFlags`
GCC=`cat Gcc`
AddOns=`cat AddOns`

%ifarch %{rtkaioarches}
AddOns=,rtkaio$AddOns
%endif

if [ -x /usr/bin/getconf ] ; then
  numprocs=$(/usr/bin/getconf _NPROCESSORS_ONLN)
  if [ $numprocs -eq 0 ]; then
    numprocs=1
  fi
else
  numprocs=1
fi
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT
make -j1 install_root=$RPM_BUILD_ROOT install -C build-%{_target_cpu}-linux PARALLELMFLAGS=-s
%ifnarch %{auxarches}
cd build-%{_target_cpu}-linux && \
    make -j$numprocs install_root=$RPM_BUILD_ROOT install-locales -C ../localedata objdir=`pwd` && \
    cd ..
%endif

SubDir=

%ifarch i686 athlon
cd build-%{_target_cpu}-linuxltfs
Pthreads=linuxthreads
SubDir=i686
mkdir -p $RPM_BUILD_ROOT/lib/$SubDir/
cp -a libc.so $RPM_BUILD_ROOT/lib/$SubDir/`basename $RPM_BUILD_ROOT/lib/libc-*.so`
ln -sf `basename $RPM_BUILD_ROOT/lib/libc-*.so` $RPM_BUILD_ROOT/lib/$SubDir/`basename $RPM_BUILD_ROOT/lib/libc.so.*`
cp -a math/libm.so $RPM_BUILD_ROOT/lib/$SubDir/`basename $RPM_BUILD_ROOT/lib/libm-*.so`
ln -sf `basename $RPM_BUILD_ROOT/lib/libm-*.so` $RPM_BUILD_ROOT/lib/$SubDir/`basename $RPM_BUILD_ROOT/lib/libm.so.*`
cp -a $Pthreads/libpthread.so $RPM_BUILD_ROOT/lib/$SubDir/`basename $RPM_BUILD_ROOT/lib/libpthread-*.so`
pushd $RPM_BUILD_ROOT/lib/$SubDir
ln -sf libpthread-*.so `basename $RPM_BUILD_ROOT/lib/libpthread.so.*`
popd
%ifarch %{rtkaioarches}
cp -a rtkaio/librtkaio.so $RPM_BUILD_ROOT/lib/$SubDir/`basename $RPM_BUILD_ROOT/lib/librt-*.so | sed s/librt-/librtkaio-/`
ln -sf `basename $RPM_BUILD_ROOT/lib/librt-*.so | sed s/librt-/librtkaio-/` $RPM_BUILD_ROOT/lib/$SubDir/`basename $RPM_BUILD_ROOT/lib/librt.so.*`
%else
cp -a rt/librt.so $RPM_BUILD_ROOT/lib/$SubDir/`basename $RPM_BUILD_ROOT/lib/librt-*.so`
ln -sf `basename $RPM_BUILD_ROOT/lib/librt-*.so` $RPM_BUILD_ROOT/lib/$SubDir/`basename $RPM_BUILD_ROOT/lib/librt.so.*`
%endif

cd ..
%endif

%ifarch %{nptlarches}
cd build-%{nptl_target_cpu}-linuxnptl
Pthreads=nptl
SubDir=%{tls_subdir}
mkdir -p $RPM_BUILD_ROOT/%{_lib}/$SubDir/
cp -a libc.so $RPM_BUILD_ROOT/%{_lib}/$SubDir/`basename $RPM_BUILD_ROOT/%{_lib}/libc-*.so`
ln -sf `basename $RPM_BUILD_ROOT/%{_lib}/libc-*.so` $RPM_BUILD_ROOT/%{_lib}/$SubDir/`basename $RPM_BUILD_ROOT/%{_lib}/libc.so.*`
cp -a math/libm.so $RPM_BUILD_ROOT/%{_lib}/$SubDir/`basename $RPM_BUILD_ROOT/%{_lib}/libm-*.so`
ln -sf `basename $RPM_BUILD_ROOT/%{_lib}/libm-*.so` $RPM_BUILD_ROOT/%{_lib}/$SubDir/`basename $RPM_BUILD_ROOT/%{_lib}/libm.so.*`
cp -a $Pthreads/libpthread.so $RPM_BUILD_ROOT/%{_lib}/$SubDir/libpthread-%{version}.so
pushd $RPM_BUILD_ROOT/%{_lib}/$SubDir
ln -sf libpthread-*.so `basename $RPM_BUILD_ROOT/%{_lib}/libpthread.so.*`
popd
%ifarch %{rtkaioarches}
cp -a rtkaio/librtkaio.so $RPM_BUILD_ROOT/%{_lib}/$SubDir/`basename $RPM_BUILD_ROOT/%{_lib}/librt-*.so | sed s/librt-/librtkaio-/`
ln -sf `basename $RPM_BUILD_ROOT/%{_lib}/librt-*.so | sed s/librt-/librtkaio-/` $RPM_BUILD_ROOT/%{_lib}/$SubDir/`basename $RPM_BUILD_ROOT/%{_lib}/librt.so.*`
%else
cp -a rt/librt.so $RPM_BUILD_ROOT/%{_lib}/$SubDir/`basename $RPM_BUILD_ROOT/%{_lib}/librt-*.so`
ln -sf `basename $RPM_BUILD_ROOT/%{_lib}/librt-*.so` $RPM_BUILD_ROOT/%{_lib}/$SubDir/`basename $RPM_BUILD_ROOT/%{_lib}/librt.so.*`
%endif
cp -a ${Pthreads}_db/libthread_db.so $RPM_BUILD_ROOT/%{_lib}/$SubDir/`basename $RPM_BUILD_ROOT/%{_lib}/libthread_db-*.so`
ln -sf `basename $RPM_BUILD_ROOT/%{_lib}/libthread_db-*.so` $RPM_BUILD_ROOT/%{_lib}/$SubDir/`basename $RPM_BUILD_ROOT/%{_lib}/libthread_db.so.*`

mkdir -p $RPM_BUILD_ROOT%{_prefix}/%{_lib}/nptl
cp -a libc.a nptl/libpthread.a nptl/libpthread_nonshared.a rt/librt.a \
  $RPM_BUILD_ROOT%{_prefix}/%{_lib}/nptl/
sed "s| /%{_lib}/| /%{_lib}/$SubDir/|" $RPM_BUILD_ROOT%{_prefix}/%{_lib}/libc.so \
  > $RPM_BUILD_ROOT%{_prefix}/%{_lib}/nptl/libc.so
sed "s|^GROUP (.*)|GROUP ( /%{_lib}/$SubDir/"`basename $RPM_BUILD_ROOT/%{_lib}/libpthread.so.*`' %{_prefix}/%{_lib}/nptl/libpthread_nonshared.a )|' \
  $RPM_BUILD_ROOT%{_prefix}/%{_lib}/libc.so \
  > $RPM_BUILD_ROOT%{_prefix}/%{_lib}/nptl/libpthread.so
%ifarch %{rtkaioarches}
ln -sf /%{_lib}/$SubDir/`basename $RPM_BUILD_ROOT/%{_lib}/librt-*.so | sed 's/librt-/librtkaio-/'` \
  $RPM_BUILD_ROOT%{_prefix}/%{_lib}/nptl/librt.so
%else
ln -sf /%{_lib}/$SubDir/`basename $RPM_BUILD_ROOT/%{_lib}/librt-*.so` \
  $RPM_BUILD_ROOT%{_prefix}/%{_lib}/nptl/librt.so
%endif
strip -g $RPM_BUILD_ROOT%{_prefix}/%{_lib}/nptl/*.a
mkdir -p $RPM_BUILD_ROOT/nptl $RPM_BUILD_ROOT%{_prefix}/include/nptl
make -j1 install_root=$RPM_BUILD_ROOT/nptl install-headers PARALLELMFLAGS=-s
pushd $RPM_BUILD_ROOT/nptl%{_prefix}/include
  for i in `find . -type f`; do
    if ! [ -f $RPM_BUILD_ROOT%{_prefix}/include/$i ] \
       || ! cmp -s $i $RPM_BUILD_ROOT%{_prefix}/include/$i; then
      mkdir -p $RPM_BUILD_ROOT%{_prefix}/include/nptl/`dirname $i`
      cp -a $i $RPM_BUILD_ROOT%{_prefix}/include/nptl/$i
    fi
  done
popd
rm -rf $RPM_BUILD_ROOT/nptl

cd ..

%ifarch i386
for i in i586 i686; do
  mkdir $RPM_BUILD_ROOT/%{_lib}/tls/$i
  pushd $RPM_BUILD_ROOT/%{_lib}/tls/$i
    ln -sf ../i486/*.so .
    cp -a ../i486/*.so.* .
  popd
done
%endif
%endif

# compatibility hack: this locale has vanished from glibc, but some other
# programs are still using it. Normally we would handle it in the %pre
# section but with glibc that is simply not an option
mkdir -p $RPM_BUILD_ROOT%{_prefix}/lib/locale/ru_RU/LC_MESSAGES

# Remove the files we don't want to distribute
rm -f $RPM_BUILD_ROOT%{_prefix}/%{_lib}/libNoVersion*
%ifnarch %{ix86} alpha alphaev6 sparc sparcv9
rm -f $RPM_BUILD_ROOT/%{_lib}/libNoVersion*
%endif

# the man pages for the linuxthreads require special attention
make -C linuxthreads/man
mkdir -p $RPM_BUILD_ROOT%{_mandir}/man3
install -m 0644 linuxthreads/man/*.3thr $RPM_BUILD_ROOT%{_mandir}/man3
gzip -9nvf $RPM_BUILD_ROOT%{_mandir}/man3/*

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
touch $RPM_BUILD_ROOT/etc/ld.so.cache
chmod 644 $RPM_BUILD_ROOT/etc/ld.so.conf
mkdir -p $RPM_BUILD_ROOT/etc/ld.so.conf.d

# Include %{_prefix}/%{_lib}/gconv/gconv-modules.cache
> $RPM_BUILD_ROOT%{_prefix}/%{_lib}/gconv/gconv-modules.cache
chmod 644 $RPM_BUILD_ROOT%{_prefix}/%{_lib}/gconv/gconv-modules.cache

# Install the upgrade program
install -m 700 build-%{_target_cpu}-linux/glibc_post_upgrade $RPM_BUILD_ROOT/usr/sbin/glibc_post_upgrade

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

%ifarch %{prelinkarches}
%ifarch i686 athlon
# Prelink ld.so and libc.so
> prelink.conf
# For now disable prelinking of ld.so, as it breaks statically linked
# binaries built against non-NDEBUG old glibcs (assert unknown dynamic tag)
# /usr/sbin/prelink -c ./prelink.conf -C ./prelink.cache \
#  --mmap-region-start=0x00101000 $RPM_BUILD_ROOT/%{_lib}/ld-*.so
/usr/sbin/prelink --reloc-only=0x00e80000 $RPM_BUILD_ROOT/%{_lib}/$SubDir/libc-*.so
%endif
%ifarch alpha alphaev6
# Prelink ld.so and libc.so
> prelink.conf
# For now disable prelinking of ld.so, as it breaks statically linked
# binaries built against non-NDEBUG old glibcs (assert unknown dynamic tag)
# /usr/sbin/prelink -c ./prelink.conf -C ./prelink.cache \
# --mmap-region-start=0x0000020000000000 $RPM_BUILD_ROOT/%{_lib}/ld-*.so
/usr/sbin/prelink --reloc-only=0x0000020010000000 $RPM_BUILD_ROOT/%{_lib}/$SubDir/libc-*.so
%endif
%endif

# rquota.x and rquota.h are now provided by quota
rm -f $RPM_BUILD_ROOT%{_prefix}/include/rpcsvc/rquota.[hx]

# Hardlink identical locale files together
%ifnarch %{auxarches}
gcc -O2 -o build-%{_target_cpu}-linux/hardlink fedora/hardlink.c
build-%{_target_cpu}-linux/hardlink -vc $RPM_BUILD_ROOT%{_prefix}/lib/locale
%endif

%ifarch %{ix86} alpha alphaev6 sparc sparcv9
rm -f ${RPM_BUILD_ROOT}/%{_lib}/libnss1-*
rm -f ${RPM_BUILD_ROOT}/%{_lib}/libnss-*.so.1
%endif

# BUILD THE FILE LIST
find $RPM_BUILD_ROOT -type f -or -type l |
	sed -e 's|.*/etc|%config &|' \
	    -e 's|.*/gconv/gconv-modules$|%verify(not md5 size mtime) %config(noreplace) &|' \
	    -e 's|.*/gconv/gconv-modules.cache|%verify(not md5 size mtime) &|' \
	    -e '/lib\/debug/d' > rpm.filelist.in
for n in %{_prefix}/share %{_prefix}/include %{_prefix}/lib/locale; do
    find ${RPM_BUILD_ROOT}${n} -type d | \
	grep -v '%{_prefix}/share$' | \
	grep -v '\(%{_mandir}\|%{_infodir}\)' | \
	sed "s/^/%dir /" >> rpm.filelist.in
done

# primary filelist
SHARE_LANG='s|.*/share/locale/\([^/_]\+\).*/LC_MESSAGES/.*\.mo|%lang(\1) &|'
LIB_LANG='s|.*/lib/locale/\([^/_]\+\)|%lang(\1) &|'
# rpm does not handle %lang() tagged files hardlinked together accross
# languages very well, temporarily disable
# LIB_LANG=''
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
    $i.tmp > $i
  chmod 755 $i; rm -f $i.tmp
done

grep '%{_prefix}/%{_lib}/lib.*_p\.a' < rpm.filelist > profile.filelist || :
egrep "(%{_prefix}/include)|(%{_infodir})" < rpm.filelist |
	grep -v %{_prefix}/include/nptl |
	grep -v %{_infodir}/dir > devel.filelist

mv rpm.filelist rpm.filelist.full
grep -v '%{_prefix}/%{_lib}/lib.*_p.a' rpm.filelist.full |
	egrep -v "(%{_prefix}/include)|(%{_infodir})" > rpm.filelist

grep '%{_prefix}/%{_lib}/lib.*\.a' < rpm.filelist >> devel.filelist
grep '%{_prefix}/%{_lib}/.*\.o' < rpm.filelist >> devel.filelist
grep '%{_prefix}/%{_lib}/lib.*\.so' < rpm.filelist >> devel.filelist
grep '%{_mandir}' < rpm.filelist >> devel.filelist

grep '%{_prefix}/include' < devel.filelist > headers.filelist
grep -v '%{_prefix}/include' < devel.filelist > devel.filelist.tmp
mv -f devel.filelist.tmp devel.filelist

mv rpm.filelist rpm.filelist.full
grep -v '%{_prefix}/%{_lib}/lib.*\.a' < rpm.filelist.full |
	grep -v '%{_prefix}/%{_lib}/.*\.o' |
	grep -v '%{_prefix}/%{_lib}/lib.*\.so'|
	grep -v '%{_prefix}/%{_lib}/nptl' |
	grep -v '%{_mandir}' |
	grep -v 'nscd' > rpm.filelist

grep '%{_prefix}/bin' < rpm.filelist >> common.filelist
grep '%{_prefix}/lib/locale' < rpm.filelist >> common.filelist
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

echo '%{_prefix}/sbin/build-locale-archive' >> common.filelist
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

cd fedora
$GCC -Os -static -o build-locale-archive build-locale-archive.c \
  ../build-%{_target_cpu}-linux/locale/locarchive.o \
  ../build-%{_target_cpu}-linux/locale/md5.o \
  -DDATADIR=\"%{_datadir}\" -DPREFIX=\"%{_prefix}\" \
  -L../build-%{_target_cpu}-linux
install -m 700 build-locale-archive $RPM_BUILD_ROOT/usr/sbin/build-locale-archive
cd ..

# the last bit: more documentation
rm -rf documentation
mkdir documentation
cp linuxthreads/ChangeLog  documentation/ChangeLog.threads
cp linuxthreads/Changes documentation/Changes.threads
cp linuxthreads/README documentation/README.threads
cp linuxthreads/FAQ.html documentation/FAQ-threads.html
cp -r linuxthreads/Examples documentation/examples.threads
cp crypt/README.ufc-crypt documentation/README.ufc-crypt
cp timezone/README documentation/README.timezone
cp ChangeLog* documentation
gzip -9n documentation/ChangeLog*

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

# Increase timeouts
export TIMEOUTFACTOR=16
echo ====================TESTING=========================
cd build-%{_target_cpu}-linux
make -j$numprocs -k check PARALLELMFLAGS=-s 2>&1 | tee check.log || :
cd ..
%ifarch i686 athlon
echo ====================TESTING LINUXTHREADS FS=========
cd build-%{_target_cpu}-linuxltfs
make -j$numprocs -k check PARALLELMFLAGS=-s 2>&1 | tee check.log || :
cd ..
%endif
%ifarch %{nptlarches}
echo ====================TESTING NPTL====================
cd build-%{nptl_target_cpu}-linuxnptl
make -j$numprocs -k check PARALLELMFLAGS=-s 2>&1 | tee check.log || :
cd ..
%endif
echo ====================TESTING DETAILS=================
for i in `sed -n 's|^.*\*\*\* \[\([^]]*\.out\)\].*$|\1|p' build-*-linux*/check.log`; do
  echo =====$i=====
  cat $i || :
  echo ============
done
%ifarch i686 athlon
echo ====================TESTING LINUXTHREADS FS LD.SO===
cd build-%{_target_cpu}-linuxltfs
mv elf/ld.so elf/ld.so.orig
cp -a ../build-%{_target_cpu}-linux/elf/ld.so elf/ld.so
find . -name \*.out -exec mv -f '{}' '{}'.origldso \;
make -j$numprocs -k check PARALLELMFLAGS=-s 2>&1 | tee check2.log || :
cd ..
%endif
%ifarch %{nptlarches}
echo ====================TESTING NPTL LD.SO==============
cd build-%{nptl_target_cpu}-linuxnptl
mv elf/ld.so elf/ld.so.orig
cp -a ../build-%{_target_cpu}-linux/elf/ld.so elf/ld.so
find . -name \*.out -exec mv -f '{}' '{}'.origldso \;
make -j$numprocs -k check PARALLELMFLAGS=-s 2>&1 | tee check2.log || :
cd ..
%endif
echo ====================TESTING DETAILS=================
for i in `sed -n 's|^.*\*\*\* \[\([^]]*\.out\)\].*$|\1|p' build-*-linux*/check2.log`; do
  echo =====$i=====
  cat $i || :
  echo ============
done
echo ====================TESTING END=====================
PLTCMD='/^Relocation section .*\(\.rela\?\.plt\|\.rela\.IA_64\.pltoff\)/,/^$/p'
echo ====================PLT RELOCS LD.SO================
readelf -Wr $RPM_BUILD_ROOT/%{_lib}/ld-*.so | sed -n -e "$PLTCMD"
echo ====================PLT RELOCS LIBC.SO==============
readelf -Wr $RPM_BUILD_ROOT/%{_lib}/$SubDir/libc-*.so | sed -n -e "$PLTCMD"
echo ====================PLT RELOCS END==================

%if "%{_enable_debug_packages}" == "1"

case "$-" in *x*) save_trace=yes;; esac
set +x
echo Building debuginfo subpackage...

blf=debugfiles.list
sf=debugsources.list
cblf=debugcommonfiles.list
csf=debugcommonsources.list

echo -n > $sf
echo -n > $csf

strip $RPM_BUILD_ROOT/{sbin/ldconfig,usr/sbin/glibc_post_upgrade,usr/sbin/build-locale-archive}

# Strip ELF binaries
for f in `grep -v '%%\(dir\|lang\|config\|verify\)' rpm.filelist`; do
  bf=$RPM_BUILD_ROOT$f
  if [ -f $bf -a -x $bf -a ! -h $bf ]; then
    if `file $bf 2>/dev/null | grep 'ELF.*, not stripped' | grep -vq 'statically linked'`; then
      bd=`dirname $f`
      outd=$RPM_BUILD_ROOT/usr/lib/debug$bd
      mkdir -p $outd
      echo extracting debug info from $f
      /usr/lib/rpm/debugedit -b $RPM_BUILD_DIR -d /usr/src/debug -l $sf $bf
      bn=`basename $f`
      case $f in
        /%{_lib}/*) eu-strip -g -f $outd/$bn.debug $bf || :;;
        *) eu-strip -f $outd/$bn.debug $bf || :;;
      esac
      if [ -f $outd/$bn.debug ]; then echo /usr/lib/debug$bd/$bn.debug >> $blf; fi
    fi
  fi
done

for f in `cat common.filelist utils.filelist nscd.filelist \
          | grep -v '%%\(dir\|lang\|config\|verify\)'`; do
  bf=$RPM_BUILD_ROOT$f
  if [ -f $bf -a -x $bf -a ! -h $bf ]; then
    if `file $bf 2>/dev/null | grep 'ELF.*, not stripped' | grep -vq 'statically linked'`; then
      bd=`dirname $f`
      outd=$RPM_BUILD_ROOT/usr/lib/debug$bd
      mkdir -p $outd
      echo extracting debug info from $f
      /usr/lib/rpm/debugedit -b $RPM_BUILD_DIR -d /usr/src/debug -l $csf $bf
      bn=`basename $f`
      eu-strip -f $outd/$bn.debug $bf || :
      if [ -f $outd/$bn.debug ]; then echo /usr/lib/debug$bd/$bn.debug >> $cblf; fi
    fi
  fi
done

for f in `find $RPM_BUILD_ROOT/%{_lib} -type l`; do
  l=`ls -l $f`
  l=${l#* -> }
  t=/usr/lib/debug`dirname ${f#$RPM_BUILD_ROOT}`
  if grep -q "^$t/$l.debug\$" $blf; then
    ln -sf $l.debug $RPM_BUILD_ROOT$t/`basename $f`.debug
    echo $t/`basename $f`.debug >> $blf
  elif grep -q "^$t.debug/$l\$" $cblf; then
    ln -sf $l.debug $RPM_BUILD_ROOT$t/`basename $f`.debug
    echo $t/`basename $f`.debug >> $cblf
  fi
done

echo Sorting source file lists. Might take a while...
xargs -0 -n 1 echo < $sf | LANG=C sort -u > $sf.sorted
xargs -0 -n 1 echo < $csf | LANG=C sort -u > $csf.sorted
mkdir -p $RPM_BUILD_ROOT/usr/src/debug
cat $sf.sorted $csf.sorted \
  | (cd $RPM_BUILD_DIR; LANG=C sort -u | cpio -pdm ${RPM_BUILD_ROOT}/usr/src/debug)
# stupid cpio creates new directories in mode 0700, fixup
find $RPM_BUILD_ROOT/usr/src/debug -type d -print | xargs chmod a+rx

%ifarch %{debuginfocommonarches}
%ifarch %{auxarches}
%ifarch %{ix86}
%define basearch i386
%endif
%ifarch alpha alphaev6
%define basearch alpha
%endif
%ifarch sparc sparcv9
%define basearch sparc
%endif
cat $blf > debuginfo.filelist
find $RPM_BUILD_ROOT/usr/src/debug/%{glibcsrcdir} -type d \
  | sed "s#^$RPM_BUILD_ROOT#%%dir #" >> debuginfo.filelist
grep '/generic/\|/linux/\|/%{basearch}/\|/nptl\(_db\)\?/\|^%{glibcsrcdir}/build' \
  $sf.sorted | sed 's|^|/usr/src/debug/|' >> debuginfo.filelist
touch debuginfocommon.filelist
%else
( grep '^%{glibcsrcdir}/build-\|dl-osinfo\.h' $csf.sorted || : ) > $csf.sorted.build
cat $blf > debuginfo.filelist
cat $cblf > debuginfocommon.filelist
grep '^%{glibcsrcdir}/build-\|dl-osinfo\.h' $sf.sorted \
  | sed 's|^|/usr/src/debug/|' >> debuginfo.filelist
find $RPM_BUILD_ROOT/usr/src/debug/%{glibcsrcdir} -type d \
  | sed "s#^$RPM_BUILD_ROOT#%%dir #" >> debuginfocommon.filelist
( cat $csf.sorted; grep -v -f $csf.sorted.build $sf.sorted ) \
  | grep -v 'dl-osinfo\.h' | LC_ALL=C sort -u \
  | sed 's|^|/usr/src/debug/|' >> debuginfocommon.filelist
%endif
%else
cat $blf $cblf | LC_ALL=C sort -u > debuginfo.filelist
echo '/usr/src/debug/%{glibcsrcdir}' >> debuginfo.filelist
%endif

[ "x$save_trace" = xyes ] && set -x

%endif

%ifarch %{auxarches}
case "$-" in *x*) save_trace=yes;; esac
set +x
echo Cutting down the list of unpackaged files
for i in `sed '/%%dir/d;/%%config/d;/%%verify/d;s/%%lang([^)]*) //' \
	  common.filelist devel.filelist headers.filelist profile.filelist \
	  utils.filelist nscd.filelist`; do
  [ -f "$RPM_BUILD_ROOT$i" ] && rm -f "$RPM_BUILD_ROOT$i" || :
done
[ "x$save_trace" = xyes ] && set -x

%else

mkdir -p $RPM_BUILD_ROOT/var/{db,run}/nscd
touch $RPM_BUILD_ROOT/var/{db,run}/nscd/{passwd,group,hosts}
touch $RPM_BUILD_ROOT/var/run/nscd/{socket,nscd.pid}
%endif

touch $RPM_BUILD_ROOT/%{_prefix}/lib/locale/locale-archive

%post -p /usr/sbin/glibc_post_upgrade

%postun -p /sbin/ldconfig

%post common -p /usr/sbin/build-locale-archive

%post devel
/sbin/install-info %{_infodir}/libc.info.gz %{_infodir}/dir

%pre headers
# this used to be a link and it is causing nightmares now
if [ -L %{_prefix}/include/scsi ] ; then
    rm -f %{_prefix}/include/scsi
fi

%preun devel
if [ "$1" = 0 ]; then
    /sbin/install-info --delete %{_infodir}/libc.info.gz %{_infodir}/dir
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

%clean
rm -rf "$RPM_BUILD_ROOT"
rm -f *.filelist*

%files -f rpm.filelist
%defattr(-,root,root)
%ifarch %{nptlarches}
%dir /%{_lib}/%{tls_subdir}
%ifarch i386
%dir /%{_lib}/tls/i586
%dir /%{_lib}/tls/i686
%endif
%endif
%ifarch i686 athlon
%dir /lib/i686
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
%attr(0644,root,root) %verify(not md5 size mtime) %ghost %config(missingok,noreplace) /etc/ld.so.cache
%doc README NEWS INSTALL FAQ BUGS NOTES PROJECTS CONFORMANCE
%doc COPYING COPYING.LIB README.libm LICENSES
%doc hesiod/README.hesiod

%ifnarch %{auxarches}
%files -f common.filelist common
%defattr(-,root,root)
%attr(0644,root,root) %verify(not md5 size mtime mode) %ghost %config(missingok,noreplace) %{_prefix}/lib/locale/locale-archive
%dir %attr(755,root,root) /etc/default
%verify(not md5 size mtime) %config(noreplace) /etc/default/nss
%doc documentation/*

%files -f devel.filelist devel
%defattr(-,root,root)

%files -f headers.filelist headers
%defattr(-,root,root)
%ifarch %{nptlarches}
%{_prefix}/include/nptl
%endif

%files -f profile.filelist profile
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
%attr(0600,root,root) %verify(not md5 size mtime) %ghost %config(missingok,noreplace) /var/db/nscd/passwd
%attr(0600,root,root) %verify(not md5 size mtime) %ghost %config(missingok,noreplace) /var/db/nscd/group
%attr(0600,root,root) %verify(not md5 size mtime) %ghost %config(missingok,noreplace) /var/db/nscd/hosts
%endif

%ifarch %{nptlarches}
%files -n nptl-devel
%defattr(-,root,root)
%{_prefix}/%{_lib}/nptl
%endif

%if "%{_enable_debug_packages}" == "1"
%files debuginfo -f debuginfo.filelist
%defattr(-,root,root)
%ifarch %{debuginfocommonarches}
%ifnarch %{auxarches}
%files debuginfo-common -f debuginfocommon.filelist
%defattr(-,root,root)
%dir %{_prefix}/lib/debug
%dir %{_prefix}/lib/debug/%{_prefix}
%dir %{_prefix}/lib/debug/%{_prefix}/%{_lib}
%{_prefix}/lib/debug/%{_prefix}/%{_lib}/*.a
%endif
%else
%dir %{_prefix}/lib/debug
%dir %{_prefix}/lib/debug/%{_prefix}
%dir %{_prefix}/lib/debug/%{_prefix}/%{_lib}
%{_prefix}/lib/debug/%{_prefix}/%{_lib}/*.a
%endif
%endif

%changelog
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
