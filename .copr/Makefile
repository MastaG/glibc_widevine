srpm:
	dnf install -y rpmdevtools dnf-plugins-core
	dnf build-dep -y glibc
	spectool -g -R glibc.spec
	mkdir -p /builddir/build/SOURCES
	cp -af *.patch /builddir/build/SOURCES/
	rpmbuild -bs glibc.spec
	cp ~/rpmbuild/SRPMS/* $(outdir)/
