#!/bin/bash
set -e

code_path=$(dirname "$(readlink -f "$0")")/..
plugin_version=1.2

# 打包ibmc_client
cd "${code_path}"/ibmc_client
rm -rf tests
rm -rf .gitignore

cd "${code_path}"
tar -zcvf ibmc_client.tar.gz ibmc_client
sha256sum ibmc_client.tar.gz >ibmc_client.sha256.sum

# 打包ironic-ibmc-driver-patch
cd "${code_path}"/ironic-ibmc-driver-patch/
rm -rf ironic/tests

chmod -R 755 ironic
chmod -R 644 ironic/conf/ibmc.py
chmod -R 644 ironic/drivers/ibmc.py
chmod -R 644 ironic/drivers/modules/ibmc/*.py
chmod +x install.sh

tar -cvf ironic-ibmc-driver-patch.tar ./ironic
tar -zcvf ../ironic-ibmc-driver-patch_${plugin_version}.tar.gz ironic-ibmc-driver-patch.tar install.sh
rm -f ironic-ibmc-driver-patch.tar

cd ..
sha256sum ironic-ibmc-driver-patch_${plugin_version}.tar.gz >ironic-ibmc-driver-patch_${plugin_version}.sha256.sum