<#
.Synopsis
   Download the latest version of QDT executable from GitHub Releases.
.DESCRIPTION
   This script will:
      1. retrieve latest version of QDT from GitHub Releases API
      2. identify the asset to download (*.exe)
      3. download it as C:\Users\{username}\AppData\Roaming\QDT\qdt.exe
      4. launch it with --help args to check it runs well
.LICENSE
   SPDX-License-Identifier: Apache-2.0
#>

# -- VARIABLES

# source repository
$repository = "qgis-deployment/qgis-deployment-toolbelt-cli"

# GitHub API URL for the latest release
$apiUrl = "https://api.github.com/repos/$repository/releases/latest"

# API request headers
$apiHeaders = @{"User-Agent" = "QDT upgrader from $env:computername" }

# destination path
$destinationFile = "$env:APPDATA/QDT/qdt.exe"
New-Item -ItemType Directory -Path (Split-Path $destinationFile) -Force

# -- MAIN
try {
    # Retrieve the latest release data
    Write-Host "Retrieving latest QDT release from $apiUrl..."
    $releaseData = Invoke-RestMethod -Uri $apiUrl -Headers $apiHeaders

    # Extract the latest tag and the asset download URL
    $latestTag = $releaseData.tag_name
    $asset = $releaseData.assets | Where-Object { $_.name -like "*.exe" }

    if (-not $asset) {
        Write-Error "No executable asset found in the latest release: &apiUrl"
        exit 1
    }

    Write-Host "Downloading QDT version $latestTag from $downloadUrl to $destinationFile"
    $downloadUrl = $asset.browser_download_url

    # Download the asset
    $webClient = New-Object System.Net.WebClient
    $webClient.Proxy = [System.Net.WebRequest]::DefaultWebProxy
    $webClient.Proxy.Credentials = [System.Net.CredentialCache]::DefaultNetworkCredentials
    $webClient.DownloadFile($downloadUrl, $destinationFile)

    # log it
    Write-Host "Download successful! File saved as $destinationFile" -ForegroundColor Green
}
catch {
    # If there's an error, output details
    if ($null -ne $_.Exception.Response) {
        $statusCode = $_.Exception.Response.StatusCode
        $statusDescription = $_.Exception.Response.StatusDescription
        Write-Error "API request failed with status code ${statusCode}: ${statusDescription}"
    }
    else {
        Write-Error "An error occurred: $_"
    }
}

# Run the downloaded executable with --help
Write-Host "Running qdt.exe with --help..."
#Start-Process -FilePath $destinationFile -ArgumentList "--help" -NoNewWindow -Wait
#Start-Process -FilePath $destinationFile -ArgumentList "--help" -Wait -WindowStyle Hidden
Start-Process -FilePath $destinationFile -ArgumentList "--help" -NoNewWindow -Wait
