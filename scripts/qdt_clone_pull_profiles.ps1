<#
.SYNOPSIS
    Clone or update a Git repository to a network location specified through an environment variable.

.DESCRIPTION
    This script clones a remote Git repository to a directory specified by an environment variable.
    If the repository already exists locally, it resets it on the remote branch.

    Designed to run unattended (scheduled task): it checks the exit code of every git
    command, never prompts for credentials and supports a GitLab deploy token.

.LICENSE
    SPDX-License-Identifier: MIT
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# -- VARIABLES --

# Default value if the environment variable is not set
$basePath = if ($env:QDT_LOCAL_CLONE_PROFILES_PATH) { $env:QDT_LOCAL_CLONE_PROFILES_PATH } else { "$env:USERPROFILE\GitRepositories\qdt-qgis-profiles" }

# Remote Git repository URL, without any credential in it
$gitRepo = if ($env:QDT_REMOTE_PROFILES_GIT) { $env:QDT_REMOTE_PROFILES_GIT } else { "https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli.git" }

# Branch to deploy
$gitBranch = if ($env:QDT_PROFILES_GIT_BRANCH) { $env:QDT_PROFILES_GIT_BRANCH } else { "main" }

# Optional access token (ypically deploy token)
$gitToken = $env:QDT_GIT_TOKEN
$gitUsername = $env:QDT_GIT_USERNAME

# Target folder for the local repository
$repoName = ($gitRepo.TrimEnd("/") -split "/")[-1] -replace "\.git$", ""
$repoPath = Join-Path -Path $basePath -ChildPath $repoName

# Long paths are required for QGIS profiles (python/plugins/...)
$gitOptions = @("-c", "core.longpaths=true")

# The token is passed as a transient HTTP header: it is never written into
# <repoPath>\.git\config, which is readable by every workstation of the fleet.
if ($gitToken) {
    $basicAuth = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes("${gitUsername}:${gitToken}"))
    $gitOptions += @("-c", "http.extraHeader=Authorization: Basic $basicAuth")
}

# disable prompts for credentials: on a scheduled task it would hang forever
$env:GIT_TERMINAL_PROMPT = "0"
$env:GCM_INTERACTIVE = "never"


# -- FUNCTIONS --

function Invoke-Git {
    <#
    .SYNOPSIS
        Run git and throw if it fails.

    .DESCRIPTION
        PowerShell try/catch does not catch native command failures: without this
        check, a failed clone or reset is ignored and the script reports success
        while the whole fleet keeps deploying outdated profiles.
    #>
    param([Parameter(Mandatory = $true)][string[]]$Arguments)

    & git @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "git $($Arguments -join ' ') failed with exit code $LASTEXITCODE."
    }
}


# -- MAIN --

# Check if Git is installed
if (-not (Get-Command -Name "git" -CommandType Application -ErrorAction SilentlyContinue)) {
    Write-Error "Git is required for this script. Please install Git and ensure it is in your PATH."
    exit 1
}

# Ensure the base directory exists, create it if necessary
if (-not (Test-Path -LiteralPath $basePath)) {
    Write-Host "The directory '$basePath' does not exist. Creating it..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $basePath -Force | Out-Null
}

try {
    # An interrupted clone leaves a folder that exists but is not a repository
    & git -C $repoPath rev-parse --git-dir 2>$null | Out-Null
    $isGitRepository = ($LASTEXITCODE -eq 0)

    if ($isGitRepository) {
        Write-Host "Repository already exists locally at $repoPath. Updating..." -ForegroundColor Cyan

        # `git -C` is used instead of Push-Location: a UNC path is not a valid
        # working directory for a native process.
        Invoke-Git -Arguments ($gitOptions + @("-C", $repoPath, "fetch", "--prune", "--depth=1", "origin", $gitBranch))
        Invoke-Git -Arguments ($gitOptions + @("-C", $repoPath, "reset", "--hard", "FETCH_HEAD"))
        # `reset --hard` keeps untracked files: without `clean`, a file deleted
        # upstream would be deployed to the workstations forever.
        Invoke-Git -Arguments ($gitOptions + @("-C", $repoPath, "clean", "-ffd"))
    }
    else {
        if (Test-Path -LiteralPath $repoPath) {
            Write-Warning "'$repoPath' is not a Git repository. Removing it."
            Remove-Item -LiteralPath $repoPath -Recurse -Force
        }
        Write-Host "No Git repository identified. Cloning remote repository to $repoPath..." -ForegroundColor Cyan
        Invoke-Git -Arguments ($gitOptions + @("clone", "--depth=1", "--single-branch", "--branch", $gitBranch, "--", $gitRepo, $repoPath))
    }

    $head = (& git -C $repoPath log -1 --format="%h %cI")
    Write-Host "Operation completed successfully! HEAD=$head" -ForegroundColor Green
}
catch {
    Write-Error "An error occurred: $_"
    exit 1
}
