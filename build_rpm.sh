#!/bin/bash

BUILDROOT="`pwd`/build"
VERSION=`cat setup.py| awk -F= '/version/ { print $2 }' | sed "s/[',]//g"`
# Setup environment
mkdir -p ${BUILDROOT}/{BUILD,RPMS,SOURCES,SPECS,SRPMS}

# Build Python source package and move it to the RPM build root
python setup.py sdist
mv ./dist/zems-*.tar.gz ${BUILDROOT}/SOURCES/

rpmbuild --define "_topdir ${BUILDROOT}" --define "version ${VERSION}" -ba ./spec/zems.spec
mv ${BUILDROOT}/RPMS/noarch/zems-*.rpm ./dist/
mv ${BUILDROOT}/SRPMS/zems-*.rpm ./dist/
rm -rf ${BUILDROOT}
echo "Build of version ${VERSION} complete! RPMS can be found in the ./dist/ directory.."