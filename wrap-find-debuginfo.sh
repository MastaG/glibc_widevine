#!/bin/bash
# Wrapper script for find-debuginfo.sh
#
# Usage:
#  wrap-find-debuginfo.sh SYSROOT-PATH SCRIPT-PATH SCRIPT-ARGS...
#
# The wrapper saves the original version of ld.so found in SYSROOT-PATH,
# invokes SCRIPT-PATH with SCRIPT-ARGS, and then restores the
# LDSO-PATH file, followed by note merging and DWZ compression.
# As a result, ld.so has (mostly) unchanged debuginfo even
# after debuginfo extraction.
#
# For libc.so.6 and other shared objects, a set of strategic symbols
# is preserved in .symtab that are frequently used in valgrind
# suppressions and elsewhere.

set -ex

ldso_tmp="$(mktemp)"
libc_tmp="$(mktemp)"
libdl_tmp="$(mktemp)"
libpthread_tmp="$(mktemp)"
librt_tmp="$(mktemp)"

# Prefer a separately installed debugedit over the RPM-integrated one.
if command -v debugedit >/dev/null ; then
    debugedit=debugedit
else
    debugedit=/usr/lib/rpm/debugedit
fi

cleanup () {
    rm -f "$ldso_tmp" "$libc_tmp" "$libdl_tmp" "$libpthread_tmp" "$librt_tmp"
}
trap cleanup 0

sysroot_path="$1"
shift
script_path="$1"
shift

# See run_ldso setting in glibc.spec.
ldso_path=
for ldso_candidate in `find "$sysroot_path" -name 'ld-*.so' -type f` ; do
    if test -z "$ldso_path" ; then
	ldso_path="$ldso_candidate"
    else
	echo "error: multiple ld.so candidates: $ldso_path, $ldso_candidate"
	exit 1
    fi
done

libc_path=
for libc_candidate in `find "$sysroot_path" -name 'libc-*.so' -type f` ; do
    if test -z "$libc_path" ; then
	libc_path="$libc_candidate"
    else
	echo "error: multiple libc.so.6 candidates: $libc_path, $libc_candidate"
	exit 1
    fi
done

libdl_path=
for libdl_candidate in `find "$sysroot_path" -name 'libdl-*.so' -type f` ; do
    if test -z "$libdl_path" ; then
	libdl_path="$libdl_candidate"
    else
	echo "error: multiple libdl.so.6 candidates: $libdl_path, $libdl_candidate"
	exit 1
    fi
done

libpthread_path=
for libpthread_candidate in `find "$sysroot_path" -name 'libpthread-*.so' -type f` ; do
    if test -z "$libpthread_path" ; then
	libpthread_path="$libpthread_candidate"
    else
	echo "error: multiple libpthread.so.6 candidates: $libpthread_path, $libpthread_candidate"
	exit 1
    fi
done

librt_path=
for librt_candidate in `find "$sysroot_path" -name 'librt-*.so' -type f` ; do
    if test -z "$librt_path" ; then
	librt_path="$librt_candidate"
    else
	echo "error: multiple librt.so.6 candidates: $librt_path, $librt_candidate"
	exit 1
    fi
done

# Preserve the original files.
cp "$ldso_path" "$ldso_tmp"
cp "$libc_path" "$libc_tmp"
cp "$libdl_path" "$libdl_tmp"
cp "$libpthread_path" "$libpthread_tmp"
cp "$librt_path" "$librt_tmp"

# Run the debuginfo extraction.
"$script_path" "$@"

# Restore the original files.
cp "$ldso_tmp" "$ldso_path"
cp "$libc_tmp" "$libc_path"
cp "$libdl_tmp" "$libdl_path"
cp "$libpthread_tmp" "$libpthread_path"
cp "$librt_tmp" "$librt_path"

# Reduce the size of notes.  Primarily for annobin.
objcopy --merge-notes "$ldso_path"
objcopy --merge-notes "$libc_path"
objcopy --merge-notes "$libdl_path"
objcopy --merge-notes "$libpthread_path"
objcopy --merge-notes "$librt_path"

# libc.so.6 and other shared objects: Reduce to valuable symbols.
# Eliminate file symbols, annobin symbols, and symbols used by the
# glibc build to implement hidden aliases (__EI_*).  We would also
# like to remove __GI_* symbols, but even listing them explicitly (as
# in -K __GI_strlen) still causes strip to remove them, so there is no
# filtering of __GI_* here.  (Debuginfo is gone after this, so no need
# to optimize it.)
for p in "$libc_path" "$libdl_path" "$libpthread_path" "$librt_path"; do
    strip -w \
	  -K '*' \
	  -K '!*.c' \
	  -K '!*.os' \
	  -K '!.annobin_*' \
	  -K '!__EI_*' \
	  -K '!__PRETTY_FUNCTION__*' \
	  "$p"
done

# ld.so: Rewrite the source file paths to match the extracted
# locations.  First compute the arguments for invoking debugedit.
# See find-debuginfo.sh.
debug_dest_name="/usr/src/debug"
last_arg=
while true ; do
    arg="$1"
    shift || break
    case "$arg" in
	(--unique-debug-src-base)
	    debug_dest_name="/usr/src/debug/$1"
	    shift
	    ;;
	(-*)
	    ;;
	(*)
	    last_arg="$arg"
	    ;;
    esac
done
debug_base_name=${last_arg:-$RPM_BUILD_ROOT}
$debugedit -b "$debug_base_name" -d "$debug_dest_name" -n $ldso_path

# Apply single-file DWARF optimization.
dwz $ldso_path
