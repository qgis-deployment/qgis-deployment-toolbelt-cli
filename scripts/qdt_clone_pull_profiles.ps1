<#
.SYNOPSIS
    Clone or update a Git repository to a network location specified through an environment variable.

.DESCRIPTION
    This script clones a remote Git repository to a directory specified by an environment variable.
    If the repository already exists locally, it performs a `git pull` to update it.

.LICENSE
    SPDX-License-Identifier: MIT
#>

# -- VARIABLES --

# Default value if the environment variable is not set
$basePath = if ($env:QDT_LOCAL_CLONE_PROFILES_PATH) { $env:QDT_LOCAL_CLONE_PROFILES_PATH } else { "$env:USERPROFILE\GitRepositories\qdt-qgis-profiles" };

# Remote Git repository URL
$gitRepo = if ($env:QDT_REMOTE_PROFILES_GIT) { $env:QDT_REMOTE_PROFILES_GIT} else { "https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli.git" };

# Target folder for the local repository
$repoName = $gitRepo.Split("/")[-1].Replace(".git", "")
$repoPath = Join-Path -Path $basePath -ChildPath $repoName


# -- FUNCTIONS --
function Test-GitInstalled {
    try {
        # Check if Git is installed and operational
        $gitVersion = git --version 2>&1
        if ($gitVersion -match "git version") {
            Write-Host "Git is installed: $gitVersion" -ForegroundColor Green
            return $true
        } else {
            Write-Host "Git is installed but not operational." -ForegroundColor Yellow
            return $false
        }
    } catch {
        Write-Host "Git is not installed or not found in the PATH." -ForegroundColor Red
        return $false
    }
}

# -- MAIN --

# Check if Git is installed
if (-not (Test-GitInstalled)) {
    Write-Error "Git is required for this script. Please install Git and ensure it is in your PATH."
    exit 1
}

# Ensure the base directory exists, create it if necessary
if (-not (Test-Path -Path $basePath)) {
    Write-Host "The directory '$basePath' does not exist. Creating it..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $basePath | Out-Null
}


# Perform git clone or pull
try {
    # Check if the repository already exists locally
    if (Test-Path -Path $repoPath) {
        Write-Host "Repository already exists locally at $repoPath. Performing 'git pull'..." -ForegroundColor Cyan

        # Change to the repository directory
        Push-Location -Path $repoPath

        # Pull the latest changes
        git fetch --all
        git reset --hard origin/main
        # $pullResult = git pull
        # Write-Host $pullResult

        # Return to the original directory
        Pop-Location
    } else {
        Write-Host "No Git repository identified. Cloning remote repository to $repoPath..." -ForegroundColor Cyan

        # Clone the repository
        git clone --config remote.origin.pushurl="DISABLED" `
                  --depth=5 `
                  $gitRepo `
                  $repoPath
    }

    Write-Host "Operation completed successfully!" -ForegroundColor Green
} catch {
    Write-Error "An error occurred: $_"
    exit 1
}
