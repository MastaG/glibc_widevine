srpm:
	dnf install -y rpmdevtools
	dnf build-dep -y glibc
	spectool -g glibc.spec
	rpmbuild -bs glibc.spec
	cp ~/rpmbuild/SRPMS/* $(outdir)/
