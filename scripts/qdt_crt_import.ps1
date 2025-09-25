<#
.Synopsis
   Download the certificate use to sign the QDT executable and import it to the local store.
.DESCRIPTION
   This script downloads a CRT certificate file from a GitHub repository, imports it into a specified certificate store on the local machine,
and sets a friendly name and description for the certificate.
.PARAMETER storeName
    The name of the Windows certificate store where the certificate will be imported. Default: "TrustedPublisher"
.PARAMETER storeScope
    The scope of the certificate store. Can be "CurrentUser" or "LocalMachine". Default: "CurrentUser".
.PARAMETER friendlyName
    The friendly name to assign to the certificate in the Windows certificate store.
.PARAMETER description
    The description to assign to the certificate (stored as a certificate property).
.EXAMPLE
    .\import_cert.ps1 -storeName Root -storeScope LocalMachine
.NOTES
    Requires to be run as administrator to import into machine-level stores.
.LICENSE
   SPDX-License-Identifier: Apache-2.0
#>


# -- VARIABLES
param(
    [string]$storeName = "TrustedPublisher",  # Default store is Trusted Publishers
    [string]$storeScope = "CurrentUser",      # default scope is CurrentUser; use "LocalMachine" for machine-wide store (requires admin rights)
    [string]$friendlyName = "QDT Code Signing Certificate",
    [string]$description = "Certificate issued by Oslandia for signing QDT executables. See online documentation: https://qgis-deployment.github.io/qgis-deployment-toolbelt-cli/."
)
# remote CRT URL
$certUrl = "https://raw.githubusercontent.com/qgis-deployment/qgis-deployment-toolbelt-cli/refs/heads/main/builder/code_signing_certificate.crt"
# local path where storing the downloaded certificate
$localCertPath = "$env:TEMP\qdt_code_signing_certificate.crt"

# -- MAIN
# validate store scope
if ($storeScope -notin @("CurrentUser","LocalMachine")) {
    Write-Error "Invalid store scope. Use 'CurrentUser' or 'LocalMachine'."
    exit 1
}

# if LocalMachine scope is requested, ensure the script is running with admin rights
if ($storeScope -eq "LocalMachine") {
    $currentUser = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
    if (-not $currentUser.IsInRole([Security.Principal.WindowsBuiltinRole]::Administrator)) {
        Write-Warning "This script requires administrator privileges for LocalMachine scope. Relaunching with elevation..."
        Start-Process -FilePath "powershell" -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`" $args" -Verb RunAs
        exit
    }
}

Invoke-WebRequest -Uri $certUrl -OutFile $localCertPath
Write-Host "Certificate downloaded to $localCertPath"

# Load the certificate
$cert = New-Object System.Security.Cryptography.X509Certificates.X509Certificate2($localCertPath)

# Add metadata to improve integration with Windows certificate manager
$cert.FriendlyName = "QDT Code Signing Certificate"
$cert.Extensions.Add(
    New-Object System.Security.Cryptography.X509Certificates.X509Extension("2.5.29.17", [System.Text.Encoding]::ASCII.GetBytes($description), $false)
)

# Open the specified certificate store (LocalMachine)
$store = New-Object System.Security.Cryptography.X509Certificates.X509Store($storeName, $storeScope)
$store.Open("ReadWrite")

# Import the certificate
$store.Add($cert)
$store.Close()


Write-Host "Certificate imported into $storeName store with scope $storeScope and Friendly Name: '$friendlyName'"
