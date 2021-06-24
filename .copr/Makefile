srpm:
	dnf install -y rpmdevtools dnf-plugins-core
	dnf build-dep -y glibc
	spectool -g -R glibc.spec
	rpmbuild -bs glibc.spec
	cp ~/rpmbuild/SRPMS/* $(outdir)/
