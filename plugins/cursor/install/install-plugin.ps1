#Requires -Version 5.1
<#
.SYNOPSIS
  Install Tugite Cursor plugin for the current user from a Git remote (main by default).

.DESCRIPTION
  Clones the Tugite repository and copies plugins/cursor into
  $env:USERPROFILE\.cursor\plugins\local\tugite. Symlink installs are not supported.

.PARAMETER Check
  Report installation status without changing files.

.PARAMETER Force
  Explicitly overwrite an existing or outdated installation.

.PARAMETER User
  Install to the Cursor user local plugin directory. Required.

.PARAMETER RepoUrl
  Git remote URL or local repository path.

.PARAMETER Ref
  Branch or tag to install. Default: main.
#>
[CmdletBinding()]
param(
    [switch]$Check,
    [switch]$Force,
    [switch]$User,
    [string]$RepoUrl = "https://github.com/akitanabe/tugite.git",
    [string]$Ref = "main"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Write-Usage {
    @"
Usage:
  install-plugin.ps1 [-Check | -Force] -User [-RepoUrl <url>] [-Ref <ref>]

Clone the Tugite repository and copy plugins/cursor into the Cursor user local plugin directory.

Options:
  -Check               Report installation status without changing files
  -Force               Explicitly overwrite an existing or outdated installation
  -User                Install to `$env:USERPROFILE\.cursor\plugins\local\tugite
  -RepoUrl <url>       Git remote or local repository path
  -Ref <ref>           Branch or tag to install (default: main)
"@
}

function Test-IsReparsePoint {
    param([Parameter(Mandatory = $true)][string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) {
        return $false
    }
    $item = Get-Item -LiteralPath $Path -Force
    return [bool]($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint)
}

function Assert-NotReparsePoint {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$Label
    )
    if (Test-IsReparsePoint -Path $Path) {
        throw "Refusing symlinked ${Label}: $Path"
    }
}

function Get-ManifestVersion {
    param([Parameter(Mandatory = $true)][string]$ManifestPath)
    $json = Get-Content -LiteralPath $ManifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
    if (-not $json.version) {
        throw "Unable to read version from $ManifestPath"
    }
    return [string]$json.version
}

function Copy-Tree {
    param(
        [Parameter(Mandatory = $true)][string]$Source,
        [Parameter(Mandatory = $true)][string]$Destination
    )
    New-Item -ItemType Directory -Path $Destination -Force | Out-Null
    Copy-Item -Path (Join-Path $Source "*") -Destination $Destination -Recurse -Force
}

if ($Check -and $Force) {
    Write-Usage | Write-Error
    exit 2
}
if (-not $User) {
    Write-Usage | Write-Error
    exit 2
}

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    throw "Required command not found: git"
}

$homeDir = $env:USERPROFILE
if ([string]::IsNullOrWhiteSpace($homeDir)) {
    throw "USERPROFILE is required"
}

$cursorRoot = Join-Path $homeDir ".cursor"
$pluginsRoot = Join-Path $cursorRoot "plugins"
$localRoot = Join-Path $pluginsRoot "local"
$destDir = Join-Path $localRoot "tugite"
$versionFile = Join-Path $destDir ".tugite-version"
$commitFile = Join-Path $destDir ".tugite-commit"
$sourceFile = Join-Path $destDir ".tugite-source"
$refFile = Join-Path $destDir ".tugite-ref"

Assert-NotReparsePoint -Path $homeDir -Label "home directory"
Assert-NotReparsePoint -Path $cursorRoot -Label ".cursor directory"
Assert-NotReparsePoint -Path $pluginsRoot -Label "plugins directory"
Assert-NotReparsePoint -Path $localRoot -Label "local plugins directory"
Assert-NotReparsePoint -Path $destDir -Label "plugin destination"
Assert-NotReparsePoint -Path $versionFile -Label "version marker"
Assert-NotReparsePoint -Path $commitFile -Label "commit marker"

$workDir = Join-Path ([System.IO.Path]::GetTempPath()) ("tugite-cursor-install-" + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $workDir -Force | Out-Null
try {
    $cloneDir = Join-Path $workDir "src"
    & git clone --depth 1 --branch $Ref --single-branch -- $RepoUrl $cloneDir | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw "git clone failed with exit code $LASTEXITCODE"
    }

    $pluginSrc = Join-Path $cloneDir "plugins\cursor"
    $manifest = Join-Path $pluginSrc ".cursor-plugin\plugin.json"
    if (-not (Test-Path -LiteralPath $manifest -PathType Leaf)) {
        throw "Missing Cursor plugin manifest in cloned source: $manifest"
    }

    $bundledVersion = Get-ManifestVersion -ManifestPath $manifest
    $bundledCommit = (& git -C $cloneDir rev-parse HEAD).Trim()
    if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($bundledCommit)) {
        throw "Unable to resolve cloned commit"
    }

    $installedVersion = "not installed"
    $installedCommit = "not installed"
    if (Test-Path -LiteralPath $versionFile -PathType Leaf) {
        $installedVersion = (Get-Content -LiteralPath $versionFile -Raw).Trim()
    }
    if (Test-Path -LiteralPath $commitFile -PathType Leaf) {
        $installedCommit = (Get-Content -LiteralPath $commitFile -Raw).Trim()
    }
    elseif (Test-Path -LiteralPath $destDir) {
        $installedCommit = "unknown"
        if ($installedVersion -eq "not installed") {
            $installedVersion = "unknown"
        }
    }

    $manifestInstalled = Join-Path $destDir ".cursor-plugin\plugin.json"
    $isUpToDate = ($installedCommit -eq $bundledCommit) -and
        ($installedVersion -eq $bundledVersion) -and
        (Test-Path -LiteralPath $manifestInstalled -PathType Leaf)

    if ($isUpToDate) {
        Write-Output "Cursor plugin is up to date (version $bundledVersion, commit $bundledCommit): $destDir"
        exit 0
    }

    Write-Output @"
Cursor plugin update status:
  installed version: $installedVersion
  installed commit:  $installedCommit
  bundled version:   $bundledVersion
  bundled commit:    $bundledCommit
  source:            $RepoUrl ($Ref)
  target:            $destDir
"@

    if ($Check) {
        exit 3
    }

    if ($installedVersion -ne "not installed" -and -not $Force) {
        Write-Error "Existing Cursor plugin was not changed. Confirm the overwrite explicitly, then rerun with -Force."
        exit 3
    }

    $stagingDir = Join-Path $workDir "staging"
    Copy-Tree -Source $pluginSrc -Destination $stagingDir
    Set-Content -LiteralPath (Join-Path $stagingDir ".tugite-version") -Value $bundledVersion -Encoding ascii
    Set-Content -LiteralPath (Join-Path $stagingDir ".tugite-commit") -Value $bundledCommit -Encoding ascii
    Set-Content -LiteralPath (Join-Path $stagingDir ".tugite-source") -Value $RepoUrl -Encoding ascii
    Set-Content -LiteralPath (Join-Path $stagingDir ".tugite-ref") -Value $Ref -Encoding ascii

    New-Item -ItemType Directory -Path $localRoot -Force | Out-Null
    if (Test-Path -LiteralPath $destDir) {
        Remove-Item -LiteralPath $destDir -Recurse -Force
    }
    Move-Item -LiteralPath $stagingDir -Destination $destDir

    Write-Output @"
Installed Tugite Cursor plugin version $bundledVersion
  commit: $bundledCommit
  path:   $destDir

IMPORTANT:
  Restart Cursor, or run Developer: Reload Window, before using the plugin.
  Symlink installs are not supported; rerun this installer to update from Git.
"@
}
finally {
    if (Test-Path -LiteralPath $workDir) {
        Remove-Item -LiteralPath $workDir -Recurse -Force -ErrorAction SilentlyContinue
    }
}
