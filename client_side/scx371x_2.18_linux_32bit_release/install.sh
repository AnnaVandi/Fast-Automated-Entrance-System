#!/bin/bash
# Install script 

# Identify the bundle path

# Try to get the USB bundle path on the fly
#bundle_path=`pkg-config libpcsclite --variable=usbdropdir`
bundle_path=
ini_path="/usr/local/identiv/ini"
ini_name="scx371x.ini"
old_bundle="SCx371x.bundle"

machine=`uname -m`
distro=`cat /etc/issue`

# if the pkg-config has failed or it returned null
# then use the default locations for copying the bundle
if [ $? != 0 -o -z "$bundle_path" ]
then
	case "$distro" in

	# Check if the distribution is SUSE
	*[Ss][Uu][Ss][Ee]*)

		# Check if it is a 64-bit OS
		if [ $machine = "x86_64" ]
		then
			bundle_path="/usr/lib64/readers"
		else
			bundle_path="/usr/lib/readers"
		fi
		;;

    # Check if the distribution is RHEL
    *[Rr][Ee][Dd]\ [Hh][Aa][Tt]\ [Ee][Nn][Tt][Ee[Rr][Pp][Rr][Ii][Ss][Ee]*)
        # Check if it is a 64-bit OS
        if [ $machine = "x86_64" ]
        then
            bundle_path="/usr/lib64/pcsc/drivers"
        else
            bundle_path="/usr/lib/pcsc/drivers"
        fi
        ;;

	# Check if the distribution is Fedora
	*[Ff][Ee][Dd][Oo][Rr][Aa]*)

		# Check if it is a 64-bit OS
		if [ $machine = "x86_64" ]
		then
			bundle_path="/usr/lib64/pcsc/drivers"
		else
			bundle_path="/usr/lib/pcsc/drivers"
		fi
		;;

	# Check if the distribution is Ubuntu
	*[Uu][Bb][Uu][Nn][Tt][Uu]*)
		bundle_path="/usr/lib/pcsc/drivers"
		;;

	# Check if the distribution is Debian
	*[De][Ee][Bb][Ii][Aa][Nn]*)
		bundle_path="/usr/lib/pcsc/drivers"
		;;

	# Check if the distribution is PCLinuxOS
	*[Pp][Cc][Ll][Ii][Nn][Uu][Xx][Oo][Ss]*)
		bundle_path="/usr/lib/pcsc/drivers"
		;;

	# For other distributions
	*)
		bundle_path="/usr/local/pcsc/drivers"
		;;
	esac
fi

#Adding script to uninstall the old bundle (i.e. SCLGENERIC.bundle Ver: 2.09)
echo "Uninstalling old bundle..."

if [ "$bundle_path" != "/usr/local/pcsc/drivers" ]
then
	echo "Removing symbolic links from : /usr/local/pcsc/drivers"
	cd ./proprietary
	for bundle in $old_bundle 
	do
		if [ $bundle = $old_bundle ]
		then
			rm -rf /usr/local/pcsc/drivers/$bundle
			break
		fi

		if [ \$? != 0 ]
		then
			echo "Failed to remove /usr/local/pcsc/drivers/$bundle symbolic link"
			exit 1
		fi
	done
	cd ..
	echo "Removed symbolic links"
fi

if [ "$bundle_path" != "/usr/local/lib/pcsc/drivers" ]
then
	echo "Removing symbolic links from : /usr/local/lib/pcsc/drivers"
	cd ./proprietary
	for bundle in $old_bundle
	do
		if [ $bundle = $old_bundle ]
		then
			rm -rf /usr/local/lib/pcsc/drivers/$bundle
			break
		fi

		if [ \$? != 0 ]
		then
			echo "Failed to remove /usr/local/lib/pcsc/drivers/$bundle symbolic link"
			exit 1
		fi
	done
	cd ..
	echo "Removed symbolic links"
fi

echo "Removing driver bundle(s) from : $bundle_path"

cd ./proprietary

for bundle in $old_bundle
do
	if [ $bundle = $old_bundle ]
	then
		rm -rf $bundle_path/$old_bundle
		break
	fi
	if [ \$? != 0 ]
	then
		echo "Failed to remove $bundle_path/$bundle bundle"
		echo "exit 1"
	fi
#	echo "Removed $old"
done

cd ..

echo "Uninstallation of old bundle completed."

# Installing the new bundle (Ver: 2.11)
echo "Installing new bundle..."

# Installation of ini file
# Create the appropriate directory for placing the ini
mkdir -p /usr/local/identiv/ini/

# Copy the ini file
echo "Copying ini file to : /usr/local/identiv/ini"
cp -f scx371x.ini /usr/local/identiv/ini/
if [ $? = 0 ]
then
	echo "Copied the ini file"
else
	echo "Failed to copy the ini file"
	exit 1
fi

# Installation of the driver bundle(s)
# Create the appropriate directory for placing the bundle(s)
mkdir -p $bundle_path

# Copy the driver bundle(s)
echo "Copying driver bundle(s) to : $bundle_path"
cp -rf ./proprietary/*.bundle $bundle_path
if [ $? = 0 ]
then
	echo "Copied driver bundle(s)"
else
	echo "Failed to copy driver bundle(s)"
	exit 1
fi


# Create symbolic link from open source pcscd bundle path
if [ "$bundle_path" != "/usr/local/pcsc/drivers" ]
then
	echo "Creating symbolic links from : /usr/local/pcsc/drivers"
	mkdir -p /usr/local/pcsc/drivers

	cd ./proprietary
	for bundle in *.bundle
	do
		ln -sf $bundle_path/$bundle /usr/local/pcsc/drivers
	done
	cd ..

	echo "Created symbolic links"
fi

if [ "$bundle_path" != "/usr/local/lib/pcsc/drivers" ]
then
	echo "Creating symbolic links from : /usr/local/lib/pcsc/drivers"
	mkdir -p /usr/local/lib/pcsc/drivers

	cd ./proprietary
	for bundle in *.bundle
	do
		ln -sf $bundle_path/$bundle /usr/local/lib/pcsc/drivers
	done
	cd ..

	echo "Created symbolic links"
fi

echo "Installation completed."

# Create uninstall script

echo "#!/bin/bash" > uninstall.sh
echo "# Uninstall script" >> uninstall.sh

echo "" >> uninstall.sh
echo "echo \"Uninstalling...\"" >> uninstall.sh

echo "" >> uninstall.sh
echo "# Uninstallation of the ini file" >> uninstall.sh
echo "echo \"Removing ini file from : /usr/local/identiv/ini\"" >> uninstall.sh
echo "rm -f /usr/local/identiv/ini/scx371x.ini" >> uninstall.sh
echo "if [ \$? = 0 ]" >> uninstall.sh
echo "then" >> uninstall.sh
echo "	echo \"Removed the ini file\"" >> uninstall.sh
echo "else" >> uninstall.sh
echo "	echo \"Failed to remove the ini file\"" >> uninstall.sh
echo "	exit 1" >> uninstall.sh
echo "fi" >> uninstall.sh
echo "" >> uninstall.sh
echo "# Uninstallation of the driver bundles(s)" >> uninstall.sh

if [ "$bundle_path" != "/usr/local/pcsc/drivers" ]
then
echo "# Remove symbolic link from open source pcscd bundle path" >> uninstall.sh
echo "echo \"Removing symbolic links from : /usr/local/pcsc/drivers\"" >> uninstall.sh
cd ./proprietary
for bundle in *.bundle
do
echo "rm -rf /usr/local/pcsc/drivers/$bundle" >> ../uninstall.sh
echo "if [ \$? != 0 ]" >> ../uninstall.sh
echo "then" >> ../uninstall.sh
echo "	echo \"Failed to remove /usr/local/pcsc/drivers/$bundle symbolic link\"" >> ../uninstall.sh
echo "	exit 1" >> ../uninstall.sh
echo "fi" >> ../uninstall.sh
done
cd ..
echo "echo \"Removed symbolic links\"" >> uninstall.sh
fi

if [ "$bundle_path" != "/usr/local/lib/pcsc/drivers" ]
then
echo "# Remove symbolic link from open source pcscd bundle path" >> uninstall.sh
echo "echo \"Removing symbolic links from : /usr/local/lib/pcsc/drivers\"" >> uninstall.sh
cd ./proprietary
for bundle in *.bundle
do
echo "rm -rf /usr/local/lib/pcsc/drivers/$bundle" >> ../uninstall.sh
echo "if [ \$? != 0 ]" >> ../uninstall.sh
echo "then" >> ../uninstall.sh
echo "	echo \"Failed to remove /usr/local/lib/pcsc/drivers/$bundle symbolic link\"" >> ../uninstall.sh
echo "	exit 1" >> ../uninstall.sh
echo "fi" >> ../uninstall.sh
done
cd ..
echo "echo \"Removed symbolic links\"" >> uninstall.sh
fi

echo "echo \"Removing driver bundle(s) from : $bundle_path\"" >> uninstall.sh

cd ./proprietary

for bundle in *.bundle
do
echo "rm -rf $bundle_path/$bundle" >> ../uninstall.sh
echo "if [ \$? != 0 ]" >> ../uninstall.sh
echo "then" >> ../uninstall.sh
echo "	echo \"Failed to remove $bundle_path/$bundle bundle\"" >> ../uninstall.sh
echo "	exit 1" >> ../uninstall.sh
echo "fi" >> ../uninstall.sh
echo "echo \"Removed $bundle\"" >> ../uninstall.sh
done

cd ..

echo "" >> uninstall.sh
echo "echo \"Uninstallation completed.\"" >> uninstall.sh

echo "" >> uninstall.sh
echo "# Remove the uninstall script" >> uninstall.sh
echo "rm -f \$0"  >> uninstall.sh

chmod +x uninstall.sh

