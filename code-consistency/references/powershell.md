# PowerShell Code Consistency Reference

## Table of Contents
1. [Naming Conventions](#1-naming-conventions)
2. [Error Handling](#2-error-handling)
3. [Module Structure & Packaging](#3-module-structure--packaging)
4. [Logging & Observability](#4-logging--observability)

---

## 1. Naming Conventions

### Authoritative baseline: PowerShell Practice and Style Guide + Cmdlet Development Guidelines
Detect and match the project's existing style first. Below is the standard baseline.

| Symbol | Convention | Example |
|---|---|---|
| Functions (public) | `PascalCase` Verb-Noun | `Get-UserAccount`, `Set-DatabaseConfig` |
| Functions (private/helper) | `PascalCase`, may omit approved verb | `ValidateInput`, `FormatOutput` |
| Variables | `PascalCase` or `camelCase` (match project) | `$UserName`, `$retryCount` |
| Parameters | `PascalCase` | `-FilePath`, `-ComputerName` |
| Constants | `PascalCase` with descriptive name | `$MaxRetryCount`, `$DefaultTimeout` |
| Modules | `PascalCase` | `ActiveDirectoryTools` |
| Classes | `PascalCase` | `[ServerConfiguration]` |
| Enums | `PascalCase` type + values | `[LogLevel]::Warning` |
| Script filenames | `PascalCase` Verb-Noun or descriptive | `Deploy-Application.ps1` |
| Private scope | Prefix with script scope or `_` convention | `$script:_cache` |

**Approved verbs:** Always use `Get-Verb` output. Common: Get, Set, New, Remove, Start, Stop,
Enable, Disable, Invoke, Test, Update, Import, Export, ConvertTo, ConvertFrom.

**Critical rules:**
- 🔴 Always use approved verbs for public functions — `Get-Verb` is authoritative
- 🔴 Use full parameter names in scripts, not aliases (`-ComputerName` not `-CN`)
- 🔴 Never use positional parameters in scripts (only OK in interactive shell)
- 🟡 Use singular nouns: `Get-Process` not `Get-Processes`
- 🟡 Avoid Hungarian notation (`$strName`, `$intCount`) — PowerShell is dynamically typed

---

## 2. Error Handling

### ErrorAction and try/catch
```powershell
# CRITICAL: Set strict mode at script top
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# Try/catch for terminating errors
try {
    $result = Get-Content -Path $FilePath -ErrorAction Stop
} catch [System.IO.FileNotFoundException] {
    Write-Error "Config file not found: $FilePath"
    return $null
} catch {
    Write-Error "Unexpected error reading ${FilePath}: $_"
    throw
}
```

### Terminating vs non-terminating
- 🔴 Use `-ErrorAction Stop` when you need to catch errors from cmdlets
- 🔴 Use `$ErrorActionPreference = 'Stop'` at script scope for safety
- 🔴 Use `throw` for custom terminating errors, not `Write-Error` alone
- 🟡 Check `$LASTEXITCODE` after native executables: `if ($LASTEXITCODE -ne 0) { throw "..." }`

### Validation
```powershell
# Parameter validation (preferred over manual checks)
param(
    [Parameter(Mandatory)]
    [ValidateNotNullOrEmpty()]
    [string]$ServerName,

    [ValidateRange(1, 65535)]
    [int]$Port = 443,

    [ValidateSet('Production', 'Staging', 'Development')]
    [string]$Environment = 'Production'
)
```

**Critical rules:**
- 🔴 Use `[CmdletBinding()]` on all advanced functions
- 🔴 Use `[Parameter(Mandatory)]` not manual null checks
- 🔴 Support `-WhatIf` and `-Confirm` for destructive operations via `SupportsShouldProcess`

---

## 3. Module Structure & Packaging

### Script module layout
```
MyModule/
├── MyModule.psd1              # module manifest
├── MyModule.psm1              # root module (dot-sources others)
├── Public/
│   ├── Get-Widget.ps1
│   └── Set-Widget.ps1
├── Private/
│   ├── ValidateWidget.ps1
│   └── FormatOutput.ps1
├── Classes/
│   └── WidgetConfig.ps1
├── Tests/
│   ├── Get-Widget.Tests.ps1   # Pester tests
│   └── Set-Widget.Tests.ps1
└── README.md
```

### Module manifest essentials (.psd1)
```powershell
@{
    RootModule        = 'MyModule.psm1'
    ModuleVersion     = '1.0.0'
    FunctionsToExport = @('Get-Widget', 'Set-Widget')  # explicit, never '*'
    CmdletsToExport   = @()
    VariablesToExport  = @()
    AliasesToExport    = @()
}
```

**Critical rules:**
- 🔴 Never use `Export-ModuleMember *` or wildcard exports
- 🔴 Separate public and private functions into directories
- 🟡 One function per file, filename matches function name
- 🟡 Use Pester for testing, follow `*.Tests.ps1` naming convention
- 🟡 Dot-source in `.psm1`: `Get-ChildItem "$PSScriptRoot/Public/*.ps1" | ForEach-Object { . $_ }`

---

## 4. Logging & Observability

### Write-* cmdlets
```powershell
Write-Verbose "Processing item $($item.Name)"      # -Verbose flag
Write-Debug   "Cache state: $($cache | ConvertTo-Json)"  # -Debug flag
Write-Warning "Deprecated parameter used: -OldParam"
Write-Error   "Failed to connect to $ServerName"
Write-Information "Operation completed: $count items"  # -InformationAction

# NEVER use Write-Host for logging (it bypasses streams)
# Write-Host is ONLY for interactive UI/formatting
```

### Structured output for automation
```powershell
# Emit objects, not strings — consumers can format as needed
[PSCustomObject]@{
    Timestamp  = Get-Date -Format 'o'
    Level      = 'INFO'
    Message    = 'Deployment complete'
    Server     = $ServerName
    Duration   = $elapsed.TotalSeconds
}
```

**Critical rules:**
- 🔴 Never use `Write-Host` for logging — use `Write-Verbose`/`Write-Information`
- 🔴 Always support `-Verbose` via `[CmdletBinding()]`
- 🟡 Use `Write-Progress` for long-running operations with clear activity descriptions
- 🟡 Emit structured objects when output may be piped or consumed programmatically
- 🟡 For transcript logging: `Start-Transcript` at script entry, `Stop-Transcript` in finally block
