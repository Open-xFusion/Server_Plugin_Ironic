# Server_Management_Plugin_ironic

## Ⅰ. Plug-in Introduction

The Ironic plug-in is a plug-in integrated in the OpenStack software. It is used to manage servers. By adding servers,  
you can implement the OS deployment on servers by using this plug-in.

- Plug-in name: `ironic_driver_for_iBMC`
- Plug-in version: `v1.2`
- Supported version: `OpenStack Ussuri`, `OpenStack Yoga`, `OpenStack Zed`
- Supported device: `2288H V5`, `CH121 V5`, `1288H V7`, `2288H V7`, `G5500 V7`, `G8600 V7`, `5885H V7`, `2488H V7`
- Supported iBMC Versions: `3.18 or later(V5)`, `3.06.02.09 or later(V7)`

## Ⅱ. Plug-in Functions

- OS deployment
- Startup sequence query

## Ⅲ. Prerequisites

The iBMC Client library should be installed on the ironic conductor.  
You can download the iBMC_Client installation package from Github and unzip it,then enter the ibmc_client directory and use the 'python setup.py install' command to install it.  

```bash
pip uninstall python-ibmcclient -y
curl -O https://raw.githubusercontent.com/Open-xFusion/Server_Plugin_ironic/master/release/ibmc_client.tar.gz
tar -zxf ibmc_client.tar.gz
cd ibmc_client
python setup.py install
```

## Ⅳ. Install/Uninstall iBMC driver  

This guide is based on Ubuntu 18.04.
If you need to adopt yoga version, use the following OS:

- Ubuntu 20.04 or later
- CentOS Strame 8 or later

### 1. Installing Plug-in

- Connect to the OpenStack Ussuri environment.

- download and install  [driver](https://github.com/Open-xFusion/Server_Plugin_Openstack)
-- Verify the integrity of the ironic plug-in software package.
     a. Go to the directory where the plug-in software package and SHA256 verification file are stored.
     b. Run the sha256sum -c < (grep 'software package name' 'sha256 verification file name') command to verify the software package.Example: sha256sum -c <(grep 'ironic-ibmc-driver-patch.tar.gz' 'ironic-ibmc-driver-patch.tar.sha256.sum')
     c. Check whether the verification result is OK.
      - If yes, the software package has not been tampered with and can be used.
      - If no, the software package has been tampered with. Obtain a new software package.

```bash
mkdir ~/ironic-ibmc-driver
cd ~/ironic-ibmc-driver
curl -O https://raw.githubusercontent.com/Open-xFusion/Server_Plugin_ironic/master/release/ironic-ibmc-driver-patch.tar.gz
tar zxvf ironic-ibmc-driver-patch.tar.gz
sudo ./install.sh uninstall
sudo ./install.sh
```

- Export fake OpenStack authentication info

```bash
export OS_ENDPOINT=http://127.0.0.1:6385
export OS_AUTH_TYPE=none
```

- Restart Ironic conductor service

Restart ironic conductor to load ibmc hardware type, then list enabled driver list to validate whether `ibmc` driver is installed successfully.  

```bash
## restart ironic
# Ubuntu
sudo service ironic-conductor restart
# CentOS
sudo systemctl restart openstack-ironic-conductor

# query driver list
openstack baremetal driver list

+---------------------+----------------+
| Supported driver(s) | Active host(s) |
+---------------------+----------------+
| ibmc                | 192.168.0.10   |
+---------------------+----------------+
```

### 2. Uninstalling driver

``` bash
sudo ./install.sh uninstall
```

## Ⅴ. Create bare metal server node

The process below shows how to deploy an ibmc server using `pxe`, we are assuming that you are using a **[standalone Ironic](https://docs.openstack.org/project-install-guide/baremetal/newton/standalone.html)** environment. If your ironic environment is different, you can directly check the creating node segment, that is the only difference between `ibmc` driver than other drivers.

1. Setup baremetal Boot mode

    ```text
    Restart the bare metal server, press F11 to enter the Boot menu of the BIOS, and change the value of Boot Type to `Legacy Boot`.
    ```

2. Insure required services is running

    ```bash
    # Ubuntu
    systemctl status ironic-api
    systemctl status ironic-conductor
    systemctl status nginx
    systemctl status dnsmasq
    # CentOS
    systemctl status openstack-ironic-api
    systemctl status openstack-ironic-conductor
    systemctl status httpd
    systemctl status dnsmasq
    ```

    if services is not runing, use `systemctl start xxx` to run the service.

3. Enrolling node with ibmc driver

    Set node's `driver` property to `ibmc` to using the driver.
    The following properties specified in the node's `driver_info` property are required:
    - `ibmc_address`: https endpoint of ibmc server
    - `ibmc_username`: username of ibmc account
    - `ibmc_password`: password of ibmc account
    - `ibmc_verify_ca`: if ibmc_address has the https scheme, the
    driver will use a secure (TLS) connection when talking to the iBMC. By default (if this is not set or set to True), the driver will try to verify the host certificates. This can be set to the path of a certificate file or directory with trusted certificates that the driver will use for verification. To disable verifying TLS, set this to False. This is optional.

    ```bash
    baremetal_name="your-bare-metal-name"
    baremetal_deploy_kernel="file:///var/lib/ironic/http/deploy/coreos_production_pxe.vmlinuz"
    baremetal_deploy_ramdisk="file:///var/lib/ironic/http/deploy/coreos_production_pxe_image-oem.cpio.gz"
    baremetal_ibmc_addr="https://your-ibmc-server-host"
    baremetal_ibmc_user="your-ibmc-server-user-account"
    baremetal_ibmc_pass="your-ibmc-server-user-password"
    NODE=$(openstack baremetal node create --name "$baremetal_name" --network-interface "noop"\
        --boot-interface "pxe" --deploy-interface "direct" \
        --driver "ibmc" \
        --property capabilities="boot_mode:bios" \
        --driver-info ibmc_address="$baremetal_ibmc_addr" \
        --driver-info ibmc_username="$baremetal_ibmc_user" \
        --driver-info ibmc_password="$baremetal_ibmc_pass" \
        --driver-info ibmc_verify_ca="False" \
        --driver-info deploy_kernel="$baremetal_deploy_kernel" \
        --driver-info deploy_ramdisk="$baremetal_deploy_ramdisk" \
        -f value -c uuid)
    ```

4. Creating a Port

    Create port for bare metal server node. You can get MAC by:

    Log in to the iBMC WebUI, choose System Info > Network, and view the NIC MAC address information.

    ```bash
    baremetal_mac="****" # MAC address of the NIC corresponding to the bare metal server
    openstack baremetal port create --node $NODE "$baremetal_mac"
    ```

    For Example:

    ```bash
    openstack baremetal port create --node $NODE "58:F9:87:7A:A9:73"
    openstack baremetal port create --node $NODE "58:F9:87:7A:A9:74"
    openstack baremetal port create --node $NODE "58:F9:87:7A:A9:75"
    openstack baremetal port create --node $NODE "58:F9:87:7A:A9:76"
    ```

## Ⅵ. Configuring the RAID

Refer to related documents before configuring the RAID. Then node status must be：

- ironic raid configuration：<https://docs.openstack.org/ironic/latest/admin/raid.html>

### Configuring target raid config

1.Modify the logical disk configuration file as required and place the reference file in the directory of user home.

```bash

# Modify the RAID drive as required
  vi raid-config.json 

  {
    "logical_disks": [
     {
          "size_gb": "MAX",
          "raid_level": "0",
          "is_root_volume": true
    }]
  }

2. Set the RAID configuration option in the node
openstack baremetal node set --target-raid-config raid-config.json "$NODE"
```

### Execute RAID configuration

```bash

1. Modify the RAID drive as required
vi clean-steps.json

[{
    "interface": "raid",
    "step": "delete_configuration"
},
{
    "interface": "raid",
    "step": "create_configuration"
}]

2. Perform clean step

```bash
openstack baremetal node clean "$NODE" --clean-steps ./clean-steps.json
```

## Ⅶ. Deploy Nodes using ibmc driver

1. Configuring the OS Image to be deployed 

    ```bash
    baremetal_image="http://192.168.0.100/images/ubuntu-xenial-16.04.qcow2"
    # You can run md5sum /var/lib/ironic/http/images/ubuntu-xenial-16.04.qcow2 to calculate the value.
    baremetal_image_checksum="f3e563d5d77ed924a1130e01b87bf3ec" 

    openstack baremetal node set "$NODE" \
    --instance-info image_source="$baremetal_image" \
    --instance-info image_checksum="$baremetal_image_checksum" \
    --instance-info root_gb="10"
    ```

2. Inspect the created node

    Run `node show` to confirm the configurations is all right:

    ```bash
    openstack baremetal node show $NODE -f json
    ```

3. Deploying Node

    ```bash
    openstack baremetal node manage "$NODE" &&
    openstack baremetal node provide "$NODE" &&
    openstack baremetal node deploy $NODE 
    ```

## Ⅷ. Customer calls provided by ibmc driver

- Querying vendor specific pass through method:

    ```bash
    openstack baremetal node passthru list $NODE
    ```

- Querying the boot sequence:

    ```bash
    openstack baremetal node passthru call --http-method GET $NODE boot_up_seq
    ```
