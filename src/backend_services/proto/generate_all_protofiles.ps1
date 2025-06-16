$protoDir = "src/backend_services/proto"
$outDir = "src/backend_services/common/proto"

Get-ChildItem -Path $protoDir -Filter *.proto | ForEach-Object {
    $protoFile = $_.Name
    $command = "python -m grpc_tools.protoc -I `"$protoDir`" --pyi_out=`"$outDir`" --python_out=`"$outDir`" --grpc_python_out=`"$outDir`" `"$protoFile`""

    Write-Host "Running: $command" -ForegroundColor Yellow

    # Must run inside protoDir so relative path works
    Push-Location $protoDir
    python -m grpc_tools.protoc -I .  --pyi_out=../common/proto --python_out=../common/proto --grpc_python_out=../common/proto $protoFile
    Pop-Location
}