# Creating New Backend Services

When creating new services, they must be set up correctly before they can be used and implemented.
If all of the required setup and configs are not adhered to, the service will be unreachable or uncallable.
To avoid this, please read the following guide below on what to change and configure.



## Docker Compose

All services are run in Docker with a dedicated container per service.
Other than common and proto, the service should be located in the src/backend_services directory with a folder named after the service.
Within this folder, there must be a server.py or main.py to startup the server and a Dockerfile used to setup the service in its container correctly.
Then, in the docker-compose.yml file at the root directory, add in the service with all of the necessary details.

Such details include:-

build - specifies the files to copy and the dockerfile to use

ports - the specified ports the service runs on

networks - the required networks that are neded for database and service to service communication

volumes - used to store persistent data in relation to the service

depends_on - what containers the specified service relies on for functionality

env_file - the link to the environment variables the service requires

If the service being added needs to communicate with other gRPC services, then include the `grpc-network` to enable service to service communication.
Use the container-name that you define in the compose file in your url requests.
The service name (first line of the defined container) will not be recognised as a valid name unless both container-name and service name are the same.

If the service being added needs to store and access data, then include the `pg-network` to enable database communication.

If the service being added needs to access sessions or similar data, then include the `redis-network` to enable session communication.



## Certificate Generation

Now with the service created and functional, we need to now enable secure communications between the client and service.
Only apply these changes if the service is using https for encrypted communications.

In the ```openssl.cnf``` file at the root directory, add in DNS.# = service-name underneath [ alt_names ].
Ensure that the # in DNS.# is unique to all other alt names and then generate the self-signed certificates.

In the current implementation, all services use the exact same openssl config file.
This is for testing purposes, but can be altered in the near future to only have a config file that doesn't encapsulate all services at once.
