# Generating HTTPS Certificates and Private Keys For Services
## Single File Action

All services use https to securely encrypt data between the client and server which protects against man-in-the-middle attacks.
This involves both a certificate which is publically accessible and a private key that is stored server side.
The server sends the certificate to the client for them to check the validity of the certificate before establishing a connection.

To generate both the certificate and private key, the following command below creates a self-signed certificate.
Self-signed certificates should only be used for development and testing.
In production or public-facing systems, it is recommended to obtain certificates from a trusted Certificate Authority (CA) such as DigiCert at ```https://www.digicert.com```.

For development purposes only, use the following command below to generate the certificate and private key.

```
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout ./src/backend_services/common/certificates/account/account-key.pem -out ./src/backend_services/common/certificates/account/account-cert.pem -config ./openssl.cnf -extensions v3_req
```

The above command is an example of generating a certificate for the account service.
To use and adapt the command to your own needs use the following command below and switch the placeholders for your own unique circumstance.

```
openssl req -x509 -nodes -days DAYS -newkey rsa:2048 -keyout FILE_LOCATION-key.pem -out FILE_LOCATION-cert.pem -config CONFIG_LOCATION -extensions v3_req
```

Each variable in the command you can safely alter
DAYS: - an integer representing how long the certificate should be valid for in days.
FILE_LOCATION: - the location of the specified file. Note: the file location for both the -cert.pem and -key.pem can be different.
CONFIG_LOCATION: - the location of the config file that openssl requires to format the certificates. Note: the config file should contain detains about the website and "your company".



## Proto Folder Action

Another more simple way to create the required certificates is to run the ps1 file (Windows 10/11).
This by default will not work for Windows as it uses PowerShell to execute.
Running scripts on Windows is disabled by default due to security reasons.
To bypass this, the following command below enables the execution of LOCAL scripts.
Downloaded scripts must be signed for.

```
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

To reset the execution policy to its previous state, run the following command below.

```
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy Restricted
```

When the PowerShell execution policy has been enabled, it is now possible to run the following command below.

```
./src/backend_services/common/certificates/generate_certificates.ps1
```

This command will execute all certificate generation commands for every service listed within the ps1 file.
All the services are listed in the $services variable (Line 8).

Once ran, make sure to reset the execution policy to its default settings.
