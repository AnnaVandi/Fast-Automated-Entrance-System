// ReadMe file for SCx371x driver

Version           : 2.18
Required Packages : pcsc daemon 
		    libusb library

Installation Procedure:

Step 1: Install pcsclite. The latest version of pcsclite is available at
	http://pcsclite.alioth.debian.org/

Step 2: Install libusb library. The latest version of libusb is available at
	http://libusb.sourceforge.net/download.html#stable

Step 3: Extract the tar archive and run the ./install script that comes with this package
	This will copy the following files
	1. Driver bundle to pcsclite usb drop directory

Step 5: Restart the pcsclite daemon.

Notes:
In cases where there are multiple version of the pcsclite library is present,
the daemon may get linked with the wrong library, based on the library path
settings in the user system. In that case, to link the correct library with
the pcscd as well as utilites using the library, it is advised to use the
LD_LIBRARY_PATH variable to specify the correct path. 

The exact libraries that are getting linked with the a particular
application/utility can be found be executing the "ldd" command. For ex, to
find the libraries that are linked with pcscd in /usr/local/sbin, type as below

ldd /usr/local/sbin/pcscd

To make the utility load the needed library, use LD_LIBRARY_PATH. For ex, to 
launch pcscd with the library present in /usr/local/lib, the 
following command needs to be run from the command line

LD_LIBRARY_PATH=/usr/local/lib pcscd

This links the pcscd with the library present in /usr/local/lib overriding any
other library files present in other directories.

