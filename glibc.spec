%define glibcsrcdir  glibc-2.22-621-g90c400b
%define glibcversion 2.22.90
%define glibcrelease 51%{?dist}
# Pre-release tarballs are pulled in from git using a command that is
# effectively:
#
# git archive HEAD --format=tar --prefix=$(git describe --match 'glibc-*')/ \
#	> $(git describe --match 'glibc-*').tar
# gzip -9 $(git describe --match 'glibc-*').tar
#
# glibc_release_url is only defined when we have a release tarball.
# % define glibc_release_url http://ftp.gnu.org/gnu/glibc/
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
%ifarch s390 ppc64 ppc64p7
# There is no valgrind support for 31-bit s390.
# The valgrind test does not work on ppc64, ppc64p7 (bug 1273103).
%undefine with_valgrind
%endif
%endif
%if %{with werror}
%ifarch s390 s390x
# The s390 and s390x builds are not -Werror clean yet.  For s390, the
# latest problem may be due to questionable code in test-string.h
# (upstream bug 19261, rhbz#1283184).
%undefine with_werror
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
# Enable lock elision support for these architectures
#
# At the moment lock elision is disabled on x86_64 until there's a CPU that
# would actually benefit from enabling it.  Intel released a microcode update
# to disable HLE and RTM at boot and the Fedora kernel now applies it early
# enough that keeping lock elision enabled should be harmless, but we have
# disabled it anyway as a conservative measure.
%define lock_elision_arches s390 s390x
##############################################################################
# We build a special package for Xen that includes TLS support with
# no negative segment offsets for use with Xen guests. This is
# purely an optimization for increased performance on those arches.
%define xenarches i686 athlon
%ifarch %{xenarches}
%define buildxen 1
%define xenpackage 0
%else
%define buildxen 0
%define xenpackage 0
%endif
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
%define buildpower6 1
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
# If the architecture has multiarch support in glibc then it should be listed
# here to enable support in the build. Multiarch support is a single library
# with implementations of certain functions for multiple architectures. The
# most optimal function is selected at runtime based on the hardware that is
# detected by glibc. The underlying support for function selection and
# execution is provided by STT_GNU_IFUNC.
%define multiarcharches %{power64} %{ix86} x86_64 %{sparc}
##############################################################################
# Add -s for a less verbose build output.
%define silentrules PARALLELMFLAGS=
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
Group: System Environment/Libraries
URL: http://www.gnu.org/software/glibc/
Source0: %{?glibc_release_url}%{glibcsrcdir}.tar.gz
Source1: build-locale-archive.c
Source2: glibc_post_upgrade.c
Source3: libc-lock.h
Source4: nscd.conf
Source7: nsswitch.conf
Source8: power6emul.c
Source9: bench.mk
Source10: glibc-bench-compare

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

Patch0003: glibc-fedora-ldd.patch

Patch0004: glibc-fedora-ppc-unwind.patch

# Build info files in the source tree, then move to the build
# tree so that they're identical for multilib builds
Patch0005: glibc-rh825061.patch

# Horrible hack, never to be upstreamed.  Can go away once the world
# has been rebuilt to use the new ld.so path.
Patch0006: glibc-arm-hardfloat-3.patch

# Needs to be sent upstream
Patch0009: glibc-fedora-include-bits-ldbl.patch

# All these were from the glibc-fedora.patch mega-patch and need another
# round of reviewing.  Ideally they'll either be submitted upstream or
# dropped.
Patch0012: glibc-fedora-linux-tcsetattr.patch
Patch0014: glibc-fedora-nptl-linklibc.patch
Patch0015: glibc-fedora-localedef.patch
Patch0016: glibc-fedora-i386-tls-direct-seg-refs.patch
Patch0019: glibc-fedora-nis-rh188246.patch
Patch0020: glibc-fedora-manual-dircategory.patch
Patch0024: glibc-fedora-locarchive.patch
Patch0025: glibc-fedora-streams-rh436349.patch
Patch0028: glibc-fedora-localedata-rh61908.patch
Patch0030: glibc-fedora-uname-getrlimit.patch
Patch0031: glibc-fedora-__libc_multiple_libcs.patch
Patch0033: glibc-fedora-elf-ORIGIN.patch

# Needs to be sent upstream.
# Support mangling and demangling null pointers.
Patch0037: glibc-rh952799.patch

# ARM: Accept that some objects marked hard ABI are now not because of a
#      binutils bug.
Patch0044: glibc-rh1009145.patch

# Allow applications to call pthread_atfork without libpthread.so.
Patch0046: glibc-rh1013801.patch

Patch0047: glibc-nscd-sysconfig.patch

# Disable rwlock elision if --enable-lock-elision is not used.
Patch0052: glibc-disable-rwlock-elision.patch

# confstr _CS_PATH should only return /usr/bin on Fedora since /bin is just a
# symlink to it.
Patch0053: glibc-cs-path.patch

# Fix -Warray-bounds warning for GCC5, likely PR/59124 or PR/66422.
# See Fedora bug #1263817.
Patch0054: glibc-res-hconf-gcc5.patch
Patch0055: glibc-ld-ctype-gcc5.patch
Patch0056: glibc-gethnamaddr-gcc5.patch
Patch0057: glibc-dns-host-gcc5.patch
Patch0058: glibc-bug-regex-gcc5.patch

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

Patch2033: glibc-aarch64-tls-fixes.patch
Patch2034: glibc-aarch64-workaround-nzcv-clobber-in-tlsdesc.patch

# Group Merge Patch:
Patch2035: glibc-nsswitch-Add-group-merging-support.patch

# New pthread_barrier algorithm:
Patch2036: glibc-pthread-barrier.patch

##############################################################################
#
# Benchmark comparison patches.
#
##############################################################################
Patch3002: glibc-bench-build.patch

##############################################################################
# End of glibc patches.
##############################################################################

##############################################################################
# Continued list of core "glibc" package information:
##############################################################################
Buildroot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
Obsoletes: glibc-profile < 2.4
Obsoletes: nss_db
Provides: ldconfig

# The dynamic linker supports DT_GNU_HASH
Provides: rtld(GNU_HASH)

# This is a short term need until everything is rebuilt in the ARM world
# to use the new dynamic linker path
%ifarch armv7hl armv7hnl
Provides: ld-linux.so.3
Provides: ld-linux.so.3(GLIBC_2.4)
%endif

Requires: glibc-common = %{version}-%{release}

# Require libgcc in case some program calls pthread_cancel in its %%post
Requires(pre): basesystem, libgcc

# This is for building auxiliary programs like memusage, nscd
# For initial glibc bootstraps it can be commented out
BuildRequires: gd-devel libpng-devel zlib-devel
%if %{with docs}
# Removing texinfo will cause check-safety.sh test to fail because it seems to
# trigger documentation generation based on dependencies.  We need to fix this
# upstream in some way that doesn't depend on generating docs to validate the
# texinfo.  I expect it's simply the wrong dependency for that target.
BuildRequires: texinfo
%endif
%if %{without bootstrap}
BuildRequires: libselinux-devel >= 1.33.4-3
BuildRequires: nss-devel
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
BuildRequires: /usr/bin/valgrind
%endif

# We use systemd rpm macros for nscd
BuildRequires: systemd

# We use python for the microbenchmarks
BuildRequires: python

# This is to ensure that __frame_state_for is exported by glibc
# will be compatible with egcs 1.x.y
BuildRequires: gcc >= 3.2
%define enablekernel 2.6.32
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

%ifarch %{multiarcharches}
# Need STT_IFUNC support
%ifarch %{power64}
BuildRequires: binutils >= 2.20.51.0.2
Conflicts: binutils < 2.20.51.0.2
%else
%ifarch s390 s390x
# Needed for STT_GNU_IFUNC support for s390/390x
BuildRequires: binutils >= 2.23.52.0.1-8
Conflicts: binutils < 2.23.52.0.1-8
%else
# Default to this version
BuildRequires: binutils >= 2.19.51.0.10
Conflicts: binutils < 2.19.51.0.10
%endif
%endif
# Earlier releases have broken support for IRELATIVE relocations
Conflicts: prelink < 0.4.2
%else
# Need AS_NEEDED directive
# Need --hash-style=* support
BuildRequires: binutils >= 2.17.50.0.2-5
%endif

BuildRequires: gcc >= 3.2.1-5
%ifarch s390 s390x
BuildRequires: gcc >= 4.1.0-0.17
%endif
%if 0%{?_enable_debug_packages}
BuildRequires: elfutils >= 0.72
BuildRequires: rpm >= 4.2-0.56
%endif

%if %{without boostrap}
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
%endif
%endif

# Filter out all GLIBC_PRIVATE symbols since they are internal to
# the package and should not be examined by any other tool.
%global __filter_GLIBC_PRIVATE 1

%description
The glibc package contains standard libraries which are used by
multiple programs on the system. In order to save disk space and
memory, as well as to make upgrading easier, common system code is
kept in one place and shared between programs. This particular package
contains the most important sets of shared libraries: the standard C
library and the standard math library. Without these two libraries, a
Linux system will not function.

##############################################################################
# glibc "xen" sub-package
##############################################################################
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

##############################################################################
# glibc "devel" sub-package
##############################################################################
%package devel
Summary: Object files for development using standard C libraries.
Group: Development/Libraries
Requires(pre): /sbin/install-info
Requires(pre): %{name}-headers
Requires: %{name}-headers = %{version}-%{release}
Requires: %{name} = %{version}-%{release}

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
Group: Development/Libraries
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
Group: Development/Libraries
Provides: %{name}-headers(%{_target_cpu})
%ifarch x86_64
# If both -m32 and -m64 is to be supported on AMD64, x86_64 glibc-headers
# have to be installed, not i586 ones.
Obsoletes: %{name}-headers(i586)
Obsoletes: %{name}-headers(i686)
%endif
Requires(pre): kernel-headers
Requires: kernel-headers >= 2.2.1, %{name} = %{version}-%{release}
BuildRequires: kernel-headers >= 2.6.22

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
Group: System Environment/Base

%description common
The glibc-common package includes common binaries for the GNU libc
libraries, as well as national language (locale) support.

%package locale-source
Summary: The sources for the locales
Requires: %{name} = %{version}-%{release}
Requires: %{name}-common = %{version}-%{release}
Group: System Environment/Base

%description locale-source
The sources for the locales

%define lang_package() \
%package langpack-%{1}\
Summary: Locale data for %{1}\
Requires: %{name} = %{version}-%{release}\
Requires: %{name}-common = %{version}-%{release}\
Requires: tzdata >= 2003a\
%define supplements_list %(locale -a | grep ^%{1}_ | cut -d @ -f 1 | cut -d . -f 1 | sort -u | tr "\\\\n" " " | sed 's/ $//' | sed 's/ / or langpacks-/g' | sed 's/^/ or langpacks-/')\
Supplements: (glibc = %{version}-%{release} and (langpacks-%{1}%{supplements_list}))\
Group: System Environment/Base\
%description langpack-%{1}\
The glibc-langpack-%{1} package includes the locale data for %{1}.\
%ifnarch %{auxarches}\
%files -f langpack-%{1}.filelist langpack-%{1}\
%defattr(-,root,root)\
%endif\
%{nil}

%lang_package aa
%lang_package af
%lang_package ak
%lang_package am
%lang_package an
%lang_package anp
%lang_package ar
%lang_package as
%lang_package ast
%lang_package ayc
%lang_package az
%lang_package be
%lang_package bem
%lang_package ber
%lang_package bg
%lang_package bhb
%lang_package bho
%lang_package bn
%lang_package bo
%lang_package br
%lang_package brx
%lang_package bs
%lang_package byn
%lang_package ca
%lang_package ce
%lang_package cmn
%lang_package crh
%lang_package cs
%lang_package csb
%lang_package cv
%lang_package cy
%lang_package da
%lang_package de
%lang_package doi
%lang_package dv
%lang_package dz
%lang_package el
%lang_package en
%lang_package eo
%lang_package es
%lang_package et
%lang_package eu
%lang_package fa
%lang_package ff
%lang_package fi
%lang_package fil
%lang_package fo
%lang_package fr
%lang_package fur
%lang_package fy
%lang_package ga
%lang_package gd
%lang_package gez
%lang_package gl
%lang_package gu
%lang_package gv
%lang_package ha
%lang_package hak
%lang_package he
%lang_package hi
%lang_package hne
%lang_package hr
%lang_package hsb
%lang_package ht
%lang_package hu
%lang_package hy
%lang_package ia
%lang_package id
%lang_package ig
%lang_package ik
%lang_package is
%lang_package it
%lang_package iu
%lang_package iw
%lang_package ja
%lang_package ka
%lang_package kk
%lang_package kl
%lang_package km
%lang_package kn
%lang_package ko
%lang_package kok
%lang_package ks
%lang_package ku
%lang_package kw
%lang_package ky
%lang_package lb
%lang_package lg
%lang_package li
%lang_package lij
%lang_package lo
%lang_package lt
%lang_package lv
%lang_package lzh
%lang_package mag
%lang_package mai
%lang_package mg
%lang_package mhr
%lang_package mi
%lang_package mk
%lang_package ml
%lang_package mn
%lang_package mni
%lang_package mr
%lang_package ms
%lang_package mt
%lang_package my
%lang_package nan
%lang_package nb
%lang_package nds
%lang_package ne
%lang_package nhn
%lang_package niu
%lang_package nl
%lang_package nn
%lang_package nr
%lang_package nso
%lang_package oc
%lang_package om
%lang_package or
%lang_package os
%lang_package pa
%lang_package pap
%lang_package pl
%lang_package ps
%lang_package pt
%lang_package quz
%lang_package raj
%lang_package ro
%lang_package ru
%lang_package rw
%lang_package sa
%lang_package sat
%lang_package sc
%lang_package sd
%lang_package se
%lang_package shs
%lang_package si
%lang_package sid
%lang_package sk
%lang_package sl
%lang_package so
%lang_package sq
%lang_package sr
%lang_package ss
%lang_package st
%lang_package sv
%lang_package sw
%lang_package szl
%lang_package ta
%lang_package tcy
%lang_package te
%lang_package tg
%lang_package th
%lang_package the
%lang_package ti
%lang_package tig
%lang_package tk
%lang_package tl
%lang_package tn
%lang_package tr
%lang_package ts
%lang_package tt
%lang_package ug
%lang_package uk
%lang_package unm
%lang_package ur
%lang_package uz
%lang_package ve
%lang_package vi
%lang_package wa
%lang_package wae
%lang_package wal
%lang_package wo
%lang_package xh
%lang_package yi
%lang_package yo
%lang_package yue
%lang_package zh
%lang_package zu

%package all-langpacks
Summary: Meta package to require all langpacks
Group: System Environment/Base
Requires: %{name}-langpack-aa = %{version}-%{release}
Requires: %{name}-langpack-af = %{version}-%{release}
Requires: %{name}-langpack-ak = %{version}-%{release}
Requires: %{name}-langpack-am = %{version}-%{release}
Requires: %{name}-langpack-an = %{version}-%{release}
Requires: %{name}-langpack-anp = %{version}-%{release}
Requires: %{name}-langpack-ar = %{version}-%{release}
Requires: %{name}-langpack-as = %{version}-%{release}
Requires: %{name}-langpack-ast = %{version}-%{release}
Requires: %{name}-langpack-ayc = %{version}-%{release}
Requires: %{name}-langpack-az = %{version}-%{release}
Requires: %{name}-langpack-be = %{version}-%{release}
Requires: %{name}-langpack-bem = %{version}-%{release}
Requires: %{name}-langpack-ber = %{version}-%{release}
Requires: %{name}-langpack-bg = %{version}-%{release}
Requires: %{name}-langpack-bhb = %{version}-%{release}
Requires: %{name}-langpack-bho = %{version}-%{release}
Requires: %{name}-langpack-bn = %{version}-%{release}
Requires: %{name}-langpack-bo = %{version}-%{release}
Requires: %{name}-langpack-br = %{version}-%{release}
Requires: %{name}-langpack-brx = %{version}-%{release}
Requires: %{name}-langpack-bs = %{version}-%{release}
Requires: %{name}-langpack-byn = %{version}-%{release}
Requires: %{name}-langpack-ca = %{version}-%{release}
Requires: %{name}-langpack-ce = %{version}-%{release}
Requires: %{name}-langpack-cmn = %{version}-%{release}
Requires: %{name}-langpack-crh = %{version}-%{release}
Requires: %{name}-langpack-cs = %{version}-%{release}
Requires: %{name}-langpack-csb = %{version}-%{release}
Requires: %{name}-langpack-cv = %{version}-%{release}
Requires: %{name}-langpack-cy = %{version}-%{release}
Requires: %{name}-langpack-da = %{version}-%{release}
Requires: %{name}-langpack-de = %{version}-%{release}
Requires: %{name}-langpack-doi = %{version}-%{release}
Requires: %{name}-langpack-dv = %{version}-%{release}
Requires: %{name}-langpack-dz = %{version}-%{release}
Requires: %{name}-langpack-el = %{version}-%{release}
Requires: %{name}-langpack-en = %{version}-%{release}
Requires: %{name}-langpack-eo = %{version}-%{release}
Requires: %{name}-langpack-es = %{version}-%{release}
Requires: %{name}-langpack-et = %{version}-%{release}
Requires: %{name}-langpack-eu = %{version}-%{release}
Requires: %{name}-langpack-fa = %{version}-%{release}
Requires: %{name}-langpack-ff = %{version}-%{release}
Requires: %{name}-langpack-fi = %{version}-%{release}
Requires: %{name}-langpack-fil = %{version}-%{release}
Requires: %{name}-langpack-fo = %{version}-%{release}
Requires: %{name}-langpack-fr = %{version}-%{release}
Requires: %{name}-langpack-fur = %{version}-%{release}
Requires: %{name}-langpack-fy = %{version}-%{release}
Requires: %{name}-langpack-ga = %{version}-%{release}
Requires: %{name}-langpack-gd = %{version}-%{release}
Requires: %{name}-langpack-gez = %{version}-%{release}
Requires: %{name}-langpack-gl = %{version}-%{release}
Requires: %{name}-langpack-gu = %{version}-%{release}
Requires: %{name}-langpack-gv = %{version}-%{release}
Requires: %{name}-langpack-ha = %{version}-%{release}
Requires: %{name}-langpack-hak = %{version}-%{release}
Requires: %{name}-langpack-he = %{version}-%{release}
Requires: %{name}-langpack-hi = %{version}-%{release}
Requires: %{name}-langpack-hne = %{version}-%{release}
Requires: %{name}-langpack-hr = %{version}-%{release}
Requires: %{name}-langpack-hsb = %{version}-%{release}
Requires: %{name}-langpack-ht = %{version}-%{release}
Requires: %{name}-langpack-hu = %{version}-%{release}
Requires: %{name}-langpack-hy = %{version}-%{release}
Requires: %{name}-langpack-ia = %{version}-%{release}
Requires: %{name}-langpack-id = %{version}-%{release}
Requires: %{name}-langpack-ig = %{version}-%{release}
Requires: %{name}-langpack-ik = %{version}-%{release}
Requires: %{name}-langpack-is = %{version}-%{release}
Requires: %{name}-langpack-it = %{version}-%{release}
Requires: %{name}-langpack-iu = %{version}-%{release}
Requires: %{name}-langpack-iw = %{version}-%{release}
Requires: %{name}-langpack-ja = %{version}-%{release}
Requires: %{name}-langpack-ka = %{version}-%{release}
Requires: %{name}-langpack-kk = %{version}-%{release}
Requires: %{name}-langpack-kl = %{version}-%{release}
Requires: %{name}-langpack-km = %{version}-%{release}
Requires: %{name}-langpack-kn = %{version}-%{release}
Requires: %{name}-langpack-ko = %{version}-%{release}
Requires: %{name}-langpack-kok = %{version}-%{release}
Requires: %{name}-langpack-ks = %{version}-%{release}
Requires: %{name}-langpack-ku = %{version}-%{release}
Requires: %{name}-langpack-kw = %{version}-%{release}
Requires: %{name}-langpack-ky = %{version}-%{release}
Requires: %{name}-langpack-lb = %{version}-%{release}
Requires: %{name}-langpack-lg = %{version}-%{release}
Requires: %{name}-langpack-li = %{version}-%{release}
Requires: %{name}-langpack-lij = %{version}-%{release}
Requires: %{name}-langpack-lo = %{version}-%{release}
Requires: %{name}-langpack-lt = %{version}-%{release}
Requires: %{name}-langpack-lv = %{version}-%{release}
Requires: %{name}-langpack-lzh = %{version}-%{release}
Requires: %{name}-langpack-mag = %{version}-%{release}
Requires: %{name}-langpack-mai = %{version}-%{release}
Requires: %{name}-langpack-mg = %{version}-%{release}
Requires: %{name}-langpack-mhr = %{version}-%{release}
Requires: %{name}-langpack-mi = %{version}-%{release}
Requires: %{name}-langpack-mk = %{version}-%{release}
Requires: %{name}-langpack-ml = %{version}-%{release}
Requires: %{name}-langpack-mn = %{version}-%{release}
Requires: %{name}-langpack-mni = %{version}-%{release}
Requires: %{name}-langpack-mr = %{version}-%{release}
Requires: %{name}-langpack-ms = %{version}-%{release}
Requires: %{name}-langpack-mt = %{version}-%{release}
Requires: %{name}-langpack-my = %{version}-%{release}
Requires: %{name}-langpack-nan = %{version}-%{release}
Requires: %{name}-langpack-nb = %{version}-%{release}
Requires: %{name}-langpack-nds = %{version}-%{release}
Requires: %{name}-langpack-ne = %{version}-%{release}
Requires: %{name}-langpack-nhn = %{version}-%{release}
Requires: %{name}-langpack-niu = %{version}-%{release}
Requires: %{name}-langpack-nl = %{version}-%{release}
Requires: %{name}-langpack-nn = %{version}-%{release}
Requires: %{name}-langpack-nr = %{version}-%{release}
Requires: %{name}-langpack-nso = %{version}-%{release}
Requires: %{name}-langpack-oc = %{version}-%{release}
Requires: %{name}-langpack-om = %{version}-%{release}
Requires: %{name}-langpack-or = %{version}-%{release}
Requires: %{name}-langpack-os = %{version}-%{release}
Requires: %{name}-langpack-pa = %{version}-%{release}
Requires: %{name}-langpack-pap = %{version}-%{release}
Requires: %{name}-langpack-pl = %{version}-%{release}
Requires: %{name}-langpack-ps = %{version}-%{release}
Requires: %{name}-langpack-pt = %{version}-%{release}
Requires: %{name}-langpack-quz = %{version}-%{release}
Requires: %{name}-langpack-raj = %{version}-%{release}
Requires: %{name}-langpack-ro = %{version}-%{release}
Requires: %{name}-langpack-ru = %{version}-%{release}
Requires: %{name}-langpack-rw = %{version}-%{release}
Requires: %{name}-langpack-sa = %{version}-%{release}
Requires: %{name}-langpack-sat = %{version}-%{release}
Requires: %{name}-langpack-sc = %{version}-%{release}
Requires: %{name}-langpack-sd = %{version}-%{release}
Requires: %{name}-langpack-se = %{version}-%{release}
Requires: %{name}-langpack-shs = %{version}-%{release}
Requires: %{name}-langpack-si = %{version}-%{release}
Requires: %{name}-langpack-sid = %{version}-%{release}
Requires: %{name}-langpack-sk = %{version}-%{release}
Requires: %{name}-langpack-sl = %{version}-%{release}
Requires: %{name}-langpack-so = %{version}-%{release}
Requires: %{name}-langpack-sq = %{version}-%{release}
Requires: %{name}-langpack-sr = %{version}-%{release}
Requires: %{name}-langpack-ss = %{version}-%{release}
Requires: %{name}-langpack-st = %{version}-%{release}
Requires: %{name}-langpack-sv = %{version}-%{release}
Requires: %{name}-langpack-sw = %{version}-%{release}
Requires: %{name}-langpack-szl = %{version}-%{release}
Requires: %{name}-langpack-ta = %{version}-%{release}
Requires: %{name}-langpack-tcy = %{version}-%{release}
Requires: %{name}-langpack-te = %{version}-%{release}
Requires: %{name}-langpack-tg = %{version}-%{release}
Requires: %{name}-langpack-th = %{version}-%{release}
Requires: %{name}-langpack-the = %{version}-%{release}
Requires: %{name}-langpack-ti = %{version}-%{release}
Requires: %{name}-langpack-tig = %{version}-%{release}
Requires: %{name}-langpack-tk = %{version}-%{release}
Requires: %{name}-langpack-tl = %{version}-%{release}
Requires: %{name}-langpack-tn = %{version}-%{release}
Requires: %{name}-langpack-tr = %{version}-%{release}
Requires: %{name}-langpack-ts = %{version}-%{release}
Requires: %{name}-langpack-tt = %{version}-%{release}
Requires: %{name}-langpack-ug = %{version}-%{release}
Requires: %{name}-langpack-uk = %{version}-%{release}
Requires: %{name}-langpack-unm = %{version}-%{release}
Requires: %{name}-langpack-ur = %{version}-%{release}
Requires: %{name}-langpack-uz = %{version}-%{release}
Requires: %{name}-langpack-ve = %{version}-%{release}
Requires: %{name}-langpack-vi = %{version}-%{release}
Requires: %{name}-langpack-wa = %{version}-%{release}
Requires: %{name}-langpack-wae = %{version}-%{release}
Requires: %{name}-langpack-wal = %{version}-%{release}
Requires: %{name}-langpack-wo = %{version}-%{release}
Requires: %{name}-langpack-xh = %{version}-%{release}
Requires: %{name}-langpack-yi = %{version}-%{release}
Requires: %{name}-langpack-yo = %{version}-%{release}
Requires: %{name}-langpack-yue = %{version}-%{release}
Requires: %{name}-langpack-zh = %{version}-%{release}
Requires: %{name}-langpack-zu = %{version}-%{release}

%description all-langpacks
Meta package to require all langpacks

%files all-langpacks

##############################################################################
# glibc "nscd" sub-package
##############################################################################
%package -n nscd
Summary: A Name Service Caching Daemon (nscd).
Group: System Environment/Daemons
Requires: %{name} = %{version}-%{release}
%if %{with bootstrap}
Requires: libselinux >= 1.17.10-1
%endif
Requires: audit-libs >= 1.1.3
Requires(pre): /usr/sbin/useradd, coreutils
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd, /usr/sbin/userdel

%description -n nscd
Nscd caches name service lookups and can dramatically improve
performance with NIS+, and may help with DNS as well.

##############################################################################
# glibc "utils" sub-package
##############################################################################
%package utils
Summary: Development utilities from GNU C library
Group: Development/Tools
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

%package debuginfo
Summary: Debug information for package %{name}
Group: Development/Debug
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
Group: Development/Debug
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
Group: Development/Debug
%description benchtests
This package provides built benchmark binaries and scripts to run
microbenchmark tests on the system.
%endif

##############################################################################
# Prepare for the build.
##############################################################################
%prep
# Log system information
uname -a
cat /proc/cpuinfo
cat /proc/meminfo

%setup -q -n %{glibcsrcdir}

# Patch order matters.
%patch0001 -p1
%patch0003 -p1
%patch0004 -p1
%patch0005 -p1
%patch0006 -p1
%patch2007 -p1
%patch0009 -p1
%patch0012 -p1
%patch2013 -p1
%patch0014 -p1
%patch0015 -p1
%patch0016 -p1
%patch0019 -p1
%patch0020 -p1
%patch2023 -p1
%patch0024 -p1
%patch0025 -p1
%patch2027 -p1
%patch0028 -p1
%patch0030 -p1
%patch0031 -p1
%patch0033 -p1
%patch0037 -p1
%patch0044 -p1
%patch0046 -p1
%patch2031 -p1
%patch0047 -p1
%patch2033 -p1
%patch2034 -p1
%patch0052 -p1
%patch0053 -p1
%patch3002 -p1
%patch0054 -p1
%patch0055 -p1
%patch0056 -p1
%patch0057 -p1
%patch0058 -p1
%patch0059 -p1
%patch2035 -p1
%patch2036 -p1

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

##############################################################################
# Build glibc...
##############################################################################
%build

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
# %%build - SPARC options.
##############################################################################
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
%ifarch %{power64}
BuildFlags=""
GCC="gcc -m64"
GXX="g++ -m64"
%ifarch ppc64p7
GCC="$GCC -mcpu=power7 -mtune=power7"
GXX="$GXX -mcpu=power7 -mtune=power7"
%endif
%endif

##############################################################################
# %%build - Generic options.
##############################################################################
BuildFlags="$BuildFlags -fasynchronous-unwind-tables"
# Add -DNDEBUG unless using a prerelease
case %{version} in
  *.*.9[0-9]*) ;;
  *)
     BuildFlags="$BuildFlags -DNDEBUG"
     ;;
esac
EnableKernel="--enable-kernel=%{enablekernel}"
# Save the used compiler and options into the file "Gcc" for use later
# by %%install.
echo "$GCC" > Gcc
AddOns=`echo */configure | sed -e 's!/configure!!g;s!\(nptl\|powerpc-cpu\)\( \|$\)!!g;s! \+$!!;s! !,!g;s!^!,!;/^,\*$/d'`

##############################################################################
# build()
#	Build glibc in `build-%{target}$1', passing the rest of the arguments
#	as CFLAGS to the build (not the same as configure CFLAGS). Several
#	global values are used to determine build flags, add-ons, kernel
#	version, multiarch support, system tap support, etc.
##############################################################################
build()
{
	builddir=build-%{target}${1:+-$1}
	${1+shift}
	rm -rf $builddir
	mkdir $builddir
	pushd $builddir
	build_CFLAGS="$BuildFlags -g -O3 $*"
	# Some configure checks can spuriously fail for some architectures if
	# unwind info is present
	configure_CFLAGS="$build_CFLAGS -fno-asynchronous-unwind-tables"
	../configure CC="$GCC" CXX="$GXX" CFLAGS="$configure_CFLAGS" \
		--prefix=%{_prefix} \
		--enable-add-ons=$AddOns \
		--with-headers=%{_prefix}/include $EnableKernel --enable-bind-now \
		--build=%{target} \
%ifarch %{multiarcharches}
		--enable-multi-arch \
%endif
		--enable-obsolete-rpc \
		--enable-systemtap \
%ifarch ppc64p7
		--with-cpu=power7 \
%endif
%ifarch %{lock_elision_arches}
		--enable-lock-elision \
%endif
%if %{without werror}
		--disable-werror \
%endif
		--disable-profile \
%if %{with bootstrap}
		--without-selinux \
		--disable-nss-crypt ||
%else
		--enable-nss-crypt ||
%endif
		{ cat config.log; false; }

	make %{?_smp_mflags} -r CFLAGS="$build_CFLAGS" %{silentrules}
	popd
}

##############################################################################
# Build glibc for the default set of options.
##############################################################################
build

##############################################################################
# Build glibc for xen:
# If we support xen build glibc again for xen support.
##############################################################################
%if %{buildxen}
build nosegneg -mno-tls-direct-seg-refs
%endif

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
	AddOns="$AddOns --with-cpu=power6"
	GCC="$GCC -mcpu=power6"
	GXX="$GXX -mcpu=power6"
	build power6
)
%endif # %{buildpower6}

%if %{buildpower7}
(
  AddOns="$AddOns --with-cpu=power7"
  GCC="$GCC -mcpu=power7 -mtune=power7"
  GXX="$GXX -mcpu=power7 -mtune=power7"
  build power7
)
%endif

%if %{buildpower8}
(
  AddOns="$AddOns --with-cpu=power8"
  GCC="$GCC -mcpu=power8 -mtune=power8"
  GXX="$GXX -mcpu=power8 -mtune=power8"
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

# Cleanup any previous installs...
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT
make -j1 install_root=$RPM_BUILD_ROOT \
	install -C build-%{target} %{silentrules}
# If we are not building an auxiliary arch then install all of the supported
# locales.
%ifnarch %{auxarches}
pushd build-%{target}
make %{?_smp_mflags} install_root=$RPM_BUILD_ROOT \
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
# Install the xen build files.
##############################################################################
%if %{buildxen}
%define nosegneg_subdir_base i686
%define nosegneg_subdir i686/nosegneg
%define nosegneg_subdir_up ../..
pushd build-%{target}-nosegneg
destdir=$RPM_BUILD_ROOT/%{_lib}
install_different "$destdir" "%{nosegneg_subdir}" "%{nosegneg_subdir_up}"
popd
%endif # %{buildxen}

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

# rquota.x and rquota.h are now provided by quota
rm -f $RPM_BUILD_ROOT%{_prefix}/include/rpcsvc/rquota.[hx]

# In F7+ this is provided by rpcbind rpm
rm -f $RPM_BUILD_ROOT%{_sbindir}/rpcinfo

# Remove the old nss modules.
rm -f ${RPM_BUILD_ROOT}/%{_lib}/libnss1-*
rm -f ${RPM_BUILD_ROOT}/%{_lib}/libnss-*.so.1

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
# Create the file lists for the language specific sub-packages:
for i in *_*
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
mkdir -p $RPM_BUILD_ROOT/etc/default
install -p -m 644 nis/nss $RPM_BUILD_ROOT/etc/default/nss

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

# NPTL <bits/stdio-lock.h> is not usable outside of glibc, so include
# the generic one (#162634). This header is required by older gcc builds
# which shared libio. Once we stop supporting building old compilers which
# need shared libio we can remove this.
cp -a sysdeps/generic/stdio-lock.h \
	$RPM_BUILD_ROOT%{_prefix}/include/bits/stdio-lock.h
# And <bits/libc-lock.h> needs sanitizing as well.
cp -a %{SOURCE3} $RPM_BUILD_ROOT%{_prefix}/include/bits/libc-lock.h

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
# There are 11 main file lists (and many more for
# the langpack sub-packages (langpack-${lang}.filelist)):
# * rpm.fileslist
#	- Master file list. Eventually, after removing files from this list
#	  we are left with the list of files for the glibc package.
# * common.filelist
#	- Contains the list of flies for the common subpackage.
# * utils.filelist
#	- Contains the list of files for the utils subpackage.
# * nscd.filelist
#	- Contains the list of files for the nscd subpackage.
# * devel.filelist
#	- Contains the list of files for the devel subpackage.
# * headers.filelist
#	- Contains the list of files for the headers subpackage.
# * static.filelist
#	- Contains the list of files for the static subpackage.
# * nosegneg.filelist
#	- Contains the list of files for the xen subpackage.
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

  # remove the locale sources, they go into the sub-package "locale-source":
  I18N_LANG='\,.*/share/i18n/locales/.*,d'
  # Also remove the *.mo entries.  We will add them to the
  # language specific sub-packages.
  sed -e '\,.*/share/locale/\([^/_]\+\).*/LC_MESSAGES/.*\.mo,d' \
      -e "$I18N_LANG" \
      -e '\,/etc/\(localtime\|nsswitch.conf\|ld\.so\.conf\|ld\.so\.cache\|default\|rpc\|gai\.conf\),d' \
      -e '\,/%{_lib}/lib\(pcprofile\|memusage\)\.so,d' \
      -e '\,bin/\(memusage\|mtrace\|xtrace\|pcprofiledump\),d'
} | sort > rpm.filelist

touch common.filelist

mkdir -p $RPM_BUILD_ROOT%{_libdir}
mv -f $RPM_BUILD_ROOT/%{_lib}/lib{pcprofile,memusage}.so $RPM_BUILD_ROOT%{_libdir}

# The xtrace and memusage scripts have hard-coded paths that need to be
# translated to a correct set of paths using the $LIB token which is
# dynamically translated by ld.so as the default lib directory.
for i in $RPM_BUILD_ROOT%{_prefix}/bin/{xtrace,memusage}; do
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
  | grep '/lib\(\(c\|pthread\|nldbl\|mvec\)_nonshared\|g\|ieee\|mcheck\|rpcsvc\)\.a$' \
  >> devel.filelist

# Put the rest of the static files into the static package.
grep '%{_libdir}/lib.*\.a' < rpm.filelist \
  | grep -v '/lib\(\(c\|pthread\|nldbl\|mvec\)_nonshared\|g\|ieee\|mcheck\|rpcsvc\)\.a$' \
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

##############################################################################
# Build the xen package file list (nosegneg.filelist)
##############################################################################
truncate -s 0 nosegneg.filelist
%if %{xenpackage}
grep '/%{_lib}/%{nosegneg_subdir}' < rpm.filelist >> nosegneg.filelist
sed -i -e '\|/%{_lib}/%{nosegneg_subdir}|d' rpm.filelist
# TODO: There are files in the nosegneg list which should be in the devel
#	pacakge, but we leave them instead in the xen subpackage. We may
#	wish to clean that up at some point.
%endif

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
%{_prefix}/bin/memusage
%{_prefix}/bin/memusagestat
%{_prefix}/bin/mtrace
%{_prefix}/bin/pcprofiledump
%{_prefix}/bin/xtrace
EOF

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

# We allow undefined symbols in shared libraries because the libraries
# referenced at link time here, particularly ld.so, may be different than
# the one used at runtime.  This is really only needed during the ARM
# transition from ld-linux.so.3 to ld-linux-armhf.so.3.
pushd build-%{target}
$GCC -Os -g -static -o build-locale-archive %{SOURCE1} \
	../build-%{target}/locale/locarchive.o \
	../build-%{target}/locale/md5.o \
	-I. -DDATADIR=\"%{_datadir}\" -DPREFIX=\"%{_prefix}\" \
	-L../build-%{target} \
	-Wl,--allow-shlib-undefined \
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

# Leave a compatibility symlink for the dynamic loader on armhfp targets,
# at least until the world gets rebuilt
%ifarch armv7hl armv7hnl
ln -sf /lib/ld-linux-armhf.so.3 $RPM_BUILD_ROOT/lib/ld-linux.so.3
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
	-l nscd.filelist \
	-p '.*/(sbin|libexec)/.*' \
	-o debuginfocommon.filelist \
	-l rpm.filelist \
%if %{with benchtests}
	-l nosegneg.filelist -l benchtests.filelist"
%else
	-l nosegneg.filelist"
%endif
%endif
eval /usr/lib/rpm/find-debuginfo.sh \
	"$find_debuginfo_args" \
	-o debuginfo.filelist

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

mkdir -p $RPM_BUILD_ROOT/var/cache/ldconfig
truncate -s 0 $RPM_BUILD_ROOT/var/cache/ldconfig/aux-cache

##############################################################################
# Run the glibc testsuite
##############################################################################
%check
%if %{with testsuite}

# Run the glibc tests. If any tests fail to build we exit %check with an error
# of 1, otherwise we print the test failure list and the failed test output
# and exit with 0. In the future we want to compare against a baseline and
# exit with 1 if the results deviate from the baseline.
run_tests () {
	truncate -s 0 check.log
	tail -f check.log &
	tailpid=$!
	# Run the make a sub-shell (to avoid %check failing if make fails)
	# but capture the status for use later. We use the normal sub-shell
	# trick of printing the status. The actual result of the sub-shell
	# is the successful execution of the echo.
	status=$(set +e
		 make %{?_smp_mflags} check %{silentrules} > check.log 2>&1
		 status=$?
		 echo $status)
	# Wait for the tail to catch up with the output and then kill it.
	sleep 10
	kill $tailpid
	# Print the header, so we can find it, but skip the error printing
	# if there aren't any failrues.
	echo ===================FAILED TESTS=====================
	if [ $status -ne 0 ]; then
		# We are not running with `-k`, therefore a test build failure
		# terminates the test run and that terminates %check with an
		# error which terminates the build. We want this behaviour to
		# ensure that all tests build, and all tests run.
		# If the test result summary is not present it means one of
		# tests failed to build.
		if ! grep 'Summary of test results:' check.log; then
			echo "FAIL: Some glibc tests failed to build."
			exit 1
		fi

		# Print out information about all of the failed tests.
		grep -e ^FAIL -e ^ERROR tests.sum \
			| awk '{print $2}' \
			| while read testcase;
		do
			echo "$testcase"
			cat $testcase.out
			echo -------------------------
		done
	fi
}

# Increase timeouts
export TIMEOUTFACTOR=16
parent=$$
echo ====================TESTING=========================
##############################################################################
# - Test the default runtime.
# 	- Power 620 / 970 ISA for 64-bit POWER BE.
#	- POWER8 for 64-bit POWER LE.
#	- ??? for 64-bit x86_64
#	- ??? for 32-bit x86
#	- ??? for 64-bit AArch64
#	- ??? for 32-bit ARM
#	- ??? for 64-bit s390x
#	- ??? for 32-bit s390
##############################################################################
pushd build-%{target}
run_tests
popd

%if %{buildxen}
echo ====================TESTING -mno-tls-direct-seg-refs=============
##############################################################################
# - Test the xen runtimes (nosegneg).
##############################################################################
pushd build-%{target}-nosegneg
run_tests
popd
%endif

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

%if %{with valgrind}
# Finally, check if valgrind runs with the new glibc.
# We want to fail building if valgrind is not able to run with this glibc so
# that we can then coordinate with valgrind to get it fixed before we update
# glibc.
pushd build-%{target}
elf/ld.so --library-path .:elf:nptl:dlfcn /usr/bin/valgrind \
	elf/ld.so --library-path .:elf:nptl:dlfcn /usr/bin/true
popd
%endif

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

%post common
# remove old archive file:
rm -f %{_prefix}/lib/locale/locale-archive

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

%if %{xenpackage}
%post xen -p /sbin/ldconfig
%postun xen -p /sbin/ldconfig
%endif

%clean
rm -rf "$RPM_BUILD_ROOT"
rm -f *.filelist*

%files -f rpm.filelist
%defattr(-,root,root)
%dir %{_prefix}/%{_lib}/audit
%if %{buildxen} && !%{xenpackage}
%dir /%{_lib}/%{nosegneg_subdir_base}
%dir /%{_lib}/%{nosegneg_subdir}
%endif
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
%ifarch armv7hl armv7hnl
/lib/ld-linux.so.3
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
%doc README NEWS INSTALL BUGS PROJECTS CONFORMANCE elf/rtld-debugger-interface.txt
# If rpm doesn't support %license, then use %doc instead.
%{!?_licensedir:%global license %%doc}
%license COPYING COPYING.LIB LICENSES
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
%dir %{_prefix}/lib/locale/C.utf8
%{_prefix}/lib/locale/C.utf8/*
%dir %attr(755,root,root) /etc/default
%verify(not md5 size mtime) %config(noreplace) /etc/default/nss
%doc documentation/*

%files locale-source
%defattr(-,root,root)
%dir %{_prefix}/share/i18n/locales
%{_prefix}/share/i18n/locales/*

%files -f devel.filelist devel
%defattr(-,root,root)

%files -f static.filelist static
%defattr(-,root,root)

%files -f headers.filelist headers
%defattr(-,root,root)

%files -f utils.filelist utils
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
* Sun Jan 17 2016 Mike FABIAN <mfabian@redhat.com> - 2.22.90-51
- Testing 51

* Wed Jan 13 2016 Carlos O'Donell <carlos@redhat.com> - 2.22.90-29
- New pthread_barrier algorithm with improved standards compliance.

* Wed Jan 13 2016 Carlos O'Donell <carlos@redhat.com> - 2.22.90-28
- Add group merging support for distributed management (#1146822).

* Tue Jan 12 2016 Carlos O'Donell <carlos@redhat.com> - 2.22.90-27
- Remove 32-bit POWER support.
- Add 64-bit POWER7 BE and 64-bit POWER8 BE optimized libraries.

* Mon Dec 21 2015 Florian Weimer <fweimer@redhat.com> - 2.22.90-26
- Auto-sync with upstream master.

* Wed Dec 16 2015 Florian Weimer <fweimer@redhat.com> - 2.22.90-25
- Auto-sync with upstream master.
- Includes fix for malloc assertion failure in get_free_list.  (#1281714)
- Drop Unicode 8.0 patches (now merged upstream).

* Sat Dec  5 2015 Florian Weimer <fweimer@redhat.com> - 2.22.90-24
- Put libmvec_nonshared.a into the -devel package.  (#1288738)

* Sat Dec 05 2015 Florian Weimer <fweimer@redhat.com> - 2.22.90-23
- Auto-sync with upstream master.

* Thu Nov 26 2015 Carlos O'Donell <carlos@redhat.com> - 2.22.90-22
- The generic hidden directive support is already used for
  preinit/init/fini-array symbols so we drop the Fedora-specific
  patch that does the same thing.
  Reported by Dmitry V. Levin <ldv@altlinux.org>

* Thu Nov 26 2015 DJ Delorie <dj@redhat.com> - 2.22.90-22
- Require glibc-static for C++ tests.
- Require gcc-c++, libstdc++-static, and glibc-static only when needed.
- Fix --without docs to not leave info files.

* Fri Nov 20 2015 Florian Weimer <fweimer@redhat.com> - 2.22.90-21
- Auto-sync with upstream master.

* Wed Nov 18 2015 Florian Weimer <fweimer@redhat.com> - 2.22.90-20
- Auto-sync with upstream master.

* Wed Nov 18 2015 Florian Weimer <fweimer@redhat.com> - 2.22.90-19
- Disable -Werror on s390 (#1283184).

* Mon Nov 16 2015 Florian Weimer <fweimer@redhat.com> - 2.22.90-18
- Auto-sync with upstream master.

* Mon Nov 16 2015 Florian Weimer <fweimer@redhat.com> - 2.22.90-17
- Revert temporary armhfp build fix.

* Mon Nov  9 2015 Florian Weimer <fweimer@redhat.com> - 2.22.90-16
- Apply temporary fix for armhfp build issue.

* Mon Nov 09 2015 Florian Weimer <fweimer@redhat.com> - 2.22.90-15
- Auto-sync with upstream master.

* Tue Nov  3 2015 Florian Weimer <fweimer@redhat.com> - 2.22.90-14
- Log uname, cpuinfo, meminfo during build (#1276636)

* Fri Oct 30 2015 Florian Weimer <fweimer@redhat.com> - 2.22.90-13
- Auto-sync with upstream master.

* Fri Oct 30 2015 Florian Weimer <fweimer@redhat.com> - 2.22.90-12
- Revert to upstream implementation of condition variables (#1229659)

* Wed Oct 28 2015 Florian Weimer <fweimer@redhat.com> - 2.22.90-11
- Disable valgrind test on ppc64p7, too.

* Mon Oct 26 2015 Carlos O'Donell <carlos@redhat.com> - 2.22.90-10
- Disable valgrind test for ppc64.

* Wed Oct 21 2015 Carlos O'Donell <carlos@redhat.com> - 2.22.90-9
- Sync with upstream master.
- Update new condvar implementation.

* Fri Oct  9 2015 Carlos O'Donell <carlos@redhat.com> - 2.22.90-8
- Remove libbsd.a (#1193168).

* Wed Sep 16 2015 Mike FABIAN <mfabian@redhat.com> - 2.22.90-7
- Add the C.UTF-8 locale (#902094).

* Wed Sep 16 2015 Carlos O'Donell <carlos@systemhalted.org> - 2.22.90-6
- Fix GCC 5 and -Werror related build failures.
- Fix --install-langs bug which causes SIGABRT (#1262040).

* Fri Aug 28 2015 Carlos O'Donell <carlos@systemhalted.org> - 2.22.90-5
- Auto-sync with upstream master.

* Thu Aug 27 2015 Carlos O'Donell <carlos@redhat.com> - 2.22.90-4
- Build require gcc-c++ for the C++ tests.
- Support --without testsuite option to disable testing after build.
- Support --without benchtests option to disable microbenchmarks.
- Update --with bootstrap to disable benchtests, valgrind, documentation,
  selinux, and nss-crypt during bootstrap.
- Support --without werror to disable building with -Werror.
- Support --without docs to disable build requirement on texinfo.
- Support --without valgrind to disable testing with valgrind.
- Remove c_stubs add-on and enable fuller support for static binaries.
- Remove librtkaio support (#1227855).

* Sun Aug 16 2015 Siddhesh Poyarekar <siddhesh@redhat.com> - 2.22.90-3
- Auto-sync with upstream master.

* Fri Aug 14 2015 Siddhesh Poyarekar <siddhesh@redhat.com> - 2.22.90-2
- Remove initgroups from the default nsswitch.conf (#751450).

* Fri Aug 14 2015 Siddhesh Poyarekar <siddhesh@redhat.com> - 2.22.90-1
- Sync with upstream master.

* Tue Jul 28 2015 Siddhesh Poyarekar <siddhesh@redhat.com> - 2.21.90-20
- Sync with upstream master.

* Thu Jul 23 2015 Mike FABIAN <mfabian@redhat.com> - 2.21.90-19
- some more additions to the translit_neutral file by Marko Myllynen

* Tue Jul 14 2015 Mike FABIAN <mfabian@redhat.com> - 2.21.90-18
- Unicode 8.0.0 updates, including the transliteration files (#1238412).

* Sun Jun 21 2015 Carlos O'Donell <carlos@redhat.com> - 2.21.90-17
- Remove all linuxthreads handling from glibc spec file.

* Wed Jun 17 2015 Carlos O'Donell <carlos@redhat.com> - 2.21.90-16
- Move split out architecture-dependent header files into devel package
  and keep generic variant in headers package, thus keeping headers package
  content and file list identical across multilib rpms.

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.21.90-15.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Wed Jun  3 2015 Carlos O'Donell <carlos@redhat.com> - 2.21.90-15
- Remove patch to increase DTV surplus which is no longer needed after
  upstream commit f8aeae347377f3dfa8cbadde057adf1827fb1d44.

* Sat May 30 2015 Siddhesh Poyarekar <siddhesh@redhat.com> - 2.21.90-14
- Fix build failure on aarch64 (#1226459).

* Mon May 18 2015 Siddhesh Poyarekar <siddhesh@redhat.com> - 2.21.90-13
- Sync with upstream master.
- Install new condvar implementation.

* Fri May 08 2015 Siddhesh Poyarekar <siddhesh@redhat.com> - 2.21.90-12
- Add benchmark comparison scripts.

* Thu May 07 2015 Siddhesh Poyarekar <siddhesh@redhat.com> - 2.21.90-11
- Auto-sync with upstream master.
- Revert arena threshold fix to work around #1209451.

* Tue Apr 07 2015 Siddhesh Poyarekar <siddhesh@redhat.com> - 2.21.90-10
- Revert last auto-sync (#1209451).

* Mon Apr 06 2015 Siddhesh Poyarekar <siddhesh@redhat.com> - 2.21.90-9
- Auto-sync with upstream master.

* Tue Mar 24 2015 Siddhesh Poyarekar <siddhesh@redhat.com> - 2.21.90-8
- Auto-sync with upstream master.

* Tue Mar 17 2015 Carlos O'Donell <carlos@redhat.com> - 2.21.90-7
- Use rpm.expand in scripts to reduce set of required RPM features.

* Thu Mar 12 2015 Siddhesh Poyarekar <siddhesh@redhat.com> - 2.21.90-6
- Auto-sync with upstream master.

* Tue Mar  3 2015 Mike Fabian <mfabian@redhat.com> - 2.21.90-5
- Support installing only those locales specified by the RPM macro
  %%_install_langs (#156477).

* Mon Feb 23 2015 Siddhesh Poyarekar <siddhesh@redhat.com> - 2.21.90-4
- Auto-sync with upstream master.

* Sat Feb 21 2015 Till Maas <opensource@till.name> - 2.21.90-3.1
- Rebuilt for Fedora 23 Change
  https://fedoraproject.org/wiki/Changes/Harden_all_packages_with_position-independent_code

* Thu Feb 12 2015 Carlos O'Donell <carlos@systemhalted.org> - 2.21.90-3
- Fix missing clock_* IFUNCs in librtkaio.

* Thu Feb 12 2015 Carlos O'Donell <carlos@systemhalted.org> - 2.21.90-2
- Auto-sync with upstream master.

* Wed Feb 11 2015 Carlos O'Donell <carlos@systemhalted.org> - 2.21.90-1
- Add back x86 vDSO support.
- Fix rtkaio build to reference clock_* functions from libc.

* Wed Jan 21 2015 Siddhesh Poyarekar <siddhesh@redhat.com> - 2.20.90-20
- Sync with upstream master.
- Disable werror on s390x.
- Revert x86 vDSO support since it breaks i686 rtkaio build.

* Tue Jan 20 2015 Peter Robinson <pbrobinson@fedoraproject.org> 2.20.90-19
- Drop large ancient ChangeLogs (rhbz #1169546)

* Mon Jan 12 2015 Siddhesh Poyarekar <siddhesh@redhat.com> - 2.20.90-18
- Pass address of main_arena.mutex to mutex_lock/unlock.

* Thu Jan 08 2015 Siddhesh Poyarekar <siddhesh@redhat.com> - 2.20.90-17
- Define a __tls_get_addr macro to avoid a conflicting declaration.

* Wed Jan 07 2015 Siddhesh Poyarekar <siddhesh.poyarekar@gmail.com> - 2.20.90-16
- Disable -Werror for s390 as well.

* Wed Jan 07 2015 Siddhesh Poyarekar <siddhesh.poyarekar@gmail.com> - 2.20.90-14
- Sync with upstream master.
- Disable -Werror on powerpc and armv7hl.
- Temporarily disable valgrind test on ppc64.

* Sun Dec 28 2014 Dan Horák <dan[at]danny.cz>
- valgrind available only on selected arches (missing on s390)

* Wed Dec 10 2014 Kyle McMartin <kmcmarti@redhat.com>
- aarch64: Drop strchrnul.S revert, apply fix from Richard Earnshaw.

* Fri Dec 05 2014 Carlos O'Donell <carlos@redhat.com> - 2.20.90-13
- Fix permission of debuginfo source files to allow multiarch
  debuginfo packages to be installed and upgraded.

* Fri Dec 05 2014 Siddhesh Poyarekar <siddhesh@redhat.com> - 2.20.90-12
- Remove LIB_LANG since we don't install locales in /usr/lib/locale anymore.
- Don't own any directories in /usr/share/locale (#1167445).
- Use the %%find_lang macro to get the *.mo files (#1167445).
- Add %%lang tags to language locale files in /usr/share/i18n/locale (#1169044).

* Wed Dec 03 2014 Kyle McMartin <kyle@fedoraproject.org> - 2.20.90-11
- aarch64: revert optimized strchrnul.S implementation (rhbz#1167501)
  until it can be debugged.

* Fri Nov 28 2014 Carlos O'Donell <carlos@redhat.com> - 2.20.90-10
- Auto-sync with upstream master.

* Wed Nov 19 2014 Carlos O'Donell <carlos@redhat.com> - 2.20.90-9
- Sync with upstream master.

* Wed Nov 05 2014 Siddhesh Poyarekar <siddhesh@redhat.com> - 2.20.90-8
- Make getconf return only /usr/bin (#1138835).
- Sync with upstream master.

* Tue Nov 04 2014 Arjun Shankar <arjun.is@lostca.se> - 2.20.90-7
- Add patch that modifies several tests to use test-skeleton.c.
  The patch is accepted but not yet committed upstream.
  https://sourceware.org/ml/libc-alpha/2014-10/msg00744.html

* Tue Sep 30 2014 Siddhesh Poyarekar <siddhesh@redhat.com> - 2.20.90-6
- Sync with upstream master.
- Disable more Intel TSX usage in rwlocks (#1146967).
- Enable lock elision again on s390 and s390x.
- Enable Systemtap SDT probes for all architectures (#985109).

* Fri Sep 26 2014 Carlos O'Donell <carlos@redhat.com> - 2.20.90-5
- Disable lock elision support for Intel hardware until microcode
  updates can be done in early bootup (#1146967).
- Fix building test tst-strtod-round for ARM.

* Tue Sep 23 2014 Siddhesh Poyarekar <siddhesh@redhat.com> - 2.20.90-4
- Sync with upstream master.
- Don't own the common debuginfo directories (#1144853).
- Run valgrind in the %%check section to ensure that it does not break.

* Tue Sep 16 2014 Siddhesh Poyarekar <siddhesh@redhat.com> - 2.20.90-3
- Sync with upstream master.
- Revert patch for #737223.

* Mon Sep 08 2014 Siddhesh Poyarekar <siddhesh@redhat.com> - 2.20.90-2
- Build build-locale-archive statically again.

* Mon Sep 08 2014 Siddhesh Poyarekar <siddhesh@redhat.com> - 2.20.90-1
- Sync with upstream master.

* Thu Sep  4 2014 Carlos O'Donell <carlos@redhat.com> - 2.19.90-36
- Allow up to 32 dlopened modules to use static TLS (#1124987).
- Run glibc tests in %%check section of RPM spec file.
- Do not run tests with `-k` and fail if any test fails to build.

* Tue Aug 26 2014 Siddhesh Poyarekar <siddhesh@redhat.com> - 2.19.90-35
- Sync with upstream master.
- Use INTERNAL_SYSCALL in TLS_INIT_TP (#1133134).
- Remove gconv loadable module transliteration support (CVE-2014-5119, #1119128).

* Fri Aug 22 2014 Dennis Gilmore <dennis@ausil.us> - 2.19.90-34
- add back sss to nsswitch.conf we have added workarounds in the tools

* Thu Aug 21 2014 Kevin Fenzi <kevin@scrye.com> - 2.19.90-33.1
- Rebuild for rpm bug 1131960

* Tue Aug 19 2014 Dennis Gilmore <dennis@ausil.us> - 2.19.90-33
- remove sss from default nsswitch.conf it causes issues with live image composing

* Wed Aug 13 2014 Siddhesh Poyarekar <siddhesh@redhat.com> - 2.19.90-32
- Auto-sync with upstream master.
- Revert to only defining __extern_always_inline for g++-4.3+.
- Fix build failure in compat-gcc-32 (#186410).

* Mon Jul 28 2014 Siddhesh Poyarekar <siddhesh@redhat.com> - 2.19.90-31
- Auto-sync with upstream master.

* Wed Jul 23 2014 Siddhesh Poyarekar <siddhesh@redhat.com> - 2.19.90-30
- Undo last master sync to fix up rawhide.

* Tue Jul 15 2014 Siddhesh Poyarekar <siddhesh@redhat.com> - 2.19.90-29
- Auto-sync with upstream master.

* Sat Jul 12 2014 Tom Callaway <spot@fedoraproject.org> - 2.19.90-28
- fix license handling

* Mon Jul 07 2014 Siddhesh Poyarekar <siddhesh@redhat.com> - 2.19.90-27
- Auto-sync with upstream master.

* Fri Jul 04 2014 Siddhesh Poyarekar <siddhesh@redhat.com> - 2.19.90-26
- Sync with upstream roland/nptl branch.
- Improve testsuite failure outputs in build.log

* Thu Jul 03 2014 Siddhesh Poyarekar <siddhesh@redhat.com> - 2.19.90-25
- Sync with upstream roland/nptl branch.

* Wed Jul 02 2014 Siddhesh Poyarekar <siddhesh@redhat.com> - 2.19.90-24
- Sync with upstream master.

* Tue Jun 24 2014 Siddhesh Poyarekar <siddhesh@redhat.com> - 2.19.90-23
- Sync with upstream master.
- Add fix to unbreak i386 ABI breakage due to a change in scalbn.

* Fri Jun 20 2014 Kyle McMartin <kmcmarti@redhat.com> - 2.19.90-22
- AArch64: Save & restore NZCV (flags) upon entry to _dl_tlsdesc_dynamic
  in order to work around GCC reordering compares across the TLS
  descriptor sequence (GCC PR61545.) Committing a (temporary) fix here
  allows us to avoid rebuilding the world with gcc 4.9.0-11.fc21.

* Mon Jun 16 2014 Kyle McMartin <kmcmarti@redhat.com> - 2.19.90-21
- Auto-sync with upstream master.

* Thu Jun 12 2014 Siddhesh Poyarekar <siddhesh@redhat.com> - 2.19.90-20
- Auto-sync with upstream master.

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.19.90-19.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Tue Jun 03 2014 Siddhesh Poyarekar <siddhesh@redhat.com> - 2.19.90-19
- Sync with upstream master.

* Mon May 26 2014 Siddhesh Poyarekar <siddhesh@redhat.com> - 2.19.90-18
- Sync with upstream master.
- Adjust rtkaio patches to build with upstream master.

* Wed May 21 2014 Kyle McMartin <kyle@fedoraproject.org> - 2.19.90-17
- Backport some upstream-wards patches to fix TLS issues on AArch64.

* Wed May 21 2014 Kyle McMartin <kyle@fedoraproject.org> - 2.19.90-16
- AArch64: Fix handling of nocancel syscall failures (#1098327)

* Thu May 15 2014 Siddhesh Poyarekar <siddhesh@redhat.com> - 2.19.90-15
- Sync with upstream master.

* Wed May 14 2014 Carlos O'Donell <carlos@redhat.com> - 2.19.90-14
- Add support for displaying all test results in build logs.

* Wed May 14 2014 Carlos O'Donell <carlos@redhat.com> - 2.19.90-13
- Add initial support for ppc64le.

* Tue Apr 29 2014 Siddhesh Poyarekar <siddhesh@redhat.com> - 2.19.90-12
- Auto-sync with upstream master.
- Remove ports addon.

* Fri Apr 18 2014 Siddhesh Poyarekar <siddhesh@redhat.com> - 2.19.90-11
- Sync with upstream master.

* Thu Apr 10 2014 Siddhesh Poyarekar <siddhesh@redhat.com> - 2.19.90-10
- Sync with upstream master.

* Thu Apr 03 2014 Siddhesh Poyarekar <siddhesh@redhat.com> - 2.19.90-9
- Sync with upstream master.

* Wed Mar 26 2014 Siddhesh Poyarekar <siddhesh@redhat.com> - 2.19.90-8
- Sync with upstream master.

* Wed Mar 19 2014 Siddhesh Poyarekar <siddhesh@redhat.com> - 2.19.90-7
- Sync with upstream master.
- Fix offset computation for append+ mode on switching from read (#1078355).

* Wed Mar 12 2014 Carlos O'Donell <carlos@redhat.com> - 2.19.90-6
- Sync with upstream master.
- Use cleaner upstream solution for -ftree-loop-distribute-patterns (#911307).

* Tue Mar 04 2014 Siddhesh Poyarekar <siddhesh@redhat.com> - 2.19.90-5
- Sync with upstream master.

* Thu Feb 27 2014 Siddhesh Poyarekar <siddhesh@redhat.com> - 2.19.90-4
- Use nscd service files from glibc sources.
- Make nscd service forking in systemd service file.

* Tue Feb 25 2014 Siddhesh Poyarekar <siddhesh@redhat.com> - 2.19.90-3
- Sync with upstream master.
- Separate ftell from fseek logic and avoid modifying FILE data (#1069559).

* Mon Feb 24 2014 Carlos O'Donell <carlos@redhat.com> - 2.19.90-2
- Fix build-locale-archive failure to open default template.

* Tue Feb 18 2014 Siddhesh Poyarekar <siddhesh@redhat.com> - 2.19.90-1
- Sync with upstream master.

* Tue Feb 04 2014 Siddhesh Poyarekar <siddhesh@redhat.com> - 2.18.90-27
- Sync with upstream master.

* Wed Jan 29 2014 Siddhesh Poyarekar <siddhesh@redhat.com> - 2.18.90-26
- Modify regular expressions to include powerpcle stubs-*.h (#1058258).

* Wed Jan 29 2014 Siddhesh Poyarekar <siddhesh@redhat.com> - 2.18.90-25
- Sync with upstream master.

* Sat Jan 25 2014 Ville Skyttä <ville.skytta@iki.fi> - 2.18.90-24
- Own the %%{_prefix}/lib/locale dir.

* Thu Jan 23 2014 Siddhesh Poyarekar <siddhesh@redhat.com> - 2.18.90-23
- Sync with upstream master.

* Thu Jan 16 2014 Siddhesh Poyarekar <siddhesh@redhat.com> - 2.18.90-22
- Back out ftell test case (#1052846).

* Tue Jan 14 2014 Siddhesh Poyarekar <siddhesh@redhat.com> - 2.18.90-21
- Sync with upstream master.
- Fix infinite loop in ftell when writing wide char data (#1052846).

* Tue Jan  7 2014 Siddhesh Poyarekar <siddhesh@redhat.com> - 2.18.90-20
- Sync with upstream master.
- Enable systemtap probes on Power and S/390.
