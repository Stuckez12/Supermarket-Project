Write-Output "Generating Certificates And Private Keys"

$certificate_lifetime_days = 365
$certificate_directory = "./src/backend_services/common/certificates"

$config_directory = "./openssl.cnf"

$services  = @("account", "website")

foreach ($service in $services) {
    $certificate_folder = $certificate_directory + "/$service"

    ## Create Folder For Certificates
    if (-not (Test-Path $certificate_folder)) { New-Item -ItemType Directory -Path $certificate_folder | Out-Null }

    ## Generate Certificates
    openssl req -x509 -nodes -days $certificate_lifetime_days -newkey rsa:2048 -keyout ($certificate_folder + "/$service-key.pem") -out ($certificate_folder + "/$service-cert.pem") -config $config_directory -extensions v3_req *> $null
    Write-Output "Generated $service Certificate And Private Key"
}

Write-Output "Generation Complete"