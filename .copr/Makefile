srpm:
	dnf install -y rpmdevtools dnf-plugins-core
	dnf build-dep -y glibc
	spectool -g -R glibc.spec
	mkdir -p /builddir/build/SOURCES
	mkdir -p /builddir/build/SPECS
	mv glibc.spec /builddir/build/SPECS/
	mv * /builddir/build/SOURCES/
	cd /builddir/build/SPECS
	rpmbuild -bs glibc.spec
	cp /builddir/build/SRPMS/* $(outdir)/
