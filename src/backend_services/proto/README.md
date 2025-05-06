# Converting Proto Files to Python

Communications between each service will be handled by Googles protobufs' method.
Proto files are created specifying the name and type of data that will be sent across.
However, python is unable to use these .proto files as they are formatted to transfer data.

To solve this, we use the following command shown below.

```
python -m grpc_tools.protoc -Isrc/backend_services/proto --pyi_out=src/backend_services/common/proto --python_out=src/backend_services/common/proto --grpc_python_out=src/backend_services/common/proto  src/backend_services/proto/your_protofile_here.proto
```

This command generates two python files that can be used to communicate between the services.
To use the command, replace ```your_protofile_here.proto``` with the name of the protofile
you want to generate and then execute in the command terminal.

Another more simple way to create these .py proto files is to run the ps1 file (Windows 10/11).
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

When the PowerShell execution policy has been enabled, it is now possible
to run the following command below.

```
.\src\backend_services\proto\generate_all_protofiles.ps1
```

This command will execute the python protofile generation command for
every protofile within ```src/backend_services/proto``` file location.

Once ran, make sure to reset the execution policy to its default settings.
