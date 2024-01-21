#!/bin/bash
# Uninstall script

echo "Uninstalling..."

# Uninstallation of the ini file
echo "Removing ini file from : /usr/local/identiv/ini"
rm -f /usr/local/identiv/ini/scx371x.ini
if [ $? = 0 ]
then
	echo "Removed the ini file"
else
	echo "Failed to remove the ini file"
	exit 1
fi

# Uninstallation of the driver bundles(s)
# Remove symbolic link from open source pcscd bundle path
echo "Removing symbolic links from : /usr/local/lib/pcsc/drivers"
rm -rf /usr/local/lib/pcsc/drivers/SCx371x.bundle
if [ $? != 0 ]
then
	echo "Failed to remove /usr/local/lib/pcsc/drivers/SCx371x.bundle symbolic link"
	exit 1
fi
echo "Removed symbolic links"
echo "Removing driver bundle(s) from : /usr/local/pcsc/drivers"
rm -rf /usr/local/pcsc/drivers/SCx371x.bundle
if [ $? != 0 ]
then
	echo "Failed to remove /usr/local/pcsc/drivers/SCx371x.bundle bundle"
	exit 1
fi
echo "Removed SCx371x.bundle"

echo "Uninstallation completed."

# Remove the uninstall script
rm -f $0
