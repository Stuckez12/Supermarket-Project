# Supermarket-Project
## Overview



## Creating openssl certificates
### Installing openssl (Windows 11)

Instruction Source: ```https://www.youtube.com/watch?v=PgP9oGGxLG0```

To download openssl first visit this link
```https://sourceforge.net/projects/openssl/files```
to download the latest version of openssl on your computer.

Select the zip file ending in x86 and wait for it to download.
Once downloaded, extract the folder to the ```C:\``` directory.

Next, navigate yourself to the environment variables accessed through
either the advanced system settings or by typing environment variables
into the search bar in the taskbar.

Add a new user PATH to the environment settings using this directory.
```C:\OpenSSL-OQS\bin```
Note: The folder name may vary depending on which version you download.

Also add a new system variable with the following name and value:
Name: ```OPENSSL_CONF```
Value: ```C:\OpenSSL-OQS\etc\openssl.cnf```
Note: Again, the folder directory for the value may vary depending on
      which version you download and/or the location of the config file.

Once the environment variables have been set, you must restart your
computer for the changes to take effect.

Once restarted, open up the terminal in administrator mode and verify
the installation using the following command.
```openssl version```
This should display a single line output stating the installation
version, verifying the application was correctly installed.



### Generating certificates

To generate the certificate and its private key, use the following command:
```
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout localhost-key.pem -out localhost-cert.pem -config ./openssl.cnf -extensions v3_req
```

This command relies on the existance of the openssl.cnf file that
controls how the certificates and keys are generated and handled.
This prevents the need of inputting all the required information
every time you want to generate the certificates.

The following command is the same as the previously mentioned but with
each variable explained.
```
openssl req -x509 -nodes -days NUMBER_OF_DAYS -newkey rsa:2048 -keyout PRIV_KEY_LOC -out PUBL_CERT_LOC -config CONF_LOC -extensions v3_req
```

NUMBER_OF_DAYS: how long until the certificate expires
PRIV_KEY_LOC: the directory where the private key will be placed
PUBL_CERT_LOC: the directory where the public certificate will be placed
CONF_LOC: the directory where the openssl config file is located



### Setting the certificates to be trusted (Windows 11) (Google)

When running the server with an openssl certificate, Google will throw a
privacy error with the following error message and code.

This server could not prove that it is {your website}; its security certificate
is not trusted by your computer's operating system. This may be caused by a
misconfiguration or an attacker intercepting your connection.

Error Code: ```NET::ERR_CERT_DATE_INVALID```

To resolve this, we will tell Windows 11 that this certificate is to
be trusted for all users.

Instruction Source: ```https://www.youtube.com/watch?v=7oB1my_SAps&t=38s```

First, navigate yourself to ```Manage computer certificates``` accessed by typing 
```Manage computer certificates``` into the search bar in the taskbar.

Next direct yourself to ```Trusted Root Certification Authorities\Certificates```
then right-click, select `All Tasks` then `Import`.

Click Next then browse to the directory containing your `certificate.pem`.
Click Next then Finish.
